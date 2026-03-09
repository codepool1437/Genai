import json
import re
import ollama
from fastapi import APIRouter

from app.schemas.models import QuizRequest
from app.rag.prompts import QUIZ_GENERATE_PROMPT, QUIZ_EVALUATE_PROMPT

router = APIRouter()
MODEL = "llama3.2:3b"


def _safe_json(raw: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON object found in LLM response")


@router.post("/quiz")
async def quiz_handler(req: QuizRequest):
    # --- Generate questions --------------------------------------------------
    if req.action == "generate":
        difficulty_hint = f" (difficulty: {req.difficulty})" if req.difficulty and req.difficulty != "mixed" else ""
        prompt = QUIZ_GENERATE_PROMPT.format(
            count=req.questionCount or 5,
            skill=req.skill or "Python",
            difficulty_hint=difficulty_hint,
        )
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a technical quiz generator. Return ONLY valid JSON."},
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

    # --- Evaluate answers ----------------------------------------------------
    if req.action == "evaluate":
        # Build a readable Q&A summary for the LLM
        # req.answers is a positional list: answers[i] = selected option index for question i
        answers_list = req.answers or []
        qa_lines = []
        for i, q in enumerate(req.questions or []):
            answer_idx = answers_list[i] if i < len(answers_list) else -1
            user_answer = q.options[answer_idx] if 0 <= answer_idx < len(q.options) else "Not answered"
            correct_answer = q.options[q.correct_index] if 0 <= q.correct_index < len(q.options) else q.options[0]
            correct = answer_idx == q.correct_index
            qa_lines.append(
                f"Q{q.id}: {q.question}\n"
                f"  User answered: {user_answer} ({'✓' if correct else '✗'})\n"
                f"  Correct answer: {correct_answer}"
            )
        qa_text = "\n".join(qa_lines)

        # Compute score stats for prompt
        total = len(req.questions or [])
        correct_count = sum(
            1 for i, q in enumerate(req.questions or [])
            if (answers_list[i] if i < len(answers_list) else -1) == q.correct_index
        )
        percentage = round(correct_count / total * 100) if total > 0 else 0

        # Escape { } in qa_text so .format() doesn't treat them as placeholders
        safe_qa = qa_text[:4000].replace("{", "{{").replace("}", "}}")

        prompt = QUIZ_EVALUATE_PROMPT.format(
            skill=req.skill or "the topic",
            qa_summary=safe_qa,
            correct=correct_count,
            total=total,
            percentage=percentage,
        )
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a technical skill evaluator. Return ONLY valid JSON."},
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
                    "proficiency_level": "unknown",
                    "score_percentage": 0,
                    "summary": f"Evaluation failed: {str(e)}",
                    "strengths": [],
                    "weaknesses": [],
                    "recommendations": [],
                }
            }

    return {"error": f"Unknown action: {req.action}"}
