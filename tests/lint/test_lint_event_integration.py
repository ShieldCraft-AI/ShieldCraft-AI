from __future__ import annotations

import json

from scripts import lint_forbidden_flags
from scripts.lint.lint_contract import validate_lint_payload
from scripts.lint.lint_events import build_event


def _read_lines(capsys) -> list[str]:
    out = capsys.readouterr().out.strip()
    return [line for line in out.splitlines() if line]


def test_build_event_produces_valid_payload():
    event = build_event("lint_forbidden", "ok", "diagnostic")
    assert validate_lint_payload(event) is True
    assert event["diagnostic"] == "diagnostic"


def test_lint_forbidden_flags_clean_emits_ok(tmp_path, capsys):
    sample = tmp_path / "clean.py"
    sample.write_text("print('ok')\n", encoding="utf-8")

    exit_code = lint_forbidden_flags.lint_changed_files([sample.as_posix()])

    assert exit_code == 0
    lines = _read_lines(capsys)
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["status"] == "ok"
    assert payload["diagnostic"] == "no-violations"


def test_lint_forbidden_flags_single_violation(tmp_path, capsys):
    sample = tmp_path / "bad.py"
    sample.write_text(
        f"echo '{lint_forbidden_flags.FORBIDDEN_TOKEN}'\n", encoding="utf-8"
    )

    exit_code = lint_forbidden_flags.lint_changed_files([sample.as_posix()])

    assert exit_code == 1
    lines = _read_lines(capsys)
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["status"] == "fail"
    assert lint_forbidden_flags.FORBIDDEN_TOKEN in payload["diagnostic"]


def test_lint_forbidden_flags_multiple_violations(tmp_path, capsys):
    bad_one = tmp_path / "bad_a.py"
    bad_two = tmp_path / "bad_b.py"
    bad_one.write_text(lint_forbidden_flags.FORBIDDEN_TOKEN, encoding="utf-8")
    bad_two.write_text(f"# {lint_forbidden_flags.FORBIDDEN_TOKEN}", encoding="utf-8")

    exit_code = lint_forbidden_flags.lint_changed_files(
        [bad_one.as_posix(), bad_two.as_posix()]
    )

    assert exit_code == 1
    lines = _read_lines(capsys)
    assert len(lines) == 2
    statuses = [json.loads(line)["status"] for line in lines]
    assert statuses == ["fail", "fail"]
