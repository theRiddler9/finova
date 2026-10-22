from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CaseStatus(StrEnum):
    RECEIVED = "RECEIVED"
    COLLECTING = "COLLECTING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    SUBMITTED = "SUBMITTED"
    WON = "WON"
    LOST = "LOST"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class EvidenceSource(StrEnum):
    PAYPAL = "paypal"
    SHOPIFY = "shopify"
    SHIPPO = "shippo"
    ZENDESK = "zendesk"
    VISION = "vision"
    MERCHANT = "merchant"


class EvidenceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    source: EvidenceSource
    kind: str = Field(min_length=1, max_length=100)
    occurred_at: datetime | None = None
    summary: str = Field(min_length=1)
    payload: dict[str, object] = Field(default_factory=dict)
    confidence: float | None = Field(default=None, ge=0, le=1)


class EvidenceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    items: list[EvidenceItem] = Field(default_factory=list)
    missing_sources: list[EvidenceSource] = Field(default_factory=list)


class CaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    merchant_id: UUID
    paypal_dispute_id: str = Field(min_length=1, max_length=128)
    response_deadline: datetime


class CaseRead(CaseCreate):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    status: CaseStatus
    created_at: datetime
    updated_at: datetime


class WebhookEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=200)
    merchant_id: UUID
    payload: dict[str, object] = Field(default_factory=dict)
