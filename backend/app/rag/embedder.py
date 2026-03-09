"""
Embedding model wrapper — singleton so the model is loaded once at startup.

Model: all-MiniLM-L6-v2
  - 384 dimensions
  - ~22 MB download, runs on CPU in ~10 ms per sentence
  - State-of-the-art for semantic similarity tasks
  - Fully local — no API key, no internet required at inference time
"""

from __future__ import annotations

import logging
import threading

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None
_model_lock = threading.Lock()


def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                logger.info("Loading embedding model '%s'...", MODEL_NAME)
                _model = SentenceTransformer(MODEL_NAME)
                logger.info("Embedding model loaded.")
    return _model


def embed(texts: list[str], batch_size: int = 64) -> np.ndarray:
    """
    Embed a list of strings. Returns shape (N, 384) float32 array,
    L2-normalised so dot product == cosine similarity.
    """
    model = get_embedder()
    vecs = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vecs.astype(np.float32)


def embed_one(text: str) -> np.ndarray:
    """Embed a single string. Returns shape (384,) float32 array."""
    return embed([text])[0]
