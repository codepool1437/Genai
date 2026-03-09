"""
RAGAS-style RAG Evaluation — Phase 5
Scores the RAG pipeline on three metrics using pure cosine similarity
(no external RAGAS library).

Metrics
-------
• Context Relevance  : cos(query_emb, context_emb)
  → "Did we retrieve context that is actually related to the question?"

• Answer Faithfulness: cos(context_emb, answer_emb)
  → "Is the answer grounded in the retrieved context?"

• Answer Relevance   : cos(query_emb, answer_emb)
  → "Does the answer actually address the question asked?"

All embeddings come from all-MiniLM-L6-v2 (L2-normalised → dot == cosine).
"""
from __future__ import annotations

import logging
import time
from typing import Optional

import numpy as np
import ollama
from fastapi import APIRouter

from app.rag.embedder import embed_one
from app.rag.retriever import retrieve

logger = logging.getLogger(__name__)
router = APIRouter()
MODEL = "llama3.2:3b"

# ── Default evaluation question set ─────────────────────────────────────────

DEFAULT_QUESTIONS = [
    "What skills do I need to become a machine learning engineer?",
    "What are the best Python courses for data science beginners?",
    "How long does it take to learn React for frontend development?",
    "What certifications should I get for cloud computing?",
    "What tools do DevOps engineers use daily?",
    "How do I transition from software developer to product manager?",
    "What programming languages should a backend developer know?",
    "What is the difference between deep learning and machine learning?",
]

_RAG_SYSTEM = (
    "You are a helpful career guidance assistant. "
    "Answer the user's question using ONLY the context provided below. "
    "If the context doesn't contain enough information, say so briefly. "
    "Keep your answer concise (2-4 sentences).\n\n"
    "CONTEXT:\n{context}"
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two L2-normalised vectors (dot product)."""
    val = float(np.dot(a, b))
    # Clamp to [0, 1] — embeddings are normalised, values slightly outside
    # [-1,1] can happen due to float32 rounding.
    return round(max(0.0, min(1.0, val)), 4)


def _llm_answer(question: str, context: str) -> str:
    """Call Ollama to generate a RAG answer."""
    system = _RAG_SYSTEM.format(context=context[:3000])
    try:
        resp = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": question},
            ],
            options={"temperature": 0.2, "num_predict": 200},
        )
        return resp["message"]["content"].strip()
    except Exception as e:
        logger.warning("LLM call failed for question %r: %s", question[:40], e)
        return f"[LLM error: {e}]"


def _evaluate_one(question: str) -> dict:
    """Run retrieve → generate → score for a single question."""
    t0 = time.time()

    # 1. Retrieve context
    context_str, sources = retrieve(question)
    context_for_score = context_str[:2000] if context_str else question

    # 2. Generate answer
    answer = _llm_answer(question, context_str)

    # 3. Embed all three
    q_emb   = embed_one(question)
    ctx_emb = embed_one(context_for_score)
    ans_emb = embed_one(answer)

    # 4. Score
    context_relevance   = _cosine(q_emb,   ctx_emb)
    answer_faithfulness = _cosine(ctx_emb,  ans_emb)
    answer_relevance    = _cosine(q_emb,    ans_emb)

    return {
        "question":            question,
        "context_snippet":     context_str[:400] if context_str else "(no context retrieved)",
        "answer":              answer,
        "sources_count":       len(sources),
        "context_relevance":   context_relevance,
        "answer_faithfulness": answer_faithfulness,
        "answer_relevance":    answer_relevance,
        "latency_s":           round(time.time() - t0, 2),
    }


# ── Endpoint ─────────────────────────────────────────────────────────────────

class EvaluateRequest(
    # Inline pydantic model — keeps things self-contained
    __import__("pydantic").BaseModel
):
    questions: Optional[list[str]] = None   # use DEFAULT_QUESTIONS if omitted
    max_questions: int = 8                  # safety cap for slow LLM


@router.post("/evaluate")
async def run_evaluation(req: EvaluateRequest):
    """
    Run RAGAS-style evaluation on the RAG pipeline.

    Returns per-question triplets (question / context / answer) with three
    cosine-similarity metrics, plus aggregate averages.
    """
    questions = (req.questions or DEFAULT_QUESTIONS)[: req.max_questions]

    results = []
    for q in questions:
        logger.info("Evaluating: %s", q[:60])
        try:
            results.append(_evaluate_one(q))
        except Exception as e:
            logger.error("Eval failed for %r: %s", q[:40], e)
            results.append({
                "question": q,
                "context_snippet": "",
                "answer": f"[error: {e}]",
                "sources_count": 0,
                "context_relevance":   0.0,
                "answer_faithfulness": 0.0,
                "answer_relevance":    0.0,
                "latency_s":          0.0,
            })

    # Aggregate
    def _avg(key: str) -> float:
        vals = [r[key] for r in results if isinstance(r[key], float)]
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    aggregate = {
        "context_relevance":   _avg("context_relevance"),
        "answer_faithfulness": _avg("answer_faithfulness"),
        "answer_relevance":    _avg("answer_relevance"),
        "avg_latency_s":       _avg("latency_s"),
        "num_questions":       len(results),
    }

    return {"results": results, "aggregate": aggregate}
