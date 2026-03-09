import json
import re
import ollama
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.models import InterviewRequest
from app.rag.prompts import (
    INTERVIEWER_SYSTEM,
    INTERVIEW_QUESTIONS_PROMPT,
    INTERVIEW_EVALUATE_PROMPT,
)

router = APIRouter()
MODEL = "llama3.2:3b"


def _safe_json(raw: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON object found in LLM response")


def _stream_interview_chat(req: InterviewRequest):
    system = (
        INTERVIEWER_SYSTEM
        + f"\n\nYou are interviewing a candidate for the role of **{req.role or 'Software Engineer'}** "
          f"at **{req.experienceLevel or 'mid-level'}** level."
    )
    messages = [{"role": "system", "content": system}]
    for m in (req.messages or []):
        messages.append({"role": m.role, "content": m.content})

    stream = ollama.chat(
        model=MODEL,
        messages=messages,
        stream=True,
        options={"temperature": 0.7},
    )

    for chunk in stream:
        content = chunk.get("message", {}).get("content", "")
        if content:
            yield f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"

    yield "data: [DONE]\n\n"


@router.post("/interview")
async def interview_handler(req: InterviewRequest):
    # --- Generate questions --------------------------------------------------
    if req.action == "generate_questions":
        prompt = INTERVIEW_QUESTIONS_PROMPT.format(
            count=req.questionCount or 5,
            level=req.experienceLevel or "mid-level",
            role=req.role or "Software Engineer",
            type=req.interviewType or "mixed",
        )
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                format="json",
                options={"temperature": 0.5},
            )
            raw = response["message"]["content"]
            data = _safe_json(raw)
            return {"questions": data.get("questions", [])}
        except Exception as e:
            return {"questions": [], "error": str(e)}

    # --- Evaluate conversation -----------------------------------------------
    if req.action == "evaluate":
        conversation = "\n".join(
            f"{m.role.upper()}: {m.content}"
            for m in (req.messages or [])
        )
        prompt = INTERVIEW_EVALUATE_PROMPT.format(
            role=req.role or "Software Engineer",
            transcript=conversation[:4000].replace("{", "{{").replace("}", "}}"),
        )
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert interview evaluator. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                format="json",
                options={"temperature": 0.3},
            )
            raw = response["message"]["content"]
            data = _safe_json(raw)
            return {"evaluation": data.get("evaluation", data)}
        except Exception as e:
            return {
                "evaluation": {
                    "overall_score": 0,
                    "communication_score": 0,
                    "technical_score": 0,
                    "problem_solving_score": 0,
                    "confidence_score": 0,
                    "summary": f"Evaluation failed: {str(e)}",
                    "strengths": [],
                    "improvements": [],
                    "tips": [],
                }
            }

    # --- Streaming chat (default action = "chat") ----------------------------
    return StreamingResponse(
        _stream_interview_chat(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
