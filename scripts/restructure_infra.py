#!/usr/bin/env python
"""Infra restructuring utility.

Dry-run by default. Use --commit to apply.

Moves existing *service.py style stack files into a domain-oriented layout and
optionally rewrites class names from FooService to FooStack.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
INFRA = ROOT / "infra"
STACKS = INFRA / "stacks"


@dataclass
class MoveSpec:
    source: Path
    target: Path
    rewrite_class: bool = True

    def needed(self) -> bool:
        return self.source.exists() and not self.target.exists()


def build_specs() -> List[MoveSpec]:
    m: List[MoveSpec] = []
    a = m.append
    # Foundation
    a(
        MoveSpec(
            STACKS / "networking" / "networking.py",
            INFRA / "domains/foundation/networking/networking_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "iam" / "iam_role_service.py",
            INFRA / "domains/foundation/identity_security/iam_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "security" / "secrets_manager_service.py",
            INFRA / "domains/foundation/identity_security/secrets_manager_stack.py",
        )
    )
    # Data Platform
    a(
        MoveSpec(
            STACKS / "storage" / "s3_service.py",
            INFRA / "domains/data_platform/storage/s3_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "storage" / "lakeformation_service.py",
            INFRA / "domains/data_platform/storage/lakeformation_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "data" / "glue_service.py",
            INFRA / "domains/data_platform/catalog_etl/glue_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "data" / "dataquality_service.py",
            INFRA / "domains/data_platform/catalog_etl/data_quality_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "data" / "airbyte_service.py",
            INFRA / "domains/data_platform/ingestion_streaming/airbyte_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "compute" / "msk_service.py",
            INFRA / "domains/data_platform/ingestion_streaming/msk_stack.py",
        )
    )
    # Analytics / ML / Serverless
    a(
        MoveSpec(
            STACKS / "compute" / "opensearch_service.py",
            INFRA / "domains/analytics_search/opensearch_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "compute" / "sagemaker_service.py",
            INFRA / "domains/ml/sagemaker_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "compute" / "lambda_service.py",
            INFRA / "domains/serverless_compute/lambda_stack.py",
        )
    )
    # Orchestration
    a(
        MoveSpec(
            STACKS / "orchestration" / "eventbridge_service.py",
            INFRA / "domains/orchestration/eventbridge_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "orchestration" / "stepfunctions_service.py",
            INFRA / "domains/orchestration/stepfunctions_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "orchestration" / "cloudformation_service.py",
            INFRA / "domains/orchestration/cloudformation_orchestrator_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "orchestration" / "controltower_service.py",
            INFRA / "domains/orchestration/control_tower_stack.py",
        )
    )
    # Security & Compliance
    a(
        MoveSpec(
            STACKS / "cloud_native" / "cloud_native_hardening_service.py",
            INFRA / "domains/security_compliance/cloud_native_hardening_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "cloud_native" / "attack_simulation_service.py",
            INFRA / "domains/security_compliance/attack_simulation_stack.py",
        )
    )
    a(
        MoveSpec(
            STACKS / "compliance_service.py",
            INFRA / "domains/security_compliance/compliance_stack.py",
        )
    )
    # FinOps
    a(
        MoveSpec(
            STACKS / "cost" / "budget_service.py",
            INFRA / "domains/finops/budget_stack.py",
        )
    )
    return m


def rewrite_service_to_stack(text: str) -> str:
    return re.sub(
        r"class (\w+)Service(\s*\()",
        lambda m: f"class {m.group(1)}Stack{m.group(2)}",
        text,
    )


def move_one(spec: MoveSpec, commit: bool, rewrite: bool) -> str:
    if not spec.source.exists():
        return f"MISSING {spec.source}"
    if spec.target.exists():
        return f"EXISTS  {spec.target}"
    if not commit:
        return f"PLAN    {spec.source} -> {spec.target}"
    spec.target.parent.mkdir(parents=True, exist_ok=True)
    content = spec.source.read_text(encoding="utf-8")
    if rewrite and spec.rewrite_class:
        content = rewrite_service_to_stack(content)
    spec.target.write_text(content, encoding="utf-8")
    spec.source.unlink()
    return f"MOVED   {spec.source} -> {spec.target}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Restructure infra stacks")
    ap.add_argument(
        "--commit", action="store_true", help="Apply moves (default dry-run)"
    )
    ap.add_argument(
        "--rewrite-classes",
        action="store_true",
        help="Rename *Service classes to *Stack",
    )
    args = ap.parse_args()

    specs = build_specs()
    for s in specs:
        print(move_one(s, args.commit, args.rewrite_classes))

    dup = INFRA / "controltower_service.py"
    if dup.exists():
        print(f"NOTE duplicate root file present: {dup}")
    if not args.commit:
        print("\nDry-run only. Re-run with --commit to apply.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
