import importlib.util

import pytest
from fastapi.testclient import TestClient

fastapi_spec = importlib.util.find_spec("fastapi")
if not fastapi_spec:  # pragma: no cover - safety for stripped environments
    pytest.skip(
        "fastapi not installed; skipping auth API tests", allow_module_level=True
    )

from api.app import app  # noqa: E402
from src.api.models.auth_models import AuthErrorResponse  # noqa: E402

client = TestClient(app)
ERROR_PAYLOAD = AuthErrorResponse().model_dump()


@pytest.mark.parametrize(
    "route",
    [
        "/api/dashboard/summary",
        "/api/dashboard/evidence",
        "/api/evidence/ingest/preview",
        "/api/evidence/status",
    ],
)
def test_routes_reject_missing_api_key(route: str):
    response = client.get(route)
    assert response.status_code == 401
    assert response.json() == ERROR_PAYLOAD


def test_route_rejects_invalid_api_key():
    response = client.get(
        "/api/dashboard/summary",
        headers={"X-Shieldcraft-Api-Key": "invalid-key"},
    )
    assert response.status_code == 401
    assert response.json() == ERROR_PAYLOAD
