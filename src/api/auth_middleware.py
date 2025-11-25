from __future__ import annotations

from fastapi.responses import JSONResponse

from src.api.models.auth_models import APIKeyContext, AuthErrorResponse

API_KEY_HEADER = "X-Shieldcraft-Api-Key"
EXPECTED_API_KEY = "shieldcraft-demo-key"

_ERROR_PAYLOAD = AuthErrorResponse().model_dump()


def build_auth_context(provided_key: str | None) -> APIKeyContext | None:
    """Validate the provided API key and return a typed context when authorized."""

    if provided_key is None:
        return None
    candidate = provided_key.strip()
    if not candidate:
        return None
    if candidate != EXPECTED_API_KEY:
        return None
    return APIKeyContext(api_key=candidate)


def unauthorized_response() -> JSONResponse:
    """Create the canonical unauthorized JSON response."""

    return JSONResponse(status_code=401, content=_ERROR_PAYLOAD)


__all__ = [
    "API_KEY_HEADER",
    "EXPECTED_API_KEY",
    "build_auth_context",
    "unauthorized_response",
]
