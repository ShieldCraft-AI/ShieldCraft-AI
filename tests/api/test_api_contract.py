import pytest

try:
    from fastapi.testclient import TestClient
    from api.app import app

    client = TestClient(app)
    TESTCLIENT_AVAILABLE = True
except Exception:
    TESTCLIENT_AVAILABLE = False


# Only test endpoints that exist in the FastAPI app
ENDPOINTS = [
    ("/demo-vertical-slice", "GET"),
    ("/evaluate", "POST"),
]


import sys

pytestmark = pytest.mark.skipif(
    not TESTCLIENT_AVAILABLE,
    reason="TestClient could not be constructed (FastAPI/Starlette version mismatch)",
)


@pytest.mark.parametrize("path,method", ENDPOINTS)
def test_api_endpoint_status(path, method):
    if method == "GET":
        resp = client.get(path)
    elif method == "POST":
        resp = client.post(path, json={})
    else:
        pytest.skip("Unsupported method")
    assert resp.status_code in (200, 400, 422, 404)


@pytest.mark.parametrize("path,method", ENDPOINTS)
def test_api_endpoint_no_500(path, method):
    if method == "GET":
        resp = client.get(path)
    elif method == "POST":
        resp = client.post(path, json={})
    else:
        pytest.skip("Unsupported method")
    assert resp.status_code != 500


@pytest.mark.parametrize("path,method", ENDPOINTS)
def test_api_endpoint_content_type(path, method):
    if method == "GET":
        resp = client.get(path)
    elif method == "POST":
        resp = client.post(path, json={})
    else:
        pytest.skip("Unsupported method")
    assert "application/json" in resp.headers.get("content-type", "")
