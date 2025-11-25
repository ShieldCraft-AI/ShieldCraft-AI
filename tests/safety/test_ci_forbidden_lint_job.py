from pathlib import Path

import yaml


WORKFLOW_PATH = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


def test_ci_push_job_enforces_forbidden_lint():
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))

    triggers = workflow.get("on") or {}
    assert "push" in triggers, "push trigger missing in CI workflow"
    assert "pull_request" in triggers, "pull_request trigger missing in CI workflow"

    jobs = workflow.get("jobs", {})
    flow_commit = jobs.get("flow_commit")
    assert flow_commit, "flow_commit job missing"

    steps = flow_commit.get("steps", [])
    assert steps, "flow_commit job must define steps"

    run_commands = [step.get("run", "") for step in steps]
    lint_indices = [
        idx for idx, cmd in enumerate(run_commands) if "lint_forbidden" in cmd
    ]
    assert lint_indices, "Forbidden flag lint step missing from push/pull_request path"
    lint_index = lint_indices[0]

    test_indices = [
        idx
        for idx, cmd in enumerate(run_commands)
        if "pytest" in cmd or "poetry run nox -s commit_flow" in cmd
    ]
    assert test_indices, "Unable to locate downstream nox/pytest step"
    assert lint_index < min(test_indices), "Forbidden lint must precede pytest/tests"

    drift_job = jobs.get("drift_check")
    assert drift_job, "drift_check job missing"
    drift_run = "\n".join(step.get("run", "") for step in drift_job.get("steps", []))
    assert (
        "lint_forbidden" not in drift_run
    ), "Scheduled drift job must not run forbidden lint"
