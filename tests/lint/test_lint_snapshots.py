from __future__ import annotations

import importlib

import pytest

from scripts.lint import lint_snapshots
from scripts.lint.lint_events import build_event


def _lint_module():
    return importlib.import_module("nox_sessions.lint")


@pytest.fixture
def snapshot_dir(tmp_path, monkeypatch):
    root = tmp_path / "lint_snapshots"
    root.mkdir()

    def _dir():
        return root

    monkeypatch.setattr(lint_snapshots, "snapshot_dir", _dir)
    return root


def _set_snapshot(target: str, diagnostic: str) -> None:
    event = build_event(target, "ok", diagnostic)
    lint_snapshots.write_snapshot(target, event)


def test_handle_snapshot_mismatch_fails(snapshot_dir, monkeypatch):
    _ = snapshot_dir
    lint_module = _lint_module()
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    _set_snapshot("lint", "expected")

    emitted = []

    def fake_emit(event, *, allow_quiet):  # pylint: disable=unused-argument
        emitted.append(event)

    monkeypatch.setattr(lint_module, "safe_emit", fake_emit)

    context = lint_module.LintRunContext(
        verbose=False,
        snapshot_update=False,
        snapshot_ignore=False,
    )
    mismatch = build_event("lint", "ok", "mismatch")

    with pytest.raises(RuntimeError):
        lint_module._handle_snapshot(mismatch, context)

    assert emitted[-1]["diagnostic"] == "snapshot-mismatch"
    assert emitted[-1]["status"] == "error"


def test_handle_snapshot_override_requires_verbose_ignore(snapshot_dir, monkeypatch):
    _ = snapshot_dir
    lint_module = _lint_module()
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    _set_snapshot("lint", "expected")

    emitted = []

    def fake_emit(event, *, allow_quiet):  # pylint: disable=unused-argument
        emitted.append(event)

    monkeypatch.setattr(lint_module, "safe_emit", fake_emit)

    context = lint_module.LintRunContext(
        verbose=True,
        snapshot_update=False,
        snapshot_ignore=True,
    )
    mismatch = build_event("lint", "ok", "mismatch")

    lint_module._handle_snapshot(mismatch, context)

    assert emitted[-1]["diagnostic"] == "snapshot-mismatch"
    assert emitted[-1]["status"] == "error"


def test_handle_snapshot_no_override_in_ci(snapshot_dir, monkeypatch):
    _ = snapshot_dir
    lint_module = _lint_module()
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    _set_snapshot("lint", "expected")

    emitted = []

    def fake_emit(event, *, allow_quiet):  # pylint: disable=unused-argument
        emitted.append(event)

    monkeypatch.setattr(lint_module, "safe_emit", fake_emit)

    context = lint_module.LintRunContext(
        verbose=True,
        snapshot_update=False,
        snapshot_ignore=True,
    )
    mismatch = build_event("lint", "ok", "mismatch")

    with pytest.raises(RuntimeError):
        lint_module._handle_snapshot(mismatch, context)

    assert emitted[-1]["diagnostic"] == "snapshot-mismatch"
    assert emitted[-1]["status"] == "error"
