"""Shared lint event helpers for consistent log payloads."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from scripts.lint.lint_contract import (
    LINT_VERSION,
    CONTRACT_FIELDS,
    validate_lint_payload,
)
from scripts.lint.lint_registry import register_module

register_module(
    "lint_events",
    {
        "enabled": True,
        "tier": "core",
        "owner": "platform",
        "capabilities": ["events_unified"],
    },
)


def _iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_event(target: str, status: str, diagnostic: Optional[str] = None) -> dict:
    """Build a lint event dict that satisfies the lint contract."""

    if not isinstance(target, str) or not target.strip():
        raise ValueError("target must be a non-empty string")
    if not isinstance(status, str) or not status.strip():
        raise ValueError("status must be a non-empty string")

    event = {
        "target": target,
        "status": status,
        "stdout": "",
        "stderr": "",
        "timestamp": _iso_timestamp(),
        "lint_version": LINT_VERSION,
    }
    if diagnostic is not None:
        if not isinstance(diagnostic, str):
            raise ValueError("diagnostic must be a string")
        event["diagnostic"] = diagnostic

    missing = [field for field in CONTRACT_FIELDS if field not in event]
    if missing:
        raise ValueError(f"event missing required fields: {missing}")

    if not validate_lint_payload(event):
        raise ValueError("event failed lint contract validation")

    return event
