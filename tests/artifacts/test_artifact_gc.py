import json
import os
from pathlib import Path

from scripts.drift_remediation import artifact_gc


def _make_detection_artifact(stack_dir: Path, stack: str, idx: int) -> None:
    ts = f"20240101T0001{idx:02d}Z"
    diff_path = stack_dir / f"{stack}-{ts}.diff"
    diff_path.write_text(f"diff-{idx}", encoding="utf-8")
    json_path = stack_dir / f"{stack}-{ts}.json"
    payload = {
        "stack": stack,
        "timestamp": ts,
        "diff_artifacts": [str(diff_path)],
    }
    json_path.write_text(json.dumps(payload), encoding="utf-8")
    # ensure deterministic ordering by tweaking mtimes
    os.utime(diff_path, (idx, idx))
    os.utime(json_path, (idx, idx))


def test_gc_retains_latest_detection_pairs(tmp_path):
    repo_root = tmp_path
    drift_dir = repo_root / "artifacts" / "drift" / "TestStack"
    drift_dir.mkdir(parents=True)
    for i in range(12):
        _make_detection_artifact(drift_dir, "TestStack", i)

    artifact_gc.run_gc(repo_root=repo_root, retention=5)

    remaining_json = sorted(drift_dir.glob("*.json"))
    remaining_diff = sorted(drift_dir.glob("*.diff"))
    assert len(remaining_json) == 5
    assert len(remaining_diff) == 5
    latest_suffix = "20240101T000111Z"
    assert (drift_dir / f"TestStack-{latest_suffix}.json").exists()
    assert (drift_dir / f"TestStack-{latest_suffix}.diff").exists()


def test_gc_protects_latest_diff_and_summaries(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    repo_root = tmp_path
    stack_dir = repo_root / "artifacts" / "drift" / "StackA"
    stack_dir.mkdir(parents=True)
    # Old diff with custom mtime but referenced by latest JSON
    _make_detection_artifact(stack_dir, "StackA", 0)
    latest_ts = "20240101T000150Z"
    protected_diff = stack_dir / f"StackA-{latest_ts}.diff"
    protected_diff.write_text("important", encoding="utf-8")
    json_path = stack_dir / f"StackA-{latest_ts}.json"
    json_payload = {
        "stack": "StackA",
        "timestamp": latest_ts,
        "diff_artifacts": [str(protected_diff)],
    }
    json_path.write_text(json.dumps(json_payload), encoding="utf-8")
    os.utime(protected_diff, (1, 1))
    os.utime(json_path, (2, 2))

    # Add older artifacts that should be removed
    for i in range(1, 8):
        extra_ts = f"20240101T0001{i:02d}Z"
        path = stack_dir / f"StackA-{extra_ts}.json"
        path.write_text(
            json.dumps({"stack": "StackA", "timestamp": extra_ts}), encoding="utf-8"
        )
        os.utime(path, (i + 2, i + 2))

    summary_dir = repo_root / "artifacts" / "drift_summary"
    summary_dir.mkdir(parents=True)
    for i in range(12):
        summary = summary_dir / f"summary-20240101T0002{i:02d}Z.json"
        summary.write_text("{}", encoding="utf-8")
        os.utime(summary, (i, i))
    (summary_dir / "latest.json").write_text("{}", encoding="utf-8")
    (summary_dir / "latest.md").write_text("# latest", encoding="utf-8")
    artifact_gc.run_gc(repo_root=repo_root, retention=3)

    out = capsys.readouterr().out
    assert "[gc] protected:" in out

    assert protected_diff.exists()
    assert not (stack_dir / "StackA-20240101T000101Z.json").exists()
    # Only 3 summary json files plus latest should remain
    summary_json = [p for p in summary_dir.glob("summary-*.json")]
    assert len(summary_json) == 3
    newest_summary = summary_dir / "summary-20240101T000211Z.json"
    assert newest_summary.exists()
    assert not (summary_dir / "summary-20240101T000200Z.json").exists()
    assert (summary_dir / "latest.json").exists()
    assert (summary_dir / "latest.md").exists()


def test_gc_logging_suppressed_in_ci(tmp_path, capsys, monkeypatch):
    def _seed_repo(root: Path) -> None:
        stack_dir = root / "artifacts" / "drift" / "StackB"
        stack_dir.mkdir(parents=True)
        _make_detection_artifact(stack_dir, "StackB", 0)
        latest_diff = stack_dir / "StackB-20240101T000150Z.diff"
        latest_diff.write_text("keep", encoding="utf-8")
        latest_json = stack_dir / "StackB-20240101T000150Z.json"
        latest_json.write_text(
            json.dumps({"stack": "StackB", "diff_artifacts": [str(latest_diff)]}),
            encoding="utf-8",
        )
        summary_dir = root / "artifacts" / "drift_summary"
        summary_dir.mkdir(parents=True)
        summary = summary_dir / "summary-20240101T000299Z.json"
        summary.write_text("{}", encoding="utf-8")

    local_root = tmp_path / "local"
    _seed_repo(local_root)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    artifact_gc.run_gc(repo_root=local_root, retention=1)
    assert "[gc] protected:" in capsys.readouterr().out

    ci_root = tmp_path / "ci"
    _seed_repo(ci_root)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    artifact_gc.run_gc(repo_root=ci_root, retention=1)
    assert "[gc] protected:" not in capsys.readouterr().out
