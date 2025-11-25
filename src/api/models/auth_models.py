from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class APIKeyContext(BaseModel):
    """Represents a validated API key from the request headers."""

    api_key: str = Field(..., min_length=1)


class AuthErrorResponse(BaseModel):
    """Canonical error payload returned for unauthorized requests."""

    error: Literal["unauthorized"] = "unauthorized"
    details: Literal["missing or invalid key"] = "missing or invalid key"


__all__ = ["APIKeyContext", "AuthErrorResponse"]
