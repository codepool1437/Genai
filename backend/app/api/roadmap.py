"""
POST /api/roadmap — Generate a structured career roadmap for a given user profile.
Uses RAG to pull real course recommendations, then asks Ollama for a JSON plan.
"""

import json
import re
import ollama
from fastapi import APIRouter

from app.schemas.models import RoadmapRequest
from app.rag.retriever import retrieve
from app.rag.prompts import ROADMAP_SYSTEM

router = APIRouter()
MODEL = "llama3.2:3b"


def _safe_json(raw: str) -> dict:
    """Extract the first JSON object from LLM output even if wrapped in markdown."""
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON object in LLM response")


def _profile_summary(profile) -> str:
    parts = []
    if profile.name:
        parts.append(f"Name: {profile.name}")
    if profile.currentRole:
        parts.append(f"Current role: {profile.currentRole}")
    if profile.education:
        parts.append(f"Education: {profile.education}")
    if profile.skills:
        parts.append(f"Current skills: {profile.skills}")
    if profile.experience:
        parts.append(f"Experience: {profile.experience}")
    if profile.goals:
        parts.append(f"Career goal: {profile.goals}")
    if profile.industries:
        parts.append(f"Target industries: {profile.industries}")
    return "\n".join(parts) if parts else "No profile provided"


@router.post("/roadmap")
async def generate_roadmap(req: RoadmapRequest):
    profile = req.profile
    query = f"{profile.goals or 'career guidance'} {profile.currentRole or ''} roadmap courses"

    # RAG: pull relevant courses as context
    rag_context, _ = retrieve(query, profile=profile.model_dump(), top_k_courses=12, top_k_docs=2)

    user_prompt = (
        f"Generate a personalized career roadmap for this person:\n\n"
        f"{_profile_summary(profile)}\n\n"
        f"Use ONLY these verified courses for your recommendations:\n\n"
        f"{rag_context}"
    )

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": ROADMAP_SYSTEM},
                {"role": "user",   "content": user_prompt},
            ],
            format="json",
            options={"temperature": 0.4},
        )
        raw = response["message"]["content"]
        roadmap = _safe_json(raw)
        return {"roadmap": roadmap}

    except Exception as e:
        # Graceful fallback — return a minimal valid roadmap
        return {
            "roadmap": None,
            "error": str(e),
        }
