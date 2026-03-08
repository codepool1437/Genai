# AI Career Roadmap Generator

A personalized career growth plan generator using Generative AI and RAG (Retrieval-Augmented Generation).

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 + Tailwind CSS |
| Visualization | React Flow + Recharts |
| Backend | Python + FastAPI |
| LLM | Llama 3.2 3B (local via Ollama) |
| Embeddings | all-MiniLM-L6-v2 (HuggingFace) |
| Vector DB | ChromaDB |
| RAG Framework | LangChain |
| Database | PostgreSQL |
| Cache | Redis |
| Monitoring | Langfuse |

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Config, auth, security
│   │   ├── db/           # PostgreSQL models
│   │   ├── rag/          # LangChain pipeline
│   │   ├── schemas/      # Pydantic models
│   │   └── services/     # Business logic
│   └── data/             # Raw datasets (course catalog, job-skill mappings)
├── frontend/
│   ├── app/              # Next.js app router pages
│   ├── components/
│   │   ├── roadmap/      # React Flow flowchart components
│   │   └── charts/       # Recharts skill radar chart
│   └── lib/              # API client, utilities
└── scripts/              # Data ingestion and vectorization scripts
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL
- Redis
- [Ollama](https://ollama.com) with `llama3.2:3b` pulled

### Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # Fill in your values
alembic upgrade head          # Run DB migrations
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local    # Fill in your values
npm run dev
```

### Pull the LLM
```bash
ollama pull llama3.2:3b
```
