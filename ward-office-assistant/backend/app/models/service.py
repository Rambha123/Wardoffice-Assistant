"""
Service model — represents one ward service (e.g. "Birth Registration",
"Citizenship Recommendation"). This is the structured backbone the dynamic
checklist engine and readiness checker key off of; the RAG layer is used
for free-text Q&A on top of it.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))                # e.g. "Birth Registration"
    name_ne: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Nepali name
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    fee: Mapped[str | None] = mapped_column(String(100), nullable=True)      # store as text: fees vary/have conditions
    estimated_time: Mapped[str | None] = mapped_column(String(100), nullable=True)
    responsible_department: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Follow-up questions used by the Dynamic Checklist Generator, e.g.:
    # [{"id": "birth_in_nepal", "question": "Was the birth in Nepal?", "type": "yes_no"}, ...]
    checklist_questions: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Base document requirements before conditional logic is applied, e.g.:
    # [{"doc": "Citizenship of parents", "condition": None}, ...]
    base_documents: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # TODO: normalize checklist_questions / base_documents into proper
    # child tables once the rule engine's conditional logic is finalized —
    # JSON is fine for the prototype stage.
