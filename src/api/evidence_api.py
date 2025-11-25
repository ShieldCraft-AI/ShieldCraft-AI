from __future__ import annotations

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from src.api.auth_middleware import (
    API_KEY_HEADER,
    build_auth_context,
    unauthorized_response,
)
from src.api.evidence_ingestion import ingestion_status, preview_batch
from src.api.models.evidence_models import EvidenceBatch, EvidenceIngestionStatus

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.get("/ingest/preview", response_model=EvidenceBatch)
async def get_evidence_preview(
    api_key: str | None = Header(default=None, alias=API_KEY_HEADER)
) -> EvidenceBatch | JSONResponse:
    context = build_auth_context(api_key)
    if context is None:
        return unauthorized_response()
    return preview_batch()


@router.get("/status", response_model=EvidenceIngestionStatus)
async def get_evidence_status(
    api_key: str | None = Header(default=None, alias=API_KEY_HEADER)
) -> EvidenceIngestionStatus | JSONResponse:
    context = build_auth_context(api_key)
    if context is None:
        return unauthorized_response()
    return ingestion_status()
