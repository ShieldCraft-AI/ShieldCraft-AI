"""Run drift checks and produce non-destructive diff artifacts.

Conservative, dry-run first implementation:
- Uses existing CloudFormationService.detect_drift() for detection.
- Runs `cdk diff <stack>` to produce an IaC diff artifact.
- Writes artifacts to `artifacts/drift/` by default.
- Does NOT apply any changes. Optionally posts a summary to stdout or (if enabled)
  creates a GitHub issue when GITHUB_TOKEN is present in Secrets Manager or env.

This script is safe to run locally with --dry-run and is intended to be wired into
CI (CodeBuild) or scheduled (EventBridge) later.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Iterable, Optional

try:
    # Project imports (assumes repo root in PYTHONPATH)
    from infra.domains.orchestration.cloudformation_orchestrator_stack import (
        CloudFormationService,
    )
    from infra.utils.config_loader import get_config_loader
except Exception:  # pragma: no cover - import errors handled in tests via monkeypatch
    CloudFormationService = None  # type: ignore
    get_config_loader = None  # type: ignore

logger = logging.getLogger("drift_remediation")
logging.basicConfig(level=logging.INFO)


def _now_ts() -> str:
    return datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def run_cdk_diff(stack: str, repo_root: Path) -> str:
    """Run `cdk diff` for a stack and return stdout (diff)."""
    cmd = ["poetry", "run", "cdk", "diff", stack, "--no-color"]
    logger.info("Running CDK diff for %s: %s", stack, " ".join(cmd))
    proc = subprocess.run(
        cmd,
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return proc.stdout or ""


def write_artifact(stack: str, diff_text: str, artifacts_dir: Path) -> Path:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{stack}-{_now_ts()}.diff"
    path = artifacts_dir / fname
    path.write_text(diff_text, encoding="utf-8")
    logger.info("Wrote diff artifact: %s", path)
    return path


def run_check(
    stacks: Iterable[str],
    repo_root: Path,
    artifacts_dir: Path,
    dry_run: bool = True,
    post: bool = False,
    config_loader=None,
):
    """Run detection + diff for each stack.

    Args:
        stacks: iterable of stack names to check (e.g., ['NetworkingStack']).
        repo_root: repository root Path where `cdk` commands should run.
        artifacts_dir: directory to write artifacts to.
        dry_run: if True, do not attempt any writes beyond artifact creation.
        post: if True and credentials available, attempt to create a GitHub Issue (best-effort).
        config_loader: optional injected config loader for tests.
    """
    # Resolve config
    cfg = None
    env = "dev"
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    if config_loader:
        try:
            exported = (
                config_loader.export() if hasattr(config_loader, "export") else {}
            )
            cfg = exported
            env = exported.get("app", {}).get("env", env)
            region = exported.get("app", {}).get("region", region)
        except Exception:
            logger.warning(
                "Provided config_loader failed to export; continuing with defaults"
            )
    else:
        if get_config_loader is not None:
            try:
                cfg = get_config_loader().export()
                env = cfg.get("app", {}).get("env", env)
                region = cfg.get("app", {}).get("region", region)
            except Exception:
                logger.warning(
                    "Could not load config via get_config_loader(); using defaults"
                )

    # Instantiate CloudFormationService if available
    if CloudFormationService is None:
        logger.error("CloudFormationService not available (imports failed). Aborting.")
        return 1

    cf = CloudFormationService(region_name=region, environment=env)

    results = []
    for stack in stacks:
        logger.info("Checking stack: %s", stack)
        try:
            detect_resp = cf.detect_drift(stack)
            logger.info("Detect drift response: %s", json.dumps(detect_resp))
        except Exception as e:  # pragma: no cover - exercised via mocks in tests
            logger.exception("Drift detection failed for %s: %s", stack, e)
            results.append({"stack": stack, "error": str(e)})
            continue

        diff = run_cdk_diff(stack, repo_root)
        if diff and diff.strip():
            artifact_path = write_artifact(stack, diff, artifacts_dir)
            results.append(
                {"stack": stack, "drift": True, "artifact": str(artifact_path)}
            )
            # Optionally post: best-effort, requires credentials
            if post:
                logger.info(
                    "Post requested but posting is not implemented in dry-run scaffold. Skipping."
                )
        else:
            logger.info("No diff detected for %s", stack)
            results.append({"stack": stack, "drift": False})

    # Summary
    logger.info("Drift check summary: %s", json.dumps(results, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run drift checks and produce diff artifacts (dry-run)"
    )
    p.add_argument(
        "--stacks",
        type=str,
        default="",
        help="Comma-separated list of stack logical names to check (e.g. NetworkingStack,S3Stack). If empty, caller should supply stacks via config.",
    )
    p.add_argument("--artifacts-dir", type=str, default="artifacts/drift")
    p.add_argument("--dry-run", action="store_true", default=True)
    p.add_argument(
        "--post",
        action="store_true",
        help="Attempt to post a GitHub issue if token available (optional).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    artifacts_dir = Path(args.artifacts_dir)
    stacks = [s.strip() for s in args.stacks.split(",") if s.strip()]
    if not stacks:
        # Best-effort: load from config 'infra' section if present
        try:
            cfg = get_config_loader().export() if get_config_loader else {}
            stacks = list(cfg.get("stacks", {}).keys()) if cfg else []
        except Exception:
            stacks = []
    if not stacks:
        logger.error(
            "No stacks specified and none found in config. Provide --stacks or add to config."
        )
        return 2
    return run_check(
        stacks, repo_root, artifacts_dir, dry_run=args.dry_run, post=args.post
    )


if __name__ == "__main__":
    raise SystemExit(main())
