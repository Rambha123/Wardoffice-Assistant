"""
Dynamic Checklist Generator.

Rather than showing a fixed checklist for a service, this walks the citizen
through the service's `checklist_questions` (stored on the Service model)
one at a time, then applies conditional logic to produce a personalized
document checklist.

Example (Birth Registration):
    Q1: Was the birth in Nepal?        -> yes/no
    Q2: Is it a late registration?      -> yes/no
    Q3: Are both parents Nepali?        -> yes/no
    => personalized list of required documents.
"""

from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.service import (
    ChecklistQuestionAnswer,
    ChecklistResponse,
    ChecklistNextQuestion,
)


def get_next_step(
    db: Session,
    service_id: str,
    answers: list[ChecklistQuestionAnswer],
) -> ChecklistResponse:
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service or not service.checklist_questions:
        return ChecklistResponse(is_complete=True, checklist=[])

    questions = service.checklist_questions  # list[dict] as defined on the model
    answered_ids = {a.question_id for a in answers}

    # 1. Find the next unanswered question, in order.
    for q in questions:
        if q["id"] not in answered_ids:
            return ChecklistResponse(
                next_question=ChecklistNextQuestion(
                    question_id=q["id"],
                    question_text=q["question"],
                    question_type=q.get("type", "yes_no"),
                    options=q.get("options"),
                ),
                is_complete=False,
            )

    # 2. All questions answered -> build the personalized checklist.
    checklist = _build_checklist(service, answers)
    return ChecklistResponse(checklist=checklist, is_complete=True)


def _build_checklist(service: Service, answers: list[ChecklistQuestionAnswer]) -> list[str]:
    """
    TODO: implement the actual conditional rule engine. Rough shape:

        answers_by_id = {a.question_id: a.answer for a in answers}
        checklist = [doc["doc"] for doc in service.base_documents if doc.get("condition") is None]
        for doc in service.base_documents:
            cond = doc.get("condition")
            if cond and _condition_met(cond, answers_by_id):
                checklist.append(doc["doc"])
        return checklist

    Where `_condition_met` evaluates simple rules like
    {"question_id": "late_registration", "equals": "yes"}.
    Start simple (equality checks); this can grow into a small rules DSL
    if the supervisor wants something more "advanced" to showcase.
    """
    base_docs = service.base_documents or []
    return [doc.get("doc", "") for doc in base_docs if doc.get("condition") is None]
