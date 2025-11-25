"""Lint contract helpers ensuring consistent payloads across lint modules."""

from __future__ import annotations

from typing import Any, Dict

LINT_VERSION = "1.0"
CONTRACT_FIELDS = ["target", "status", "stdout", "stderr", "timestamp"]
_ALLOWED_STATUSES = {"ok", "fail", "error"}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_lint_payload(payload: Dict[str, Any]) -> bool:
    """Validate lint payloads before they are surfaced to callers."""

    if not isinstance(payload, dict):
        return False

    for field in CONTRACT_FIELDS:
        if field not in payload:
            return False

    target = payload["target"]
    status = payload["status"]
    stdout = payload["stdout"]
    stderr = payload["stderr"]
    timestamp = payload["timestamp"]

    if not _is_non_empty_string(target):
        return False
    if not isinstance(status, str) or status not in _ALLOWED_STATUSES:
        return False
    if not isinstance(stdout, str) or not isinstance(stderr, str):
        return False
    if not _is_non_empty_string(timestamp):
        return False

    return True


def validate_capability_names(values: Any) -> bool:
    """Return True when the provided capability list is schema-compliant."""

    if values is None:
        return True
    if not isinstance(values, list):
        return False
    return all(_is_non_empty_string(value) for value in values)


def _register_self() -> None:
    from scripts.lint.lint_registry import register_module

    register_module(
        "lint_contract",
        {
            "enabled": True,
            "tier": "core",
            "owner": "platform",
            "capabilities": ["contracts"],
        },
    )


_register_self()
