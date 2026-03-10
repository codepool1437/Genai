"""
LangGraph StateGraph — 4-node career roadmap pipeline.

Graph topology (sequential):
  profile_analyzer → skill_gap_identifier → career_path_recommender → resource_suggester → END

Node responsibilities
─────────────────────
1. profile_analyzer
   • Reads the raw user profile dict
   • Uses LLM to produce a concise professional assessment
   • Extracts: current_level (beginner/intermediate/advanced), target_role

2. skill_gap_identifier
   • Reads profile_analysis + target_role
   • Uses LLM to enumerate the specific skills the user still needs
   • Produces: skill_gaps (list[str]), enriched rag_query string for better retrieval

3. career_path_recommender
   • Uses the enriched rag_query to retrieve relevant courses (no LLM)
   • Populates rag_context + produces a brief career_paths summary via LLM

4. resource_suggester
   • Combines all prior state (analysis + gaps + paths + courses)
   • Calls LLM with the full ROADMAP_SYSTEM prompt to produce the final JSON roadmap
"""

from __future__ import annotations

import json
import logging
import re
from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.llm import chat
from app.rag.retriever import retrieve
from app.rag.prompts import ROADMAP_SYSTEM

logger = logging.getLogger(__name__)


# ── Shared state ─────────────────────────────────────────────────────────────

class RoadmapState(TypedDict):
    # ── Input ──
    profile: dict            # raw UserProfile fields as a dict

    # ── Node 1 output ──
    profile_analysis: str    # prose assessment of the candidate
    current_level: str       # beginner | intermediate | advanced
    target_role: str         # inferred or explicit target role

    # ── Node 2 output ──
    skill_gaps: list[str]    # skills the user still needs to acquire
    rag_query: str           # enriched query string for course retrieval

    # ── Node 3 output ──
    rag_context: str         # formatted course list from FAISS retrieval
    career_paths: str        # brief text summary of recommended paths

    # ── Node 4 output ──
    roadmap: dict            # final structured JSON roadmap
    error: str               # non-empty if any node fails


# ── Prompts ───────────────────────────────────────────────────────────────────

_PROFILE_ANALYZER_SYSTEM = """You are a career coach who builds concise candidate assessments.

Given a user profile, produce a SHORT assessment (3-5 sentences) covering:
- Their current professional standing and experience level
- Their stated career goal and how realistic it is
- One key strength and one key area for growth

After the assessment, on a NEW LINE output exactly:
LEVEL: <beginner|intermediate|advanced>
TARGET_ROLE: <single job title — the user's target role or best match>

Keep the assessment professional but encouraging."""

_SKILL_GAP_SYSTEM = """You are a skills gap analyst. You identify exactly what skills a professional needs to acquire.

Given a candidate profile analysis and their target role, return ONLY valid JSON with this structure:
{
  "skill_gaps": ["skill1", "skill2", "skill3", ...],
  "rag_query": "<15-25 word search query optimised to find the most relevant courses for this person>"
}

Rules:
- skill_gaps: 5-10 specific, actionable technical and soft skills (not vague like "communication")
- rag_query: combine target role + 3-4 most important missing skills into a natural sentence
- Return ONLY the JSON — no markdown, no extra text"""

_CAREER_PATH_SYSTEM = """You are a career strategist. Given a candidate's profile, skill gaps, and target role, briefly
outline 2-3 realistic career progression paths in plain text (no JSON).

For each path write 1-2 sentences describing the route and approximate timeline.
Be concrete and encouraging. Total response under 200 words."""


# ── Helper ────────────────────────────────────────────────────────────────────

def _profile_text(profile: dict) -> str:
    """Convert profile dict to readable text for LLM prompts."""
    lines = []
    mapping = [
        ("name",        "Name"),
        ("currentRole", "Current role"),
        ("education",   "Education"),
        ("skills",      "Current skills"),
        ("experience",  "Experience"),
        ("goals",       "Career goal"),
        ("industries",  "Target industries"),
    ]
    for key, label in mapping:
        val = profile.get(key, "")
        if val:
            lines.append(f"{label}: {val}")
    return "\n".join(lines) if lines else "No profile information provided."


