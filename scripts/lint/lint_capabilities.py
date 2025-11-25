"""Machine-readable manifest of available lint subsystem capabilities."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from scripts.lint.lint_contract import LINT_VERSION
from scripts.lint.lint_failure import fail_event
from scripts.lint.lint_registry import register_module

LINT_CAPABILITIES: Dict[str, object] = {
    "lint_version": LINT_VERSION,
    "supports_snapshots": True,
    "supports_resilience_layer": True,
    "supports_health_checks": True,
    "supports_formatter": True,
    "supports_schema_drift_guard": True,
    "requires_contract_validation": True,
    "quiet_mode_default": True,
    "verbose_mode_supported": True,
}

_REQUIRED_KEYS = tuple(LINT_CAPABILITIES.keys())
_BOOL_KEYS = tuple(key for key in _REQUIRED_KEYS if key != "lint_version")

register_module(
    "lint_capabilities",
    {
        "enabled": True,
        "tier": "core",
        "owner": "platform",
        "capabilities": ["contracts"],
    },
)


def get_capabilities() -> Dict[str, object]:
    """Return a shallow copy of the lint capabilities manifest."""

    return dict(LINT_CAPABILITIES)


def _validate_manifest_structure(manifest: Dict[str, object]) -> None:
    missing = [key for key in _REQUIRED_KEYS if key not in manifest]
    if missing:
        raise ValueError(f"missing-fields:{','.join(sorted(missing))}")

    version = manifest.get("lint_version")
    if not isinstance(version, str):
        raise ValueError("lint_version-must-be-string")
    if version != LINT_VERSION:
        raise ValueError("lint_version-mismatch")

    for key in _BOOL_KEYS:
        if not isinstance(manifest.get(key), bool):
            raise ValueError(f"{key}-must-be-bool")


def validate_capabilities() -> Tuple[bool, Optional[Dict[str, str]]]:
    """Validate the manifest, returning (ok, fail_event|None) on completion."""

    manifest = get_capabilities()
    if not isinstance(manifest, dict):
        return False, fail_event(
            "lint-capabilities-invalid",
            "manifest-not-dict",
        )

    try:
        _validate_manifest_structure(manifest)
    except ValueError as exc:  # noqa: BLE001
        return False, fail_event("lint-capabilities-invalid", str(exc))

    return True, None
