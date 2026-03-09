"""
Lightweight vector store using numpy cosine similarity.
No external C++ compilation needed — works on any platform.

Architecture:
  - One "collection" = one .npy (embeddings) + one .json (metadata) file pair
  - Embeddings are L2-normalised so dot product == cosine similarity
  - Singleton pattern: one instance shared across the whole FastAPI process
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# Where embedding + metadata files are persisted
_STORE_DIR = Path(__file__).parent.parent.parent / "data" / "vector_store"


class VectorStore:
    """Thread-safe, file-backed vector store."""

    def __init__(self, store_dir: Path = _STORE_DIR):
        self._dir = store_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        # collection_name -> {"embeddings": np.ndarray, "docs": list[dict]}
        self._data: dict[str, dict] = {}
        self._load_all()

    # ── Persistence helpers ──────────────────────────────────────────────────

    def _emb_path(self, name: str) -> Path:
        return self._dir / f"{name}.npy"

    def _meta_path(self, name: str) -> Path:
        return self._dir / f"{name}.json"

    def _load_all(self):
        for meta_file in self._dir.glob("*.json"):
            name = meta_file.stem
            emb_file = self._emb_path(name)
            if emb_file.exists():
                try:
                    docs = json.loads(meta_file.read_text(encoding="utf-8"))
                    embeddings = np.load(str(emb_file))
                    self._data[name] = {"embeddings": embeddings, "docs": docs}
                    logger.info("Loaded collection '%s': %d docs", name, len(docs))
                except Exception as e:
                    logger.warning("Could not load collection '%s': %s", name, e)

    def _save(self, name: str):
        data = self._data[name]
        np.save(str(self._emb_path(name)), data["embeddings"])
        self._meta_path(name).write_text(
            json.dumps(data["docs"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ── Write operations ─────────────────────────────────────────────────────

    def upsert(self, collection: str, docs: list[dict], embeddings: np.ndarray):
        """Replace entire collection with new docs + embeddings."""
        with self._lock:
            self._data[collection] = {
                "embeddings": embeddings.astype(np.float32),
                "docs": docs,
            }
            self._save(collection)

    def add(self, collection: str, docs: list[dict], embeddings: np.ndarray):
        """Append docs to an existing collection (or create it)."""
        with self._lock:
            if collection in self._data and len(self._data[collection]["docs"]) > 0:
                existing = self._data[collection]
                self._data[collection] = {
                    "embeddings": np.vstack(
                        [existing["embeddings"], embeddings.astype(np.float32)]
                    ),
                    "docs": existing["docs"] + docs,
                }
            else:
                self._data[collection] = {
                    "embeddings": embeddings.astype(np.float32),
                    "docs": docs,
                }
            self._save(collection)

    def delete_by_id(self, collection: str, doc_id: str):
        """Remove all docs where doc['id'] == doc_id."""
        with self._lock:
            if collection not in self._data:
                return
            data = self._data[collection]
            keep = [i for i, d in enumerate(data["docs"]) if d.get("id") != doc_id]
            if len(keep) == len(data["docs"]):
                return  # nothing removed
            self._data[collection] = {
                "embeddings": data["embeddings"][keep],
                "docs": [data["docs"][i] for i in keep],
            }
            self._save(collection)

    def delete_collection(self, collection: str):
        with self._lock:
            self._data.pop(collection, None)
            self._emb_path(collection).unlink(missing_ok=True)
            self._meta_path(collection).unlink(missing_ok=True)

    # ── Read operations ──────────────────────────────────────────────────────

    def search(
        self,
        collection: str,
        query_embedding: np.ndarray,
        top_k: int = 5,
        min_score: float = 0.25,
    ) -> list[dict]:
        """Return top_k docs sorted by cosine similarity, filtered by min_score."""
        if collection not in self._data:
            return []
        data = self._data[collection]
        if len(data["docs"]) == 0:
            return []

        q = query_embedding.astype(np.float32).flatten()
        scores: np.ndarray = data["embeddings"] @ q  # dot product = cosine (normalised)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for i in top_indices:
            s = float(scores[i])
            if s < min_score:
                break
            results.append({"score": round(s, 4), **data["docs"][i]})
        return results

    def count(self, collection: str) -> int:
        return len(self._data.get(collection, {}).get("docs", []))

    def collection_names(self) -> list[str]:
        return list(self._data.keys())


# ── Singleton ────────────────────────────────────────────────────────────────

_instance: VectorStore | None = None
_init_lock = threading.Lock()


def get_store() -> VectorStore:
    global _instance
    if _instance is None:
        with _init_lock:
            if _instance is None:
                _instance = VectorStore()
    return _instance
