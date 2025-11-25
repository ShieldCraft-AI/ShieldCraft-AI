from __future__ import annotations

import json
import hashlib
from pathlib import Path

import nox

from nox_sessions.utils import nox_session_guard, now_str
from nox_sessions.utils_color import matrix_log

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = PROJECT_ROOT / "artifacts" / "sbom" / "shieldcraft-sbom.json"
SBOM_SCRIPT = PROJECT_ROOT / "scripts" / "sbom" / "publish_sbom.py"


@nox_session_guard
@nox.session()
def sbom(session):
    matrix_log(session, f"[SBOM] Session started at {now_str()}", color="yellow")
    destination_dir = str(ARTIFACT_PATH.parent)
    sbom_file = str(ARTIFACT_PATH)

    session.run(
        "python",
        str(SBOM_SCRIPT),
        "--destination",
        destination_dir,
        "--filename",
        ARTIFACT_PATH.name,
        external=True,
    )

    document = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert document["metadata"]["generated_at"] == "2025-01-01T00:00:00Z"
    assert document["components"]

    digest = hashlib.sha256(json.dumps(document, sort_keys=True).encode("utf-8"))
    matrix_log(
        session,
        f"[SBOM] Artifact ready at {sbom_file} (sha256={digest.hexdigest()[:12]})",
        color="green",
    )
    matrix_log(session, f"[SBOM] Session ended at {now_str()}", color="yellow")
