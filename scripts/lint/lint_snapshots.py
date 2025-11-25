"""Snapshot helpers for lint event stabilization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from scripts.lint.lint_contract import validate_lint_payload
from scripts.lint.lint_registry import register_module

_SNAPSHOT_DIRNAME = "lint_snapshots"
_FATAL_SUBDIR = "fatal"
_CANONICAL_TIMESTAMP = "SNAPSHOT"


def snapshot_dir() -> Path:
    """Return the snapshot directory path, creating it if necessary."""

    path = Path(__file__).resolve().parents[2] / _SNAPSHOT_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def _snapshot_path(target: str) -> Path:
    safe_target = target.replace("/", "_")
    return snapshot_dir() / f"{safe_target}.json"


def _fatal_snapshot_path(target: str) -> Path:
    safe_target = target.replace("/", "_")
    return snapshot_dir() / _FATAL_SUBDIR / f"{safe_target}.json"


def normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Return a canonical version of an event suitable for snapshot storage."""

    normalized = dict(event)
    normalized["timestamp"] = _CANONICAL_TIMESTAMP
    return normalized


def load_snapshot(target: str) -> Optional[Dict[str, Any]]:
    path = _snapshot_path(target)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not validate_lint_payload(data):
        raise ValueError(f"Snapshot for {target} failed contract validation")
    return data


def write_snapshot(target: str, event: Dict[str, Any]) -> None:
    canonical = normalize_event(event)
    if not validate_lint_payload(canonical):
        raise ValueError("Snapshot event failed lint contract validation")
    path = _snapshot_path(target)
    path.write_text(
        json.dumps(canonical, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )


def snapshot_matches(target: str, event: Dict[str, Any]) -> bool:
    snapshot = load_snapshot(target)
    if snapshot is None:
        return False
    return snapshot == normalize_event(event)


def write_fatal_snapshot(target: str, event: Dict[str, Any]) -> Path:
    """Persist a fatal snapshot for multi-module failures without comparisons."""

    canonical = normalize_event(event)
    if not validate_lint_payload(canonical):
        raise ValueError("Fatal snapshot event failed lint contract validation")

    path = _fatal_snapshot_path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(canonical, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


register_module(
    "lint_snapshots",
    {
        "enabled": True,
        "tier": "core",
        "owner": "platform",
        "capabilities": ["snapshots"],
    },
)
