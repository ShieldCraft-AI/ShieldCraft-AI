from __future__ import annotations

from infra.environment.environment_config import (
    EnvironmentConfig,
    EnvironmentName,
    load_environment_config,
)


def provision_environment(env: EnvironmentName) -> dict[str, str]:
    config: EnvironmentConfig = load_environment_config(env)
    return {
        "requested_env": env,
        "account_id": config.account_id,
        "region": config.region,
        "provisioning_state": "placeholder",
        "generated_at": "2025-01-01T00:00:00Z",
    }


__all__ = ["provision_environment"]
