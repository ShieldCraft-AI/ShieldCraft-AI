from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SBOM_SCRIPT_DIR = PROJECT_ROOT / "scripts" / "sbom"
if str(SBOM_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SBOM_SCRIPT_DIR))

try:
    from generate_sbom import generate_sbom  # type: ignore[import]
    from publish_sbom import publish_sbom  # type: ignore[import]
except ModuleNotFoundError:  # pragma: no cover - safety guard
    pytest.skip(
        "SBOM scripts unavailable; skipping sbom pipeline tests",
        allow_module_level=True,
    )


@pytest.fixture
def sbom_document():
    return generate_sbom()


def test_generate_sbom_contains_required_schema(sbom_document):
    assert sbom_document["bom_format"] == "CycloneDX"
    assert sbom_document["spec_version"].startswith("1.")
    assert sbom_document["metadata"]["component"]["name"] == "shieldcraft-ai"
    assert sbom_document["metadata"]["generated_at"] == "2025-01-01T00:00:00Z"


def test_components_are_sorted_and_hashed(sbom_document):
    names = [component["name"] for component in sbom_document["components"]]
    assert names == sorted(names, key=str.lower)

    for component in sbom_document["components"]:
        digest = hashlib.sha256(
            (component["name"] + component["version"]).encode("utf-8")
        ).hexdigest()
        assert component["sha256"] == digest


def test_publish_sbom_emits_artifact(tmp_path):
    artifact_path = publish_sbom(destination_dir=tmp_path)
    assert artifact_path.exists()

    document = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert document["components"]
    assert document["metadata"]["generated_at"] == "2025-01-01T00:00:00Z"

    # Subsequent publish must overwrite with identical content
    second_artifact = publish_sbom(destination_dir=tmp_path)
    assert artifact_path.read_text(encoding="utf-8") == second_artifact.read_text(
        encoding="utf-8"
    )
