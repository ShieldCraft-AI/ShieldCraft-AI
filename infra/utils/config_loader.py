import os
import yaml
import logging
import re
from typing import Any, Dict, Optional, Union
from threading import Lock
from pydantic import BaseModel, ValidationError
from .config_backends import ConfigBackend, LocalYamlBackend, S3Backend, SSMBackend



CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
_VALID_ENVS = {"dev", "staging", "prod"}
_DEFAULT_ENV = "dev"
_SECRET_PATTERN = re.compile(r"^aws-vault:(.+)$")
_CONFIG_LOADER_SINGLETON = None
_CONFIG_LOADER_LOCK = Lock()

class ConfigSchema(BaseModel):
    app: dict
    s3: dict
    glue: dict
    msk: dict
    lambda_: Optional[dict] = None
    opensearch: Optional[dict] = None
    airbyte: Optional[dict] = None
    data_quality: Optional[dict] = None
    lakeformation: Optional[dict] = None


class ConfigLoader:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        # If a backend is provided, always create a new instance (for testability)
        backend = kwargs.get('backend')
        if backend is not None:
            return super().__new__(cls)
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, env: str = None, strict: bool = False, schema: Optional[BaseModel] = None, backend: Optional[ConfigBackend] = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.backend = backend
        # If a backend is provided (e.g., for testing), skip env validation and backend selection
        if backend is not None:
            self.env = env
            self.strict = strict
            self.schema = schema or ConfigSchema
            self.config = self._load_config()
            self._initialized = True
            return
        self.env = env or os.environ.get("ENV") or os.environ.get("APP_ENV") or _DEFAULT_ENV
        self.env = self.env.lower()
        if self.env not in _VALID_ENVS:
            raise ValueError(f"Invalid environment: {self.env}. Must be one of {_VALID_ENVS}.")
        self.strict = strict
        self.schema = schema or ConfigSchema
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

    def _load_config(self) -> Dict[str, Any]:
        config = self.backend.load(self.env)
        if not config or not isinstance(config, dict):
            raise ValueError(f"Config for env {self.env} is empty or invalid.")
        # Validate schema
        try:
            self.schema(**{k.replace('-', '_'): v for k, v in config.items()})
        except ValidationError as e:
            if self.strict:
                raise ValueError(f"Config schema validation failed: {e}")
        return config

    def reload(self):
        self.config = self._load_config()

    def _resolve_env_override(self, key_path: str) -> Optional[Any]:
        env_key = key_path.upper().replace('.', '_')
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
        keys = key.split('.')
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

    def get_section(self, section: str, strict: Optional[bool] = None) -> Dict[str, Any]:
        if section in self.config:
            return self.config[section]
        if strict if strict is not None else self.strict:
            raise KeyError(f"Missing config section: {section}")
        return {}

    def export(self, redact_secrets: bool = True) -> Dict[str, Any]:
        def redact(obj):
            if isinstance(obj, dict):
                return {k: redact(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [redact(v) for v in obj]
            if isinstance(obj, str) and _SECRET_PATTERN.match(obj):
                return "[REDACTED]"
            return obj
        return redact(self.config) if redact_secrets else self.config.copy()

    # (Removed: duplicate legacy _load_config method that accessed the file system directly)

    # (Removed duplicate get and get_section methods that bypassed advanced logic)

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
