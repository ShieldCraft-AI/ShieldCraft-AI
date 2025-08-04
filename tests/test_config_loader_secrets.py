"""
Test secret resolution in ConfigLoader using a dummy backend.
"""

import pytest
from infra.utils.config_loader import ConfigLoader


class DummyBackend:
    def load(self, env):
        # Simulate config with aws-vault secret reference and required sections (valid structure)
        return {
            "app": {"name": "test-app"},
            "s3": {"buckets": [{"name": "test-bucket", "id": "test-bucket-id"}]},
            "glue": {"database_name": "test-db"},
            "vector_store": {"db_password": "aws-vault:test/vector_store/db_password"},
        }


def make_config_loader_with_dummy_backend():
    # Use dummy backend to avoid real AWS calls
    return ConfigLoader(env="dev", backend=DummyBackend())


def test_secret_resolution(monkeypatch):
    # Ensure test isolation: clear ConfigLoader singleton
    from infra.utils import config_loader as config_loader_mod

    ConfigLoader._instance = None
    config_loader_mod._CONFIG_LOADER_SINGLETON = None

    # Patch _resolve_secret to simulate secret fetch
    def dummy_resolve_secret(self, value):
        if isinstance(value, str) and value.startswith("aws-vault:"):
            return "super-secret-password"
        return value

    monkeypatch.setattr(ConfigLoader, "_resolve_secret", dummy_resolve_secret)
    loader = make_config_loader_with_dummy_backend()
    password = loader.get("vector_store.db_password")
    assert password == "super-secret-password"


def test_no_secret_resolution(monkeypatch):
    # Ensure test isolation: clear ConfigLoader singleton
    from infra.utils import config_loader as config_loader_mod

    ConfigLoader._instance = None
    config_loader_mod._CONFIG_LOADER_SINGLETON = None

    # Patch _resolve_secret to pass through non-secret values
    def dummy_resolve_secret(self, value):
        return value

    monkeypatch.setattr(ConfigLoader, "_resolve_secret", dummy_resolve_secret)
    loader = make_config_loader_with_dummy_backend()
    password = loader.get("vector_store.db_password")
    assert password == "aws-vault:test/vector_store/db_password"
