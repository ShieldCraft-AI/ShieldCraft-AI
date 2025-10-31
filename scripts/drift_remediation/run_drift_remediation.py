"""Automated drift remediation pipeline: applies safe, minimal remediations for detected drift.

- Uses CloudFormationService to detect and remediate drifted stacks.
- For each drifted stack, attempts a safe update_stack() using the current template.
- Writes remediation results to `artifacts/drift_remediation/`.
- Only applies changes if --apply is set; otherwise, dry-run only.
- Intended for CI/CD or scheduled automation, with opt-in remediation.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
from pathlib import Path
from typing import Iterable, Optional

try:
    from infra.domains.orchestration.cloudformation_orchestrator_stack import (
        CloudFormationService,
    )
    from infra.utils.config_loader import get_config_loader
except Exception:
    CloudFormationService = None  # type: ignore
    get_config_loader = None  # type: ignore

logger = logging.getLogger("drift_remediation")
logging.basicConfig(level=logging.INFO)


def _now_ts() -> str:
    return datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def write_remediation_artifact(stack: str, result: dict, artifacts_dir: Path) -> Path:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{stack}-remediation-{_now_ts()}.json"
    path = artifacts_dir / fname
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info("Wrote remediation artifact: %s", path)
    return path


def remediate_drift(
    stacks: Iterable[str],
    repo_root: Path,
    artifacts_dir: Path,
    apply: bool = False,
    config_loader=None,
):
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

    if CloudFormationService is None:
        logger.error("CloudFormationService not available (imports failed). Aborting.")
        return 1

    cf = CloudFormationService(region_name=region, environment=env)
    results = []
    for stack in stacks:
        logger.info("Remediation check for stack: %s", stack)
        try:
            drift_resp = cf.detect_drift(stack)
            drift_status = drift_resp.get("StackDriftDetectionStatus", "UNKNOWN")
            if drift_status != "DETECTION_COMPLETE":
                logger.info("Drift detection not complete for %s, skipping.", stack)
                results.append(
                    {
                        "stack": stack,
                        "remediated": False,
                        "reason": "Detection incomplete",
                    }
                )
                continue
            # If drift detected, attempt remediation
            if drift_resp.get("StackDriftStatus") == "DRIFTED":
                if apply:
                    # Attempt update_stack with current template
                    try:
                        # For demo: assume template_url is available in config
                        template_url = (
                            cfg.get("stacks", {}).get(stack, {}).get("template_url")
                        )
                        parameters = (
                            cfg.get("stacks", {}).get(stack, {}).get("parameters")
                        )
                        capabilities = (
                            cfg.get("stacks", {}).get(stack, {}).get("capabilities")
                        )
                        update_resp = cf.update_stack(
                            stack, template_url, parameters, capabilities
                        )
                        logger.info(
                            "Remediation applied for %s: %s", stack, update_resp
                        )
                        results.append(
                            {
                                "stack": stack,
                                "remediated": True,
                                "update_response": update_resp,
                            }
                        )
                    except Exception as e:
                        logger.exception("Remediation failed for %s: %s", stack, e)
                        results.append(
                            {"stack": stack, "remediated": False, "error": str(e)}
                        )
                else:
                    logger.info(
                        "Drift detected for %s, but --apply not set. Dry-run only.",
                        stack,
                    )
                    results.append(
                        {
                            "stack": stack,
                            "remediated": False,
                            "reason": "Drift detected, dry-run only",
                        }
                    )
            else:
                logger.info("No drift detected for %s", stack)
                results.append(
                    {"stack": stack, "remediated": False, "reason": "No drift"}
                )
        except Exception as e:
            logger.exception("Drift remediation failed for %s: %s", stack, e)
            results.append({"stack": stack, "remediated": False, "error": str(e)})
        write_remediation_artifact(stack, results[-1], artifacts_dir)
    logger.info("Remediation summary: %s", json.dumps(results, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Automated drift remediation pipeline")
    p.add_argument(
        "--stacks",
        type=str,
        default="",
        help="Comma-separated list of stack logical names to remediate (e.g. NetworkingStack,S3Stack). If empty, will use config.",
    )
    p.add_argument("--artifacts-dir", type=str, default="artifacts/drift_remediation")
    p.add_argument(
        "--apply",
        action="store_true",
        help="Actually apply remediations (default: dry-run)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    artifacts_dir = Path(args.artifacts_dir)
    stacks = [s.strip() for s in args.stacks.split(",") if s.strip()]
    if not stacks:
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
    return remediate_drift(stacks, repo_root, artifacts_dir, apply=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
