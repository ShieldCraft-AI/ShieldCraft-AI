from __future__ import annotations

import pytest

from infra.environment.environment_config import (
    EnvironmentConfig,
    load_environment_config,
)
from infra.environment.main import provision_environment


def test_load_environment_config_returns_typed_config():
    config = load_environment_config("dev")
    assert isinstance(config, EnvironmentConfig)
    assert config.name == "dev"
    assert config.region == "us-east-1"


def test_provision_environment_returns_placeholder_payload():
    payload = provision_environment("staging")
    assert payload == {
        "requested_env": "staging",
        "account_id": "111111111111",
        "region": "us-east-2",
        "provisioning_state": "placeholder",
        "generated_at": "2025-01-01T00:00:00Z",
    }


def test_provision_environment_rejects_unknown_env():
    with pytest.raises(KeyError):
        load_environment_config("qa")  # type: ignore[arg-type]
