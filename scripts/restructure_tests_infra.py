#!/usr/bin/env python
"""Restructure infra tests to mirror new domain-oriented stack layout.

Dry-run by default. Use --commit to apply moves.

1. Moves tests/infra/test_*_service.py into tests/infra/domains/<domain>/... folders
   matching the production stack locations created by restructure_infra.py.
2. Optionally renames files replacing _service with _stack.
3. Rewrites import statements from infra.stacks.* to infra.domains.* per mapping.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
TEST_ROOT = ROOT / "tests" / "infra"

# Mapping of old stack module (relative after infra.stacks.) to new domain path (after infra.domains.)
STACK_PATH_MAP = {
    "networking.networking": "foundation.networking.networking_stack",
    "iam.iam_role_service": "foundation.identity_security.iam_stack",
    "security.secrets_manager_service": "foundation.identity_security.secrets_manager_stack",
    "storage.s3_service": "data_platform.storage.s3_stack",
    "storage.lakeformation_service": "data_platform.storage.lakeformation_stack",
    "data.glue_service": "data_platform.catalog_etl.glue_stack",
    "data.dataquality_service": "data_platform.catalog_etl.data_quality_stack",
    "data.airbyte_service": "data_platform.ingestion_streaming.airbyte_stack",
    "compute.msk_service": "data_platform.ingestion_streaming.msk_stack",
    "compute.opensearch_service": "analytics_search.opensearch_stack",
    "compute.sagemaker_service": "ml.sagemaker_stack",
    "compute.lambda_service": "serverless_compute.lambda_stack",
    "orchestration.eventbridge_service": "orchestration.eventbridge_stack",
    "orchestration.stepfunctions_service": "orchestration.stepfunctions_stack",
    "orchestration.cloudformation_service": "orchestration.cloudformation_orchestrator_stack",
    "orchestration.controltower_service": "orchestration.control_tower_stack",
    "cloud_native.cloud_native_hardening_service": "security_compliance.cloud_native_hardening_stack",
    "cloud_native.attack_simulation_service": "security_compliance.attack_simulation_stack",
    "compliance_service": "security_compliance.compliance_stack",
    "cost.budget_service": "finops.budget_stack",
}

# Domain root mapping derived from new paths (first two components form domain root except foundation which may have two-level identity)


def target_path_for(old_module: str) -> Path:
    new_mod = STACK_PATH_MAP[old_module]
    parts = new_mod.split(".")
    # Build directory under tests/infra/domains/<domain path excluding final module>
    dir_parts = ["domains"] + parts[:-1]
    return TEST_ROOT / Path("/".join(dir_parts))


@dataclass
class TestMove:
    source: Path
    target: Path

    def action(self) -> str:
        return f"{self.source} -> {self.target}"


def discover_moves(rename: bool) -> List[TestMove]:
    moves: List[TestMove] = []
    for pattern_old, mapped in STACK_PATH_MAP.items():
        # Derive test file name pattern based on last segment before _service
        last = pattern_old.split(".")[-1]
        # Build typical test filename variants
        candidates = [
            TEST_ROOT / f"test_{last}.py",
            TEST_ROOT / f"test_{last}_service.py",
            TEST_ROOT / f"test_{last.replace('_service','')}_service.py",
        ]
        for src in candidates:
            if src.exists():
                new_dir = target_path_for(pattern_old)
                base_name = src.name
                if rename:
                    base_name = base_name.replace("_service", "_stack").replace(
                        last, mapped.split(".")[-1]
                    )
                dest = new_dir / base_name
                moves.append(TestMove(src, dest))
                break
    return moves


IMPORT_PATTERN = re.compile(r"from\s+infra\.stacks\.(.+?)\s+import\s+")


def rewrite_imports(text: str) -> str:
    def repl(match):
        old_mod = match.group(1)
        # find best key in STACK_PATH_MAP that is prefix of old_mod
        key = None
        for k in sorted(STACK_PATH_MAP.keys(), key=len, reverse=True):
            if old_mod.startswith(k):
                key = k
                break
        if not key:
            return match.group(0)
        new_mod = STACK_PATH_MAP[key] + old_mod[len(key) :]
        return match.group(0).replace(
            f"infra.stacks.{old_mod}", f"infra.domains.{new_mod}"
        )

    return IMPORT_PATTERN.sub(repl, text)


def process_file(src: Path, dest: Path, commit: bool, rewrite: bool) -> str:
    if not src.exists():
        return f"MISSING {src}"
    if not commit:
        return f"PLAN {src} -> {dest}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = src.read_text(encoding="utf-8")
    if rewrite:
        content = rewrite_imports(content)
    dest.write_text(content, encoding="utf-8")
    # Remove original after writing
    src.unlink()
    return f"MOVED {src} -> {dest}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Restructure infra tests to domain layout")
    ap.add_argument(
        "--commit", action="store_true", help="Apply moves (default dry-run)"
    )
    ap.add_argument(
        "--rename-files",
        action="store_true",
        help="Rename *_service test files to *_stack & new module name",
    )
    ap.add_argument(
        "--rewrite-imports",
        action="store_true",
        help="Rewrite infra.stacks.* imports to infra.domains.*",
    )
    args = ap.parse_args()

    moves = discover_moves(rename=args.rename_files)
    if not moves:
        print("No test files discovered to move.")
        return 0
    for mv in moves:
        print(process_file(mv.source, mv.target, args.commit, args.rewrite_imports))
    if not args.commit:
        print("\nDry-run complete. Re-run with --commit to apply.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
