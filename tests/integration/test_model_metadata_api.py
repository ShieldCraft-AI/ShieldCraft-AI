import importlib.util

import pytest
from fastapi.testclient import TestClient

fastapi_spec = importlib.util.find_spec("fastapi")
if not fastapi_spec:  # pragma: no cover - safety for stripped environments
    pytest.skip(
        "fastapi not installed; skipping model metadata API tests",
        allow_module_level=True,
    )

from api.app import app  # noqa: E402
from src.model.metadata_schema import ModelMetadata  # noqa: E402

client = TestClient(app)


def test_list_models_endpoint_returns_sorted_metadata():
    response = client.get("/api/models")
    assert response.status_code == 200

    payload = [ModelMetadata.model_validate(item) for item in response.json()]
    model_ids = [model.model_id for model in payload]
    assert model_ids == sorted(model_ids)


def test_get_model_endpoint_returns_single_entry():
    response = client.get("/api/models/shield-embed")
    assert response.status_code == 200

    metadata = ModelMetadata.model_validate(response.json())
    assert metadata.model_id == "shield-embed"
    assert metadata.params["dimension"] == 1536


def test_get_model_endpoint_missing_returns_404():
    response = client.get("/api/models/unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "model not found"
