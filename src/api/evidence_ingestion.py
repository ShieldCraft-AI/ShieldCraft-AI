from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.api.models.evidence_models import EvidenceBatch, EvidenceIngestionStatus


FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures"


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _sort_batch(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload["items"] = sorted(
        payload["items"],
        key=lambda item: (item["collected_at"], item["id"]),
        reverse=True,
    )
    return payload


@lru_cache(maxsize=1)
def preview_batch() -> EvidenceBatch:
    raw = _load_json(FIXTURE_DIR / "evidence_ingest.json")
    return EvidenceBatch.model_validate(_sort_batch(raw))


@lru_cache(maxsize=1)
def ingestion_status() -> EvidenceIngestionStatus:
    raw = _load_json(FIXTURE_DIR / "evidence_status.json")
    return EvidenceIngestionStatus.model_validate(raw)
