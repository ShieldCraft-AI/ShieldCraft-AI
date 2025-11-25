from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from scripts.lint import lint_snapshots
from scripts.lint.lint_events import build_event


@pytest.fixture
def lint_module():
    return importlib.import_module("scripts.lint.lint_health")


@pytest.fixture
def snapshot_dir(tmp_path, monkeypatch):
    root = tmp_path / "lint_snapshots"
    root.mkdir()

    def _dir():
        return root

    monkeypatch.setattr(lint_snapshots, "snapshot_dir", _dir)
    return root


def _write_snapshot(target: str, payload: dict, directory: Path) -> None:
    path = directory / f"{target}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")


def _valid_snapshot(target: str) -> dict:
    event = build_event(target, "ok")
    event["timestamp"] = "SNAPSHOT"
    return event


def test_health_checks_pass_with_valid_state(lint_module, snapshot_dir):
    payload = _valid_snapshot("lint")
    _write_snapshot("lint", payload, snapshot_dir)

    lint_module.check_formatter_contract()
    lint_module.check_builder_contract()
    lint_module.check_snapshot_consistency()


def test_snapshot_consistency_fails_on_corrupt_json(lint_module, snapshot_dir):
    bad = snapshot_dir / "lint.json"
    bad.write_text("{broken", encoding="utf-8")

    with pytest.raises(RuntimeError):
        lint_module.check_snapshot_consistency()


def test_snapshot_consistency_fails_on_missing_fields(lint_module, snapshot_dir):
    payload = _valid_snapshot("lint")
    payload.pop("stdout")
    _write_snapshot("lint", payload, snapshot_dir)

    with pytest.raises(RuntimeError):
        lint_module.check_snapshot_consistency()


def test_snapshot_consistency_fails_on_unknown_fields(lint_module, snapshot_dir):
    payload = _valid_snapshot("lint")
    payload["unexpected"] = "value"
    _write_snapshot("lint", payload, snapshot_dir)

    with pytest.raises(RuntimeError):
        lint_module.check_snapshot_consistency()


def test_lint_all_skips_health_without_env(monkeypatch):
    lint_mod = importlib.import_module("nox_sessions.lint")

    class DummySession:
        posargs = []
        env = {}

    session = DummySession()
    called = {
        "sequence": False,
        "health": False,
    }

    def fake_sequence(sess, *, context):  # pylint: disable=unused-argument
        called["sequence"] = True

    def fake_check():
        called["health"] = True

    monkeypatch.setattr(lint_mod, "lint_all_sequence", fake_sequence)
    monkeypatch.setattr(lint_mod, "_run_lint_health_checks", fake_check)
    monkeypatch.delenv("SHIELDCRAFT_LINT_HEALTH", raising=False)

    lint_mod.lint_all(session)

    assert called["sequence"] is True
    assert called["health"] is False


def test_lint_all_runs_health_when_env_set(monkeypatch):
    lint_mod = importlib.import_module("nox_sessions.lint")

    class DummySession:
        posargs = []
        env = {}

    session = DummySession()
    called = {
        "sequence": False,
        "health": False,
    }

    def fake_sequence(sess, *, context):  # pylint: disable=unused-argument
        called["sequence"] = True

    def fake_check():
        called["health"] = True

    monkeypatch.setattr(lint_mod, "lint_all_sequence", fake_sequence)
    monkeypatch.setattr(lint_mod, "_run_lint_health_checks", fake_check)
    monkeypatch.setenv("SHIELDCRAFT_LINT_HEALTH", "1")

    lint_mod.lint_all(session)

    assert called["sequence"] is True
    assert called["health"] is True
