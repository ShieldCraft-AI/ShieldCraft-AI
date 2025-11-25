import json
from pathlib import Path

from nox_sessions import drift as drift_sessions
from scripts.drift_remediation import baseline_utils


def _disable_validate_env(monkeypatch):
    def _noop(session, extra_args=None):
        return None

    monkeypatch.setattr(drift_sessions, "_run_validate_env", _noop)


class DummySession:
    def __init__(self, posargs=None):
        self.posargs = posargs or []
        self.env = {}
        self.run_calls = []
        self.logged = []

    def run(self, *args, **kwargs):
        self.run_calls.append((args, kwargs))

    def log(self, message):
        self.logged.append(message)


def test_drift_check_session_invokes_script(monkeypatch, tmp_path):
    custom_artifacts = tmp_path / "artifacts"
    session = DummySession(
        ["TestStack", "--post", "--artifacts-dir", str(custom_artifacts)]
    )

    _disable_validate_env(monkeypatch)

    drift_sessions.drift_check(session)

    assert session.run_calls, "session.run should be invoked"
    args, kwargs = session.run_calls[0]
    assert list(args) == [
        "poetry",
        "run",
        "python",
        "scripts/drift_remediation/run_drift_check.py",
        "--artifacts-dir",
        str(custom_artifacts),
        "--dry-run",
        "--stacks",
        "TestStack",
        "--post",
    ]
    assert kwargs["env"]["NO_APPLY"] == "1"


def test_drift_acknowledge_updates_baseline(monkeypatch, tmp_path):
    drift_root = tmp_path / "artifacts" / "drift"
    drift_sessions.DRIFT_ARTIFACTS_DIR = drift_root
    stack_dir = drift_root / "TestStack"
    stack_dir.mkdir(parents=True, exist_ok=True)
    diff_path = stack_dir / "latest.diff"
    diff_content = "resource change"
    diff_path.write_text(diff_content, encoding="utf-8")

    baseline_root = tmp_path / "baselines"
    monkeypatch.setattr(baseline_utils, "BASELINE_ROOT", baseline_root)
    baseline_utils.ensure_baseline_dir()

    session = DummySession(["TestStack"])
    _disable_validate_env(monkeypatch)
    drift_sessions.drift_acknowledge(session)

    baseline_file = baseline_root / "TestStack.json"
    payload = json.loads(baseline_file.read_text())
    assert payload["last_known_hash"] == baseline_utils.hash_diff_text(diff_content)
    assert payload["stack"] == "TestStack"


def test_drift_report_generates_summary(tmp_path, monkeypatch):
    artifacts_dir = tmp_path / "artifacts" / "drift"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    stack_dir = artifacts_dir / "TestStack"
    stack_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "stack": "TestStack",
        "comparison_status": "new_drift",
        "drifted": True,
        "timestamp": "2024-01-01T00:00:00Z",
    }
    (stack_dir / "artifact.json").write_text(json.dumps(payload), encoding="utf-8")

    drift_sessions.DRIFT_ARTIFACTS_DIR = artifacts_dir
    summary_dir = tmp_path / "artifacts" / "drift_summary"
    drift_sessions.SUMMARY_DIR = summary_dir

    session = DummySession()
    _disable_validate_env(monkeypatch)
    drift_sessions.drift_report(session)

    summary_path = summary_dir / "latest.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text())
    assert summary["new_drift"] == ["TestStack"]
