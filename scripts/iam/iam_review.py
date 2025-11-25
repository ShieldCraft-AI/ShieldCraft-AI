from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Iterable
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
ROLES_FIXTURE = FIXTURE_DIR / "iam_roles.json"
POLICIES_FIXTURE = FIXTURE_DIR / "iam_policies.json"
GENERATED_AT = "2025-01-01T00:00:00Z"


@dataclass(frozen=True)
class PolicyStatementSummary:
    policy_name: str
    effect: str
    actions: List[str]
    resources: List[str]
    services: List[str]


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Fixture not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_list(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(item) for item in value]
    return []


def _summarize_statement(
    policy_name: str, statement: Dict[str, Any]
) -> PolicyStatementSummary:
    actions = sorted(_ensure_list(statement.get("Action")), key=str.lower)
    resources = sorted(_ensure_list(statement.get("Resource")), key=str.lower)
    services = sorted({action.split(":", 1)[0] for action in actions if ":" in action})
    return PolicyStatementSummary(
        policy_name=policy_name,
        effect=str(statement.get("Effect", "Allow")),
        actions=actions,
        resources=resources,
        services=services,
    )


def _has_wildcard(values: Iterable[str]) -> bool:
    return any(
        value == "*" or value.endswith(":*") or value.endswith("*") for value in values
    )


def _score_role(
    statements: List[PolicyStatementSummary], privilege_threshold: int = 5
) -> Dict[str, Any]:
    wildcard_action = any(_has_wildcard(summary.actions) for summary in statements)
    wildcard_resource = any(_has_wildcard(summary.resources) for summary in statements)
    privilege_count = sum(len(summary.actions) for summary in statements)

    issues: List[str] = []
    if wildcard_action:
        issues.append("wildcard_action")
    if wildcard_resource:
        issues.append("wildcard_resource")
    if privilege_count > privilege_threshold:
        issues.append("broad_service_surface")

    if "wildcard_action" in issues and "wildcard_resource" in issues:
        risk_level = "critical"
    elif "wildcard_action" in issues or "wildcard_resource" in issues:
        risk_level = "high"
    elif "broad_service_surface" in issues:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "issues": issues,
        "risk_level": risk_level,
        "privilege_count": privilege_count,
    }


def _evaluate_role(
    role: Dict[str, Any], policy_documents: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    attached_policies = sorted(role.get("policies", []))
    statements: List[PolicyStatementSummary] = []
    for policy_name in attached_policies:
        document = policy_documents.get(policy_name, {})
        policy_statements = document.get("Statement", [])
        for statement in policy_statements:
            statements.append(_summarize_statement(policy_name, statement))

    scoring = _score_role(statements)
    policy_summaries = [
        {
            "policy_name": summary.policy_name,
            "effect": summary.effect,
            "actions": summary.actions,
            "resources": summary.resources,
            "services": summary.services,
        }
        for summary in statements
    ]

    return {
        "role_name": role.get("name"),
        "arn": role.get("arn"),
        "last_used": role.get("last_used"),
        "tags": role.get("tags", {}),
        "attached_policies": attached_policies,
        "policy_summaries": policy_summaries,
        **scoring,
    }


def _relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def evaluate_roles(
    roles_fixture: Path | None = None,
    policies_fixture: Path | None = None,
) -> Dict[str, Any]:
    roles_path = roles_fixture or ROLES_FIXTURE
    policies_path = policies_fixture or POLICIES_FIXTURE

    roles_data = _load_json(roles_path).get("roles", [])
    policies_data = _load_json(policies_path).get("policies", [])
    policy_lookup = {
        policy.get("name"): policy.get("document", {}) for policy in policies_data
    }

    evaluated_roles = [
        _evaluate_role(role, policy_lookup)
        for role in sorted(roles_data, key=lambda item: item.get("name", ""))
    ]

    return {
        "generated_at": GENERATED_AT,
        "total_roles": len(evaluated_roles),
        "high_risk_roles": [
            role["role_name"]
            for role in evaluated_roles
            if role["risk_level"] in {"critical", "high"}
        ],
        "roles": evaluated_roles,
        "sources": {
            "roles_fixture": _relative_path(roles_path),
            "policies_fixture": _relative_path(policies_path),
        },
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the deterministic IAM access review."
    )
    parser.add_argument("--roles", type=Path, default=ROLES_FIXTURE)
    parser.add_argument("--policies", type=Path, default=POLICIES_FIXTURE)
    args = parser.parse_args()

    review = evaluate_roles(args.roles, args.policies)
    print(json.dumps(review, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
