"""Utilities for summarizing drift detection artifacts."""

from __future__ import annotations

import datetime as _dt
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def _load_artifact(path: Path) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - guardrail
        logger.warning("Failed to parse drift artifact %s: %s", path, exc)
        return None
    payload["_artifact_path"] = str(path)
    return payload


def load_detection_artifacts(artifacts_dir: Path) -> List[dict]:
    """Return every JSON artifact under artifacts_dir (recursive)."""

    artifacts: List[dict] = []
    if not artifacts_dir.exists():
        logger.info("Drift artifacts directory %s does not exist", artifacts_dir)
        return artifacts
    for path in sorted(artifacts_dir.rglob("*.json")):
        artifact = _load_artifact(path)
        if artifact:
            artifacts.append(artifact)
    return artifacts


def _latest_per_stack(artifacts: List[dict]) -> Dict[str, dict]:
    latest: Dict[str, dict] = {}
    for item in artifacts:
        stack = item.get("stack")
        ts = item.get("timestamp", "")
        if not stack:
            continue
        existing = latest.get(stack)
        if not existing or ts >= existing.get("timestamp", ""):
            latest[stack] = item
    return latest


def latest_artifacts_by_stack(
    artifacts_dir: Path, artifacts: Optional[List[dict]] = None
) -> Dict[str, dict]:
    """Helper returning the latest artifact per stack for a directory."""

    loaded = (
        artifacts if artifacts is not None else load_detection_artifacts(artifacts_dir)
    )
    return _latest_per_stack(loaded)


def build_summary(artifacts_dir: Path) -> dict:
    artifacts = load_detection_artifacts(artifacts_dir)
    per_stack = latest_artifacts_by_stack(artifacts_dir, artifacts)
    generated_at = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    stacks_data = []
    new_drift = []
    for stack, item in sorted(per_stack.items()):
        status = item.get("comparison_status", "unknown")
        stacks_data.append(
            {
                "stack": stack,
                "comparison_status": status,
                "drifted": bool(item.get("drifted", False)),
                "timestamp": item.get("timestamp"),
                "artifact": item.get("_artifact_path"),
                "reason": item.get("comparison_reason"),
            }
        )
        if status == "new_drift":
            new_drift.append(stack)
    summary = {
        "generated_at": generated_at,
        "artifacts_dir": str(artifacts_dir),
        "artifact_count": len(artifacts),
        "stacks": stacks_data,
        "new_drift": new_drift,
    }
    return summary


def write_summary(summary: dict, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info("Wrote drift summary to %s", destination)
    return destination


def render_markdown(summary: dict) -> str:
    """Return a markdown table describing the latest drift state."""

    lines = [
        "| Stack | Status | Drifted | Artifact | Timestamp |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in summary.get("stacks", []):
        lines.append(
            "| {stack} | {status} | {drifted} | {artifact} | {timestamp} |".format(
                stack=item.get("stack", "?"),
                status=item.get("comparison_status", "?"),
                drifted=item.get("drifted", False),
                artifact=item.get("artifact", ""),
                timestamp=item.get("timestamp", ""),
            )
        )
    if len(lines) == 2:
        lines.append("| _No drift artifacts_ | | | | |")
    return "\n".join(lines)


__all__ = [
    "build_summary",
    "latest_artifacts_by_stack",
    "load_detection_artifacts",
    "render_markdown",
    "write_summary",
]
