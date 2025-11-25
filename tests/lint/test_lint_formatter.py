from __future__ import annotations

import importlib
import json

import pytest

from scripts.lint.lint_contract import LINT_VERSION
from scripts.lint.lint_formatter import format_event

BASE_EVENT = {
    "target": "lint_forbidden",
    "status": "ok",
    "stdout": "",
    "stderr": "",
    "timestamp": "2025-11-21T00:00:00Z",
    "lint_version": LINT_VERSION,
}


def _lint_module():
    return importlib.import_module("nox_sessions.lint")


def test_format_event_serializes_single_line():
    payload = dict(BASE_EVENT)
    line = format_event(payload)
    assert "\n" not in line
    data = json.loads(line)
    assert data["lint_version"] == LINT_VERSION
    assert data["status"] == "ok"


def test_format_event_missing_field_raises():
    payload = dict(BASE_EVENT)
    payload.pop("timestamp")
    with pytest.raises(ValueError):
        format_event(payload)


def test_quiet_mode_suppresses_pass_events(monkeypatch):
    lint_module = _lint_module()

    class DummySession:
        def __init__(self):
            self.calls = []

        def run(self, *args, **kwargs):
            self.calls.append({"args": args, "silent": kwargs.get("silent")})

    session = DummySession()
    emitted = []

    def fake_emit(event, *, allow_quiet):
        emitted.append((event, allow_quiet))

    monkeypatch.setattr(lint_module, "safe_emit", fake_emit)

    lint_module._run_lint_target(session, "lint_forbidden", verbose=False)

    assert [call["silent"] for call in session.calls] == [True]
    assert emitted[0][0]["status"] == "ok"
    assert emitted[0][1] is True


def test_verbose_mode_prints_all_events(monkeypatch):
    lint_module = _lint_module()

    class DummySession:
        def __init__(self):
            self.calls = []

        def run(self, *args, **kwargs):
            self.calls.append({"args": args, "silent": kwargs.get("silent")})

    session = DummySession()
    emitted = []

    def fake_emit(event, *, allow_quiet):
        emitted.append((event, allow_quiet))

    monkeypatch.setattr(lint_module, "safe_emit", fake_emit)

    lint_module._run_lint_target(session, "lint_forbidden", verbose=True)

    assert [call["silent"] for call in session.calls] == [False]
    assert len(emitted) == 1
    assert emitted[0][0]["status"] == "ok"
    assert emitted[0][1] is False


def test_retry_logging_prints_prefix(monkeypatch):
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
    assert [entry[0]["diagnostic"] for entry in emitted] == [
        "quiet-mode-failure",
        "retrying-verbose",
        "retry-verbose",
    ]
