"""
POST /api/roadmap — Generate a structured career roadmap via the LangGraph pipeline.

LangGraph StateGraph (4 nodes, sequential):
  profile_analyzer → skill_gap_identifier → career_path_recommender → resource_suggester

Each node does one focused task and passes enriched state to the next.
"""

import asyncio
from fastapi import APIRouter

from app.schemas.models import RoadmapRequest
from app.rag.roadmap_graph import roadmap_graph, RoadmapState

router = APIRouter()


@router.post("/roadmap")
async def generate_roadmap(req: RoadmapRequest):
    profile_dict = req.profile.model_dump()

    # Initial state — only profile is populated; all other fields are empty
    initial_state: RoadmapState = {
        "profile":          profile_dict,
        "profile_analysis": "",
        "current_level":    "",
        "target_role":      "",
        "skill_gaps":       [],
        "rag_query":        "",
        "rag_context":      "",
        "career_paths":     "",
        "roadmap":          {},
        "error":            "",
    }

    # Run the graph in a thread pool so FastAPI's event loop is not blocked
    loop = asyncio.get_event_loop()
    try:
        final_state: RoadmapState = await loop.run_in_executor(
            None, roadmap_graph.invoke, initial_state
        )
    except Exception as exc:
        return {"roadmap": None, "error": str(exc)}

    return {
        "roadmap":       final_state.get("roadmap") or None,
        "current_level": final_state.get("current_level"),
        "target_role":   final_state.get("target_role"),
        "skill_gaps":    final_state.get("skill_gaps", []),
        "career_paths":  final_state.get("career_paths"),
        "error":         final_state.get("error") or None,
    }
