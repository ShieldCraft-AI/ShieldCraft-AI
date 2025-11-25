import importlib.util

import pytest
from fastapi.testclient import TestClient

fastapi_spec = importlib.util.find_spec("fastapi")
if not fastapi_spec:  # pragma: no cover - safety for stripped environments
    pytest.skip(
        "fastapi not installed; skipping dashboard API tests", allow_module_level=True
    )

from api.app import app  # noqa: E402
from src.api.auth_middleware import (  # noqa: E402
    API_KEY_HEADER,
    EXPECTED_API_KEY,
)
from src.api.models.dashboard import (  # noqa: E402
    DashboardSummaryResponse,
    EvidenceFeedResponse,
)

client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    return {API_KEY_HEADER: EXPECTED_API_KEY}


def test_dashboard_summary_endpoint_returns_valid_payload():
    response = client.get("/api/dashboard/summary", headers=_auth_headers())
    assert response.status_code == 200

    payload = DashboardSummaryResponse.model_validate(response.json())
    section_ids = [section.section_id for section in payload.sections]
    assert section_ids == sorted(section_ids)
    for section in payload.sections:
        item_ids = [item.id for item in section.items]
        assert item_ids == sorted(item_ids)


def test_dashboard_evidence_endpoint_returns_valid_payload():
    response = client.get("/api/dashboard/evidence", headers=_auth_headers())
    assert response.status_code == 200

    payload = EvidenceFeedResponse.model_validate(response.json())
    timestamps = [item.collected_at for item in payload.items]
    assert timestamps == sorted(timestamps, reverse=True)
    assert [item.id for item in payload.items] == ["evt-001", "evt-002", "evt-003"]
