import base64
import io
import json
import re
import ollama
from docx import Document as DocxDocument
from fastapi import APIRouter
from pypdf import PdfReader

from app.schemas.models import ResumeRequest
from app.rag.prompts import RESUME_ANALYSIS_SYSTEM, RESUME_EXTRACT_PROFILE_SYSTEM

router = APIRouter()
MODEL = "llama3.2:3b"


def _extract_text(req: ResumeRequest) -> str:
    """Extract plain text from PDF (base64), DOCX (base64), or raw resumeText."""
    if req.pdfBase64:
        raw_bytes = base64.b64decode(req.pdfBase64)
        fname = (req.filename or "").lower()
        if fname.endswith(".docx"):
            doc = DocxDocument(io.BytesIO(raw_bytes))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        else:
            reader = PdfReader(io.BytesIO(raw_bytes))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
    return req.resumeText or ""


def _safe_json(raw: str) -> dict:
    """Extract first JSON object from LLM output, even if wrapped in markdown."""
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON object found in LLM response")


@router.post("/resume/extract-profile")
async def extract_profile(req: ResumeRequest):
    """Extract structured profile fields from a resume for auto-filling the profile form."""
    resume_text = _extract_text(req)
    if not resume_text.strip():
        return {"profile": None, "error": "Could not extract text."}
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": RESUME_EXTRACT_PROFILE_SYSTEM},
                {"role": "user",   "content": resume_text[:5000]},
            ],
            format="json",
            options={"temperature": 0.1},
        )
        profile = _safe_json(response["message"]["content"])
        return {"profile": profile}
    except Exception as e:
        return {"profile": None, "error": str(e)}


@router.post("/resume/analyze")
async def analyze_resume(req: ResumeRequest):
    resume_text = _extract_text(req)

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
