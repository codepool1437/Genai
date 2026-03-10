"""
Profile persistence
GET    /api/profile         → reads  backend/data/profile.json
POST   /api/profile         → writes backend/data/profile.json
POST   /api/profile/extract → parses a CV/resume file and returns structured profile fields
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.llm import chat

logger = logging.getLogger(__name__)
router = APIRouter()

# One level up from this file:  backend/app/api/ → backend/data/
DATA_DIR     = Path(__file__).parent.parent.parent / "data"
PROFILE_FILE = DATA_DIR / "profile.json"


class ProfileData(BaseModel):
    name:        Optional[str] = None
    currentRole: Optional[str] = None
    education:   Optional[str] = None
    skills:      Optional[str] = None
    experience:  Optional[str] = None
    goals:       Optional[str] = None
    industries:  Optional[str] = None
    bio:         Optional[str] = None


_EXTRACT_SYSTEM = """You are a CV parser. Extract structured information from the resume text provided.

Return ONLY valid JSON with exactly these keys (use null if not found):
{
  "name":        "<full name>",
  "currentRole": "<most recent job title or student status>",
  "education":   "<highest degree, field, institution>",
  "skills":      "<comma-separated list of technical and soft skills>",
  "experience":  "<1-3 sentence summary of work/project experience>",
  "goals":       "<inferred or stated career goal>",
  "industries":  "<industries worked in or interested in>"
}

Rules:
- Return ONLY the JSON object — no markdown, no explanation
- Keep each value concise (skills as comma-separated, experience as short prose)
- Infer goals from the overall profile if not explicitly stated"""


@router.get("/profile")
def get_profile():
    """Return the saved profile or null if none exists yet."""
    if not PROFILE_FILE.exists():
        return {"profile": None}
    try:
        return {"profile": json.loads(PROFILE_FILE.read_text(encoding="utf-8"))}
    except Exception as e:
        logger.error("Failed to read profile.json: %s", e)
        return {"profile": None}


@router.post("/profile")
def save_profile(data: ProfileData):
    """Persist the profile to disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        PROFILE_FILE.write_text(
            json.dumps(data.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return {"ok": True}
    except Exception as e:
        logger.error("Failed to write profile.json: %s", e)
        return {"ok": False, "error": str(e)}


@router.post("/profile/extract")
async def extract_profile_from_cv(file: UploadFile = File(...)):
    """
    Accept a CV/resume file (PDF, DOCX, TXT, MD), extract text,
    and use the LLM to parse structured profile fields from it.
    Returns a ProfileData-shaped dict ready to populate the form.
    """
    allowed = {".pdf", ".docx", ".txt", ".md"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{suffix}'. Use PDF, DOCX, TXT, or MD.")

    raw = await file.read()
    if len(raw) > 5 * 1024 * 1024:  # 5 MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5 MB.")

    # Reuse the existing text extractor from the document ingestor (lazy import to avoid cold-start crash)
    try:
        from app.rag.ingestor import _extract_text_from_bytes
        text = _extract_text_from_bytes(file.filename or "resume.pdf", raw)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not extract text: {e}")

    if not text.strip():
        raise HTTPException(status_code=422, detail="No readable text found in the uploaded file.")

    # Trim to first 6000 chars to stay within token limits while keeping essentials
    trimmed = text[:6000]

    try:
        resp = chat(
            messages=[
                {"role": "system", "content": _EXTRACT_SYSTEM},
                {"role": "user",   "content": f"Parse this CV:\n\n{trimmed}"},
            ],
            temperature=0.1,
            max_tokens=600,
            json_mode=True,
        )
        import re, json as _json
        raw_json = resp["message"]["content"]
        match = re.search(r"\{[\s\S]*\}", raw_json)
        if not match:
            raise ValueError("No JSON in LLM response")
        extracted = _json.loads(match.group())
    except Exception as e:
        logger.error("LLM extraction failed: %s", e)
        raise HTTPException(status_code=502, detail="AI extraction failed. Please fill the form manually.")

    # Return only the keys ProfileData expects; null → empty string for the frontend
    fields = ["name", "currentRole", "education", "skills", "experience", "goals", "industries"]
    return {k: (extracted.get(k) or "") for k in fields}
