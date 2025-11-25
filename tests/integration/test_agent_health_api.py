import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

fastapi_spec = importlib.util.find_spec("fastapi")
if not fastapi_spec:  # pragma: no cover
    pytest.skip(
        "fastapi not installed; skipping agent health API tests",
        allow_module_level=True,
    )

from api.app import app  # noqa: E402

client = TestClient(app)
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "agent_health.json"


def test_agent_health_endpoint_returns_fixture_payload():
    expected = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    response = client.get("/api/agent/health")

    assert response.status_code == 200
    assert response.json() == expected
    assert list(response.json().keys()) == [
        "status",
        "last_heartbeat_ts",
        "agent_version",
        "ready",
    ]
