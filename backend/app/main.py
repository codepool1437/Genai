import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, resume, cover_letter, interview, quiz, documents, roadmap, evaluate
from app.rag.seed_courses import seed_courses
from app.rag.embedder import get_embedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: warm the embedding model and seed the course corpus."""
    logger.info("Warming up embedding model …")
    get_embedder()          # loads all-MiniLM-L6-v2 into memory
    logger.info("Seeding course corpus …")
    seed_courses()          # no-op if already seeded
    logger.info("Backend ready.")
    yield

app = FastAPI(title="AI Career Roadmap API", version="2.0.0", lifespan=lifespan)

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
app.include_router(roadmap.router,      prefix="/api")
app.include_router(evaluate.router,     prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
