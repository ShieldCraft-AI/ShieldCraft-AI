import json
from pathlib import Path

from src.ai.agents.agent_health import AgentHealthStatus, get_agent_health_snapshot

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "agent_health.json"


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_agent_health_snapshot_matches_fixture():
    expected = _load_fixture()

    snapshot = get_agent_health_snapshot()

    assert isinstance(snapshot, AgentHealthStatus)
    assert snapshot.model_dump() == expected


def test_agent_health_snapshot_is_deterministic():
    first = get_agent_health_snapshot()
    second = get_agent_health_snapshot()

    assert first is not second
    assert first.model_dump() == second.model_dump()
    assert first.last_heartbeat_ts == "2025-11-01T00:00:00Z"
    assert "uuid" not in first.model_dump().keys()
