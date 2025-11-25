from __future__ import annotations

import importlib
import json

import pytest

from scripts.lint import lint_feature_flags


class DummySession:
    def __init__(self, args=None):
        self.posargs = list(args or [])
        self.env = {}


def _reload_lint_module(monkeypatch):
    module = importlib.reload(importlib.import_module("nox_sessions.lint"))

    def fake_sequence(session, *, context):  # pylint: disable=unused-argument
        return None

    monkeypatch.setattr(module, "lint_all_sequence", fake_sequence)
    monkeypatch.setattr(module, "_run_lint_health_checks", lambda: None)
    return module


def test_feature_flags_validate_success():
    valid, failure_event = lint_feature_flags.validate_flags()
    assert valid is True
    assert failure_event is None


def test_feature_flags_missing_required(monkeypatch):
    original = lint_feature_flags.get_flags

    def fake_flags():
        flags = original()
        flags.pop("contracts", None)
        return flags

    monkeypatch.setattr(lint_feature_flags, "get_flags", fake_flags)
    valid, failure_event = lint_feature_flags.validate_flags()
    assert valid is False
    assert failure_event["target"] == "lint-feature-flags-invalid"
    assert "contracts" in failure_event["diagnostic"]


def test_feature_flags_unknown_required(monkeypatch):
    original = lint_feature_flags.get_flags

    def fake_flags():
        flags = original()
        flags["new_required"] = True
        return flags

    monkeypatch.setattr(lint_feature_flags, "get_flags", fake_flags)
    valid, failure_event = lint_feature_flags.validate_flags()
    assert valid is False
    assert "unknown-flags" in failure_event["diagnostic"]


def test_lint_all_prints_flags_in_verbose_mode(monkeypatch, capsys):
    lint_mod = _reload_lint_module(monkeypatch)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    session = DummySession(["--verbose"])
    lint_mod.lint_all(session)

    captured = capsys.readouterr().out.strip().splitlines()
    expected = json.dumps(lint_feature_flags.get_flags(), sort_keys=True)
    assert expected in captured


def test_lint_all_hides_flags_in_ci_quiet(monkeypatch, capsys):
    lint_mod = _reload_lint_module(monkeypatch)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    session = DummySession()
    lint_mod.lint_all(session)

    captured = capsys.readouterr().out.strip()
    assert captured == ""
