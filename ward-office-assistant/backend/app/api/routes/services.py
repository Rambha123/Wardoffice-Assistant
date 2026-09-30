"""
Ward services, ward information, and the Dynamic Checklist Generator.

    GET  /services/               -> list all services (for a directory/search UI)
    GET  /services/{service_id}   -> service detail
    POST /services/checklist      -> stateless step of the dynamic checklist Q&A
    GET  /services/office-info    -> hours, contacts, departments, map
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.service import ServiceOut, ChecklistRequest, ChecklistResponse
from app.services import checklist_service
from app.models.service import Service

router = APIRouter()


@router.get("/", response_model=list[ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).all()


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: str, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/checklist", response_model=ChecklistResponse)
def get_next_checklist_step(payload: ChecklistRequest, db: Session = Depends(get_db)):
    """
    Given the answers so far, either returns the next follow-up question or,
    once enough is known, the final personalized document checklist.
    """
    return checklist_service.get_next_step(
        db=db, service_id=payload.service_id, answers=payload.answers
    )


# TODO: add /office-info route once OfficeInfo/Notice/FAQ CRUD (admin panel)
# is built out.
