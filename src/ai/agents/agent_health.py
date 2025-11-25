from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class AgentHealthStatus(BaseModel):
    """Deterministic heartbeat payload exposed via the API layer."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "degraded"]
    last_heartbeat_ts: str
    agent_version: str
    ready: bool


_HEALTH_SNAPSHOT = AgentHealthStatus(
    status="ok",
    last_heartbeat_ts="2025-11-01T00:00:00Z",
    agent_version="agent-runtime-v1",
    ready=True,
)


def get_agent_health_snapshot() -> AgentHealthStatus:
    """Return a copy of the static agent health snapshot."""

    return AgentHealthStatus.model_validate(_HEALTH_SNAPSHOT.model_dump())


__all__ = ["AgentHealthStatus", "get_agent_health_snapshot"]
