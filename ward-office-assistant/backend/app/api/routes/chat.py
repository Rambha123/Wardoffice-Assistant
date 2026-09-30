"""
AI Service Assistant endpoint — the RAG-powered Q&A route.

Flow: question -> rag_service.answer_question() -> retrieval + Gemini -> answer.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services import rag_service

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def ask_question(payload: ChatRequest) -> ChatResponse:
    """
    Answer a citizen's free-text question using only official ward documents
    (Citizen Charters, Forms, Circulars) via the RAG pipeline.
    """
    try:
        return await rag_service.answer_question(
            question=payload.question,
            session_id=payload.session_id,
            service_id=payload.service_id,
        )
    except Exception as exc:  # noqa: BLE001 — replace with narrower exceptions as they emerge
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {exc}") from exc


# TODO: add GET /chat/history/{session_id} once conversation persistence
# (Postgres or Redis) is decided.
