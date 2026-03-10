"""
Seeds the `courses` collection in the vector store with real course data.
Idempotent — skips seeding if the collection is already populated.
"""
import logging
from app.rag.vector_store import get_store
from app.rag.embedder import embed
from app.rag.course_data import COURSES

logger = logging.getLogger(__name__)


def seed_courses() -> None:
    """Embed and store all courses. Re-seeds automatically if industry metadata is missing."""
    store = get_store()
    if store.count("courses") >= len(COURSES):
        # Check whether the existing index already has the industry field
        sample = store.search("courses", "python programming", top_k=1, min_score=0.0)
        if sample and "industry" in sample[0]:
            logger.info("courses collection already seeded (%d docs)", store.count("courses"))
            return
        # Missing industry metadata — clear the old index and re-seed
        logger.info("Re-seeding courses collection to add industry metadata...")
        store._collections.pop("courses", None)
        for ext in (".faiss", ".pkl"):
            p = store._dir / f"courses{ext}"
            if p.exists():
                p.unlink()

    logger.info("Seeding %d courses into vector store …", len(COURSES))

    texts = [c["text"] for c in COURSES]
    embeddings = embed(texts)

    docs = [
        {
            "id":       c["id"],
            "title":    c["title"],
            "platform": c["platform"],
            "url":      c["url"],
            "duration": c["duration"],
            "level":    c["level"],
            "free":     c["free"],
            "skill":    c["skill"],
            "industry": c.get("industry", "Tech"),
            "text":     c["text"],
        }
        for c in COURSES
    ]

    store.upsert("courses", docs, embeddings)
    logger.info("Seeding complete — %d courses stored.", store.count("courses"))
