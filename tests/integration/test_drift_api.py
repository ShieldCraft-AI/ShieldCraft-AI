import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

fastapi_spec = importlib.util.find_spec("fastapi")
if not fastapi_spec:  # pragma: no cover - optional dependency guard
    pytest.skip(
        "fastapi not installed; skipping drift API tests", allow_module_level=True
    )

from api.app import app  # noqa: E402

client = TestClient(app)
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "drift_expected.json"


def test_drift_endpoint_returns_expected_payload():
    expected = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    response = client.get("/api/ai/drift")

    assert response.status_code == 200
    assert response.json() == expected
    assert list(response.json().keys()) == ["status", "signals", "recommendations"]
