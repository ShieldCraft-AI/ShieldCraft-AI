def _normalize_empty_dicts(config, model):
    """
    Recursively convert empty dicts for optional model fields to None.
    """
    if not isinstance(config, dict):
        return config
    normalized = {}
    for field, value in config.items():
        if field in model.model_fields:
            field_info = model.model_fields[field]
            annotation = field_info.annotation
            # If the field is a model and optional, and value is an empty dict, remove the key
            if (
                hasattr(annotation, "__mro__")
                and issubclass(annotation.__mro__[0], BaseModel)
                and (field_info.is_required is False or field_info.default is None)
                and value == {}
            ):
                continue  # Remove the key entirely
            elif (
                isinstance(value, dict)
                and hasattr(annotation, "__mro__")
                and issubclass(annotation.__mro__[0], BaseModel)
            ):
                normalized[field] = _normalize_empty_dicts(value, annotation)
            else:
                normalized[field] = value
        else:
            normalized[field] = value
    return normalized


def _ensure_plain_dict(obj):
    """
    Recursively convert any Pydantic models to plain dicts.
    """
    if isinstance(obj, dict):
        return {k: _ensure_plain_dict(v) for k, v in obj.items()}
    if hasattr(obj, "model_dump"):
        return _ensure_plain_dict(obj.model_dump())
    if isinstance(obj, list):
        return [_ensure_plain_dict(v) for v in obj]
    return obj


"""
ConfigLoader for ShieldCraft AI
This module provides a singleton ConfigLoader class that loads configuration
"""

import os
import logging
import re
import pathlib

from typing import Any, Dict, Optional
from threading import Lock
from pydantic import ValidationError, BaseModel
from infra.utils.config_backends import (
    ConfigBackend,
    LocalYamlBackend,
    S3Backend,
    SSMBackend,
)
from infra.utils.config_schema import ShieldCraftConfig

# Use project root /config directory, not infra/config
CONFIG_DIR = str(pathlib.Path(__file__).parent.parent.parent / "config")
_VALID_ENVS = {"dev", "staging", "prod"}
_DEFAULT_ENV = "dev"
_SECRET_PATTERN = re.compile(r"^aws-vault:(.+)$")
_CONFIG_LOADER_SINGLETON = None
_CONFIG_LOADER_LOCK = Lock()


