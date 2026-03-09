import json
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.rag.ingestor import ingest_file, remove_file as rag_remove_file

router = APIRouter()

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Persist document registry to disk so it survives restarts
_REGISTRY_PATH = Path(__file__).parent.parent.parent / "data" / "documents.json"
_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_registry() -> list[dict]:
    if _REGISTRY_PATH.exists():
        try:
            return json.loads(_REGISTRY_PATH.read_text())
        except Exception:
            return []
    return []


def _save_registry(docs: list[dict]) -> None:
    _REGISTRY_PATH.write_text(json.dumps(docs, indent=2))


@router.get("/documents")
async def list_documents():
    return {"documents": _load_registry()}


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("general"),
):
    allowed_ext = {".pdf", ".txt", ".md", ".docx"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Use: {allowed_ext}",
        )

    doc_id = str(uuid.uuid4())
    content = await file.read()

    # Save raw file for reference
    dest = UPLOAD_DIR / f"{doc_id}{ext}"
    dest.write_bytes(content)

    # Index into vector store
    meta = ingest_file(
        filename=file.filename or f"upload{ext}",
        raw_bytes=content,
        doc_id=doc_id,
        doc_type=doc_type,
    )

    from datetime import datetime, timezone
    doc = {
        "id":           doc_id,
        "file_name":    file.filename,
        "doc_type":     doc_type,
        "size_bytes":   len(content),
        "stored_path":  str(dest),
        "chunk_count":  meta.get("chunk_count", 0),
        "text_preview": meta.get("text_preview", ""),
        "status":       "indexed",
        "created_at":   datetime.now(timezone.utc).isoformat(),
    }

    docs = _load_registry()
    docs.append(doc)
    _save_registry(docs)
    return {"document": doc}


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    docs = _load_registry()
    existing = next((d for d in docs if d["id"] == doc_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove from vector store
    rag_remove_file(doc_id)

    # Remove raw file
    try:
        Path(existing["stored_path"]).unlink(missing_ok=True)
    except Exception:
        pass

    docs = [d for d in docs if d["id"] != doc_id]
    _save_registry(docs)
    return {"deleted": doc_id}
