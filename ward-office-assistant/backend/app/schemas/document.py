"""Request/response schemas for the Document Readiness Check endpoint."""

from pydantic import BaseModel


class DocumentCheckItem(BaseModel):
    document_name: str
    status: str  # "ok" | "missing" | "unreadable" | "wrong_type"
    detail: str | None = None  # e.g. "Passport photo missing", "Signature not detected"


class DocumentReadinessResponse(BaseModel):
    service_id: str
    overall_ready: bool
    checks: list[DocumentCheckItem]
    notes: str | None = None

    # Reminder (see document_readiness_service.py): this is readiness
    # checking, NOT legal validation of document authenticity.
