"""Request/response schemas for ward services and the dynamic checklist engine."""

from typing import Any

from pydantic import BaseModel


class ServiceOut(BaseModel):
    id: str
    name: str
    name_ne: str | None = None
    description: str | None = None
    fee: str | None = None
    estimated_time: str | None = None
    responsible_department: str | None = None

    class Config:
        from_attributes = True


class ChecklistQuestionAnswer(BaseModel):
    """One follow-up question the citizen has answered, e.g. {"birth_in_nepal": "yes"}."""

    question_id: str
    answer: Any


class ChecklistRequest(BaseModel):
    service_id: str
    answers: list[ChecklistQuestionAnswer] = []


class ChecklistNextQuestion(BaseModel):
    question_id: str
    question_text: str
    question_type: str  # "yes_no" | "single_select" | "text"
    options: list[str] | None = None


class ChecklistResponse(BaseModel):
    """
    Either `next_question` is set (engine needs more info) or `checklist`
    is set (engine has enough info to generate the final personalized list).
    """

    next_question: ChecklistNextQuestion | None = None
    checklist: list[str] | None = None
    is_complete: bool = False
