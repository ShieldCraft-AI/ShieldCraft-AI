from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


EnvironmentName = Literal["dev", "staging", "prod"]


class EnvironmentConfig(BaseModel):
    name: EnvironmentName
    account_id: str = Field(..., min_length=12, max_length=12)
    region: str = Field(..., min_length=3)

    def describe(self) -> dict[str, str]:
        return {
            "name": self.name,
            "account_id": self.account_id,
            "region": self.region,
        }


def load_environment_config(env: EnvironmentName) -> EnvironmentConfig:
    # Deterministic placeholder map; replace with real loader when IaC wiring is ready.
    defaults: dict[EnvironmentName, EnvironmentConfig] = {
        "dev": EnvironmentConfig(
            name="dev", account_id="000000000000", region="us-east-1"
        ),
        "staging": EnvironmentConfig(
            name="staging", account_id="111111111111", region="us-east-2"
        ),
        "prod": EnvironmentConfig(
            name="prod", account_id="222222222222", region="us-west-2"
        ),
    }
    return defaults[env]


__all__ = ["EnvironmentConfig", "EnvironmentName", "load_environment_config"]