class ConfigLoader:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        # If a backend is provided, always create a new instance (for testability)
        backend = kwargs.get("backend")
        if backend is not None:
            return super().__new__(cls)
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        env: Optional[str] = None,
        strict: bool = False,
        backend: Optional[ConfigBackend] = None,
    ):
        if not hasattr(self, "_initialized"):
            self._initialized = False
        if self._initialized:
            return
        self.backend = backend
        # If a backend is provided (e.g., for testing), skip env validation and backend selection
        if backend is not None:
            self.env = env if env is not None else _DEFAULT_ENV
            self.strict = strict
            self.config = self._load_config()
            self._initialized = True
            return
        self.env = (
            env
            if env is not None
            else os.environ.get("ENV") or os.environ.get("APP_ENV") or _DEFAULT_ENV
        )
        self.env = self.env.lower()
        if self.env not in _VALID_ENVS:
            raise ValueError(
                f"Invalid environment: {self.env}. Must be one of {_VALID_ENVS}."
            )
        self.strict = strict
        self.backend = self._select_backend()
        self.config = self._load_config()
        self._initialized = True

    def _select_backend(self) -> ConfigBackend:
        backend_type = os.environ.get("CONFIG_BACKEND", "local").lower()
        if backend_type == "local":
            return LocalYamlBackend(CONFIG_DIR)
        if backend_type == "s3":
            bucket = os.environ.get("CONFIG_S3_BUCKET")
            prefix = os.environ.get("CONFIG_S3_PREFIX", "")
            if not bucket:
                raise ValueError("CONFIG_S3_BUCKET env var required for S3 backend")
            return S3Backend(bucket, prefix)
        if backend_type == "ssm":
            param_prefix = os.environ.get("CONFIG_SSM_PREFIX", "/shieldcraft/config")
            return SSMBackend(param_prefix)
        raise ValueError(f"Unknown config backend: {backend_type}")

    def _load_config(self) -> dict:
        if self.backend is None:
            raise RuntimeError("Config backend is not set. Cannot load config.")
        config = self.backend.load(self.env)
        # Defensive: ensure config is a plain dict
        if not config or type(config) is not dict:
            if hasattr(config, "model_dump"):
                config = config.model_dump()
            else:
                config = dict(config)
        # Only keep allowed keys and remove optional sections with empty dicts
        allowed_keys = set(ShieldCraftConfig.model_fields.keys())
        cleaned = {}
        for k, v in config.items():
            if k not in allowed_keys:
                continue
            field_info = ShieldCraftConfig.model_fields.get(k)
            annotation = field_info.annotation if field_info else None
            # Remove key if optional section and value is empty dict
            if (
                field_info
                and hasattr(annotation, "__mro__")
                and issubclass(annotation.__mro__[0], BaseModel)
                and (field_info.is_required is False or field_info.default is None)
                and v == {}
            ):
                continue
            cleaned[k] = v
        config = _normalize_empty_dicts(cleaned, ShieldCraftConfig)
        # Ensure config is a plain dict before validation (handles nested models)
        config = _ensure_plain_dict(config)
        # Only enforce presence of core required fields
        required_fields = ["app", "s3", "glue"]
        missing = [k for k in required_fields if k not in config]
        if missing:
            raise ValueError(f"Missing required config sections: {missing}")
        validated = None
        try:
            validated = ShieldCraftConfig.model_validate(config)
        except ValidationError as e:
            if self.strict:
                raise ValueError(f"Config schema validation failed: {e}")
            import logging

            logging.getLogger("shieldcraft").warning(
                f"Config schema validation failed, using raw config: {e}"
            )
            return config
        return validated.model_dump() if validated is not None else config

    def reload(self):
        self.config = self._load_config()

    def _resolve_env_override(self, key_path: str) -> Optional[Any]:
        env_key = key_path.upper().replace(".", "_")
        return os.environ.get(env_key)

    def _resolve_secret(self, value: Any) -> Any:
        if isinstance(value, str):
            match = _SECRET_PATTERN.match(value)
            if match:
                secret_name = match.group(1)
                # Placeholder for AWS Vault/SecretsManager integration
                # In production, fetch secret from AWS here
                return f"[REDACTED:{secret_name}]"
        return value

    def get(self, key: str, default: Any = None, strict: Optional[bool] = None) -> Any:
        # Nested key access with dot notation
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Check env override
                env_override = self._resolve_env_override(key)
                if env_override is not None:
                    return env_override
                if strict if strict is not None else self.strict:
                    raise KeyError(f"Missing config key: {key}")
                return default
        # Check env override for leaf key
        env_override = self._resolve_env_override(key)
        if env_override is not None:
            return env_override
        return self._resolve_secret(value)

    def get_section(
        self, section: str, strict: Optional[bool] = None
    ) -> Dict[str, Any]:
        if section in self.config:
            return self.config[section]
        if strict if strict is not None else self.strict:
            raise KeyError(f"Missing config section: {section}")
        return {}

    def export(self, redact_secrets: bool = True) -> Any:
        def redact(obj):
            if isinstance(obj, dict):
                return {k: redact(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [redact(v) for v in obj]
            if isinstance(obj, str) and _SECRET_PATTERN.match(obj):
                return "[REDACTED]"
            return obj

        return redact(self.config) if redact_secrets else self.config.copy()


def get_logger(name: str = "shieldcraft") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    log_level = os.environ.get("LOG_LEVEL")
    if not log_level:
        try:
            config = ConfigLoader().get_section("app")
            log_level = config.get("log_level", "INFO")
        except Exception:
            log_level = "INFO"
    logger.setLevel(log_level.upper())
    return logger


# Singleton accessor for config loader
def get_config_loader(env: Optional[str] = None, strict: bool = False) -> ConfigLoader:
    global _CONFIG_LOADER_SINGLETON
    with _CONFIG_LOADER_LOCK:
        if _CONFIG_LOADER_SINGLETON is None:
            _CONFIG_LOADER_SINGLETON = ConfigLoader(env=env, strict=strict)
    return _CONFIG_LOADER_SINGLETON
