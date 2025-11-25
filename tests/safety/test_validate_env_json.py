import json

import pytest

from scripts.drift_remediation import validate_env


@pytest.fixture
def ensure_baseline_dir(tmp_path, monkeypatch):
    baseline_dir = tmp_path / "drift_baselines"
    baseline_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    yield baseline_dir


def test_validate_env_json_success(ensure_baseline_dir, monkeypatch, capsys):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")
    monkeypatch.setenv("NO_APPLY", "1")

    exit_code = validate_env.main(["--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out.strip())
    assert payload == {"status": "ok"}


def test_validate_env_json_failure(ensure_baseline_dir, monkeypatch, capsys):
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    monkeypatch.setenv("NO_APPLY", "1")

    with pytest.raises(SystemExit) as exc:
        validate_env.main(["--json"])
    assert exc.value.code == 1

    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["status"] == "error"
    assert "AWS_DEFAULT_REGION" in payload["reason"]
