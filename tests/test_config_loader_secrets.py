import pytest
from infra.utils.config_loader import ConfigLoader


class DummyBackend:
    def load(self, env):
        # Simulate config with aws-vault secret reference
        return {
            "vector_store": {"db_password": "aws-vault:test/vector_store/db_password"}
        }


@pytest.fixture
def config_loader_with_dummy_backend():
    # Use dummy backend to avoid real AWS calls
    return ConfigLoader(env="dev", backend=DummyBackend())


def test_secret_resolution(monkeypatch, config_loader_with_dummy_backend):
    # Patch _resolve_secret to simulate secret fetch
    def dummy_resolve_secret(self, value):
        if isinstance(value, str) and value.startswith("aws-vault:"):
            return "super-secret-password"
        return value

    monkeypatch.setattr(ConfigLoader, "_resolve_secret", dummy_resolve_secret)
    loader = config_loader_with_dummy_backend
    password = loader.get("vector_store.db_password")
    assert password == "super-secret-password"


def test_no_secret_resolution(config_loader_with_dummy_backend):
    # Patch _resolve_secret to pass through non-secret values
    def dummy_resolve_secret(self, value):
        return value

    ConfigLoader._resolve_secret = dummy_resolve_secret
    loader = config_loader_with_dummy_backend
    password = loader.get("vector_store.db_password")
    assert password == "aws-vault:test/vector_store/db_password"
