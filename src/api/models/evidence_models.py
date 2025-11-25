from __future__ import annotations

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field


SeverityLiteral = Literal["info", "medium", "high", "critical"]
StatusLiteral = Literal["idle", "running", "complete"]


class EvidenceItem(BaseModel):
    id: str
    title: str
    source: str
    collected_at: datetime
    severity: SeverityLiteral
    tags: List[str]
    link: str


class EvidenceBatch(BaseModel):
    batch_id: str = Field(..., alias="batch_id")
    page: int
    total: int
    items: List[EvidenceItem]


class EvidenceIngestionStatus(BaseModel):
    pipeline: str
    mode: Literal["read-only"] = Field(default="read-only")
    status: StatusLiteral
    last_success: datetime
    pending_batches: int


__all__ = [
    "EvidenceItem",
    "EvidenceBatch",
    "EvidenceIngestionStatus",
]
