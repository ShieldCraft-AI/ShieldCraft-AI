#!/usr/bin/env python
"""Migrate legacy tests/orchestration/* service-style tests into
tests/infra/domains/orchestration with updated imports.

Also removes empty duplicate top-level test_cloudformation_service.py.
"""
from __future__ import annotations
import shutil
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY_DIR = ROOT / "tests" / "orchestration"
TARGET_DIR = ROOT / "tests" / "infra" / "domains" / "orchestration"
TOP_LEVEL_DUP = ROOT / "tests" / "test_cloudformation_service.py"

IMPORT_MAP = {
    "from infra.stacks.orchestration.controltower_service import ControlTowerService": "from infra.domains.orchestration.control_tower_stack import ControlTowerService",
    "from infra.stacks.orchestration.cloudformation_service import CloudFormationService": "from infra.domains.orchestration.cloudformation_orchestrator_stack import CloudFormationService",
    "from infra.stacks.orchestration.stepfunctions_service import StepFunctionsStack": "from infra.domains.orchestration.stepfunctions_stack import StepFunctionsStack",
}

SERVICE_SUFFIX_PATTERN = re.compile(r"(test_.*)_service(\.py)$")


def transform_filename(path: Path) -> Path:
    m = SERVICE_SUFFIX_PATTERN.match(path.name)
    if m:
        return path.with_name(m.group(1) + "_stack" + m.group(2))
    return path


def rewrite_imports(text: str) -> str:
    for old, new in IMPORT_MAP.items():
        text = text.replace(old, new)
    return text


def migrate():
    if not LEGACY_DIR.exists():
        print("Legacy orchestration directory not present.")
        return
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for py in LEGACY_DIR.glob("test_*.py"):
        content = py.read_text(encoding="utf-8")
        content = rewrite_imports(content)
        new_path = TARGET_DIR / transform_filename(py).name.replace(
            "controltower_", "control_tower_"
        )
        new_path.write_text(content, encoding="utf-8")
        py.unlink()
        print(f"MOVED {py} -> {new_path}")
    # Remove legacy dir if empty
    try:
        LEGACY_DIR.rmdir()
        print(f"Removed empty directory {LEGACY_DIR}")
    except OSError:
        pass
    if (
        TOP_LEVEL_DUP.exists()
        and TOP_LEVEL_DUP.read_text(encoding="utf-8").strip() == ""
    ):
        TOP_LEVEL_DUP.unlink()
        print(f"Removed empty duplicate {TOP_LEVEL_DUP}")


if __name__ == "__main__":  # pragma: no cover
    migrate()
