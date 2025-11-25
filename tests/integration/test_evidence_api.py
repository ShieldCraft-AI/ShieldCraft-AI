import importlib.util

import pytest
from fastapi.testclient import TestClient

fastapi_spec = importlib.util.find_spec("fastapi")
if not fastapi_spec:  # pragma: no cover
    pytest.skip(
        "fastapi not installed; skipping evidence API tests", allow_module_level=True
    )

from api.app import app  # noqa: E402
from src.api.auth_middleware import (  # noqa: E402
    API_KEY_HEADER,
    EXPECTED_API_KEY,
)
from src.api.models.evidence_models import (
    EvidenceBatch,
    EvidenceIngestionStatus,
)  # noqa: E402

client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    return {API_KEY_HEADER: EXPECTED_API_KEY}


def test_evidence_preview_endpoint_returns_sorted_batch():
    response = client.get(
        "/api/evidence/ingest/preview",
        headers=_auth_headers(),
    )
    assert response.status_code == 200

    payload = EvidenceBatch.model_validate(response.json())
    timestamps = [item.collected_at for item in payload.items]
    assert timestamps == sorted(timestamps, reverse=True)
    assert [item.id for item in payload.items] == ["ing-002", "ing-001"]


def test_evidence_status_endpoint_returns_static_snapshot():
    response = client.get("/api/evidence/status", headers=_auth_headers())
    assert response.status_code == 200

    payload = EvidenceIngestionStatus.model_validate(response.json())
    assert payload.mode == "read-only"
    assert payload.pending_batches == 0
    assert payload.status in {"idle", "running", "complete"}
