"""
LangChain FAISS vector store.

Architecture:
  - One "collection" = one LangChain FAISS index, persisted as <name>.faiss + <name>.pkl
  - Embeddings are L2-normalised; FAISS IndexFlatL2 is used internally.
  - score = 1 - (L2_dist² / 2)  →  equivalent to cosine similarity for normalised vectors
  - Singleton pattern: one FAISSVectorStore instance shared across the FastAPI process
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path

import numpy as np
from langchain_community.vectorstores import FAISS as LangchainFAISS

from app.rag.embedder import get_embedder

logger = logging.getLogger(__name__)

_STORE_DIR = Path(__file__).parent.parent.parent / "data" / "vector_store"


def _cosine_relevance(l2_dist: float) -> float:
    """Convert L2 distance (for L2-normalised vectors) to cosine similarity.
    For unit vectors: cosine_sim = 1 - l2_dist² / 2
    """
    return float(max(0.0, min(1.0, 1.0 - (l2_dist ** 2) / 2.0)))


class FAISSVectorStore:
    """Thread-safe, file-backed FAISS vector store with named collections."""

    def __init__(self, store_dir: Path = _STORE_DIR):
        self._dir = store_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        # collection_name -> LangchainFAISS instance
        self._collections: dict[str, LangchainFAISS] = {}
        self._load_all()

    # ── Persistence helpers ──────────────────────────────────────────────────

    def _load_all(self):
        """Load all persisted FAISS collections from disk."""
        embedder = get_embedder()
        for faiss_file in self._dir.glob("*.faiss"):
            name = faiss_file.stem
            try:
                index = LangchainFAISS.load_local(
                    str(self._dir),
                    embedder,
                    index_name=name,
                    allow_dangerous_deserialization=True,
                    relevance_score_fn=_cosine_relevance,
                )
                self._collections[name] = index
                logger.info("Loaded FAISS collection '%s': %d docs", name, index.index.ntotal)
            except Exception as exc:
                logger.warning("Could not load FAISS collection '%s': %s", name, exc)

    def _save(self, name: str):
        """Persist a collection to disk."""
        self._collections[name].save_local(str(self._dir), index_name=name)

    def _build_index(self, docs: list[dict], embeddings: np.ndarray) -> LangchainFAISS:
        """Create a new LangChain FAISS index from docs + pre-computed embeddings."""
        embedder = get_embedder()
        texts = [d.get("text", "") for d in docs]
        text_embeddings = list(zip(texts, embeddings.astype(np.float32).tolist()))
        return LangchainFAISS.from_embeddings(
            text_embeddings=text_embeddings,
            embedding=embedder,
            metadatas=docs,
            relevance_score_fn=_cosine_relevance,
        )

    # ── Write operations ─────────────────────────────────────────────────────

    def upsert(self, collection: str, docs: list[dict], embeddings: np.ndarray):
        """Replace entire collection with new docs + embeddings."""
        with self._lock:
            self._collections[collection] = self._build_index(docs, embeddings)
            self._save(collection)

    def add(self, collection: str, docs: list[dict], embeddings: np.ndarray):
        """Append docs to an existing collection (or create it)."""
        with self._lock:
            if collection in self._collections and self._collections[collection].index.ntotal > 0:
                texts = [d.get("text", "") for d in docs]
                self._collections[collection].add_embeddings(
                    list(zip(texts, embeddings.astype(np.float32).tolist())),
                    metadatas=docs,
                )
            else:
                self._collections[collection] = self._build_index(docs, embeddings)
            self._save(collection)

    def delete_by_id(self, collection: str, doc_id: str):
        """Remove all docs where doc['id'] or doc['parent_id'] == doc_id. Rebuilds index."""
        with self._lock:
            if collection not in self._collections:
                return
            index = self._collections[collection]
            # LangChain FAISS docstore maps internal UUID → Document
            keys_to_delete = [
                k for k, doc in index.docstore._dict.items()
                if doc.metadata.get("id") == doc_id
                or doc.metadata.get("parent_id") == doc_id
            ]
            if keys_to_delete:
                index.delete(keys_to_delete)
                self._save(collection)
                logger.info(
                    "Deleted %d chunks with id/parent_id='%s' from '%s'",
                    len(keys_to_delete), doc_id, collection,
                )

    def delete_collection(self, collection: str):
        with self._lock:
            self._collections.pop(collection, None)
            for suffix in (".faiss", ".pkl"):
                (self._dir / f"{collection}{suffix}").unlink(missing_ok=True)

    # ── Read operations ──────────────────────────────────────────────────────

    def get_retriever(
        self,
        collection: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ):
        """
        Return a LangChain VectorStoreRetriever for the given collection.
        Uses similarity_score_threshold when min_score > 0, otherwise plain similarity.
        """
        if collection not in self._collections:
            return None  # collection doesn't exist yet (e.g. user_docs before any upload)
        if min_score > 0.0:
            return self._collections[collection].as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": top_k, "score_threshold": min_score},
            )
        return self._collections[collection].as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k},
        )

    def search(
        self,
        collection: str,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[dict]:
        """
        Search using LangChain's similarity_search_with_relevance_scores.
        This is the same mechanism used internally by VectorStoreRetriever.
        Returns list of metadata dicts enriched with a 'score' key.
        """
        if collection not in self._collections:
            return []
        if self._collections[collection].index.ntotal == 0:
            return []
        pairs = self._collections[collection].similarity_search_with_relevance_scores(
            query, k=top_k
        )
        results = []
        for doc, score in pairs:
            score = max(0.0, min(1.0, float(score)))
            if score < min_score:
                continue
            results.append({"score": round(score, 4), **doc.metadata})
        return results

    def count(self, collection: str) -> int:
        if collection not in self._collections:
            return 0
        return self._collections[collection].index.ntotal

    def collection_names(self) -> list[str]:
        return list(self._collections.keys())


# ── Singleton ────────────────────────────────────────────────────────────────

_instance: FAISSVectorStore | None = None
_init_lock = threading.Lock()


def get_store() -> FAISSVectorStore:
    global _instance
    if _instance is None:
        with _init_lock:
            if _instance is None:
                _instance = FAISSVectorStore()
    return _instance
