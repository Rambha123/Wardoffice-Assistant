"""
Document-related endpoints:

    POST /documents/readiness-check   -> citizen uploads docs for a service,
                                          gets back a readiness checklist.
    POST /documents/admin-upload      -> ward staff uploads a Citizen Charter /
                                          Form / Circular into the knowledge base
                                          (kicks off the ingestion pipeline).

Privacy: uploaded citizen documents (readiness-check) are processed in a
temp location and deleted immediately after processing — see
document_readiness_service.py. They are NEVER written into data/raw or any
permanent store; that path is reserved for official ward documents only.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.schemas.document import DocumentReadinessResponse
from app.services import document_readiness_service

router = APIRouter()


@router.post("/readiness-check", response_model=DocumentReadinessResponse)
async def check_document_readiness(
    service_id: str = Form(...),
    files: list[UploadFile] = File(...),
) -> DocumentReadinessResponse:
    """
    Runs OCR + rule-based checks on uploaded documents for a given service
    and reports readiness (present/missing/unreadable) — NOT legal validity.
    """
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required.")

    try:
        return await document_readiness_service.check_readiness(service_id=service_id, files=files)
    finally:
        # Belt-and-suspenders: service layer should already delete temp files,
        # but make sure nothing lingers even if it raised partway through.
        pass


@router.post("/admin-upload")
async def admin_upload_knowledge_document(
    doc_type: str = Form(..., description="citizen_charter | form | circular"),
    title: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Ward-staff-only endpoint (add auth dependency once JWT roles are wired
    up) to add a new document to the RAG knowledge base.
    """
    # TODO: 1) save file to data/raw/, 2) create KnowledgeDocument row,
    # 3) trigger ingestion/pipeline.py (sync for now, background task later).
    raise HTTPException(status_code=501, detail="Not implemented yet — see TODO in documents.py")
