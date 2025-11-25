import pytest

from scripts.drift_remediation import validate_env


@pytest.fixture
def ensure_baseline_dir(tmp_path, monkeypatch):
    baseline_dir = tmp_path / "drift_baselines"
    baseline_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    yield baseline_dir


def test_validate_env_success(ensure_baseline_dir, monkeypatch, capsys):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")
    monkeypatch.setenv("NO_APPLY", "1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "dummy")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "dummy")

    exit_code = validate_env.main([])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Environment looks safe" in captured.out


def test_validate_env_requires_region(ensure_baseline_dir, monkeypatch):
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    monkeypatch.setenv("NO_APPLY", "1")

    with pytest.raises(SystemExit) as exc:
        validate_env.main([])
    assert exc.value.code == 1


def test_validate_env_warns_without_no_apply(ensure_baseline_dir, monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.delenv("NO_APPLY", raising=False)

    with pytest.raises(SystemExit) as exc:
        validate_env.main([])
    assert exc.value.code == 1

    exit_code = validate_env.main(["--unsafe"])
    assert exit_code == 0


def test_validate_env_writable_baselines(tmp_path, monkeypatch):
    baseline_dir = tmp_path / "drift_baselines"
    # Create directory but remove write permissions
    baseline_dir.mkdir()
    baseline_dir.chmod(0o444)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("NO_APPLY", "1")

    with pytest.raises(SystemExit):
        validate_env.main([])

    baseline_dir.chmod(0o755)
    assert validate_env.main([]) == 0
