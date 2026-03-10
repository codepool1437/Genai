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


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    profile: Optional[UserProfile] = None
    session_id: Optional[str] = None  # client-supplied; auto-ignored if absent


class RoadmapRequest(BaseModel):
    profile: UserProfile


# ── Resume ────────────────────────────────────────────────────────────────────

class ResumeRequest(BaseModel):
    resumeText: Optional[str] = None
    pdfBase64: Optional[str] = None
    filename: Optional[str] = None
    targetRole: Optional[str] = None


# ── Cover Letter ──────────────────────────────────────────────────────────────

class CoverLetterRequest(BaseModel):
    jobDescription: str
    companyName: Optional[str] = None
    roleName: Optional[str] = None
    resumeText: Optional[str] = None
    additionalNotes: Optional[str] = None
    tone: str = "professional"


# ── Interview ─────────────────────────────────────────────────────────────────

class InterviewMessage(BaseModel):
    role: str
    content: str


class InterviewRequest(BaseModel):
    action: str  # "generate_questions" | "chat" | "evaluate"
    role: Optional[str] = None
    experienceLevel: Optional[str] = "mid-level"
    interviewType: Optional[str] = "mixed"
    questionCount: Optional[int] = 5
    messages: Optional[list[InterviewMessage]] = None


# ── Quiz ──────────────────────────────────────────────────────────────────────

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: list[str]
    correct_index: int
    explanation: str
    difficulty: str


class QuizRequest(BaseModel):
    action: str  # "generate" | "evaluate"
    skill: Optional[str] = None
    difficulty: Optional[str] = None
    questionCount: Optional[int] = 5
    questions: Optional[list[QuizQuestion]] = None
    answers: Optional[list[int]] = None
