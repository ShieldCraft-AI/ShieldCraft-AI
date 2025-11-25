from __future__ import annotations

import json
from pathlib import Path

import nox

from nox_sessions.utils import nox_session_guard, now_str
from nox_sessions.utils_color import matrix_log

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "iam"
JSON_ARTIFACT = ARTIFACT_DIR / "iam_access_review.json"
REPORT_SCRIPT = PROJECT_ROOT / "scripts" / "iam" / "iam_report.py"


@nox_session_guard
@nox.session()
def iam_review(session):
    matrix_log(session, f"[IAM] Session started at {now_str()}", color="yellow")

    session.run(
        "python",
        str(REPORT_SCRIPT),
        "--destination",
        str(ARTIFACT_DIR),
        external=True,
    )

    if not JSON_ARTIFACT.exists():
        raise RuntimeError(f"IAM review artifact missing at {JSON_ARTIFACT}")

    document = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
    assert document["generated_at"] == "2025-01-01T00:00:00Z"
    assert document["total_roles"] >= 1

    matrix_log(
        session,
        f"[IAM] Review generated with {document['total_roles']} roles (high risk: {len(document['high_risk_roles'])})",
        color="green",
    )
    matrix_log(session, f"[IAM] Session ended at {now_str()}", color="yellow")
