import subprocess
import sys
from pathlib import Path

import pytest


class DummyCF:
    def __init__(self, *args, **kwargs):
        self.client = None

    def detect_drift(self, stack_name: str):
        return {"StackDriftDetectionId": f"drift-{stack_name}"}


class DummyConfigLoader:
    def export(self):
        return {"app": {"env": "test", "region": "us-east-1"}}


def test_run_check_creates_artifact(tmp_path, monkeypatch):
    # Arrange: mock CloudFormationService and subprocess.run
    repo_root = Path.cwd()
    artifacts_dir = tmp_path / "artifacts"

    # Patch the CloudFormationService used by the script
    import importlib

    mod = importlib.import_module("scripts.drift_remediation.run_drift_check")
    monkeypatch.setattr(mod, "CloudFormationService", DummyCF)
    monkeypatch.setattr(mod, "get_config_loader", lambda: DummyConfigLoader())

    class Proc:
        def __init__(self):
            self.stdout = "--- CDK DIFF ---\nResource A will be replaced\n"

    def fake_run(*args, **kwargs):
        return Proc()

    monkeypatch.setattr(subprocess, "run", fake_run)

    # Act
    rc = mod.run_check(
        ["TestStack"],
        repo_root,
        artifacts_dir,
        dry_run=True,
        post=False,
        config_loader=DummyConfigLoader(),
    )

    # Assert
    assert rc == 0
    files = list(artifacts_dir.glob("*TestStack*.diff"))
    assert len(files) == 1
    content = files[0].read_text()
    assert "CDK DIFF" in content or "Resource A" in content
