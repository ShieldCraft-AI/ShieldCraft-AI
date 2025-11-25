"""Meta checks ensuring lint subsystem health."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from scripts.lint import lint_snapshots
from scripts.lint.lint_contract import (
    CONTRACT_FIELDS,
    LINT_VERSION,
    validate_lint_payload,
)
from scripts.lint.lint_events import build_event
from scripts.lint.lint_failure import fail_event, safe_emit
from scripts.lint.lint_formatter import format_event
from scripts.lint.lint_registry import register_module


def _health_fail(reason: str) -> None:
    safe_emit(fail_event("lint-health-failure", reason), allow_quiet=False)
    raise RuntimeError(reason)


def _minimal_event() -> dict:
    return {
        "lint_version": LINT_VERSION,
        "target": "lint-health",
        "status": "ok",
        "timestamp": "2024-01-01T00:00:00Z",
        "stdout": "",
        "stderr": "",
    }


def check_formatter_contract() -> None:
    event = _minimal_event()
    formatted = format_event(event, verbose=True)
    try:
        payload = json.loads(formatted)
    except json.JSONDecodeError as exc:  # pragma: no cover
        _health_fail(f"formatter-json-error:{exc}")
        return

    for field in ("lint_version", "target", "status", "timestamp"):
        if payload.get(field) != event[field]:
            _health_fail(f"formatter-missing-{field}")


def check_builder_contract() -> None:
    event = build_event("lint-health", "ok")
    if event.get("lint_version") != LINT_VERSION:
        _health_fail("builder-version-mismatch")
    if not validate_lint_payload(event):
        _health_fail("builder-invalid-payload")
    for field in CONTRACT_FIELDS:
        if field not in event:
            _health_fail(f"builder-missing-{field}")


def _iter_snapshot_payloads(snapshot_dir: Path | None = None) -> Iterable[dict]:
    base = snapshot_dir or lint_snapshots.snapshot_dir()
    if not base.exists():
        return []
    payloads: List[dict] = []
    for path in sorted(base.glob("*.json")):
        try:
            payloads.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            _health_fail(f"snapshot-json-error:{path.name}")
    return payloads


def check_snapshot_consistency(snapshot_dir: Path | None = None) -> None:
    allowed_keys = set(CONTRACT_FIELDS + ["lint_version", "diagnostic"])
    for payload in _iter_snapshot_payloads(snapshot_dir):
        if not validate_lint_payload(payload):
            _health_fail("snapshot-invalid-payload")
        if payload.get("lint_version") != LINT_VERSION:
            _health_fail("snapshot-version-mismatch")
        if set(payload.keys()) - allowed_keys:
            _health_fail("snapshot-unknown-fields")


register_module(
    "lint_health",
    {
        "enabled": True,
        "tier": "core",
        "owner": "platform",
        "capabilities": ["health_checks"],
    },
)
