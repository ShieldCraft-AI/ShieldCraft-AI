from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import yaml
from pydantic import ValidationError

from infra.utils.config_schema import ShieldCraftConfig

REQUIRED_SECTIONS: Tuple[str, ...] = ("app", "s3", "glue")
OPTIONAL_EMPTY_SECTIONS: Tuple[str, ...] = ("glue",)


@dataclass(frozen=True)
class ValidationResult:
    """Structured output returned by validate_config."""

    path: str
    environment: str
    valid: bool
    errors: Tuple[str, ...]
    schema_errors: Tuple[str, ...]
    missing_sections: Tuple[str, ...]
    structure_fingerprint: str

    def all_errors(self) -> Tuple[str, ...]:
        """Return every recorded error in deterministic order for reporting."""

        return (
            self.errors
            + self.schema_errors
            + tuple(f"missing section: {section}" for section in self.missing_sections)
        )


def validate_config(path: str) -> ValidationResult:
    """Validate a config file against ShieldCraftConfig and structural requirements."""

    config_path = Path(path).resolve()
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    parsed, parse_errors = _load_yaml(config_path)
    data = parsed if isinstance(parsed, dict) else {}

    missing_sections = tuple(sorted(_missing_sections(data)))
    schema_errors: Tuple[str, ...] = ()
    normalized_data = data
    if not parse_errors:
        schema_errors = _validate_schema(data)
        if not schema_errors:
            normalized_data = ShieldCraftConfig.model_validate(data).model_dump()

    structure_fp = _fingerprint_structure(normalized_data)
    environment = _resolve_environment(data, config_path)
    valid = not (parse_errors or missing_sections or schema_errors)

    return ValidationResult(
        path=str(config_path),
        environment=environment,
        valid=valid,
        errors=tuple(parse_errors),
        schema_errors=schema_errors,
        missing_sections=missing_sections,
        structure_fingerprint=structure_fp,
    )


def _load_yaml(path: Path) -> Tuple[Any, Tuple[str, ...]]:
    errors = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            parsed = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - exercised via parse tests
        errors.append(f"yaml error: {exc}")
        parsed = {}
    except OSError as exc:  # pragma: no cover - surfaced earlier in validate_config
        raise exc
    except Exception as exc:  # noqa: BLE001
        errors.append(str(exc))
        parsed = {}
    if parsed is None:
        parsed = {}
    return parsed, tuple(errors)


def _missing_sections(data: Dict[str, Any]) -> Iterable[str]:
    for section in REQUIRED_SECTIONS:
        if section not in data or data.get(section) is None:
            yield section
            continue
        candidate = data.get(section)
        if (
            section not in OPTIONAL_EMPTY_SECTIONS
            and isinstance(candidate, dict)
            and not candidate
        ):
            yield section


def _validate_schema(data: Dict[str, Any]) -> Tuple[str, ...]:
    try:
        ShieldCraftConfig.model_validate(data)
        return tuple()
    except ValidationError as exc:
        messages = []
        for err in exc.errors():
            loc = ".".join(str(part) for part in err.get("loc", ())) or "root"
            messages.append(f"{loc}: {err.get('msg', 'invalid data')}")
        return tuple(sorted(messages))
    except ValueError as exc:
        return (str(exc),)


def _fingerprint_structure(data: Dict[str, Any]) -> str:
    """Build a deterministic fingerprint that ignores raw values."""

    shape = _structure_shape(data)
    payload = json.dumps(shape, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _structure_shape(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            "type": "dict",
            "keys": (
                {k: _structure_shape(value[k]) for k in sorted(value)} if value else {}
            ),
        }
    if isinstance(value, list):
        if not value:
            return {"type": "list", "items": []}
        fingerprints = sorted(
            json.dumps(_structure_shape(item), sort_keys=True, separators=(",", ":"))
            for item in value
        )
        # Use hashed sub-structures to avoid list ordering noise.
        return {"type": "list", "items": fingerprints}
    return {"type": type(value).__name__}


def _resolve_environment(data: Dict[str, Any], path: Path) -> str:
    app = data.get("app", {}) if isinstance(data, dict) else {}
    env = ""
    if isinstance(app, dict):
        env_candidate = app.get("env")
        if isinstance(env_candidate, str) and env_candidate:
            env = env_candidate
    return env or path.stem


__all__ = ["ValidationResult", "validate_config"]
