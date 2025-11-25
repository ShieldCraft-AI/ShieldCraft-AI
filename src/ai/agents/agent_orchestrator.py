from __future__ import annotations

from typing import Dict, List

from src.ai.agents.agent_contracts import (
    AgentOrchestrationRequest,
    AgentOrchestrationResponse,
    AgentPlan,
    AgentStepTrace,
    PlanSignal,
)


_SEVERITY_WEIGHTS: Dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def orchestrate_agents(
    request: AgentOrchestrationRequest,
) -> AgentOrchestrationResponse:
    """Run the deterministic v1 agent runtime."""

    plan = request.plan

    ingestion_step = _run_plan_ingestor(plan)
    risk_step = _run_risk_profiler(plan, ingestion_step.outputs)
    planner_step = _run_action_planner(plan, risk_step.outputs)

    final_recommendation = {
        "plan_id": plan.plan_id,
        "env": plan.env,
        "priority": planner_step.outputs["priority"],
        "recommended_actions": planner_step.outputs["actions"],
    }

    return AgentOrchestrationResponse(
        status="ok",
        steps=[ingestion_step, risk_step, planner_step],
        final_recommendation=final_recommendation,
    )


def _run_plan_ingestor(plan: AgentPlan) -> AgentStepTrace:
    asset_count = len(plan.affected_assets)
    signal_sources = sorted({signal.source for signal in plan.signals})
    inputs = {
        "plan_id": plan.plan_id,
        "env": plan.env,
    }
    outputs = {
        "asset_count": asset_count,
        "signal_count": len(plan.signals),
        "signal_sources": signal_sources,
        "severity": plan.severity.lower(),
    }
    return AgentStepTrace(agent="plan_ingestor", inputs=inputs, outputs=outputs)


def _run_risk_profiler(
    plan: AgentPlan, ingestor_outputs: Dict[str, object]
) -> AgentStepTrace:
    base_weight = _severity_weight(plan.severity)
    signal_bonus = _signal_weight(plan.signals)
    asset_bonus = len(plan.affected_assets)
    tag_bonus = len(plan.tags) // 2
    risk_score = base_weight * 10 + signal_bonus + asset_bonus + tag_bonus
    inputs = {
        "severity": ingestor_outputs["severity"],
        "asset_count": ingestor_outputs["asset_count"],
        "signal_count": ingestor_outputs["signal_count"],
    }
    outputs = {
        "risk_score": risk_score,
        "severity_weight": base_weight,
        "confidence": _confidence_rating(risk_score),
    }
    return AgentStepTrace(agent="risk_profiler", inputs=inputs, outputs=outputs)


def _run_action_planner(
    plan: AgentPlan, risk_outputs: Dict[str, object]
) -> AgentStepTrace:
    priority = _priority_label(risk_outputs["risk_score"])
    actions = _build_actions(plan, priority)
    inputs = {
        "risk_score": risk_outputs["risk_score"],
        "severity_weight": risk_outputs["severity_weight"],
    }
    outputs = {
        "priority": priority,
        "actions": actions,
    }
    return AgentStepTrace(agent="action_planner", inputs=inputs, outputs=outputs)


def _severity_weight(severity: str) -> int:
    return _SEVERITY_WEIGHTS.get(severity.lower(), 1)


def _signal_weight(signals: List[PlanSignal]) -> int:
    unique_types = sorted({signal.indicator for signal in signals})
    return len(unique_types) * 2


def _confidence_rating(score: int) -> str:
    if score >= 20:
        return "high"
    if score >= 12:
        return "medium"
    return "low"


def _priority_label(score: int) -> str:
    if score >= 22:
        return "escalate"
    if score >= 14:
        return "monitor"
    return "observe"


def _build_actions(plan: AgentPlan, priority: str) -> List[Dict[str, str]]:
    actions: List[Dict[str, str]] = []
    if priority == "escalate":
        actions.append(
            {
                "type": "pagerduty",
                "target": "incident-response",
            }
        )
    if plan.affected_assets:
        actions.append(
            {
                "type": "notify-owner",
                "target": plan.affected_assets[0],
            }
        )
    actions.append(
        {
            "type": "generate-report",
            "target": plan.plan_id,
        }
    )
    return actions


__all__ = ["orchestrate_agents"]
