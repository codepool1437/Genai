"""
Embedding model wrapper — singleton so the model is loaded once at startup.

Model: all-MiniLM-L6-v2
  - 384 dimensions
  - ~22 MB download, runs on CPU in ~10 ms per sentence
  - State-of-the-art for semantic similarity tasks
  - Fully local — no API key, no internet required at inference time

Uses LangChain HuggingFaceEmbeddings as the wrapper (LangChain-compatible interface).
"""

from __future__ import annotations

import logging
import threading

import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"

_embeddings: HuggingFaceEmbeddings | None = None
_lock = threading.Lock()


def get_embedder() -> HuggingFaceEmbeddings:
    """Return the singleton LangChain HuggingFaceEmbeddings instance."""
    global _embeddings
    if _embeddings is None:
        with _lock:
            if _embeddings is None:
                logger.info("Loading embedding model '%s' via LangChain...", MODEL_NAME)
                _embeddings = HuggingFaceEmbeddings(
                    model_name=MODEL_NAME,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},
                )
                logger.info("Embedding model loaded.")
    return _embeddings


def embed(texts: list[str]) -> np.ndarray:
    """
    Embed a list of strings. Returns shape (N, 384) float32 array,
    L2-normalised so dot product == cosine similarity.
    """
    embedder = get_embedder()
    vecs = embedder.embed_documents(texts)
    return np.array(vecs, dtype=np.float32)


def embed_one(text: str) -> np.ndarray:
    """Embed a single string. Returns shape (384,) float32 array."""
    embedder = get_embedder()
    vec = embedder.embed_query(text)
    return np.array(vec, dtype=np.float32)
