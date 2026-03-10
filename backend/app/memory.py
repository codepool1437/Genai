"""
Per-session conversation memory — ConversationBufferWindowMemory pattern.

Implemented with langchain_community.chat_message_histories.ChatMessageHistory
(the modern LangChain v0.3 equivalent of ConversationBufferWindowMemory with k turns).

Each browser session gets its own sliding message window (last k=10 human/AI turns).
Sessions are stored in-process; they reset on server restart (intentional —
no DB dependency, appropriate for a demo/review context).

Usage:
    from app.memory import get_memory, save_turn, get_history_text

    save_turn(session_id, human_input, ai_output)
    history = get_history_text(session_id)   # formatted string for system prompt
"""

from __future__ import annotations

import threading
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# Keep the last k human+AI turn pairs (matches ConversationBufferWindowMemory k= param)
_WINDOW_K = 10

_sessions: dict[str, ChatMessageHistory] = {}
_lock = threading.Lock()


def get_memory(session_id: str) -> ChatMessageHistory:
    """Return (or create) the ChatMessageHistory for a session."""
    if session_id not in _sessions:
        with _lock:
            if session_id not in _sessions:
                _sessions[session_id] = ChatMessageHistory()
    return _sessions[session_id]


def save_turn(session_id: str, human_input: str, ai_output: str) -> None:
    """Persist one Human/AI exchange into the session window, trimming to k turns."""
    mem = get_memory(session_id)
    mem.add_user_message(human_input)
    mem.add_ai_message(ai_output)

    # Enforce sliding window: keep only the last _WINDOW_K * 2 messages (k pairs)
    max_msgs = _WINDOW_K * 2
    if len(mem.messages) > max_msgs:
        mem.messages = mem.messages[-max_msgs:]


def get_history_text(session_id: str) -> str:
    """
    Return a plain-text formatted conversation history for injection into
    the LLM system prompt, e.g.:
        User: ...
        Assistant: ...
    Returns an empty string when there is no history yet.
    """
    mem = get_memory(session_id)
    if not mem.messages:
        return ""
    lines: list[str] = []
    for msg in mem.messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            lines.append(f"Assistant: {msg.content}")
    return "\n".join(lines)


def clear_session(session_id: str) -> None:
    """Remove a session's memory (e.g. on explicit user reset)."""
    with _lock:
        _sessions.pop(session_id, None)

