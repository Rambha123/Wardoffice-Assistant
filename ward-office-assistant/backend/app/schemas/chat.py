"""Request/response schemas for the AI Service Assistant (RAG chat) endpoint."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., description="Citizen's question, in English/Nepali/mixed.")
    session_id: str | None = Field(None, description="Groups turns of one conversation for follow-ups.")
    service_id: str | None = Field(None, description="Optional: scope retrieval to one service.")


class SourceChunk(BaseModel):
    """A retrieved chunk used to ground the answer, returned for transparency."""

    text: str
    source_document: str
    page: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = []
    detected_language: str | None = None  # "en" | "ne" | "mixed"
    # TODO: add `suggested_next_questions` and `related_service_id` once the
    # assistant can proactively route into the Dynamic Checklist Generator.
