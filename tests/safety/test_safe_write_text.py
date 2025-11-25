import importlib
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


def test_safe_write_warning_and_exit_code(caplog, tmp_path, monkeypatch):
    caplog.set_level(logging.WARNING, logger="drift_remediation")
    mod = _setup_module(monkeypatch, tmp_path)
    artifacts_dir = tmp_path / "artifacts" / "drift"
    monkeypatch.setenv("SHIELDCRAFT_EMIT_TELEMETRY", "1")

    original_write_text = Path.write_text

    def failing_write(self, *args, **kwargs):
        if "drift_telemetry" in str(self):
            raise OSError("disk full")
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", failing_write)

    rc = mod.run_check(
        ["TestStack"],
        Path.cwd(),
        artifacts_dir,
        dry_run=True,
        post=False,
        config_loader=DummyConfigLoader({"TestStack": {}}),
    )

    assert rc == 0
    warnings = [
        record.message
        for record in caplog.records
        if "Unable to write telemetry artifact" in record.message
        and "drift_telemetry" in record.message
    ]
    assert warnings, "Expected warning from _safe_write_text when write_text fails"
