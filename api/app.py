from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from scripts.demo_vertical_slice import build_demo_payload
import os

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
