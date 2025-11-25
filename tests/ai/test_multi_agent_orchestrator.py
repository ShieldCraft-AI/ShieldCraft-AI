from __future__ import annotations

import json
from pathlib import Path

from ai_core.multi_agent import MultiAgentOrchestrator

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "ai" / "sample_plan.json"
)


def load_plan() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_orchestrator_runs_all_agents_in_order():
    orchestrator = MultiAgentOrchestrator()
    plan = load_plan()

    result = orchestrator.run(plan)

    agent_ids = [agent["agent_id"] for agent in result["agents"]]
    assert agent_ids == ["threat_intel", "remediation_planner", "risk_reviewer"]
    assert result["plan_id"] == "PLAN-SEC-001"

    threat_summary = result["agents"][0]["output"]
    assert threat_summary["signal_sources"] == ["guardduty", "securityhub"]
    assert threat_summary["watchlist_hits"] == ["UnauthorizedAccess:EC2/SSHBruteForce"]


def test_orchestrator_final_recommendation_is_deterministic():
    orchestrator = MultiAgentOrchestrator()
    plan = load_plan()

    first_run = orchestrator.run(plan)
    second_run = orchestrator.run(plan)

    assert first_run["final_recommendation"] == second_run["final_recommendation"]
    assert first_run["final_recommendation"]["residual_risk"] == "medium"
    assert first_run["final_recommendation"]["required_approvers"] == [
        "CISO",
        "Platform Lead",
    ]
