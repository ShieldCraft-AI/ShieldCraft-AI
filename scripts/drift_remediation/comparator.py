"""Drift comparator utilities for ShieldCraft drift automation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Optional, Set


class DriftStatus(str, Enum):
    """Enumeration describing drift comparison outcomes."""

    NO_DRIFT = "no_drift"
    ACKNOWLEDGED = "acknowledged"
    NEW_DRIFT = "new_drift"
    BASELINE_MISSING = "baseline_missing"


@dataclass
class ComparisonResult:
    """Container summarizing comparison verdicts."""

    status: DriftStatus
    reason: str


def _extract_allowlist(baseline: Mapping[str, object]) -> Set[str]:
    raw = baseline.get("allowlist", []) if baseline else []
    return {str(item) for item in raw} if isinstance(raw, Iterable) else set()


def _drifted_resource_ids(
    summary: Optional[Iterable[Mapping[str, object]]],
) -> Set[str]:
    if not summary:
        return set()
    ids: Set[str] = set()
    for entry in summary:
        status = str(entry.get("status", ""))
        if status not in {"IN_SYNC", "DELETED"}:
            ids.add(str(entry.get("logical_id")))
    return ids


def compare(
    diff_hash: str,
    baseline: Optional[Mapping[str, object]],
    resource_summary: Optional[Iterable[Mapping[str, object]]] = None,
) -> ComparisonResult:
    """Compare diff hash against baseline metadata."""

    if not diff_hash.strip():
        return ComparisonResult(DriftStatus.NO_DRIFT, "Empty diff")
    if baseline is None:
        return ComparisonResult(
            status=DriftStatus.BASELINE_MISSING,
            reason="Baseline not found",
        )
    baseline_hash = str(baseline.get("last_known_hash", ""))
    if diff_hash == baseline_hash:
        return ComparisonResult(DriftStatus.ACKNOWLEDGED, "Hash matches baseline")

    allowlist = _extract_allowlist(baseline)
    drift_ids = _drifted_resource_ids(resource_summary)
    if allowlist and drift_ids and drift_ids.issubset(allowlist):
        return ComparisonResult(
            DriftStatus.ACKNOWLEDGED,
            "Drift limited to allowlisted resources",
        )

    return ComparisonResult(DriftStatus.NEW_DRIFT, "Diff hash differs from baseline")


__all__ = ["DriftStatus", "ComparisonResult", "compare"]
