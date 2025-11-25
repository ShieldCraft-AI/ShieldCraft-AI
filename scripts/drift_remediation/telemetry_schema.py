"""Lightweight telemetry schema helpers (local validation only)."""

from __future__ import annotations

from typing import Mapping, Any

_LOG_FIELDS = {"telemetry_type", "stack", "comparison_status"}
_SUMMARY_FIELDS = {
    "telemetry_type",
    "stacks_scanned",
    "drift_new_detected",
    "drift_acknowledged",
    "drift_baseline_missing",
    "ci_forced",
}


def _has_fields(payload: Mapping[str, Any] | None, required: set[str]) -> bool:
    if payload is None:
        return False
    if not isinstance(payload, Mapping):
        return False
    return required.issubset(payload.keys())


def validate_telemetry_log(payload: Mapping[str, Any] | None) -> bool:
    """Return True when stack-level telemetry records contain required keys."""

    return _has_fields(payload, _LOG_FIELDS)


def validate_telemetry_artifact(payload: Mapping[str, Any] | None) -> bool:
    """Return True when summary telemetry artifacts have required counters."""

    return _has_fields(payload, _SUMMARY_FIELDS)
