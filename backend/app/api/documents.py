import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

router = APIRouter()

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory document registry (sufficient for Review 1)
_documents: list[dict] = []


@router.get("/documents")
async def list_documents():
    return {"documents": _documents}


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("general"),
):
    # Validate file type
    allowed_ext = {".pdf", ".txt", ".md", ".docx"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported. Use: {allowed_ext}")

    doc_id = str(uuid.uuid4())
    safe_name = f"{doc_id}{ext}"
    dest = UPLOAD_DIR / safe_name

    content = await file.read()
    dest.write_bytes(content)

    doc = {
        "id": doc_id,
        "file_name": file.filename,
        "doc_type": doc_type,
        "size_bytes": len(content),
        "stored_path": str(dest),
    }
    _documents.append(doc)
    return {"document": doc}


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    global _documents
    existing = next((d for d in _documents if d["id"] == doc_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove the file from disk
    try:
        Path(existing["stored_path"]).unlink(missing_ok=True)
    except Exception:
        pass

    _documents = [d for d in _documents if d["id"] != doc_id]
    return {"deleted": doc_id}
