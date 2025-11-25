"""Artifact garbage collection for drift automation outputs."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Iterable, Sequence, Set

logger = logging.getLogger("drift_remediation")
logging.basicConfig(level=logging.INFO)

RETAIN_COUNT = 10
DRIFT_RELATIVE = Path("artifacts") / "drift"
REMEDIATION_RELATIVE = Path("artifacts") / "drift_remediation"
SUMMARY_RELATIVE = Path("artifacts") / "drift_summary"
PROTECTED_TOKENS = {"latest", "current", "recent", ".keep"}


def _in_ci() -> bool:
    return (os.environ.get("GITHUB_ACTIONS") or "").lower() == "true"


def _log_protected(path: Path) -> None:
    if not _in_ci():
        print("[gc] protected:", path)


def _matches_protected_token(path: Path) -> bool:
    name = path.name.lower()
    return any(token in name for token in PROTECTED_TOKENS)


def _skip_due_to_token(path: Path) -> bool:
    if _matches_protected_token(path):
        _log_protected(path)
        return True
    return False


def _repo_root(path_arg: str | None) -> Path:
    if path_arg:
        return Path(path_arg).resolve()
    return Path(__file__).resolve().parents[2]


def _collect_stack_dirs(root: Path) -> Sequence[Path]:
    if not root.exists():
        return []
    return sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p: p.name)


def _sort_files(paths: Iterable[Path]) -> list[Path]:
    def key(path: Path) -> tuple[float, str]:
        try:
            return (path.stat().st_mtime, path.name)
        except FileNotFoundError:
            return (0.0, path.name)

    files = [p for p in paths if p.is_file()]
    return sorted(files, key=key, reverse=True)


def _delete_path(path: Path) -> None:
    if _skip_due_to_token(path):
        return
    try:
        path.unlink()
        logger.warning("Artifact GC removed %s", path)
    except FileNotFoundError:
        return


def _extract_diff_refs(json_path: Path) -> Set[Path]:
    refs: Set[Path] = set()
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:  # pragma: no cover - defensive
        logger.warning(
            "Artifact GC could not parse %s; skipping diff protection", json_path
        )
        return refs
    for entry in payload.get("diff_artifacts", []) or []:
        try:
            candidate = Path(entry)
        except TypeError:
            continue
        if not candidate.is_absolute():
            candidate = (json_path.parent / candidate).resolve()
        else:
            candidate = candidate.resolve()
        refs.add(candidate)
    return refs


def _gc_drift_stack(stack_dir: Path, retention: int) -> None:
    json_files = _sort_files(stack_dir.glob("*.json"))
    keep_json = set(json_files[:retention])
    protected_diffs: Set[Path] = set()
    for json_path in keep_json:
        protected_diffs.update(_extract_diff_refs(json_path))
    for old_json in json_files[retention:]:
        if _skip_due_to_token(old_json):
            continue
        _delete_path(old_json)

    diff_files = _sort_files(stack_dir.glob("*.diff"))
    latest_diff = diff_files[0] if diff_files else None
    for diff_path in diff_files:
        if diff_path == latest_diff:
            _log_protected(diff_path)
            continue
        if _skip_due_to_token(diff_path):
            continue
        resolved = diff_path.resolve()
        if resolved in protected_diffs:
            _log_protected(diff_path)
            continue
        # If diff belongs to a kept JSON via relative path, its resolved path will match.
        _delete_path(diff_path)


def _gc_simple_stack(root: Path, retention: int, pattern: str) -> None:
    for stack_dir in _collect_stack_dirs(root):
        files = _sort_files(stack_dir.glob(pattern))
        for old_file in files[retention:]:
            _delete_path(old_file)


def _gc_drift_dir(root: Path, retention: int) -> None:
    for stack_dir in _collect_stack_dirs(root):
        _gc_drift_stack(stack_dir, retention)


def _gc_summary_dir(summary_dir: Path, retention: int) -> None:
    if not summary_dir.exists():
        return
    protected_names = {"latest.json", "latest.md"}
    for pattern in ("*.json", "*.md"):
        ordered = _sort_files(summary_dir.glob(pattern))
        files = []
        for path in ordered:
            if path.name in protected_names:
                _log_protected(path)
                continue
            files.append(path)
        latest = files[:1]
        for latest_path in latest:
            _log_protected(latest_path)
        for old_file in files[retention:]:
            if old_file in latest:
                continue
            if _skip_due_to_token(old_file):
                continue
            _delete_path(old_file)


def run_gc(repo_root: Path | None = None, retention: int = RETAIN_COUNT) -> None:
    retention = max(1, retention)
    root = repo_root or _repo_root(None)
    _gc_drift_dir(root / DRIFT_RELATIVE, retention)
    _gc_simple_stack(root / REMEDIATION_RELATIVE, retention, "*.json")
    _gc_summary_dir(root / SUMMARY_RELATIVE, retention)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Prune drift artifacts to keep the most recent per-stack outputs.\n"
            "Never touches drift_baselines/."
        )
    )
    parser.add_argument("--repo-root", type=str, default=None)
    parser.add_argument("--retention", type=int, default=RETAIN_COUNT)
    args = parser.parse_args(list(argv) if argv is not None else None)
    run_gc(repo_root=_repo_root(args.repo_root), retention=args.retention)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
