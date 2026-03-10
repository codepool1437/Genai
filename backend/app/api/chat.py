import json
import uuid
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.models import ChatRequest
from app.rag.retriever import retrieve
from app.rag.prompts import CAREER_COUNSELOR_SYSTEM
from app.llm import stream_chat
from app.memory import get_history_text, save_turn

router = APIRouter()


def _build_sse(content: str) -> str:
    payload = {"choices": [{"delta": {"content": content}}]}
    return f"data: {json.dumps(payload)}\n\n"


def _stream_response(messages: list[dict]):
    """Stream Groq response as OpenAI-compatible SSE."""
    try:
        for chunk in stream_chat(messages):
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield _build_sse(content)
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield _build_sse(f"\n\n⚠️ Error: {str(e)}")
        yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat(req: ChatRequest):
    # Resolve or create a session ID
    session_id = req.session_id or str(uuid.uuid4())

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

    # ── Inject ConversationBufferWindowMemory history ────────────────────────
    history: str = get_history_text(session_id)

    # ── Build message list ──────────────────────────────────────────────────
    rag_block     = f"\n\n{rag_context}" if rag_context else ""
    history_block = f"\n\n=== CONVERSATION HISTORY ===\n{history}" if history else ""
    system_content = CAREER_COUNSELOR_SYSTEM + rag_block + history_block

    llm_messages = [{"role": "system", "content": system_content}]
    for msg in req.messages:
        llm_messages.append({"role": msg.role, "content": msg.content})

    def event_stream():
        # Always emit session_id first so the client can track it
        meta = {"session_id": session_id}
        if rag_sources:
            meta["sources"] = rag_sources
        yield f"data: {json.dumps(meta)}\n\n"

        full_response: list[str] = []
        try:
            for chunk in stream_chat(llm_messages):
                content = chunk.get("message", {}).get("content", "")
                if content:
                    full_response.append(content)
                    yield _build_sse(content)
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield _build_sse(f"\n\n⚠️ Error: {str(e)}")
            yield "data: [DONE]\n\n"
        finally:
            # Persist this turn into the session window memory
            if last_user_msg and full_response:
                save_turn(session_id, last_user_msg, "".join(full_response))

    return StreamingResponse(event_stream(), media_type="text/event-stream")
