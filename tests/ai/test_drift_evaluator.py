import json
from pathlib import Path

from src.ai.drift.drift_evaluator import evaluate_drift, get_default_drift_summary
from src.ai.drift.drift_models import DriftSummary

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def test_evaluate_drift_matches_expected_fixture():
    payload = _load_fixture("drift_input.json")
    expected = _load_fixture("drift_expected.json")

    summary = evaluate_drift(payload)

    assert isinstance(summary, DriftSummary)
    assert summary.model_dump() == expected


def test_default_drift_summary_is_deterministic():
    expected = _load_fixture("drift_expected.json")

    first = get_default_drift_summary()
    second = get_default_drift_summary()

    assert first is not second
    assert first.model_dump() == second.model_dump() == expected
