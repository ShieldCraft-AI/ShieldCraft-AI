"""Forward compatibility feature-flag matrix for the lint subsystem."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from scripts.lint.lint_failure import fail_event
from scripts.lint.lint_registry import register_module

REQUIRED_FLAGS: Dict[str, bool] = {
    "contracts": True,
    "snapshots": True,
    "resilience_layer": True,
    "health_checks": True,
    "formatting": True,
    "events_unified": True,
    "lint_all_quiet_retry": True,
    "schema_drift_guard": True,
}

OPTIONAL_FLAGS: Dict[str, bool] = {
    "auto_fix_mode": False,
    "plugin_support": False,
    "structured_output_v2": False,
}

register_module(
    "lint_feature_flags",
    {
        "enabled": True,
        "tier": "core",
        "owner": "platform",
        "capabilities": ["resilience_layer"],
    },
)

_ALLOWED_KEYS = set(REQUIRED_FLAGS) | set(OPTIONAL_FLAGS)


def get_flags() -> Dict[str, bool]:
    """Return the merged feature flags matrix."""

    merged = dict(REQUIRED_FLAGS)
    merged.update(OPTIONAL_FLAGS)
    return merged


def _validate_required(flags: Dict[str, bool]) -> None:
    for key, expected in REQUIRED_FLAGS.items():
        if key not in flags:
            raise ValueError(f"missing-required:{key}")
        value = flags[key]
        if not isinstance(value, bool):
            raise ValueError(f"{key}-must-be-bool")
        if value is not expected:
            raise ValueError(f"{key}-must-be-{expected}")


def _validate_optional(flags: Dict[str, bool]) -> None:
    for key in OPTIONAL_FLAGS:
        value = flags.get(key)
        if value is None:
            continue
        if not isinstance(value, bool):
            raise ValueError(f"{key}-must-be-bool")


def _validate_no_unknown(flags: Dict[str, bool]) -> None:
    extras = sorted(set(flags) - _ALLOWED_KEYS)
    if extras:
        raise ValueError(f"unknown-flags:{','.join(extras)}")


def validate_flags() -> Tuple[bool, Optional[Dict[str, str]]]:
    """Validate the feature flags matrix, mirroring lint failure semantics."""

    flags = get_flags()
    if not isinstance(flags, dict):
        return False, fail_event(
            "lint-feature-flags-invalid",
            "flags-not-dict",
        )

    try:
        _validate_no_unknown(flags)
        _validate_required(flags)
        _validate_optional(flags)
    except ValueError as exc:  # noqa: BLE001
        return False, fail_event("lint-feature-flags-invalid", str(exc))

    return True, None
