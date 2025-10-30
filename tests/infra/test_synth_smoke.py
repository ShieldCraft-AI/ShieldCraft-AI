import os
from aws_cdk import App
import pytest

from infra.shieldcraft_app_stage import ShieldcraftAppStage


@pytest.mark.unit
def test_app_synths_without_deploy(tmp_path, monkeypatch):
    # Ensure we use the dev config
    monkeypatch.setenv("ENV", "dev")
    app = App()
    # Create stage with dev config. This only constructs stacks; no deploy.
    stage = ShieldcraftAppStage(app, "ShieldcraftStageTest", env_name="dev")

    assembly = app.synth()
    assert assembly is not None
    # Basic assertion: at least one stack synthesized
    assert len(assembly.stacks) >= 1
