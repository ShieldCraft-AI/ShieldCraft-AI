"""Baseline helpers for ShieldCraft drift automation."""

from __future__ import annotations

from dataclasses import dataclass, field
import datetime as _dt
import hashlib
import json
import logging
from pathlib import Path
from typing import Iterable


logger = logging.getLogger(__name__)

BASELINE_ROOT = Path(__file__).resolve().parents[2] / "drift_baselines"
HASH_PREFIX = "sha256"


class BaselineError(RuntimeError):
    """Base exception for baseline helpers."""


class BaselineMissingError(BaselineError):
    """Raised when no baseline file exists for a stack."""


class BaselineSchemaError(BaselineError):
    """Raised when baseline JSON is missing mandatory fields."""


@dataclass
class BaselineData:
    """Canonical baseline payload."""

    stack: str
    last_known_hash: str
    last_acknowledged_timestamp: str
    comment: str = ""
    allowlist: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict) -> "BaselineData":
        required = {"stack", "last_known_hash", "last_acknowledged_timestamp"}
        missing = required.difference(payload)
        if missing:
            raise BaselineSchemaError(
                f"Baseline for {payload.get('stack', '<unknown>')} missing {sorted(missing)}"
            )
        allowlist = payload.get("allowlist")
        if allowlist is None:
            allow = []
        elif isinstance(allowlist, list):
            allow = list(allowlist)
        else:  # pragma: no cover - guardrail
            raise BaselineSchemaError("allowlist must be a list when provided")
        return cls(
            stack=payload["stack"],
            last_known_hash=payload["last_known_hash"],
            last_acknowledged_timestamp=payload["last_acknowledged_timestamp"],
            comment=payload.get("comment", ""),
            allowlist=allow,
        )

    def to_dict(self) -> dict:
        return {
            "stack": self.stack,
            "last_known_hash": self.last_known_hash,
            "last_acknowledged_timestamp": self.last_acknowledged_timestamp,
            "comment": self.comment,
            "allowlist": self.allowlist,
        }


def baseline_path(stack: str) -> Path:
    """Return the canonical baseline path for a stack."""

    return BASELINE_ROOT / f"{stack}.json"


def ensure_baseline_dir() -> Path:
    """Ensure the baseline directory exists and return the path."""

    BASELINE_ROOT.mkdir(parents=True, exist_ok=True)
    return BASELINE_ROOT


def baseline_exists(stack: str) -> bool:
    """Return True if a baseline file exists for the stack."""

    return baseline_path(stack).exists()


def hash_diff_text(diff_text: str) -> str:
    digest = hashlib.sha256(diff_text.encode("utf-8")).hexdigest()
    return f"{HASH_PREFIX}:{digest}"


def load_baseline(stack: str) -> BaselineData:
    path = baseline_path(stack)
    if not path.exists():
        raise BaselineMissingError(f"Baseline not found for stack {stack}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise BaselineSchemaError(
            f"Invalid JSON in baseline for {stack}: {exc}"
        ) from exc
    data = BaselineData.from_dict(payload)
    if data.stack != stack:
        raise BaselineSchemaError(
            f"Baseline {path} recorded stack {data.stack}, expected {stack}"
        )
    return data


def write_baseline(stack: str, data: BaselineData) -> Path:
    directory = ensure_baseline_dir()
    path = directory / f"{stack}.json"
    path.write_text(json.dumps(data.to_dict(), indent=2), encoding="utf-8")
    logger.info("Baseline for stack %s updated at %s", stack, path)
    return path


def acknowledge_drift(
    stack: str,
    diff_hash: str,
    comment: str,
    allowlist: Iterable[str] | None = None,
) -> BaselineData:
    timestamp = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    baseline = BaselineData(
        stack=stack,
        last_known_hash=diff_hash,
        last_acknowledged_timestamp=timestamp,
        comment=comment,
        allowlist=list(allowlist or []),
    )
    write_baseline(stack, baseline)
    return baseline


__all__ = [
    "BASELINE_ROOT",
    "baseline_exists",
    "baseline_path",
    "BaselineData",
    "BaselineError",
    "BaselineMissingError",
    "BaselineSchemaError",
    "acknowledge_drift",
    "ensure_baseline_dir",
    "hash_diff_text",
    "load_baseline",
    "write_baseline",
]
