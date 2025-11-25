from __future__ import annotations

import json

import pytest

from scripts import lint_forbidden_flags
from scripts.lint.lint_contract import validate_lint_payload
from scripts.lint.lint_events import build_event
from scripts.lint.lint_failure import fail_event, safe_emit


def test_fail_event_is_contract_compliant():
    event = fail_event("lint_forbidden", "boom")
    assert validate_lint_payload(event) is True
    assert event["status"] == "error"


def test_safe_emit_quiet_suppresses_ok(capsys):
    event = build_event("lint_forbidden", "ok", "clean")
    safe_emit(event, allow_quiet=True)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_safe_emit_verbose_formatter_failure(monkeypatch, capsys):
    def boom(*args, **kwargs):  # noqa: ARG001
        raise ValueError("json error")

    monkeypatch.setattr("scripts.lint.lint_formatter.json.dumps", boom)
    event = build_event("lint_forbidden", "fail", "boom")

    with pytest.raises(ValueError):
        safe_emit(event, allow_quiet=False)

    output = capsys.readouterr().out.strip().splitlines()
    assert (
        output[-1]
        == '{"lint_version":"1.0","status":"error","diagnostic":"formatter-failed"}'
    )


def test_safe_emit_quiet_formatter_failure(monkeypatch, capsys):
    def boom(*args, **kwargs):  # noqa: ARG001
        raise ValueError("json error")

    monkeypatch.setattr("scripts.lint.lint_formatter.json.dumps", boom)
    event = build_event("lint_forbidden", "fail", "boom")

    safe_emit(event, allow_quiet=True)

    output = capsys.readouterr().out.strip().splitlines()
    assert (
        output[-1]
        == '{"lint_version":"1.0","status":"error","diagnostic":"formatter-failed"}'
    )


def test_lint_forbidden_exception_emits_fail_event(tmp_path, capsys, monkeypatch):
    sample = tmp_path / "bad.py"
    sample.write_text("print('x')\n", encoding="utf-8")

    def bad_contains(path):  # noqa: ARG001
        raise RuntimeError("read failure")

    monkeypatch.setattr(lint_forbidden_flags, "_contains_forbidden_token", bad_contains)

    code = lint_forbidden_flags.lint_changed_files(
        [sample.as_posix()], allow_quiet=False, verbose=False
    )
    assert code == 1

    lines = [line for line in capsys.readouterr().out.splitlines() if line]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["status"] == "error"


def test_lint_forbidden_exception_raises_in_verbose(tmp_path, capsys, monkeypatch):
    sample = tmp_path / "bad.py"
    sample.write_text("print('x')\n", encoding="utf-8")

    def bad_contains(path):  # noqa: ARG001
        raise RuntimeError("read failure")

    monkeypatch.setattr(lint_forbidden_flags, "_contains_forbidden_token", bad_contains)

    with pytest.raises(RuntimeError):
        lint_forbidden_flags.lint_changed_files(
            [sample.as_posix()], allow_quiet=False, verbose=True
        )

    lines = [line for line in capsys.readouterr().out.splitlines() if line]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["status"] == "error"
