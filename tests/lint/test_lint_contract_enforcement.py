from __future__ import annotations

import importlib

import pytest

from scripts.lint.lint_contract import validate_lint_payload


VALID_PAYLOAD = {
    "target": "lint_forbidden",
    "status": "ok",
    "stdout": "",
    "stderr": "",
    "timestamp": "2025-11-21T00:00:00Z",
}


def _lint_module():
    return importlib.import_module("nox_sessions.lint")


def test_validate_lint_payload_accepts_valid():
    assert validate_lint_payload(dict(VALID_PAYLOAD)) is True


def test_validate_lint_payload_rejects_missing_fields():
    payload = dict(VALID_PAYLOAD)
    payload.pop("stderr")
    assert validate_lint_payload(payload) is False


def test_lint_all_aborts_on_invalid_payload(monkeypatch):
    lint_module = _lint_module()

    class DummySession:
        def __init__(self):
            self.calls = []

        def run(self, *args, **kwargs):
            self.calls.append({"args": args, "silent": kwargs.get("silent")})

    session = DummySession()

    def bad_build(*args, **kwargs):  # noqa: ARG001
        payload = dict(VALID_PAYLOAD)
        payload.pop("timestamp")
        return payload

    monkeypatch.setattr(lint_module, "build_event", bad_build)

    with pytest.raises(ValueError):
        lint_module._run_lint_target(session, "lint_forbidden", verbose=True)


def test_quiet_mode_stays_quiet_until_contract_breach(monkeypatch):
    lint_module = _lint_module()

    class DummySession:
        def __init__(self):
            self.calls = []

        def run(self, *args, **kwargs):
            self.calls.append({"args": args, "silent": kwargs.get("silent")})
            if len(self.calls) == 1:
                raise lint_module.CommandFailed("boom")

    session = DummySession()
    emitted = []

    def fake_emit(event, *, allow_quiet):
        emitted.append((event, allow_quiet))

    monkeypatch.setattr(lint_module, "safe_emit", fake_emit)

    with pytest.raises(lint_module.CommandFailed):
        lint_module._run_lint_target(session, "lint_forbidden", verbose=False)

    assert [call["silent"] for call in session.calls] == [True, False]
    assert [entry[0]["status"] for entry in emitted] == ["fail", "fail", "ok"]
    assert emitted[0][1] is True
