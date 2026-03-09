import json
import ollama
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.models import ChatRequest
from app.rag.retriever import retrieve
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
    # ── RAG: semantic search over courses + uploaded documents ───────────────
    rag_context = ""
    rag_sources = []

    # Build a search query from the latest user message + profile summary
    last_user_msg = next(
        (m.content for m in reversed(req.messages) if m.role == "user"), ""
    )
    if last_user_msg:
        profile_dict = req.profile.model_dump() if req.profile else None
        rag_context, rag_sources = retrieve(last_user_msg, profile=profile_dict)

    # ── Build message list for Ollama ────────────────────────────────────────
    rag_block = f"\n\n{rag_context}" if rag_context else ""
    system_content = CAREER_COUNSELOR_SYSTEM + rag_block
    ollama_messages = [{"role": "system", "content": system_content}]
    for msg in req.messages:
        ollama_messages.append({"role": msg.role, "content": msg.content})

    def event_stream():
        # First send RAG sources so the frontend can show the panel
        if rag_sources:
            yield f"data: {json.dumps({'sources': rag_sources})}\n\n"
        yield from _stream_response(ollama_messages)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
