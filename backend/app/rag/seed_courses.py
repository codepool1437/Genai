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
    """Embed and store all courses. No-op if already seeded."""
    store = get_store()
    if store.count("courses") >= len(COURSES):
        logger.info("courses collection already seeded (%d docs)", store.count("courses"))
        return

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
            "text":     c["text"],
        }
        for c in COURSES
    ]

    store.upsert("courses", docs, embeddings)
    logger.info("Seeding complete — %d courses stored.", store.count("courses"))
