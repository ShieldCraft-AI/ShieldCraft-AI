from __future__ import annotations

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field


StatusLiteral = Literal["steady", "watch", "investigate"]
SeverityLiteral = Literal["info", "medium", "high"]


class DashboardSummaryMetadata(BaseModel):
    atu_id: str = Field(..., alias="atu_id")
    spec_version: str = Field(..., alias="spec_version")
    last_synced: datetime = Field(..., alias="last_synced")


class DashboardSummaryItem(BaseModel):
    id: str
    label: str
    headline: str
    status: StatusLiteral
    last_reviewed: datetime
    evidence_source: str


class DashboardSummarySection(BaseModel):
    section_id: str
    title: str
    description: str
    items: List[DashboardSummaryItem]


class DashboardSummaryResponse(BaseModel):
    metadata: DashboardSummaryMetadata
    sections: List[DashboardSummarySection]


class EvidenceItem(BaseModel):
    id: str
    title: str
    source: str
    collected_at: datetime
    severity: SeverityLiteral
    tags: List[str]
    link: str


class EvidenceFeedResponse(BaseModel):
    page: int
    total: int
    items: List[EvidenceItem]


__all__ = [
    "DashboardSummaryResponse",
    "DashboardSummaryMetadata",
    "DashboardSummarySection",
    "DashboardSummaryItem",
    "EvidenceFeedResponse",
    "EvidenceItem",
]
