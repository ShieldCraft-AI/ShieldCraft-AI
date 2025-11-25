from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from src.model.metadata_schema import ModelMetadata

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "models"


def _load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def _index_payload() -> List[Dict[str, str]]:
    payload = _load_json(_FIXTURE_DIR / "models_index.json")
    models = payload.get("models", [])
    return sorted(models, key=lambda item: item["model_id"])


@lru_cache(maxsize=None)
def _model_payload(model_id: str) -> Dict:
    index = {entry["model_id"]: entry for entry in _index_payload()}
    entry = index.get(model_id)
    if entry is None:
        raise KeyError(model_id)
    model_path = _FIXTURE_DIR / entry["file"]
    return _load_json(model_path)


def list_models() -> List[ModelMetadata]:
    return [
        ModelMetadata.model_validate(_model_payload(entry["model_id"]))
        for entry in _index_payload()
    ]


def get_model(model_id: str) -> ModelMetadata:
    return ModelMetadata.model_validate(_model_payload(model_id))


__all__ = ["list_models", "get_model"]
