import pytest
import types
from pathlib import Path
import scripts.drift_remediation.run_drift_remediation as remediation


def test_remediate_drift_dry_run(monkeypatch, tmp_path):
    # Mock CloudFormationService
    class DummyCF:
        def __init__(self, *a, **kw):
            pass

        def detect_drift(self, stack):
            return {
                "StackDriftDetectionStatus": "DETECTION_COMPLETE",
                "StackDriftStatus": "DRIFTED",
            }

        def update_stack(self, stack, template_url, parameters, capabilities):
            return {"Update": "Success", "stack": stack}

    # Patch imports
    monkeypatch.setattr(remediation, "CloudFormationService", DummyCF)
    monkeypatch.setattr(
        remediation,
        "get_config_loader",
        lambda: types.SimpleNamespace(
            export=lambda: {"stacks": {"TestStack": {"template_url": "url"}}}
        ),
    )
    # Run dry-run
    result = remediation.remediate_drift(
        ["TestStack"], Path("."), tmp_path, apply=False
    )
    assert result == 0
    artifact = list(tmp_path.glob("*.json"))[0]
    data = artifact.read_text()
    assert "Drift detected, dry-run only" in data


def test_remediate_drift_apply(monkeypatch, tmp_path):
    class DummyCF:
        def __init__(self, *a, **kw):
            pass

        def detect_drift(self, stack):
            return {
                "StackDriftDetectionStatus": "DETECTION_COMPLETE",
                "StackDriftStatus": "DRIFTED",
            }

        def update_stack(self, stack, template_url, parameters, capabilities):
            return {"Update": "Success", "stack": stack}

    monkeypatch.setattr(remediation, "CloudFormationService", DummyCF)
    monkeypatch.setattr(
        remediation,
        "get_config_loader",
        lambda: types.SimpleNamespace(
            export=lambda: {"stacks": {"TestStack": {"template_url": "url"}}}
        ),
    )
    result = remediation.remediate_drift(["TestStack"], Path("."), tmp_path, apply=True)
    assert result == 0
    artifact = list(tmp_path.glob("*.json"))[0]
    data = artifact.read_text()
    assert "remediated" in data
    assert "Success" in data
