import importlib
import json
import logging
from pathlib import Path

import subprocess

DIFF_TEXT = "--- CDK DIFF ---\nResource change\n"


class DummyCF:
    def __init__(self, *_, **__):
        self.calls = []

    def detect_drift(self, stack_name: str):
        self.calls.append(stack_name)
        return {
            "StackDriftDetectionId": f"drift-{stack_name}",
            "StackDriftDetectionStatus": "DETECTION_COMPLETE",
            "StackDriftStatus": "IN_SYNC",
            "StackResourceDrifts": [],
        }


class DummyConfigLoader:
    def __init__(self, stacks: dict | None = None):
        self._payload = {"app": {"env": "dev", "region": "us-east-1"}}
        if stacks:
            self._payload["stacks"] = stacks

    def export(self):
        return self._payload


def _setup_module(monkeypatch, tmp_path):
    mod = importlib.import_module("scripts.drift_remediation.run_drift_check")
    monkeypatch.setattr(mod, "CloudFormationService", DummyCF)
    monkeypatch.setattr(
        mod, "get_config_loader", lambda: DummyConfigLoader({"TestStack": {}})
    )

    class Proc:
        def __init__(self):
            self.stdout = DIFF_TEXT

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Proc())

    from scripts.drift_remediation import baseline_utils

    baseline_utils.BASELINE_ROOT = tmp_path / "baselines"
    baseline_utils.ensure_baseline_dir()
    baseline_utils.write_baseline(
        "TestStack",
        baseline_utils.BaselineData(
            stack="TestStack",
            last_known_hash=baseline_utils.hash_diff_text(DIFF_TEXT),
            last_acknowledged_timestamp="2024-01-01T00:00:00Z",
            comment="fixture",
        ),
    )
    return mod


def test_telemetry_artifacts_written_when_enabled(caplog, tmp_path, monkeypatch):
    caplog.set_level(logging.INFO, logger="drift_remediation")
    mod = _setup_module(monkeypatch, tmp_path)
    artifacts_dir = tmp_path / "artifacts" / "drift"
    monkeypatch.setenv("SHIELDCRAFT_EMIT_TELEMETRY", "1")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    rc = mod.run_check(
        ["TestStack"],
        Path.cwd(),
        artifacts_dir,
        dry_run=True,
        post=False,
        config_loader=DummyConfigLoader({"TestStack": {}}),
    )

    assert rc == 0
    telemetry_logs = [
        record.message
        for record in caplog.records
        if record.message.startswith("[telemetry] ")
    ]
    assert telemetry_logs, "Expected telemetry log lines with [telemetry] prefix"
    telemetry_dir = tmp_path / "artifacts" / "drift_telemetry"
    files = list(telemetry_dir.glob("*.json"))
    assert files, "Telemetry file not written"
    payload = json.loads(files[0].read_text())
    assert payload["stacks_scanned"] == 1
    assert payload["ci_forced"] is True


def test_telemetry_artifacts_skipped_when_disabled(caplog, tmp_path, monkeypatch):
    caplog.set_level(logging.INFO, logger="drift_remediation")
    mod = _setup_module(monkeypatch, tmp_path)
    artifacts_dir = tmp_path / "artifacts" / "drift"
    monkeypatch.delenv("SHIELDCRAFT_EMIT_TELEMETRY", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    rc = mod.run_check(
        ["TestStack"],
        Path.cwd(),
        artifacts_dir,
        dry_run=True,
        post=False,
        config_loader=DummyConfigLoader({"TestStack": {}}),
    )

    assert rc == 0
    telemetry_logs = [
        record.message
        for record in caplog.records
        if record.message.startswith("[telemetry] ")
    ]
    assert telemetry_logs, "Telemetry log lines should always be emitted"
    telemetry_dir = tmp_path / "artifacts" / "drift_telemetry"
    assert not telemetry_dir.exists()
