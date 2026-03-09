from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, resume, cover_letter, interview, quiz, documents

app = FastAPI(title="AI Career Roadmap API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8081", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router,         prefix="/api")
app.include_router(resume.router,       prefix="/api")
app.include_router(cover_letter.router, prefix="/api")
app.include_router(interview.router,    prefix="/api")
app.include_router(quiz.router,         prefix="/api")
app.include_router(documents.router,    prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