def _safe_json(raw: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No JSON found in: {raw[:200]}")


# ── Node 1 — Profile Analyzer ─────────────────────────────────────────────────

def profile_analyzer_node(state: RoadmapState) -> dict:
    """
    Analyze the user profile and extract current_level + target_role.
    """
    logger.info("[Node 1] profile_analyzer — analyzing profile")
    profile_text = _profile_text(state["profile"])

    try:
        resp = chat(
            messages=[
                {"role": "system", "content": _PROFILE_ANALYZER_SYSTEM},
                {"role": "user",   "content": f"Analyze this candidate:\n\n{profile_text}"},
            ],
            temperature=0.3,
            max_tokens=400,
        )
        raw = resp["message"]["content"].strip()

        # Extract structured fields from the last two lines
        current_level = "beginner"
        target_role   = state["profile"].get("goals", "software engineer").strip()

        for line in raw.splitlines():
            if line.startswith("LEVEL:"):
                val = line.split(":", 1)[1].strip().lower()
                if val in ("beginner", "intermediate", "advanced"):
                    current_level = val
            elif line.startswith("TARGET_ROLE:"):
                target_role = line.split(":", 1)[1].strip()

        # Strip the structured lines from the prose
        analysis_lines = [
            l for l in raw.splitlines()
            if not l.startswith("LEVEL:") and not l.startswith("TARGET_ROLE:")
        ]
        profile_analysis = "\n".join(analysis_lines).strip()

        logger.info("[Node 1] level=%s  target=%s", current_level, target_role)
        return {
            "profile_analysis": profile_analysis,
            "current_level":    current_level,
            "target_role":      target_role,
        }

    except Exception as exc:
        logger.warning("[Node 1] LLM call failed: %s", exc)
        return {
            "profile_analysis": profile_text,
            "current_level":    "beginner",
            "target_role":      state["profile"].get("goals", "software engineer"),
            "error":            str(exc),
        }


# ── Node 2 — Skill Gap Identifier ─────────────────────────────────────────────

def skill_gap_identifier_node(state: RoadmapState) -> dict:
    """
    Identify skill gaps and produce an enriched RAG query.
    """
    logger.info("[Node 2] skill_gap_identifier — target_role=%s", state["target_role"])

    user_content = (
        f"Candidate profile analysis:\n{state['profile_analysis']}\n\n"
        f"Target role: {state['target_role']}\n"
        f"Current skills: {state['profile'].get('skills', 'none listed')}"
    )

    try:
        resp = chat(
            messages=[
                {"role": "system", "content": _SKILL_GAP_SYSTEM},
                {"role": "user",   "content": user_content},
            ],
            temperature=0.2,
            max_tokens=400,
            json_mode=True,
        )
        data = _safe_json(resp["message"]["content"])
        skill_gaps = data.get("skill_gaps", [])
        rag_query  = data.get("rag_query", f"{state['target_role']} courses learning path")

        logger.info("[Node 2] %d skill gaps identified", len(skill_gaps))
        return {"skill_gaps": skill_gaps, "rag_query": rag_query}

    except Exception as exc:
        logger.warning("[Node 2] LLM call failed: %s", exc)
        fallback_query = (
            f"{state['target_role']} {state['profile'].get('goals', '')} courses roadmap"
        )
        return {
            "skill_gaps": [],
            "rag_query":  fallback_query,
            "error":      str(exc),
        }


# ── Node 3 — Career Path Recommender ─────────────────────────────────────────

def career_path_recommender_node(state: RoadmapState) -> dict:
    """
    Use the enriched rag_query to retrieve relevant courses via FAISS,
    then ask the LLM to outline 2-3 realistic career paths.
    """
    logger.info("[Node 3] career_path_recommender — rag_query=%r", state["rag_query"][:60])

    # Step A: RAG retrieval — the core FAISS VectorStoreRetriever call
    try:
        rag_context, _ = retrieve(
            state["rag_query"],
            profile=state["profile"],
            top_k_courses=12,
            top_k_docs=2,
        )
    except Exception as exc:
        logger.warning("[Node 3] RAG retrieval failed: %s", exc)
        rag_context = ""

    # Step B: Career paths LLM call
    gaps_text = ", ".join(state.get("skill_gaps", [])) or "various skills"
    user_content = (
        f"Target role: {state['target_role']}\n"
        f"Current level: {state['current_level']}\n"
        f"Skill gaps: {gaps_text}\n\n"
        f"Profile: {state['profile_analysis'][:400]}"
    )

    try:
        resp = chat(
            messages=[
                {"role": "system", "content": _CAREER_PATH_SYSTEM},
                {"role": "user",   "content": user_content},
            ],
            temperature=0.4,
            max_tokens=300,
        )
        career_paths = resp["message"]["content"].strip()
    except Exception as exc:
        logger.warning("[Node 3] career paths LLM call failed: %s", exc)
        career_paths = f"Recommended path: work toward {state['target_role']}."

    logger.info("[Node 3] RAG context length=%d", len(rag_context))
    return {"rag_context": rag_context, "career_paths": career_paths}


# ── Node 4 — Resource Suggester ───────────────────────────────────────────────

def resource_suggester_node(state: RoadmapState) -> dict:
    """
    Synthesise all prior state into the final structured JSON roadmap.
    Uses ROADMAP_SYSTEM prompt for schema-compliant JSON output.
    """
    logger.info("[Node 4] resource_suggester — generating final roadmap")

    gaps_text  = "\n".join(f"- {g}" for g in state.get("skill_gaps", []))
    user_prompt = (
        f"Generate a personalized career roadmap for this person.\n\n"
        f"=== PROFILE ANALYSIS ===\n{state['profile_analysis']}\n\n"
        f"=== TARGET ROLE ===\n{state['target_role']}\n\n"
        f"=== CURRENT LEVEL ===\n{state['current_level']}\n\n"
        f"=== IDENTIFIED SKILL GAPS ===\n{gaps_text or 'See profile analysis'}\n\n"
        f"=== RECOMMENDED CAREER PATHS ===\n{state['career_paths']}\n\n"
        f"=== AVAILABLE COURSES (use ONLY these) ===\n{state['rag_context']}"
    )

    try:
        resp = chat(
            messages=[
                {"role": "system", "content": ROADMAP_SYSTEM},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=2048,
            json_mode=True,
        )
        raw = resp["message"]["content"]
        roadmap = _safe_json(raw)
        logger.info("[Node 4] roadmap generated — phases=%s", len(roadmap.get("phases", [])))
        return {"roadmap": roadmap}

    except Exception as exc:
        logger.warning("[Node 4] roadmap generation failed: %s", exc)
        return {
            "roadmap": {},
            "error":   str(exc),
        }


# ── Graph assembly ────────────────────────────────────────────────────────────

def _build_graph() -> "CompiledGraph":  # type: ignore[name-defined]
    graph = StateGraph(RoadmapState)

    graph.add_node("profile_analyzer",        profile_analyzer_node)
    graph.add_node("skill_gap_identifier",     skill_gap_identifier_node)
    graph.add_node("career_path_recommender",  career_path_recommender_node)
    graph.add_node("resource_suggester",       resource_suggester_node)

    graph.set_entry_point("profile_analyzer")
    graph.add_edge("profile_analyzer",       "skill_gap_identifier")
    graph.add_edge("skill_gap_identifier",   "career_path_recommender")
    graph.add_edge("career_path_recommender", "resource_suggester")
    graph.add_edge("resource_suggester",     END)

    return graph.compile()


# Singleton compiled graph — built once at import time
roadmap_graph = _build_graph()
