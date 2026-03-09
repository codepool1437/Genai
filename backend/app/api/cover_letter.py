import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.models import CoverLetterRequest
from app.rag.prompts import COVER_LETTER_SYSTEM
from app.llm import stream_chat

router = APIRouter()


def _stream_cover_letter(req: CoverLetterRequest):
    user_prompt = f"""Write a cover letter with the following details:
- Job Description: {req.jobDescription[:2000]}
- Company: {req.companyName or 'Not specified'}
- Role: {req.roleName or 'Not specified'}
- Tone: {req.tone or 'professional'}
{f"- Applicant Resume Summary: {req.resumeText[:1000]}" if req.resumeText else ""}
{f"- Additional Notes: {req.additionalNotes}" if req.additionalNotes else ""}"""

    for chunk in stream_chat(
        messages=[
            {"role": "system", "content": COVER_LETTER_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    ):
        content = chunk.get("message", {}).get("content", "")
        if content:
            yield f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"

    yield "data: [DONE]\n\n"


@router.post("/cover-letter")
async def generate_cover_letter(req: CoverLetterRequest):
    return StreamingResponse(
        _stream_cover_letter(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
