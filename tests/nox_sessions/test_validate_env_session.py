import pytest

from nox_sessions import drift as drift_sessions


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


def test_drift_check_blocks_when_validate_env_fails(monkeypatch):
    session = DummySession(["ExampleStack"])
    call_count = {"value": 0}

    def fake_validate_env(_session, extra_args=None):
        call_count["value"] += 1
        raise SystemExit(2)

    monkeypatch.setattr(drift_sessions, "_run_validate_env", fake_validate_env)

    with pytest.raises(SystemExit) as exc:
        drift_sessions.drift_check(session)

    assert exc.value.code == 2
    assert session.run_calls == []
    assert call_count["value"] == 1


def test_validate_env_session_runs_once(monkeypatch):
    session = DummySession(["--baseline-dir", "tests/fixtures/baselines"])
    observed = []

    def fake_validate_env(_session, extra_args=None):
        observed.append((tuple(_session.posargs), extra_args))

    monkeypatch.setattr(drift_sessions, "_run_validate_env", fake_validate_env)

    drift_sessions.validate_env_session(session)

    assert observed == [
        (
            ("--baseline-dir", "tests/fixtures/baselines"),
            [
                "--baseline-dir",
                "tests/fixtures/baselines",
            ],
        )
    ]
