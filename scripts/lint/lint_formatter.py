"""Lint event formatter utilities for CI-friendly output."""

from __future__ import annotations

import json
from typing import Any, Dict

from scripts.lint.lint_contract import LINT_VERSION, validate_lint_payload
from scripts.lint.lint_registry import register_module

_REQUIRED_KEYS = ["lint_version", "target", "status", "timestamp"]
_OPTIONAL_DIAGNOSTIC_KEY = "diagnostic"
FALLBACK_EVENT_JSON = (
    '{"lint_version":"1.0","status":"error","diagnostic":"formatter-failed"}'
)
register_module(
    "lint_formatter",
    {
        "enabled": True,
        "tier": "core",
        "owner": "platform",
        "capabilities": ["formatting", "events_unified"],
    },
)


def _ensure_required_fields(event: Dict[str, Any]) -> None:
    for key in _REQUIRED_KEYS:
        if key not in event:
            raise ValueError(f"lint event missing required key: {key}")


def format_event(event: Dict[str, Any], *, verbose: bool = False) -> str:
    """Serialize a contract-compliant lint event to a single-line JSON string."""

    if not isinstance(event, dict):
        raise ValueError("lint event must be a dict")

    if not validate_lint_payload(event):
        raise ValueError("lint event failed contract validation")

    enriched = dict(event)
    enriched.setdefault("lint_version", LINT_VERSION)
    _ensure_required_fields(enriched)

    formatted: Dict[str, Any] = {
        "lint_version": enriched["lint_version"],
        "target": enriched["target"],
        "status": enriched["status"],
        "timestamp": enriched["timestamp"],
    }

    if _OPTIONAL_DIAGNOSTIC_KEY in enriched:
        diagnostic = enriched[_OPTIONAL_DIAGNOSTIC_KEY]
        if not isinstance(diagnostic, str):
            raise ValueError("diagnostic must be a string when provided")
        formatted[_OPTIONAL_DIAGNOSTIC_KEY] = diagnostic

    try:
        return json.dumps(formatted, separators=(",", ":"))
    except (TypeError, ValueError):
        print(FALLBACK_EVENT_JSON)
        if verbose:
            raise
        return FALLBACK_EVENT_JSON
