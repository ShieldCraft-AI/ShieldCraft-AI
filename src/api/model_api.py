from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.model.metadata_schema import ModelMetadata
from src.model.registry import get_model, list_models

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=list[ModelMetadata])
async def list_model_metadata() -> list[ModelMetadata]:
    return list_models()


@router.get("/{model_id}", response_model=ModelMetadata)
async def get_model_metadata(model_id: str) -> ModelMetadata:
    try:
        return get_model(model_id)
    except KeyError as exc:  # pragma: no cover - error path
        raise HTTPException(status_code=404, detail="model not found") from exc
