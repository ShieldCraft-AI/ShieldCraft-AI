import json
from pathlib import Path

import pytest

from scripts.drift_remediation import baseline_utils, comparator
from scripts.drift_remediation import summary as summary_utils


def _set_baseline_root(tmp_path, monkeypatch):
    root = tmp_path / "baselines"
    monkeypatch.setattr(baseline_utils, "BASELINE_ROOT", root)
    baseline_utils.ensure_baseline_dir()
    return root


class _FixedDateTime(baseline_utils._dt.datetime):
    @classmethod
    def utcnow(cls):  # pragma: no cover - shim for deterministic timestamp
        return cls(2024, 1, 1, 12, 0, 0)


def test_baseline_write_and_load_round_trip(tmp_path, monkeypatch):
    _set_baseline_root(tmp_path, monkeypatch)
    data = baseline_utils.BaselineData(
        stack="StackA",
        last_known_hash="sha256:abc",
        last_acknowledged_timestamp="2024-01-01T00:00:00Z",
        comment="init",
        allowlist=["ResA"],
    )
    baseline_utils.write_baseline("StackA", data)

    loaded = baseline_utils.load_baseline("StackA")
    assert loaded == data


def test_baseline_missing_and_hashing(tmp_path, monkeypatch):
    _set_baseline_root(tmp_path, monkeypatch)
    with pytest.raises(baseline_utils.BaselineMissingError):
        baseline_utils.load_baseline("Unknown")

    digest_a = baseline_utils.hash_diff_text("diff-text")
    digest_b = baseline_utils.hash_diff_text("diff-text")
    digest_c = baseline_utils.hash_diff_text("other")
    assert digest_a == digest_b
    assert digest_a != digest_c


def test_acknowledge_drift_updates_file(tmp_path, monkeypatch):
    _set_baseline_root(tmp_path, monkeypatch)
    monkeypatch.setattr(baseline_utils._dt, "datetime", _FixedDateTime)
    diff_hash = baseline_utils.hash_diff_text("sample")

    baseline_utils.acknowledge_drift(
        stack="StackB",
        diff_hash=diff_hash,
        comment="approved",
        allowlist=["ResX"],
    )

    payload = baseline_utils.load_baseline("StackB")
    assert payload.last_known_hash == diff_hash
    assert payload.comment == "approved"
    assert payload.allowlist == ["ResX"]
    assert payload.last_acknowledged_timestamp.endswith("Z")


def test_comparator_paths_cover_all_statuses():
    baseline = {"last_known_hash": "sha256:abc", "allowlist": ["Res1"]}

    result = comparator.compare("", baseline)
    assert result.status == comparator.DriftStatus.NO_DRIFT

    result = comparator.compare("sha256:xyz", None)
    assert result.status == comparator.DriftStatus.BASELINE_MISSING

    result = comparator.compare("sha256:abc", baseline)
    assert result.status == comparator.DriftStatus.ACKNOWLEDGED

    summary = [{"logical_id": "Res1", "status": "MODIFIED"}]
    result = comparator.compare("sha256:new", baseline, summary)
    assert result.status == comparator.DriftStatus.ACKNOWLEDGED

    result = comparator.compare("sha256:new", {"last_known_hash": "sha256:abc"})
    assert result.status == comparator.DriftStatus.NEW_DRIFT


def test_summary_build_and_render(tmp_path):
    artifacts_dir = tmp_path / "artifacts"
    stack_a_dir = artifacts_dir / "StackA"
    stack_a_dir.mkdir(parents=True, exist_ok=True)
    stack_b_dir = artifacts_dir / "StackB"
    stack_b_dir.mkdir(parents=True, exist_ok=True)

    payload_a = {
        "stack": "StackA",
        "comparison_status": "acknowledged",
        "drifted": False,
        "timestamp": "2024-01-01T00:00:00Z",
        "comparison_reason": "baseline match",
    }
    payload_b = {
        "stack": "StackB",
        "comparison_status": "new_drift",
        "drifted": True,
        "timestamp": "2024-01-02T00:00:00Z",
        "comparison_reason": "hash mismatch",
    }
    (stack_a_dir / "a.json").write_text(json.dumps(payload_a), encoding="utf-8")
    (stack_b_dir / "b.json").write_text(json.dumps(payload_b), encoding="utf-8")

    summary = summary_utils.build_summary(artifacts_dir)
    assert summary["artifact_count"] == 2
    assert "generated_at" in summary
    stacks = {item["stack"]: item for item in summary["stacks"]}
    assert stacks["StackA"]["comparison_status"] == "acknowledged"
    assert stacks["StackB"]["comparison_status"] == "new_drift"
    assert summary["new_drift"] == ["StackB"]

    destination = tmp_path / "summary.json"
    summary_utils.write_summary(summary, destination)
    written = json.loads(destination.read_text())
    assert written["artifact_count"] == 2

    markdown = summary_utils.render_markdown(summary)
    assert "| StackA | acknowledged" in markdown
    assert "| StackB | new_drift" in markdown
