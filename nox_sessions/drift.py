"""Nox sessions for ShieldCraft drift detection and acknowledgment workflows."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import List, Tuple

import nox

from .bootstrap import PYTHON_VERSIONS
from nox_sessions.utils import nox_session_guard, now_str

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.drift_remediation import baseline_utils  # noqa: E402
from scripts.drift_remediation import summary as summary_utils  # noqa: E402

DRIFT_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "drift"
DRIFT_REMEDIATION_DIR = REPO_ROOT / "artifacts" / "drift_remediation"
SUMMARY_DIR = DRIFT_ARTIFACTS_DIR.parent / "drift_summary"
VALIDATE_ENV_CMD = ["python", "scripts/drift_remediation/validate_env.py"]
SKIP_VALIDATE_WARN = (
    "[WARN] validate_env skipped via --skip-validate; local debugging only"
)
SKIP_VALIDATE_CI_ERROR = "--skip-validate forbidden in CI (GitHub Actions)"


def _parse_drift_check_args(posargs: list[str]) -> tuple[list[str], Path, bool]:
    stacks: list[str] = []
    artifacts_dir = DRIFT_ARTIFACTS_DIR
    post_issue = False
    iterator = iter(posargs)
    for arg in iterator:
        if arg == "--post":
            post_issue = True
            continue
        if arg == "--artifacts-dir":
            try:
                artifacts_dir = Path(next(iterator))
            except StopIteration as exc:  # pragma: no cover - defensive
                raise RuntimeError("--artifacts-dir flag requires a value") from exc
            continue
        if arg.startswith("--artifacts-dir="):
            artifacts_dir = Path(arg.split("=", 1)[1])
            continue
        stacks.append(arg)
    return stacks, artifacts_dir, post_issue


def _latest_diff(stack: str, artifacts_dir: Path) -> Path:
    stack_dir = artifacts_dir / stack
    diff_files = sorted(stack_dir.glob("*.diff"))
    if not diff_files:
        raise FileNotFoundError(
            f"No diff artifacts found for stack {stack} under {stack_dir}"
        )
    return diff_files[-1]


def _extract_guard_flags(
    posargs: List[str], *, keep_json_in_filtered: bool = False
) -> Tuple[List[str], List[str], bool]:
    filtered: List[str] = []
    validate_flags: List[str] = []
    skip_validate = False
    for arg in posargs:
        if arg == "--skip-validate":
            skip_validate = True
            continue
        if arg == "--json":
            validate_flags.append("--json")
            if keep_json_in_filtered:
                filtered.append(arg)
            continue
        filtered.append(arg)
    return filtered, validate_flags, skip_validate


def _in_ci() -> bool:
    return str(os.environ.get("GITHUB_ACTIONS", "")).lower() == "true"


def _assert_not_in_ci(skip_validate: bool) -> None:
    if skip_validate and _in_ci():
        raise RuntimeError(SKIP_VALIDATE_CI_ERROR)


def _run_validate_env(session, extra_args: List[str] | None = None) -> None:
    """Ensure validate_env.py succeeds before proceeding."""

    cmd = list(VALIDATE_ENV_CMD)
    if extra_args:
        cmd.extend(extra_args)
    session.run(*cmd, external=True)


def _maybe_run_validate_env(
    session, validate_flags: List[str], skip_validate: bool
) -> None:
    _assert_not_in_ci(skip_validate)
    if skip_validate:
        session.log(SKIP_VALIDATE_WARN)
        return
    _run_validate_env(session, validate_flags)


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def drift_check(session):
    """Run drift detection via run_drift_check.py."""

    base_posargs = list(session.posargs)
    cleaned_args, validate_flags, skip_validate = _extract_guard_flags(base_posargs)
    stacks, artifacts_dir, post_issue = _parse_drift_check_args(cleaned_args)
    _maybe_run_validate_env(session, validate_flags, skip_validate)
    cmd = [
        "poetry",
        "run",
        "python",
        "scripts/drift_remediation/run_drift_check.py",
        "--artifacts-dir",
        str(artifacts_dir),
        "--dry-run",
    ]
    if stacks:
        cmd.extend(["--stacks", ",".join(stacks)])
    if post_issue:
        cmd.append("--post")
    env = dict(session.env)
    env.setdefault("NO_APPLY", "1")
    env.setdefault("PYTHONPATH", str(REPO_ROOT))
    session.log("[drift_check] Running drift detection pipeline...")
    session.run(*cmd, env=env, external=True)
    summary_path = SUMMARY_DIR / "latest.json"
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        stacks = summary.get("stacks", [])
        scanned = len(stacks)
        new_drift = len(summary.get("new_drift", []))
        acknowledged = sum(
            1 for item in stacks if item.get("comparison_status") == "acknowledged"
        )
        session.log(
            f"Drift summary: {scanned} scanned / {new_drift} new / {acknowledged} acknowledged"
        )
    except FileNotFoundError:
        session.log("Drift summary: not available (no summary file)")


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def drift_acknowledge(session):
    """Acknowledge drift by updating the baseline hash for a stack."""

    base_posargs = list(session.posargs)
    cleaned_args, validate_flags, skip_validate = _extract_guard_flags(base_posargs)
    if not cleaned_args:
        raise RuntimeError(
            "Usage: nox -s drift_acknowledge -- <STACK> [diff_path] [comment] [allowlist...]"
        )
    _maybe_run_validate_env(session, validate_flags, skip_validate)
    stack = cleaned_args[0]
    diff_arg = cleaned_args[1] if len(cleaned_args) > 1 else None
    comment = (
        cleaned_args[2]
        if len(cleaned_args) > 2
        else f"Acknowledged via nox drift_acknowledge at {now_str()}"
    )
    allowlist = cleaned_args[3:] if len(cleaned_args) > 3 else []
    artifacts_dir = DRIFT_ARTIFACTS_DIR
    diff_path = Path(diff_arg) if diff_arg else _latest_diff(stack, artifacts_dir)
    diff_text = diff_path.read_text(encoding="utf-8")
    diff_hash = baseline_utils.hash_diff_text(diff_text)
    baseline_utils.acknowledge_drift(stack, diff_hash, comment, allowlist)
    session.log(
        f"[drift_acknowledge] Updated baseline for {stack} using {diff_path.name}"
    )


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def drift_report(session):
    """Generate drift summary artifacts and markdown report."""

    base_posargs = list(session.posargs)
    cleaned_args, validate_flags, skip_validate = _extract_guard_flags(base_posargs)
    _maybe_run_validate_env(session, validate_flags, skip_validate)
    artifacts_dir = Path(cleaned_args[0]) if cleaned_args else DRIFT_ARTIFACTS_DIR
    summary = summary_utils.build_summary(artifacts_dir)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = SUMMARY_DIR / "latest.json"
    summary_utils.write_summary(summary, summary_path)
    markdown_path = SUMMARY_DIR / "latest.md"
    markdown_path.write_text(summary_utils.render_markdown(summary), encoding="utf-8")
    session.log(
        f"[drift_report] Summary saved to {summary_path} and markdown to {markdown_path}"
    )


@nox_session_guard
@nox.session(name="drift", python=PYTHON_VERSIONS)
def drift(session):
    """Alias for drift_check session."""

    session.notify("drift_check", posargs=list(session.posargs))


@nox_session_guard
@nox.session(name="report", python=PYTHON_VERSIONS)
def report(session):
    """Alias for drift_report session."""

    session.notify("drift_report", posargs=list(session.posargs))


@nox_session_guard
@nox.session(name="validate_env", python=PYTHON_VERSIONS)
def validate_env_session(session):
    """Validate drift guardrails without running other tooling."""

    filtered_args, _, skip_validate = _extract_guard_flags(
        list(session.posargs), keep_json_in_filtered=True
    )
    if skip_validate:
        session.log(SKIP_VALIDATE_WARN)
        return
    _run_validate_env(session, filtered_args)
