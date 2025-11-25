from __future__ import annotations

from typing import Any, Dict, List

from src.ai.drift.drift_models import DriftSignal, DriftStatus, DriftSummary

_EVALUATION_TIMESTAMP = "2025-11-20T00:00:00Z"

_DEFAULT_DRIFT_INPUT: Dict[str, Any] = {
    "environment": "prod",
    "signals": [
        {
            "metric": "embedding_cosine",
            "baseline_value": 0.98,
            "current_value": 0.94,
        },
        {
            "metric": "response_latency_ms",
            "baseline_value": 180.0,
            "current_value": 240.0,
        },
        {
            "metric": "guardrail_trigger_rate",
            "baseline_value": 0.02,
            "current_value": 0.05,
        },
    ],
}

_HIGH_RECOMMENDATIONS = {
    "response_latency_ms": "scale inference capacity to reduce latency drift",
    "guardrail_trigger_rate": "audit guardrail configurations for trigger anomalies",
    "embedding_cosine": "refresh embedding training dataset",
}


def evaluate_drift(payload: Dict[str, Any]) -> DriftSummary:
    """Build a deterministic drift summary from the provided payload."""

    signals = [_build_signal(entry) for entry in payload["signals"]]
    status = DriftStatus(
        environment=payload["environment"],
        state=_overall_state(signals),
        last_evaluated_ts=_EVALUATION_TIMESTAMP,
        ready=_is_ready(signals),
    )
    recommendations = _build_recommendations(signals)
    return DriftSummary(status=status, signals=signals, recommendations=recommendations)


def get_default_drift_summary() -> DriftSummary:
    """Return the canonical drift summary used by the API layer."""

    return evaluate_drift(_DEFAULT_DRIFT_INPUT)


def _build_signal(entry: Dict[str, Any]) -> DriftSignal:
    baseline = float(entry["baseline_value"])
    current = float(entry["current_value"])
    deviation_pct = _calculate_deviation_pct(baseline, current)
    severity = _severity_label(deviation_pct)
    return DriftSignal(
        metric=entry["metric"],
        baseline_value=round(baseline, 2),
        current_value=round(current, 2),
        deviation_pct=deviation_pct,
        severity=severity,
    )


def _calculate_deviation_pct(baseline: float, current: float) -> float:
    if baseline == 0:
        return 0.0
    deviation = ((current - baseline) / baseline) * 100
    return round(deviation, 2)


def _severity_label(deviation_pct: float) -> str:
    magnitude = abs(deviation_pct)
    if magnitude >= 20:
        return "high"
    if magnitude >= 8:
        return "medium"
    return "low"


def _overall_state(signals: List[DriftSignal]) -> str:
    if any(signal.severity == "high" for signal in signals):
        return "critical"
    if any(signal.severity == "medium" for signal in signals):
        return "attention"
    return "normal"


def _is_ready(signals: List[DriftSignal]) -> bool:
    return not any(signal.severity == "high" for signal in signals)


def _build_recommendations(signals: List[DriftSignal]) -> List[str]:
    notes: List[str] = []
    for signal in signals:
        if signal.severity == "high":
            notes.append(
                _HIGH_RECOMMENDATIONS.get(
                    signal.metric, f"investigate {signal.metric} drift anomaly"
                )
            )
        elif signal.severity == "medium":
            notes.append(f"monitor {signal.metric} for sustained deviation")
    if not notes:
        notes.append("maintain baseline monitoring cadence")
    return notes


__all__ = ["evaluate_drift", "get_default_drift_summary"]
