from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


def _load_workflow():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_push_workflow_runs_lint_all_before_tests():
    workflow = _load_workflow()
    jobs = workflow.get("jobs", {})
    flow_commit = jobs.get("flow_commit")
    assert flow_commit, "flow_commit job missing"

    steps = flow_commit.get("steps", [])
    run_cmds = [step.get("run", "") for step in steps]

    lint_all_index = next(
        (idx for idx, cmd in enumerate(run_cmds) if "nox -s lint_all" in cmd),
        None,
    )
    assert lint_all_index is not None, "lint_all step missing from push/pull workflow"

    test_index = next(
        (idx for idx, cmd in enumerate(run_cmds) if "nox -s commit_flow" in cmd),
        None,
    )
    assert test_index is not None, "commit_flow (tests) step missing"
    assert lint_all_index < test_index, "lint_all must run before commit_flow/tests"


def test_drift_job_does_not_run_lint_all():
    workflow = _load_workflow()
    drift_job = workflow.get("jobs", {}).get("drift_check")
    assert drift_job, "drift_check job missing"

    drift_runs = "\n".join(step.get("run", "") for step in drift_job.get("steps", []))
    assert "lint_all" not in drift_runs, "Scheduled drift jobs must not run lint_all"
