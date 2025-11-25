from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence

AgentOutput = Dict[str, Any]
AgentHandler = Callable[[Mapping[str, Any], Mapping[str, AgentOutput]], AgentOutput]


@dataclass(frozen=True)
class AgentDefinition:
    agent_id: str
    description: str
    depends_on: Sequence[str]
    handler: AgentHandler


class MultiAgentOrchestrator:
    """Executes deterministic agent pipelines backed by local handlers."""

    def __init__(self, agents: Sequence[AgentDefinition] | None = None):
        self._agents = list(agents or default_agent_definitions())
        self._validate_registry()

    def _validate_registry(self) -> None:
        seen: set[str] = set()
        for agent in self._agents:
            if agent.agent_id in seen:
                raise ValueError(f"Duplicate agent_id detected: {agent.agent_id}")
            seen.add(agent.agent_id)
            unknown_dependencies = set(agent.depends_on) - seen
            if unknown_dependencies:
                raise ValueError(
                    f"Agent {agent.agent_id} depends on unknown agents: {sorted(unknown_dependencies)}"
                )

    def run(self, plan: Mapping[str, Any]) -> Dict[str, Any]:
        results: Dict[str, AgentOutput] = {}
        trace: List[Dict[str, Any]] = []
        for agent in self._agents:
            context_input = {
                "plan": plan,
                "previous_results": {dep: results[dep] for dep in agent.depends_on},
            }
            output = agent.handler(plan, context_input["previous_results"])
            results[agent.agent_id] = output
            trace.append(
                {
                    "agent_id": agent.agent_id,
                    "depends_on": list(agent.depends_on),
                    "output": output,
                }
            )
        final_agent = self._agents[-1].agent_id if self._agents else None
        return {
            "plan_id": plan.get("plan_id", "unknown-plan"),
            "agents": trace,
            "final_recommendation": results.get(final_agent, {}),
        }


def _severity_score(severity: str) -> int:
    mapping = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    return mapping.get(severity.lower(), 1)


def _threat_intel_handler(
    plan: Mapping[str, Any], previous: Mapping[str, AgentOutput]
) -> AgentOutput:
    signals = plan.get("signals", [])
    signal_sources = sorted({signal.get("source", "unknown") for signal in signals})
    tags = sorted(plan.get("tags", []))
    critical_assets = sorted(plan.get("affected_assets", []))
    severity = plan.get("severity", "low")
    watchlist_hits = [
        signal["indicator"] for signal in signals if signal.get("confidence", 0) >= 0.9
    ]
    return {
        "summary": f"{severity.upper()} incident touching {len(critical_assets)} assets",
        "signal_sources": signal_sources,
        "critical_assets": critical_assets,
        "tags": tags,
        "watchlist_hits": watchlist_hits,
        "severity_score": _severity_score(severity),
    }


def _remediation_planner_handler(
    plan: Mapping[str, Any], previous: Mapping[str, AgentOutput]
) -> AgentOutput:
    intel = previous.get("threat_intel", {})
    assets = intel.get("critical_assets", [])
    steps: List[Dict[str, Any]] = []
    for asset in assets:
        steps.append(
            {
                "title": f"Quarantine {asset}",
                "owner": "SecOps",
                "difficulty": "medium",
            }
        )
    steps.append(
        {
            "title": "Rotate secrets for impacted services",
            "owner": "Platform",
            "difficulty": "high" if intel.get("severity_score", 1) >= 3 else "medium",
        }
    )
    return {
        "steps": steps,
        "playbook": "multi-agent-v1",
        "references": sorted(intel.get("tags", [])),
    }


def _risk_reviewer_handler(
    plan: Mapping[str, Any], previous: Mapping[str, AgentOutput]
) -> AgentOutput:
    planner = previous.get("remediation_planner", {})
    intel = previous.get("threat_intel", {})
    severity_score = intel.get("severity_score", 1)
    residual = "low"
    if severity_score >= 4:
        residual = "medium"
    elif severity_score >= 3:
        residual = "medium"
    readiness = "ready" if planner.get("steps") else "blocked"
    return {
        "readiness": readiness,
        "residual_risk": residual,
        "required_approvers": ["CISO", "Platform Lead"],
        "steps_reviewed": len(planner.get("steps", [])),
    }


def default_agent_definitions() -> Sequence[AgentDefinition]:
    return (
        AgentDefinition(
            agent_id="threat_intel",
            description="Aggregates deterministic intel across signals and assets.",
            depends_on=(),
            handler=_threat_intel_handler,
        ),
        AgentDefinition(
            agent_id="remediation_planner",
            description="Proposes remediation steps given the intel rollup.",
            depends_on=("threat_intel",),
            handler=_remediation_planner_handler,
        ),
        AgentDefinition(
            agent_id="risk_reviewer",
            description="Rates readiness and residual risk for approval gate.",
            depends_on=("threat_intel", "remediation_planner"),
            handler=_risk_reviewer_handler,
        ),
    )


__all__ = ["AgentDefinition", "MultiAgentOrchestrator", "default_agent_definitions"]
