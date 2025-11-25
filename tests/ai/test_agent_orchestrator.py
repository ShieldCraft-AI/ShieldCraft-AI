import copy
import importlib.util
import json
from pathlib import Path

import pytest

pydantic_spec = importlib.util.find_spec("pydantic")
if not pydantic_spec:  # pragma: no cover - safety for stripped envs
    pytest.skip("pydantic not installed; skipping agent tests", allow_module_level=True)

from src.ai.agents.agent_contracts import (  # noqa: E402
    AgentOrchestrationRequest,
    AgentOrchestrationResponse,
)
from src.ai.agents.agent_orchestrator import orchestrate_agents  # noqa: E402


@pytest.fixture()
def plan_payload() -> dict:
    fixture_path = (
        Path(__file__).resolve().parents[1] / "fixtures" / "ai" / "sample_plan.json"
    )
    with fixture_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_orchestrator_returns_deterministic_trace(plan_payload):
    request = AgentOrchestrationRequest(plan=plan_payload)

    first_pass = orchestrate_agents(request)
    second_pass = orchestrate_agents(request)

    assert isinstance(first_pass, AgentOrchestrationResponse)
    assert first_pass.model_dump() == second_pass.model_dump()
    assert [step.agent for step in first_pass.steps] == [
        "plan_ingestor",
        "risk_profiler",
        "action_planner",
    ]


def test_orchestrator_preserves_input_plan(plan_payload):
    original = copy.deepcopy(plan_payload)
    request = AgentOrchestrationRequest(plan=plan_payload)

    response = orchestrate_agents(request)

    assert plan_payload == original
    assert response.final_recommendation["plan_id"] == plan_payload["plan_id"]
    assert response.status == "ok"


def test_orchestrator_response_matches_contract(plan_payload):
    request = AgentOrchestrationRequest(plan=plan_payload)

    response = orchestrate_agents(request)
    validated = AgentOrchestrationResponse.model_validate(response.model_dump())

    assert validated.status == "ok"
    assert [step.agent for step in validated.steps] == [
        "plan_ingestor",
        "risk_profiler",
        "action_planner",
    ]
    assert validated.final_recommendation["priority"] == "escalate"
    assert (
        validated.final_recommendation["recommended_actions"][0]["type"] == "pagerduty"
    )
