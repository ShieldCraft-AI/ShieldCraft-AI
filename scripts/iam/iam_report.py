from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Any

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from iam_review import evaluate_roles, ROLES_FIXTURE, POLICIES_FIXTURE  # type: ignore  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "iam"
JSON_FILENAME = "iam_access_review.json"
MARKDOWN_FILENAME = "iam_access_review.md"


def _render_markdown(review: Dict[str, Any]) -> str:
    lines = [
        "# ShieldCraft IAM Access Review",
        "",
        f"- Generated at: {review['generated_at']}",
        f"- Total roles: {review['total_roles']}",
        f"- High-risk roles: {', '.join(review['high_risk_roles']) or 'none'}",
        "",
        "| Role | Risk | Issues | Attached Policies | Last Used |",
        "| --- | --- | --- | --- | --- |",
    ]

    for role in review["roles"]:
        issues = ", ".join(role["issues"]) if role["issues"] else "none"
        policies = ", ".join(role["attached_policies"])
        lines.append(
            "| {role_name} | {risk} | {issues} | {policies} | {last_used} |".format(
                role_name=role["role_name"],
                risk=role["risk_level"],
                issues=issues,
                policies=policies,
                last_used=role.get("last_used", "n/a"),
            )
        )

    lines.append("")
    lines.append(
        "Sources: roles from {roles}, policies from {policies}.".format(
            roles=review["sources"]["roles_fixture"],
            policies=review["sources"]["policies_fixture"],
        )
    )

    return "\n".join(lines) + "\n"


def generate_reports(
    output_dir: Path | str | None = None,
    roles_fixture: Path | None = None,
    policies_fixture: Path | None = None,
) -> Dict[str, Path]:
    review = evaluate_roles(roles_fixture, policies_fixture)
    destination = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    destination.mkdir(parents=True, exist_ok=True)

    json_path = destination / JSON_FILENAME
    md_path = destination / MARKDOWN_FILENAME

    json_path.write_text(json.dumps(review, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_render_markdown(review), encoding="utf-8")

    return {"json": json_path, "markdown": md_path}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate IAM access review reports.")
    parser.add_argument("--destination", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--roles", type=Path, default=ROLES_FIXTURE)
    parser.add_argument("--policies", type=Path, default=POLICIES_FIXTURE)
    args = parser.parse_args()

    paths = generate_reports(args.destination, args.roles, args.policies)
    print(json.dumps({key: str(value) for key, value in paths.items()}, indent=2))


if __name__ == "__main__":
    main()
