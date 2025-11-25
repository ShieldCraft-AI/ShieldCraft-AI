from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
LINT_FILE = REPO_ROOT / "nox_sessions" / "lint.py"


def _get_function_node(name: str) -> ast.FunctionDef | None:
    tree = ast.parse(LINT_FILE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def test_lint_all_exists_and_order():
    lint_all = _get_function_node("lint_all")
    assert lint_all is not None, "lint_all session must exist for local parity"

    delegates = False
    for node in ast.walk(lint_all):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "lint_all_sequence":
                delegates = True
                break
    assert delegates, "lint_all must delegate to lint_all_sequence"


def test_lint_all_sequence_targets():
    lint_all_sequence = _get_function_node("lint_all_sequence")
    assert lint_all_sequence is not None, "lint_all_sequence helper must exist"

    targets: list[str] = []
    for node in ast.walk(lint_all_sequence):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in {"lint_forbidden", "lint"}:
                targets.append(node.value)

    assert targets[:2] == [
        "lint_forbidden",
        "lint",
    ], "helper must run lint_forbidden first"


def _import_lint_module():
    return importlib.import_module("nox_sessions.lint")


def test_parse_lint_flags_extracts_supported_flags():
    lint_module = _import_lint_module()

    class DummySession:
        def __init__(self):
            self.posargs = ["--verbose", "--ignore-snapshot", "--foo"]

    session = DummySession()
    verbose, ignore = lint_module._parse_lint_flags(session)
    assert verbose is True
    assert ignore is True
    assert session.posargs == ["--foo"]


def test_parse_lint_flags_handles_absence():
    lint_module = _import_lint_module()

    class DummySession:
        def __init__(self):
            self.posargs = ["--foo"]

    session = DummySession()
    verbose, ignore = lint_module._parse_lint_flags(session)
    assert verbose is False
    assert ignore is False
    assert session.posargs == ["--foo"]


def test_lint_all_delegates_with_context(monkeypatch):
    lint_module = _import_lint_module()

    calls: dict[str, object] = {}
    order: list[str] = []

    def fake_parse(session):  # pylint: disable=unused-argument
        calls["parsed"] = True
        return True, False

    def fake_ensure(ignore_snapshot, verbose):
        calls["ensured"] = (ignore_snapshot, verbose)

    fake_context = lint_module.LintRunContext(
        verbose=True,
        snapshot_update=False,
        snapshot_ignore=False,
    )

    def fake_build(verbose, ignore_snapshot):
        calls["built"] = (verbose, ignore_snapshot)
        return fake_context

    def fake_sequence(session, *, context):
        calls["sequence"] = (session, context)

    def fake_registry(context):  # pylint: disable=unused-argument
        order.append("registry")

    def fake_caps(context):  # pylint: disable=unused-argument
        order.append("capabilities")

    def fake_flags(context):  # pylint: disable=unused-argument
        order.append("feature-flags")

    def fake_contract(context):  # pylint: disable=unused-argument
        order.append("registry-contracts")

    def fake_schema(context):  # pylint: disable=unused-argument
        order.append("registry-schema")

    monkeypatch.setattr(lint_module, "_parse_lint_flags", fake_parse)
    monkeypatch.setattr(lint_module, "_ensure_ignore_snapshot_allowed", fake_ensure)
    monkeypatch.setattr(lint_module, "_build_context", fake_build)
    monkeypatch.setattr(lint_module, "lint_all_sequence", fake_sequence)
    monkeypatch.setattr(lint_module, "_assert_registry_valid", fake_registry)
    monkeypatch.setattr(lint_module, "_enforce_registry_snapshot", fake_schema)
    monkeypatch.setattr(lint_module, "_assert_capabilities_valid", fake_caps)
    monkeypatch.setattr(lint_module, "_assert_feature_flags_valid", fake_flags)
    monkeypatch.setattr(lint_module, "_run_registry_contract_check", fake_contract)

    class DummySession:
        posargs: list[str] = []

    session = DummySession()
    lint_module.lint_all(session)

    assert calls["parsed"] is True
    assert calls["ensured"] == (False, True)
    assert calls["built"] == (True, False)
    assert calls["sequence"] == (session, fake_context)
    assert order == [
        "registry",
        "registry-schema",
        "capabilities",
        "feature-flags",
        "registry-contracts",
    ]


def test_run_lint_target_quiet_reruns_on_failure(monkeypatch):
    lint_module = _import_lint_module()

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
    monkeypatch.setattr(lint_module, "_handle_snapshot", lambda payload, context: None)

    with pytest.raises(lint_module.CommandFailed):
        lint_module._run_lint_target(
            session,
            "lint_forbidden",
            lint_module.LintRunContext(False, False, False),
        )

    assert [call["silent"] for call in session.calls] == [True, False]
    statuses = [entry[0]["status"] for entry in emitted]
    assert statuses == ["fail", "fail", "ok"]
    assert emitted[0][1] is True
    assert emitted[1][0]["diagnostic"] == "retrying-verbose"


def test_run_lint_target_verbose_does_not_rerun(monkeypatch):
    lint_module = _import_lint_module()

    class DummySession:
        def __init__(self):
            self.calls = []

        def run(self, *args, **kwargs):
            self.calls.append({"args": args, "silent": kwargs.get("silent")})
            raise lint_module.CommandFailed("boom")

    session = DummySession()
    emitted = []

    def fake_emit(event, *, allow_quiet):
        emitted.append((event, allow_quiet))

    monkeypatch.setattr(lint_module, "safe_emit", fake_emit)
    monkeypatch.setattr(lint_module, "_handle_snapshot", lambda payload, context: None)

    with pytest.raises(lint_module.CommandFailed):
        lint_module._run_lint_target(
            session,
            "lint_forbidden",
            lint_module.LintRunContext(True, False, False),
        )

    assert [call["silent"] for call in session.calls] == [
        False
    ], "verbose should run once"
    assert len(emitted) == 1
    assert emitted[0][0]["status"] == "fail"
    assert emitted[0][1] is False


def test_enforce_registry_snapshot_emits_verbose_retry(monkeypatch):
    lint_module = _import_lint_module()
    events: list[tuple[dict, bool]] = []

    responses = [
        (
            False,
            {
                "target": "lint-registry-schema",
                "status": "error",
                "diagnostic": "LINT_EVENT_SCHEMA_MISMATCH",
            },
        ),
        (
            False,
            {
                "target": "lint-registry-schema",
                "status": "error",
                "diagnostic": "LINT_EVENT_SCHEMA_MISMATCH|details",
            },
        ),
    ]

    def fake_detect(path, *, snapshot_update, verbose):  # noqa: D401
        _ = (path, snapshot_update)
        return responses.pop(0)

    def fake_emit(
        payload, context, enforce_snapshot=True
    ):  # pylint: disable=unused-argument
        events.append((payload, context.verbose))

    monkeypatch.setattr(lint_module, "detect_schema_drift", fake_detect)
    monkeypatch.setattr(lint_module, "_emit_lint_event", fake_emit)

    context = lint_module.LintRunContext(False, False, False)
    with pytest.raises(RuntimeError):
        lint_module._enforce_registry_snapshot(context)

    assert events[0][1] is False
    assert events[1][1] is True


def test_failure_summary_classification_order_and_snapshot(monkeypatch):
    lint_module = _import_lint_module()
    lint_module._FAILURE_AGGREGATOR.reset()

    lint_module._FAILURE_AGGREGATOR.record(
        {"target": "lint_forbidden", "status": "fail"}
    )
    lint_module._FAILURE_AGGREGATOR.record({"target": "lint", "status": "fail"})
    lint_module._FAILURE_AGGREGATOR.record(
        {"target": "lint-registry-schema", "status": "error"}
    )
    lint_module._FAILURE_AGGREGATOR.record(
        {"target": "lint_formatter", "status": "error"}
    )

    emitted: list[dict] = []
    monkeypatch.setattr(
        lint_module, "safe_emit", lambda event, allow_quiet: emitted.append(event)
    )

    recorded: list[tuple[str, dict]] = []

    def fake_write(target, event):  # noqa: D401
        recorded.append((target, event))

    monkeypatch.setattr(lint_module.lint_snapshots, "write_fatal_snapshot", fake_write)

    lint_module._emit_failure_summary()

    assert len(emitted) == 1
    diagnostic = emitted[0]["diagnostic"]
    assert diagnostic.startswith(
        "classifications=syntax,formatting,forbidden-flag,registry-drift"
    )
    assert (
        "targets=lint_forbidden,lint,lint-registry-schema,lint_formatter" in diagnostic
    )
    assert recorded and recorded[0][0] == "lint-fatal-summary"
    assert lint_module._FAILURE_AGGREGATOR.summary_event() is None
