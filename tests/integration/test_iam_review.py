from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IAM_SCRIPT_DIR = PROJECT_ROOT / "scripts" / "iam"
if str(IAM_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(IAM_SCRIPT_DIR))

from iam_review import evaluate_roles  # type: ignore  # noqa: E402
from iam_report import generate_reports  # type: ignore  # noqa: E402


@pytest.fixture(scope="module")
def review_document():
    return evaluate_roles()


def test_evaluate_roles_orders_and_scores(review_document):
    role_names = [role["role_name"] for role in review_document["roles"]]
    assert role_names == sorted(role_names)

    assert review_document["total_roles"] == 3
    assert review_document["high_risk_roles"] == [
        "ShieldcraftAdmin",
        "ShieldcraftReadOnly",
    ]

    admin_role = next(
        role
        for role in review_document["roles"]
        if role["role_name"] == "ShieldcraftAdmin"
    )
    assert admin_role["risk_level"] == "critical"
    assert set(admin_role["issues"]) == {"wildcard_action", "wildcard_resource"}

    automation_role = next(
        role
        for role in review_document["roles"]
        if role["role_name"] == "ShieldcraftAutomation"
    )
    assert automation_role["risk_level"] == "low"
    assert automation_role["issues"] == []


def test_generate_reports_writes_artifacts(tmp_path):
    paths = generate_reports(output_dir=tmp_path)
    json_path = paths["json"]
    md_path = paths["markdown"]

    assert json_path.exists()
    assert md_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["total_roles"] == 3
    assert json_path.name == "iam_access_review.json"
    assert md_path.name == "iam_access_review.md"

    md_contents = md_path.read_text(encoding="utf-8")
    assert "# ShieldCraft IAM Access Review" in md_contents
    assert "ShieldcraftAdmin" in md_contents
    assert "ShieldcraftAutomation" in md_contents

    # Running again must produce identical JSON output for determinism
    second_paths = generate_reports(output_dir=tmp_path)
    assert json_path.read_text(encoding="utf-8") == second_paths["json"].read_text(
        encoding="utf-8"
    )
