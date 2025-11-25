from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, ConfigDict


class DriftSignal(BaseModel):
    """Represents a single metric tracked for drift."""

    model_config = ConfigDict(extra="forbid")

    metric: str
    baseline_value: float
    current_value: float
    deviation_pct: float
    severity: Literal["low", "medium", "high"]


class DriftStatus(BaseModel):
    """Captures the aggregate drift health for the environment."""

    model_config = ConfigDict(extra="forbid")

    environment: str
    state: Literal["normal", "attention", "critical"]
    last_evaluated_ts: str
    ready: bool


class DriftSummary(BaseModel):
    """Top-level response returned by the drift evaluator/API."""

    model_config = ConfigDict(extra="forbid")

    status: DriftStatus
    signals: List[DriftSignal]
    recommendations: List[str]


__all__ = ["DriftSignal", "DriftStatus", "DriftSummary"]
