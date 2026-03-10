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

# Maps broad role keywords → allowed skill tags in course metadata.
# Used by retrieve() when target_role is provided to filter out off-domain courses.
_ROLE_DOMAIN_MAP: dict[str, list[str]] = {
    "frontend":        ["Web Development", "TypeScript", "UI/UX Design", "Software Engineering", "Career Skills"],
    "backend":         ["Web Development", "Software Engineering", "SQL", "DevOps", "Cloud Computing", "Python", "Career Skills"],
    "full stack":      ["Web Development", "TypeScript", "Software Engineering", "SQL", "DevOps", "Cloud Computing", "Python", "Career Skills"],
    "fullstack":       ["Web Development", "TypeScript", "Software Engineering", "SQL", "DevOps", "Cloud Computing", "Python", "Career Skills"],
    "data scientist":  ["Machine Learning", "Deep Learning", "Data Analysis", "Statistics", "SQL", "Python", "NLP / GenAI", "Mathematics for ML", "MLOps", "Career Skills"],
    "data analyst":    ["Data Analysis", "SQL", "Statistics", "Python", "R Programming", "Career Skills"],
    "data engineer":   ["Data Engineering", "SQL", "Cloud Computing", "DevOps", "Python", "Software Engineering", "Career Skills"],
    "ml engineer":     ["Machine Learning", "Deep Learning", "MLOps", "Python", "Cloud Computing", "Mathematics for ML", "Career Skills"],
    "ai engineer":     ["Machine Learning", "Deep Learning", "NLP / GenAI", "MLOps", "Python", "Cloud Computing", "Career Skills"],
    "devops":          ["DevOps", "Cloud Computing", "Software Engineering", "System Design", "Career Skills"],
    "cloud":           ["Cloud Computing", "DevOps", "System Design", "Software Engineering", "Career Skills"],
    "mobile":          ["Mobile Development", "Software Engineering", "Career Skills"],
    "android":         ["Mobile Development", "Software Engineering", "Career Skills"],
    "ios":             ["Mobile Development", "Software Engineering", "Career Skills"],
    "cybersecurity":   ["Cybersecurity", "Software Engineering", "Career Skills"],
    "product manager": ["Product Management", "Career Skills", "UI/UX Design"],
    "ux":              ["UI/UX Design", "Career Skills"],
    "ui":              ["UI/UX Design", "Career Skills"],
    "blockchain":      ["Blockchain", "Software Engineering", "Career Skills"],
    "software engineer": ["Software Engineering", "Data Structures & Algorithms", "System Design", "Web Development", "Cloud Computing", "DevOps", "Career Skills"],
    "computer vision": ["Computer Vision", "Deep Learning", "Machine Learning", "Python", "Career Skills"],
}


def _allowed_skills_for_role(target_role: str) -> list[str] | None:
    """Return the allowed skill tags for a given role, or None if no mapping found (meaning: allow all)."""
    role_lower = target_role.lower()
    for keyword, skills in _ROLE_DOMAIN_MAP.items():
        if keyword in role_lower:
            return skills
    return None


def retrieve(
    query: str,
    *,
    profile: dict | None = None,
    target_role: str | None = None,
    top_k_courses: int = _COURSE_TOP_K,
    top_k_docs: int = _DOC_TOP_K,
) -> tuple[str, list[dict]]:
    """
    Use LangChain VectorStoreRetriever to search both collections and return:
      - context_str  : formatted text to inject into the LLM system prompt
      - sources      : list of source dicts for the SSE `sources` event

    The `profile` dict (optional) is used to enrich the query with the
    user's current role/skills so the embedding is more targeted.
    The `target_role` (optional) filters retrieved courses to only those
    relevant to the role's domain, preventing off-domain suggestions.
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

    # Fetch more candidates when role-filtering so we still get top_k after filtering
    fetch_k = top_k_courses * 3 if target_role else top_k_courses
    course_hits_raw = store.search(
        "courses", enriched_query, top_k=fetch_k, min_score=_COURSE_MIN_SCORE
    )

    # Option B: post-filter by role domain if target_role is provided
    allowed = _allowed_skills_for_role(target_role) if target_role else None
    if allowed:
        course_hits = [h for h in course_hits_raw if h.get("skill") in allowed][:top_k_courses]
        if not course_hits:  # fallback: no filter if nothing passes (very niche role)
            course_hits = course_hits_raw[:top_k_courses]
            logger.debug("role-domain filter found no matches for '%s' — using unfiltered results", target_role)
        else:
            logger.debug("role-domain filter: %d/%d courses kept for role '%s'", len(course_hits), len(course_hits_raw), target_role)
    else:
        course_hits = course_hits_raw[:top_k_courses]

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
