from __future__ import annotations

import importlib
import json

import pytest

from scripts.lint import lint_capabilities


class DummySession:
    def __init__(self, args=None):
        self.posargs = list(args or [])
        self.env = {}


def test_validate_capabilities_success():
    valid, failure_event = lint_capabilities.validate_capabilities()
    assert valid is True
    assert failure_event is None


def test_validate_capabilities_missing_field(monkeypatch):
    original = lint_capabilities.get_capabilities

    def fake_caps():
        manifest = original()
        manifest.pop("supports_health_checks", None)
        return manifest

    monkeypatch.setattr(lint_capabilities, "get_capabilities", fake_caps)
    valid, failure_event = lint_capabilities.validate_capabilities()
    assert valid is False
    assert failure_event["target"] == "lint-capabilities-invalid"
    assert "supports_health_checks" in failure_event["diagnostic"]


def test_validate_capabilities_invalid_type(monkeypatch):
    original = lint_capabilities.get_capabilities

    def fake_caps():
        manifest = original()
        manifest["supports_formatter"] = "yes"
        return manifest

    monkeypatch.setattr(lint_capabilities, "get_capabilities", fake_caps)
    valid, failure_event = lint_capabilities.validate_capabilities()
    assert valid is False
    assert "supports_formatter" in failure_event["diagnostic"]


def test_lint_all_prints_capabilities_in_verbose_mode(monkeypatch, capsys):
    lint_mod = importlib.reload(importlib.import_module("nox_sessions.lint"))

    def fake_sequence(session, *, context):  # pylint: disable=unused-argument
        return None

    monkeypatch.setattr(lint_mod, "lint_all_sequence", fake_sequence)
    monkeypatch.setattr(lint_mod, "_run_lint_health_checks", lambda: None)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    session = DummySession(["--verbose"])
    lint_mod.lint_all(session)

    captured = capsys.readouterr().out.strip().splitlines()
    expected = json.dumps(lint_capabilities.get_capabilities(), sort_keys=True)
    assert expected in captured


def test_lint_all_hides_capabilities_in_ci(monkeypatch, capsys):
    lint_mod = importlib.reload(importlib.import_module("nox_sessions.lint"))

    def fake_sequence(session, *, context):  # pylint: disable=unused-argument
        return None

    monkeypatch.setattr(lint_mod, "lint_all_sequence", fake_sequence)
    monkeypatch.setattr(lint_mod, "_run_lint_health_checks", lambda: None)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    session = DummySession()
    lint_mod.lint_all(session)

    captured = capsys.readouterr().out.strip()
    assert captured == ""
