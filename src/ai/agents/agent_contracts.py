from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field


class PlanSignal(BaseModel):
    """Typed signal element pulled from the plan fixture."""

    model_config = ConfigDict(extra="forbid")

    source: str
    indicator: str
    confidence: float = Field(ge=0.0, le=1.0)


class AgentPlan(BaseModel):
    """Canonical plan contract consumed by the agent runtime."""

    model_config = ConfigDict(extra="forbid")

    plan_id: str
    severity: str
    env: str
    tags: List[str] = Field(default_factory=list)
    affected_assets: List[str] = Field(default_factory=list)
    signals: List[PlanSignal] = Field(default_factory=list)


class AgentStepTrace(BaseModel):
    """Trace wrapper for each deterministic agent execution."""

    model_config = ConfigDict(extra="forbid")

    agent: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]


class AgentOrchestrationRequest(BaseModel):
    """Envelope consumed by the orchestrator entrypoint."""

    model_config = ConfigDict(extra="forbid")

    plan: AgentPlan


class AgentOrchestrationResponse(BaseModel):
    """Response contract surfaced by the orchestrator and API."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    steps: List[AgentStepTrace]
    final_recommendation: Dict[str, Any]


__all__ = [
    "AgentOrchestrationRequest",
    "AgentOrchestrationResponse",
    "AgentPlan",
    "AgentStepTrace",
    "PlanSignal",
]
