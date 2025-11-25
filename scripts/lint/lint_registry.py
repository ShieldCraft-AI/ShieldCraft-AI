"""Declarative registry for lint modules to stabilize lifecycle and metadata."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Iterator, Optional, Tuple

_ALLOWED_TIERS = {"core", "extended", "experimental"}
CORE_MODULES = {
    "lint_capabilities",
    "lint_contract",
    "lint_events",
    "lint_failure",
    "lint_feature_flags",
    "lint_formatter",
    "lint_health",
    "lint_registry",
    "lint_snapshots",
    "nox_sessions.lint",
}

DEPRECATED_CAPABILITIES = {"structured_output_v1"}
SCHEMA_DRIFT_DIAGNOSTIC = "LINT_EVENT_SCHEMA_MISMATCH"

REGISTRY: Dict[str, Dict[str, object]] = {}


def _normalize_metadata(metadata: Dict[str, object]) -> Dict[str, object]:
    if not isinstance(metadata, dict):
        raise ValueError("metadata-must-be-dict")

    required_fields = ("enabled", "tier", "owner")
    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"missing-{field}")

    enabled = metadata["enabled"]
    tier = metadata["tier"]
    owner = metadata["owner"]
    capabilities = metadata.get("capabilities", [])
    from scripts.lint.lint_contract import validate_capability_names

    if not validate_capability_names(capabilities):
        raise ValueError("capabilities-invalid")
    normalized_capabilities = [cap.strip() for cap in (capabilities or [])]

    if not isinstance(enabled, bool):
        raise ValueError("enabled-must-be-bool")
    if not isinstance(tier, str) or tier not in _ALLOWED_TIERS:
        raise ValueError("tier-invalid")
    if not isinstance(owner, str) or not owner.strip():
        raise ValueError("owner-invalid")

    return {
        "enabled": enabled,
        "tier": tier,
        "owner": owner.strip(),
        "capabilities": normalized_capabilities,
    }


def _ordered_registry_items() -> Iterator[tuple[str, Dict[str, object]]]:
    for name in sorted(REGISTRY):
        yield name, REGISTRY[name]


def register_module(name: str, metadata: Dict[str, object]) -> Dict[str, object]:
    """Register a lint module with declarative metadata, guarding duplicates."""

    if not isinstance(name, str) or not name.strip():
        raise ValueError("module-name-invalid")

    normalized = _normalize_metadata(metadata)
    existing = REGISTRY.get(name)
    if existing is not None:
        if existing != normalized:
            raise ValueError(f"duplicate-module:{name}")
        return existing

    REGISTRY[name] = normalized
    return normalized


def get_registry_snapshot() -> Dict[str, Dict[str, object]]:
    """Return a shallow, deterministically ordered copy of the registry."""

    return {name: dict(meta) for name, meta in _ordered_registry_items()}


def _build_fail_event(reason: str) -> Dict[str, str]:
    from scripts.lint.lint_failure import fail_event

    return fail_event("lint-registry-invalid", reason)


def _validate_registry(strict: bool) -> None:
    missing = [name for name in sorted(CORE_MODULES) if name not in REGISTRY]
    if missing:
        raise ValueError(f"missing-core:{','.join(missing)}")

    for name, metadata in _ordered_registry_items():
        normalized = _normalize_metadata(metadata)
        if normalized != metadata:
            REGISTRY[name] = normalized
        if strict and normalized["tier"] == "experimental":
            raise ValueError(f"experimental-disallowed:{name}")


def validate_registry(strict: bool = False) -> Tuple[bool, Optional[Dict[str, str]]]:
    """Validate registry contents, returning (ok, fail_event|None)."""

    try:
        _validate_registry(strict)
    except ValueError as exc:  # noqa: BLE001
        return False, _build_fail_event(str(exc))

    return True, None


def persist_registry_snapshot(path: Path, *, verbose: bool = False) -> None:
    """Atomically write the ordered registry snapshot to disk."""

    snapshot = get_registry_snapshot()
    serialized = json.dumps(snapshot, separators=(",", ":"))
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_file = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        delete=False,
        dir=str(path.parent),
        prefix=f"{path.name}.",
        suffix=".tmp",
    )
    try:
        with temp_file as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        Path(temp_file.name).replace(path)
    finally:
        tmp_path = Path(temp_file.name)
        if tmp_path.exists() and tmp_path != path:
            tmp_path.unlink(missing_ok=True)

    if verbose:
        print(serialized)


def load_registry_snapshot(path: Path | str) -> Dict[str, Dict[str, object]]:
    """Load a registry snapshot from disk, validating schema integrity."""

    snapshot_path = Path(path)
    try:
        raw = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - exercised via contract tests
        raise ValueError("registry-snapshot-missing") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError("registry-snapshot-invalid") from exc
    except OSError as exc:  # pragma: no cover - surface IO failures deterministically
        raise ValueError("registry-snapshot-unreadable") from exc

    if not isinstance(raw, dict):
        raise ValueError("registry-snapshot-invalid")

    snapshot: Dict[str, Dict[str, object]] = {}
    for name, metadata in raw.items():
        if not isinstance(name, str):
            raise ValueError("registry-entry-invalid")
        snapshot[name] = _normalize_metadata(metadata)
    return snapshot


def load_feature_matrix() -> Dict[str, bool]:
    """Load the feature-flag matrix from the source module."""

    try:
        from scripts.lint import lint_feature_flags
    except ImportError as exc:  # pragma: no cover - exercised via tests
        raise ValueError("feature-matrix-missing") from exc

    try:
        matrix = lint_feature_flags.get_flags()
    except Exception as exc:  # noqa: BLE001
        raise ValueError("feature-matrix-invalid") from exc

    if not isinstance(matrix, dict):
        raise ValueError("feature-matrix-invalid")
    return matrix


def _validate_capabilities(
    contract_registry: Dict[str, Dict[str, object]], feature_matrix: Dict[str, bool]
) -> None:
    if not isinstance(contract_registry, dict):
        raise ValueError("registry-invalid")
    if not isinstance(feature_matrix, dict):
        raise ValueError("feature-matrix-invalid")

    allowed_capabilities = set(feature_matrix.keys())

    for module_name, metadata in sorted(contract_registry.items()):
        capabilities = metadata.get("capabilities") or []
        for capability in capabilities:
            if capability in DEPRECATED_CAPABILITIES:
                raise ValueError(f"deprecated-capability:{module_name}:{capability}")
            if capability not in allowed_capabilities:
                raise ValueError(f"unknown-capability:{module_name}:{capability}")
            if not feature_matrix.get(capability):
                raise ValueError(f"disabled-capability:{module_name}:{capability}")


def validate_capabilities(
    contract_registry: Dict[str, Dict[str, object]], feature_matrix: Dict[str, bool]
) -> Tuple[bool, Optional[str]]:
    """Validate capability contracts between registry entries and feature flags."""

    try:
        _validate_capabilities(contract_registry, feature_matrix)
    except ValueError as exc:  # noqa: BLE001
        return False, str(exc)
    return True, None


def lint_registry_contract_check(
    registry_path: Path, *, verbose: bool = False
) -> Dict[str, str]:
    """Run the registry capability contract validation and build a lint event."""

    from scripts.lint.lint_events import build_event
    from scripts.lint.lint_failure import fail_event

    try:
        registry_snapshot = load_registry_snapshot(registry_path)
    except ValueError as exc:
        return fail_event("lint-registry-contracts", str(exc))

    try:
        feature_matrix = load_feature_matrix()
    except ValueError as exc:
        return fail_event("lint-registry-contracts", str(exc))

    ok, reason = validate_capabilities(registry_snapshot, feature_matrix)
    if not ok:
        diagnostic = reason
        if verbose and reason is not None:
            diagnostic = f"{reason}|module-count={len(registry_snapshot)}"
        return fail_event("lint-registry-contracts", diagnostic or "capability-error")

    # Emit deterministic success diagnostics so snapshot comparison succeeds in quiet mode.
    diagnostic = f"registry-modules={len(registry_snapshot)}"
    return build_event("lint-registry-contracts", "ok", diagnostic)


def _describe_schema_drift(
    expected: Dict[str, Dict[str, object]], persisted: Dict[str, Dict[str, object]]
) -> str:
    added = sorted(set(expected) - set(persisted))
    removed = sorted(set(persisted) - set(expected))
    details = []
    if added:
        details.append(f"added={','.join(added)}")
    if removed:
        details.append(f"removed={','.join(removed)}")
    return "|".join(details)


def detect_schema_drift(
    snapshot_path: Path | str, *, snapshot_update: bool, verbose: bool = False
) -> Tuple[bool, Optional[Dict[str, str]]]:
    """Ensure the persisted registry snapshot matches the in-memory registry."""

    from scripts.lint.lint_failure import fail_event

    path = Path(snapshot_path)
    expected = get_registry_snapshot()
    try:
        persisted = load_registry_snapshot(path)
    except ValueError as exc:
        if snapshot_update:
            persist_registry_snapshot(path, verbose=verbose)
            return True, None
        return False, fail_event("lint-registry-schema", str(exc))

    if persisted == expected:
        return True, None

    if snapshot_update:
        persist_registry_snapshot(path, verbose=verbose)
        return True, None

    diagnostic = SCHEMA_DRIFT_DIAGNOSTIC
    if verbose:
        details = _describe_schema_drift(expected, persisted)
        if details:
            diagnostic = f"{SCHEMA_DRIFT_DIAGNOSTIC}|{details}"
    return False, fail_event("lint-registry-schema", diagnostic)


register_module(
    "lint_registry",
    {
        "enabled": True,
        "tier": "core",
        "owner": "platform",
        "capabilities": [],
    },
)
