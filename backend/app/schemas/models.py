from pydantic import BaseModel
from typing import Optional


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str


class UserProfile(BaseModel):
    name: Optional[str] = None
    currentRole: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    goals: Optional[str] = None
    industries: Optional[str] = None
    bio: Optional[str] = None  # free-text self-description for LLM extraction


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    profile: Optional[UserProfile] = None
    session_id: Optional[str] = None  # client-supplied; auto-ignored if absent


class RoadmapRequest(BaseModel):
    profile: UserProfile
