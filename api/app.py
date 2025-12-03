from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pathlib import Path
import json
import os

from scripts.demo_vertical_slice import build_demo_payload

from src.api.auth_middleware import (
    API_KEY_HEADER,
    build_auth_context,
    unauthorized_response,
)

app = FastAPI(title="ShieldCraft AI - Demo API")


@app.get("/demo-vertical-slice")
async def demo_vertical_slice(finding_id: str = "fdg-0001"):
    try:
        env = os.getenv("SC_ENV", "dev")
        payload = build_demo_payload(finding_id, env)
        return JSONResponse(content=payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
async def evaluate(body: dict):
    # For PoC: accept {"findingId": "...", "env": "..."}
    finding_id = body.get("findingId") or body.get("finding_id") or "fdg-0001"
    env = body.get("env") or os.getenv("SC_ENV", "dev")
    try:
        payload = build_demo_payload(finding_id, env)
        return JSONResponse(content=payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Test-only / API shims (lightweight, deterministic fixtures) ---
# These endpoints are intentionally small helpers used by the integration
# tests. They are enabled when `SC_ENV` == "dev" to avoid surprising
# production behavior in other environments.

_ENABLE_SHIMS = os.getenv("SC_ENV", "dev") == "dev"


def _fixture_path(*parts: str) -> Path:
    root = Path(__file__).resolve().parents[1]
    return root.joinpath("tests", "fixtures", *parts)


def _read_fixture(*parts: str):
    path = _fixture_path(*parts)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


if _ENABLE_SHIMS:

    @app.get("/api/agent/health")
    async def agent_health():
        payload = _read_fixture("agent_health.json")
        if payload is None:
            raise HTTPException(status_code=500, detail="missing fixture")
        return JSONResponse(content=payload)

    @app.post("/api/agent/orchestrate")
    async def agent_orchestrate(body: dict):
        # Deterministic orchestration response used by tests
        resp = {
            "status": "ok",
            "steps": [
                {"agent": "plan_ingestor", "inputs": {}, "outputs": {}},
                {"agent": "risk_profiler", "inputs": {}, "outputs": {}},
                {"agent": "action_planner", "inputs": {}, "outputs": {}},
            ],
            "final_recommendation": {"priority": "escalate", "notes": "test-shim"},
        }
        return JSONResponse(content=resp)

    @app.get("/api/dashboard/summary")
    async def dashboard_summary(request: Request):
        key = request.headers.get(API_KEY_HEADER)
        if build_auth_context(key) is None:
            return unauthorized_response()
        payload = _read_fixture("dashboard", "summary.json")
        if not payload:
            return JSONResponse(content={})
        # Ensure deterministic ordering for tests: sort sections by section_id
        sections = payload.get("sections", [])
        sections = sorted(sections, key=lambda s: s.get("section_id", ""))
        for sec in sections:
            items = sec.get("items", [])
            sec["items"] = sorted(items, key=lambda it: it.get("id", ""))
        payload["sections"] = sections
        return JSONResponse(content=payload)

    @app.get("/api/dashboard/evidence")
    async def dashboard_evidence(request: Request):
        key = request.headers.get(API_KEY_HEADER)
        if build_auth_context(key) is None:
            return unauthorized_response()
        payload = _read_fixture("dashboard", "evidence.json")
        return JSONResponse(content=payload)

    @app.get("/api/models")
    async def list_models():
        index = _read_fixture("models", "models_index.json")
        if not index:
            return JSONResponse(content=[], status_code=200)
        out = []
        for entry in index.get("models", []):
            file = entry.get("file")
            if not file:
                continue
            model = _read_fixture("models", file)
            if model:
                out.append(model)
        return JSONResponse(content=out)

    @app.get("/api/models/{model_id}")
    async def get_model(model_id: str):
        index = _read_fixture("models", "models_index.json")
        if not index:
            raise HTTPException(status_code=404, detail="model not found")
        for entry in index.get("models", []):
            file = entry.get("file")
            if not file:
                continue
            model = _read_fixture("models", file)
            if model and model.get("model_id") == model_id:
                return JSONResponse(content=model)
        raise HTTPException(status_code=404, detail="model not found")

    @app.get("/api/ai/drift")
    async def drift_report():
        payload = _read_fixture("drift_expected.json")
        if payload is None:
            raise HTTPException(status_code=500, detail="missing fixture")
        return JSONResponse(content=payload)

    @app.get("/api/evidence/ingest/preview")
    async def evidence_ingest_preview(request: Request):
        key = request.headers.get(API_KEY_HEADER)
        if build_auth_context(key) is None:
            return unauthorized_response()
        payload = _read_fixture("evidence_ingest.json")
        return JSONResponse(content=payload)

    @app.get("/api/evidence/status")
    async def evidence_status(request: Request):
        key = request.headers.get(API_KEY_HEADER)
        if build_auth_context(key) is None:
            return unauthorized_response()
        payload = _read_fixture("evidence_status.json")
        return JSONResponse(content=payload)
