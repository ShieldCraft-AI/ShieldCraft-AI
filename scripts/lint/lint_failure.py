"""Failure-mode helpers for lint event emission."""

from __future__ import annotations

from typing import Dict

from scripts.lint.lint_events import build_event
from scripts.lint.lint_formatter import FALLBACK_EVENT_JSON, format_event
from scripts.lint.lint_registry import register_module

register_module(
    "lint_failure",
    {
        "enabled": True,
        "tier": "core",
        "owner": "platform",
        "capabilities": ["resilience_layer"],
    },
)


def fail_event(target: str, reason: str) -> Dict[str, str]:
    """Return a formatter-compliant failure event for the given target."""

    diagnostic = reason or "unknown-error"
    return build_event(target, "error", diagnostic)


def safe_emit(event: Dict[str, str], *, allow_quiet: bool = False) -> None:
    """Safely emit an event, honoring quiet mode rules."""

    if allow_quiet and event.get("status") == "ok":
        return

    try:
        serialized = format_event(event, verbose=not allow_quiet)
    except ValueError:
        # format_event already handled fallback printing; only propagate for verbose flows.
        if not allow_quiet:
            raise
        return

    if serialized == FALLBACK_EVENT_JSON:
        # formatter already printed the fallback payload, avoid duplicates.
        return

    print(serialized)
