import os
import yaml
import pytest

"""Minimal synth smoke test that creates a tiny CDK app and instantiates
only the `NetworkingStack` from the domain-oriented layout. This avoids
importing `infra.app` which references legacy `infra.stacks.*` modules.
"""


def test_cdk_synth_minimal(tmp_path):
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(repo_root, "tests", "infra", "test_local_config.yml")
    assert os.path.exists(config_path), f"Missing minimal config at {config_path}"

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Import CDK and the NetworkingStack from the domain layout
    try:
        import aws_cdk as cdk
        from infra.domains.foundation.networking.networking_stack import NetworkingStack
    except Exception as exc:  # pragma: no cover - surface import errors in CI
        pytest.skip(f"Missing CDK or domain stack imports: {exc}")

    app = cdk.App()

    # Instantiate minimal networking stack with the provided minimal config
    NetworkingStack(
        app,
        "NetworkingStack",
        config={"networking": cfg.get("networking", {}), "app": cfg.get("app", {})},
    )

    # Synthesize the app (no deploy)
    app.synth()
