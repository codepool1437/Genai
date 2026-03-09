"""
Profile persistence — Phase 6
GET  /api/profile  → reads  backend/data/profile.json
POST /api/profile  → writes backend/data/profile.json
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

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
