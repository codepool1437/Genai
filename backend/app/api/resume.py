import base64
import io
import json
import re
import ollama
from fastapi import APIRouter
from pypdf import PdfReader

from app.schemas.models import ResumeRequest
from app.rag.prompts import RESUME_ANALYSIS_SYSTEM

router = APIRouter()
MODEL = "llama3.2:3b"


def _extract_pdf_text(b64: str) -> str:
    pdf_bytes = base64.b64decode(b64)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _safe_json(raw: str) -> dict:
    """Extract first JSON object from LLM output, even if wrapped in markdown."""
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON object found in LLM response")


@router.post("/resume/analyze")
async def analyze_resume(req: ResumeRequest):
    # Extract text from whichever source was provided
    if req.pdfBase64:
        try:
            resume_text = _extract_pdf_text(req.pdfBase64)
        except Exception:
            resume_text = req.resumeText or ""
    else:
        resume_text = req.resumeText or ""

    if not resume_text.strip():
        return {"analysis": None, "error": "Could not extract text from resume."}

    user_prompt = (
        f"Analyze this resume{' for the role: ' + req.targetRole if req.targetRole else ''}:\n\n"
        f"{resume_text[:6000]}"
    )

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": RESUME_ANALYSIS_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            format="json",
            options={"temperature": 0.3},
        )
        raw = response["message"]["content"]
        analysis = _safe_json(raw)
        return {"analysis": analysis}
    except Exception as e:
        # Return a graceful fallback so the frontend doesn't crash
        return {
            "analysis": {
                "overall_score": 0,
                "ats_score": 0,
                "content_score": 0,
                "skills_score": 0,
                "presentation_score": 0,
                "summary": f"Analysis failed: {str(e)}",
                "strengths": [],
                "improvements": [{"severity": "critical", "category": "System", "issue": str(e), "suggestion": "Try again."}],
                "missing_keywords": [],
                "detected_skills": [],
            }
        }
