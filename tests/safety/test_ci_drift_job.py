import re
from pathlib import Path

import yaml


WORKFLOW_PATH = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


def test_drift_check_job_contract():
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))

    triggers = workflow.get("on") or workflow.get(True) or {}
    schedule = triggers.get("schedule", [])
    assert schedule, "schedule cron entry missing"
    assert any(
        "cron" in entry and re.match(r"^\d+ \d+ \* \* \*$", entry["cron"])
        for entry in schedule
    )

    jobs = workflow.get("jobs", {})
    assert "drift_check" in jobs, "drift_check job missing"
    job = jobs["drift_check"]

    env = job.get("env", {})
    assert env.get("NO_APPLY") == "1", "NO_APPLY safeguard must be enforced"

    steps = job.get("steps", [])
    assert steps, "drift_check job must define steps"

    def step_uses(action_id: str) -> bool:
        return any(step.get("uses", "").startswith(action_id) for step in steps)

    assert step_uses("actions/checkout@v4")
    assert step_uses("actions/setup-python@v5")
    assert step_uses("aws-actions/configure-aws-credentials@v4")
    assert step_uses("actions/upload-artifact@v4")

    poetry_installs = [
        step for step in steps if "Install Poetry" in step.get("name", "")
    ]
    assert poetry_installs, "Poetry install step missing"

    run_commands = "\n".join(step.get("run", "") for step in steps)
    assert "poetry run nox -s drift_check" in run_commands
    assert "run_drift_remediation" not in run_commands
    assert "drift_remediation" not in run_commands

    configure_step = next(
        step
        for step in steps
        if step.get("uses", "").startswith("aws-actions/configure-aws-credentials@v4")
    )
    with_fields = configure_step.get("with", {})
    assert "${{ secrets.AWS_READONLY_ROLE_ARN }}" in with_fields.get(
        "role-to-assume", ""
    )
    assert "${{ vars.AWS_DEFAULT_REGION" in with_fields.get("aws-region", "")
