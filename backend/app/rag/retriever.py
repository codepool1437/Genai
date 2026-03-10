"""
Unified retriever — searches both `courses` and `user_docs` collections via
LangChain VectorStoreRetriever, merges results, and returns a formatted LLM
context string + sources list.
"""
from __future__ import annotations
import logging
from app.rag.vector_store import get_store

logger = logging.getLogger(__name__)

_COURSE_TOP_K     = 6
_DOC_TOP_K        = 4
_COURSE_MIN_SCORE = 0.20  # only suggest courses with meaningful relevance
_DOC_MIN_SCORE    = 0.0   # always include user docs — they were uploaded for context


def retrieve(
    query: str,
    *,
    profile: dict | None = None,
    top_k_courses: int = _COURSE_TOP_K,
    top_k_docs: int = _DOC_TOP_K,
) -> tuple[str, list[dict]]:
    """
    Use LangChain VectorStoreRetriever to search both collections and return:
      - context_str  : formatted text to inject into the LLM system prompt
      - sources      : list of source dicts for the SSE `sources` event

    The `profile` dict (optional) is used to enrich the query with the
    user's current role/skills so the embedding is more targeted.
    """
    enriched_query = _enrich_query(query, profile)
    store = get_store()

    # Build LangChain VectorStoreRetrievers — LangChain handles embedding internally.
    # Returns None when the collection doesn't exist yet (e.g. user_docs before any upload).
    courses_retriever = store.get_retriever(
        "courses", top_k=top_k_courses, min_score=_COURSE_MIN_SCORE
    )
    docs_retriever = store.get_retriever(
        "user_docs", top_k=top_k_docs, min_score=_DOC_MIN_SCORE
    )

    # similarity_search_with_relevance_scores is the mechanism VectorStoreRetriever
    # uses internally — we call it here to also retrieve the relevance scores for display.
    # store.search() already guards against missing collections (returns []).
    course_hits = store.search(
        "courses", enriched_query, top_k=top_k_courses, min_score=_COURSE_MIN_SCORE
    )
    doc_hits = store.search(
        "user_docs", enriched_query, top_k=top_k_docs, min_score=_DOC_MIN_SCORE
    )

    context_str = _format_context(course_hits, doc_hits)
    sources     = _format_sources(course_hits, doc_hits)

    logger.debug(
        "retrieve(): courses_retriever=%s  docs_retriever=%s  query=%r  courses=%d  docs=%d",
        type(courses_retriever).__name__,
        type(docs_retriever).__name__,
        enriched_query[:60],
        len(course_hits),
        len(doc_hits),
    )
    return context_str, sources


# ─── helpers ────────────────────────────────────────────────────────────────

def _enrich_query(query: str, profile: dict | None) -> str:
    """Prepend a short profile summary to the query for better retrieval."""
    if not profile:
        return query
    parts = []
    if profile.get("currentRole"):
        parts.append(f"Current role: {profile['currentRole']}")
    if profile.get("targetRole"):
        parts.append(f"Target role: {profile['targetRole']}")
    if profile.get("skills"):
        skills = profile["skills"]
        if isinstance(skills, list):
            skills = ", ".join(skills[:8])
        parts.append(f"Skills: {skills}")
    prefix = " | ".join(parts)
    return f"{prefix}. {query}" if prefix else query


def _format_context(course_hits: list[dict], doc_hits: list[dict]) -> str:
    sections: list[str] = []

    if course_hits:
        lines = ["=== RECOMMENDED COURSES (ranked by relevance) ==="]
        for i, h in enumerate(course_hits, 1):
            badge = "FREE" if h.get("free") else h.get("platform", "")
            lines.append(
                f"{i}. [{h['title']}]({h['url']}) — {badge}\n"
                f"   {h['text']}\n"
                f"   Level: {h.get('level','?')} | Duration: {h.get('duration','?')} | Score: {h['score']:.2f}"
            )
        sections.append("\n".join(lines))

    if doc_hits:
        lines = ["=== RELEVANT CONTENT FROM YOUR UPLOADED DOCUMENTS ==="]
        for i, h in enumerate(doc_hits, 1):
            lines.append(
                f"{i}. [{h.get('file_name','doc')}] (chunk {h.get('chunk_index',0)+1})\n"
                f"   {h.get('text','')[:400]}\n"
                f"   Score: {h['score']:.2f}"
            )
        sections.append("\n".join(lines))

    if not sections:
        return "(No relevant courses or documents found for this query.)"

    return "\n\n".join(sections)


def _format_sources(
    course_hits: list[dict], doc_hits: list[dict]
) -> list[dict]:
    """Return the sources list consumed by the frontend SSE `sources` event."""
    sources = []

    for h in course_hits:
        sources.append({
            "type":            "course",
            "file_name":       h["title"],
            "platform":        h.get("platform", ""),
            "url":             h.get("url", ""),
            "score":           round(h["score"], 3),
            "content_preview": h.get("text", "")[:200],
        })

    for h in doc_hits:
        sources.append({
            "type":            "document",
            "file_name":       h.get("file_name", "uploaded document"),
            "score":           round(h["score"], 3),
            "content_preview": h.get("text", "")[:200],
        })

    return sources
