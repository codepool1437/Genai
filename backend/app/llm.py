"""
Central LLM client — Groq backend with API key rotation.

Drop-in replacement for the old `ollama.chat()` calls:

    # Old:
    import ollama
    response = ollama.chat(model=MODEL, messages=[...], options={...})
    content  = response["message"]["content"]

    # New:
    from app.llm import chat, stream_chat
    response = chat(messages=[...], temperature=0.3)
    content  = response["message"]["content"]

    for chunk in stream_chat(messages=[...]):
        content = chunk.get("message", {}).get("content", "")
"""
from __future__ import annotations

import itertools
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIStatusError

logger = logging.getLogger(__name__)

# Load .env from the backend directory
load_dotenv(Path(__file__).parent.parent / ".env")

MODEL = "llama-3.1-8b-instant"   # Fast Groq model; swap to "llama-3.3-70b-versatile" for higher quality

# ── Key rotation ──────────────────────────────────────────────────────────────

def _load_keys() -> list[str]:
    keys = []
    for i in range(1, 10):
        k = os.getenv(f"GROQ_API_KEY_{i}", "").strip().strip('"')
        if k:
            keys.append(k)
    if not keys:
        raise RuntimeError(
            "No Groq API keys found. Set GROQ_API_KEY_1 (and optionally _2, _3) "
            "in backend/.env  —  get free keys at https://console.groq.com"
        )
    return keys

_keys = _load_keys()
_key_cycle = itertools.cycle(_keys)

def _next_client() -> Groq:
    return Groq(api_key=next(_key_cycle))


# ── Public API ────────────────────────────────────────────────────────────────

def chat(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 2048,
    json_mode: bool = False,
) -> dict:
    """
    Non-streaming chat. Returns dict with same shape as ollama.chat():
      {"message": {"role": "assistant", "content": "..."}}
    Retries once with the next key on RateLimitError.
    """
    kwargs: dict = dict(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(len(_keys) + 1):
        client = _next_client()
        try:
            resp = client.chat.completions.create(**kwargs)
            content = resp.choices[0].message.content or ""
            return {"message": {"role": "assistant", "content": content}}
        except RateLimitError:
            if attempt < len(_keys):
                logger.warning("Groq rate limit hit, rotating to next key (attempt %d)", attempt + 1)
                continue
            raise
        except APIStatusError as e:
            logger.error("Groq API error: %s", e)
            raise

    raise RuntimeError("All Groq API keys exhausted (rate limited)")


def stream_chat(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 2048,
):
    """
    Streaming chat. Yields dicts with same shape as ollama streaming chunks:
      {"message": {"role": "assistant", "content": "<token>"}}
    """
    for attempt in range(len(_keys) + 1):
        client = _next_client()
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                if content:
                    yield {"message": {"role": "assistant", "content": content}}
            return
        except RateLimitError:
            if attempt < len(_keys):
                logger.warning("Groq rate limit hit on stream, rotating key (attempt %d)", attempt + 1)
                continue
            raise
        except APIStatusError as e:
            logger.error("Groq API stream error: %s", e)
            raise
