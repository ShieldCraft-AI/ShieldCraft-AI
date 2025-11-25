from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from src.api.auth_middleware import (
    API_KEY_HEADER,
    build_auth_context,
    unauthorized_response,
)
from src.api.models.dashboard import (
    DashboardSummaryResponse,
    EvidenceFeedResponse,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _fixture_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "dashboard"


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _sort_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload["sections"] = sorted(
        payload["sections"], key=lambda section: section["section_id"]
    )
    for section in payload["sections"]:
        section["items"] = sorted(section["items"], key=lambda item: item["id"])
    return payload


def _sort_evidence(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload["items"] = sorted(
        payload["items"],
        key=lambda item: (item["collected_at"], item["id"]),
        reverse=True,
    )
    return payload


@lru_cache(maxsize=1)
def _summary_payload() -> DashboardSummaryResponse:
    summary_path = _fixture_dir() / "summary.json"
    payload = _sort_summary(_load_json(summary_path))
    return DashboardSummaryResponse.model_validate(payload)


@lru_cache(maxsize=1)
def _evidence_payload() -> EvidenceFeedResponse:
    evidence_path = _fixture_dir() / "evidence.json"
    payload = _sort_evidence(_load_json(evidence_path))
    return EvidenceFeedResponse.model_validate(payload)


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    api_key: str | None = Header(default=None, alias=API_KEY_HEADER)
) -> DashboardSummaryResponse | JSONResponse:
    context = build_auth_context(api_key)
    if context is None:
        return unauthorized_response()
    return _summary_payload()


@router.get("/evidence", response_model=EvidenceFeedResponse)
async def get_dashboard_evidence(
    api_key: str | None = Header(default=None, alias=API_KEY_HEADER)
) -> EvidenceFeedResponse | JSONResponse:
    context = build_auth_context(api_key)
    if context is None:
        return unauthorized_response()
    return _evidence_payload()
