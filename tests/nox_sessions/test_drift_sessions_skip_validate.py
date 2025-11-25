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


def test_skip_validate_warns_and_runs(monkeypatch):
    session = DummySession(["--skip-validate", "TestStack"])

    def fail_if_called(_session, extra_args=None):
        raise AssertionError("validate_env should be skipped")

    monkeypatch.setattr(drift_sessions, "_run_validate_env", fail_if_called)

    drift_sessions.drift_check(session)

    assert session.run_calls, "drift_check should still execute drift pipeline"
    assert any("[WARN]" in msg and "skip-validate" in msg for msg in session.logged)


def test_json_flag_forwarded_to_validate_env(monkeypatch):
    session = DummySession(["--json", "TestStack"])
    seen = {"args": None}

    def capture_args(_session, extra_args=None):
        seen["args"] = list(extra_args or [])

    monkeypatch.setattr(drift_sessions, "_run_validate_env", capture_args)

    drift_sessions.drift_check(session)

    assert seen["args"] == ["--json"]
    args, _ = session.run_calls[0]
    assert "--json" not in args
