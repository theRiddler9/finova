from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.contracts.cases import CaseStatus, EvidenceSource
from app.db.base import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cases: Mapped[list[Case]] = relationship(back_populates="merchant")


class WebhookEventStatus(StrEnum):
    RECEIVED = "RECEIVED"
    QUEUED = "QUEUED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    __table_args__ = (
        UniqueConstraint("merchant_id", "event_id", name="uq_webhook_merchant_event"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    merchant_id: Mapped[UUID] = mapped_column(ForeignKey("merchants.id", ondelete="CASCADE"))
    event_id: Mapped[str] = mapped_column(String(128))
    event_type: Mapped[str] = mapped_column(String(200))
    status: Mapped[WebhookEventStatus] = mapped_column(default=WebhookEventStatus.RECEIVED)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (
        UniqueConstraint("merchant_id", "paypal_dispute_id", name="uq_case_merchant_dispute"),
        Index("ix_cases_merchant_status", "merchant_id", "status"),
        Index("ix_cases_response_deadline", "response_deadline"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    merchant_id: Mapped[UUID] = mapped_column(ForeignKey("merchants.id", ondelete="CASCADE"))
    paypal_dispute_id: Mapped[str] = mapped_column(String(128))
    status: Mapped[CaseStatus] = mapped_column(default=CaseStatus.RECEIVED)
    response_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    merchant: Mapped[Merchant] = relationship(back_populates="cases")
    evidence_items: Mapped[list[EvidenceItem]] = relationship(back_populates="case")


class EvidenceItem(Base):
    __tablename__ = "evidence_items"
    __table_args__ = (Index("ix_evidence_case_occurred", "case_id", "occurred_at"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id: Mapped[UUID] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    source: Mapped[EvidenceSource] = mapped_column(String(32))
    kind: Mapped[str] = mapped_column(String(100))
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    confidence: Mapped[float | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case: Mapped[Case] = relationship(back_populates="evidence_items")
