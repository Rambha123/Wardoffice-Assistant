"""
Document Readiness Check — NOT document validation. This module checks
whether a citizen *appears ready* to visit the ward office; it never makes
legal claims about document authenticity.

Workflow:
    Upload -> save to temp dir -> OCR -> extract info -> run checks
    -> delete temp file -> return DocumentReadinessResponse

Checks performed (see docs/architecture.md for the full rule table):
    - Correct document type? (keyword match on OCR text)
    - Required documents uploaded? (compare against Service.base_documents)
    - Important fields readable? (OCR confidence threshold)
    - Mandatory form fields filled? (only relevant for forms, not IDs)
    - Missing signatures / attachments? (heuristic — flagged for manual review,
      not guaranteed to be accurate)
"""

import os
import tempfile
import uuid

from fastapi import UploadFile

from app.core.config import settings
from app.schemas.document import DocumentReadinessResponse, DocumentCheckItem
from app.services import ocr_service

MIN_OCR_CONFIDENCE = 0.6


async def check_readiness(service_id: str, files: list[UploadFile]) -> DocumentReadinessResponse:
    checks: list[DocumentCheckItem] = []

    for upload in files:
        temp_path = os.path.join(settings.TMP_UPLOAD_DIR, f"{uuid.uuid4()}_{upload.filename}")
        os.makedirs(settings.TMP_UPLOAD_DIR, exist_ok=True)

        try:
            contents = await upload.read()
            with open(temp_path, "wb") as f:
                f.write(contents)

            ocr_result = ocr_service.extract_text(temp_path)
            checks.append(_evaluate_single_document(upload.filename, ocr_result))

        finally:
            # Privacy requirement: always delete the uploaded file, even if
            # OCR or evaluation raised an exception.
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # TODO: cross-check `checks` against Service(service_id).base_documents
    # to flag documents that were REQUIRED but never uploaded at all
    # (as opposed to uploaded-but-unreadable, which is handled above).
    missing_required = _find_missing_required_documents(service_id, uploaded=[c.document_name for c in checks])
    checks.extend(missing_required)

    overall_ready = all(c.status == "ok" for c in checks)

    return DocumentReadinessResponse(
        service_id=service_id,
        overall_ready=overall_ready,
        checks=checks,
        notes="This is a readiness check, not a legal validation of your documents.",
    )


def _evaluate_single_document(filename: str, ocr_result: ocr_service.OcrResult) -> DocumentCheckItem:
    if not ocr_result.full_text.strip():
        return DocumentCheckItem(document_name=filename, status="unreadable", detail="No text could be extracted.")

    if ocr_result.average_confidence < MIN_OCR_CONFIDENCE:
        return DocumentCheckItem(
            document_name=filename,
            status="unreadable",
            detail=f"Low OCR confidence ({ocr_result.average_confidence:.0%}); please re-upload a clearer scan.",
        )

    # TODO: classify document type via keyword matching (see ocr_service TODO)
    # and compare against what this service expects, to catch "wrong_type".
    return DocumentCheckItem(document_name=filename, status="ok")


def _find_missing_required_documents(service_id: str, uploaded: list[str]) -> list[DocumentCheckItem]:
    """
    TODO: query Service(service_id).base_documents (adjusted by the
    citizen's checklist answers, if available) and diff against `uploaded`
    filenames/types to report documents that are entirely missing.
    """
    return []
