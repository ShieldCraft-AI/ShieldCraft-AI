from scripts.demo_vertical_slice import build_demo_payload
import importlib
import pytest


def test_build_demo_payload_direct():
    # Always validate the core deterministic payload builder
    payload = build_demo_payload("fdg-0001", "dev")
    assert payload["findingId"] == "fdg-0001"
    assert "evidence" in payload and isinstance(payload["evidence"], list)
    assert "risk" in payload and "score" in payload["risk"]
    assert payload["remediation"]["planId"].startswith("plan-")


def test_http_endpoints_if_available():
    # Only run HTTP integration if FastAPI and TestClient are available
    fastapi_spec = importlib.util.find_spec("fastapi")
    if not fastapi_spec:
        pytest.skip("fastapi not installed; skipping HTTP integration tests")

    from api.app import app
    import httpx
    from httpx import ASGITransport
    import asyncio

    async def run_async_checks():
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            resp = await client.get("/demo-vertical-slice?finding_id=fdg-1234")
            assert resp.status_code == 200
            json_resp = resp.json()
            expected = build_demo_payload("fdg-1234", "dev")
            assert json_resp["findingId"] == expected["findingId"]

            payload = {"findingId": "fdg-5678", "env": "staging"}
            resp = await client.post("/evaluate", json=payload)
            assert resp.status_code == 200
            json_resp = resp.json()
            expected = build_demo_payload("fdg-5678", "staging")
            assert json_resp["findingId"] == expected["findingId"]
            assert json_resp["meta"]["env"] == "staging"

    asyncio.run(run_async_checks())
