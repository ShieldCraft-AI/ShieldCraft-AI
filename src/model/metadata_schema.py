from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelMetadata(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_id: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    created_at: str = Field(..., description="ISO8601 timestamp")
    description: str
    params: Dict[str, Any]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

    @field_validator("created_at")
    @classmethod
    def _validate_created_at(cls, value: str) -> str:
        # Accept basic ISO8601 values (with or without timezone suffix) while keeping the raw string.
        normalized = value.replace("Z", "+00:00")
        datetime.fromisoformat(normalized)
        return value


__all__ = ["ModelMetadata"]
