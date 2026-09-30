"""
Ward office metadata: hours, contacts, departments, FAQs, notices.
Populated/edited by ward staff through the Admin Panel.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class OfficeInfo(Base):
    """Singleton-ish table: typically one row per ward, edited via admin panel."""

    __tablename__ = "office_info"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ward_name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    office_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    map_embed_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # [{"name": "Registration Dept", "officer": "...", "room": "..."}, ...]
    departments: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notice(Base):
    __tablename__ = "notices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FAQ(Base):
    __tablename__ = "faqs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    service_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class KnowledgeDocument(Base):
    """
    Metadata for files uploaded via the Admin Panel (Citizen Charters, Forms,
    Circulars) that get pushed into the RAG ingestion pipeline. The file
    itself lives in /data/raw, this row tracks status + ChromaDB linkage.
    """

    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[str] = mapped_column(String(50))  # citizen_charter | form | circular
    file_path: Mapped[str] = mapped_column(String(500))
    ingestion_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending|processing|indexed|failed
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
