import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

fastapi_spec = importlib.util.find_spec("fastapi")
if not fastapi_spec:  # pragma: no cover - safety for stripped envs
    pytest.skip(
        "fastapi not installed; skipping agent orchestration API tests",
        allow_module_level=True,
    )

from api.app import app  # noqa: E402
from src.ai.agents.agent_contracts import AgentOrchestrationResponse  # noqa: E402

client = TestClient(app)


@pytest.fixture()
def plan_payload() -> dict:
    fixture_path = (
        Path(__file__).resolve().parents[1] / "fixtures" / "ai" / "sample_plan.json"
    )
    with fixture_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_agent_orchestration_endpoint_returns_deterministic_payload(plan_payload):
    body = {"plan": plan_payload}

    first_response = client.post("/api/agent/orchestrate", json=body)
    second_response = client.post("/api/agent/orchestrate", json=body)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == second_response.json()

    payload = AgentOrchestrationResponse.model_validate(first_response.json())
    assert payload.final_recommendation["priority"] == "escalate"
    assert [step.agent for step in payload.steps] == [
        "plan_ingestor",
        "risk_profiler",
        "action_planner",
    ]
