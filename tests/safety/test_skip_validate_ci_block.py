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


def test_skip_validate_forbidden_in_ci(monkeypatch):
    session = DummySession(["--skip-validate", "TestStack"])
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    with pytest.raises(RuntimeError) as exc:
        drift_sessions.drift_check(session)

    assert "skip-validate forbidden in CI" in str(exc.value)
    assert session.run_calls == []
