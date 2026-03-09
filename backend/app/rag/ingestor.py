"""
Document ingestor — handles PDF, DOCX, TXT, MD files.

Pipeline:
  raw bytes → text extraction → chunking (500 chars, 100 overlap) → embed → store
"""

from __future__ import annotations

import io
import logging
import uuid
from pathlib import Path

from app.rag.embedder import embed
from app.rag.vector_store import get_store

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500      # characters
CHUNK_OVERLAP = 100   # characters


# ── Text extraction ──────────────────────────────────────────────────────────

def _extract_text_from_bytes(filename: str, raw: bytes) -> str:
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if ext == ".docx":
        from docx import Document
        doc = Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs)

    # .txt / .md and anything else — decode as utf-8
    return raw.decode("utf-8", errors="ignore")


# ── Chunking ─────────────────────────────────────────────────────────────────

def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping character-level chunks."""
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks


# ── Public API ───────────────────────────────────────────────────────────────

def ingest_file(
    filename: str,
    raw_bytes: bytes,
    doc_id: str | None = None,
    doc_type: str = "general",
    collection: str = "user_docs",
) -> dict:
    """
    Extract text from file, chunk, embed, and store in the vector store.
    Returns metadata dict for the document registry.
    """
    if doc_id is None:
        doc_id = str(uuid.uuid4())

    text = _extract_text_from_bytes(filename, raw_bytes)
    chunks = _chunk_text(text)

    if not chunks:
        logger.warning("No text extracted from '%s'", filename)
        return {
            "id": doc_id,
            "file_name": filename,
            "doc_type": doc_type,
            "size_bytes": len(raw_bytes),
            "chunk_count": 0,
            "text_preview": "",
        }

    # Build metadata for each chunk — store enough to reconstruct a useful source ref
    chunk_docs = [
        {
            "id": f"{doc_id}__chunk_{i}",
            "parent_id": doc_id,
            "file_name": filename,
            "doc_type": doc_type,
            "chunk_index": i,
            "text": chunk,
        }
        for i, chunk in enumerate(chunks)
    ]

    chunk_texts = [c["text"] for c in chunk_docs]
    embeddings = embed(chunk_texts)

    store = get_store()
    store.add(collection=collection, docs=chunk_docs, embeddings=embeddings)

    logger.info("Ingested '%s': %d chunks into collection '%s'", filename, len(chunks), collection)

    return {
        "id": doc_id,
        "file_name": filename,
        "doc_type": doc_type,
        "size_bytes": len(raw_bytes),
        "chunk_count": len(chunks),
        "text_preview": text[:300].strip(),
    }


def remove_file(doc_id: str, collection: str = "user_docs"):
    """Remove all chunks belonging to doc_id from the vector store."""
    store = get_store()
    # chunks stored as {parent_id: doc_id} — delete by parent_id
    data = store._data.get(collection)
    if not data:
        return
    keep = [
        i for i, d in enumerate(data["docs"])
        if d.get("parent_id") != doc_id and d.get("id") != doc_id
    ]
    if len(keep) == len(data["docs"]):
        return
    import numpy as np
    with store._lock:
        store._data[collection] = {
            "embeddings": data["embeddings"][keep],
            "docs": [data["docs"][i] for i in keep],
        }
        store._save(collection)
    logger.info("Removed %d chunks for doc '%s'", len(data["docs"]) - len(keep), doc_id)
