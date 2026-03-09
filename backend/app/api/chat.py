import json
import ollama
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.models import ChatRequest
from app.rag.course_db import retrieve_courses, all_courses_as_context, ROLE_SKILL_MAP
from app.rag.prompts import CAREER_COUNSELOR_SYSTEM

router = APIRouter()

MODEL = "llama3.2:3b"


def _build_sse(content: str) -> str:
    payload = {"choices": [{"delta": {"content": content}}]}
    return f"data: {json.dumps(payload)}\n\n"


def _stream_response(messages: list[dict]):
    """Stream Ollama response as OpenAI-compatible SSE."""
    try:
        stream = ollama.chat(model=MODEL, messages=messages, stream=True)
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield _build_sse(content)
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield _build_sse(f"\n\n⚠️ Error: {str(e)}. Make sure Ollama is running (`ollama serve`).")
        yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat(req: ChatRequest):
    # ── RAG: extract target role from profile and retrieve relevant courses ──
    rag_context = ""
    rag_sources = []

    if req.profile and req.profile.goals:
        # Detect target role from goals text by matching known roles
        goals_lower = req.profile.goals.lower()
        detected_role = None
        for role in ROLE_SKILL_MAP:
            if role.lower() in goals_lower:
                detected_role = role
                break

        if detected_role:
            current_skills = [s.strip() for s in (req.profile.skills or "").split(",") if s.strip()]
            courses = retrieve_courses(detected_role, current_skills)
            if courses:
                rag_context = f"\n\nVERIFIED COURSE DATABASE (recommend ONLY these — do not invent courses):\n{all_courses_as_context(courses)}"
                rag_sources = [
                    {
                        "file_name": f"{c['skill']} — {c['title']}",
                        "score": 0.95,
                        "content_preview": f"{c['platform']} | {c['duration']} | {c['level']}"
                    }
                    for c in courses[:5]
                ]

    # ── Build message list for Ollama ────────────────────────────────────────
    system_content = CAREER_COUNSELOR_SYSTEM + rag_context
    ollama_messages = [{"role": "system", "content": system_content}]
    for msg in req.messages:
        ollama_messages.append({"role": msg.role, "content": msg.content})

    def event_stream():
        # First send RAG sources so the frontend can show the panel
        if rag_sources:
            yield f"data: {json.dumps({'sources': rag_sources})}\n\n"
        yield from _stream_response(ollama_messages)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
