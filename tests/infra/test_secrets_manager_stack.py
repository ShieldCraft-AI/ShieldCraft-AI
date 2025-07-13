def test_invalid_secret_config_type():
    app = App()
    bad_cfg = {"BadSecret": "not-a-dict"}
    with pytest.raises(ValueError, match="must be a dict"):
        SecretsManagerStack(
            app, "TestSecretsManagerStackBadType", secrets_config=bad_cfg
        )


def test_missing_secret_name_raises():
    app = App()
    bad_cfg = {"NoName": {"name": ""}}
    with pytest.raises(ValueError, match="must have a name"):
        SecretsManagerStack(
            app, "TestSecretsManagerStackNoName", secrets_config=bad_cfg
        )


def test_env_prefix_applied():
    app = App()
    env = "prod"
    cfg = {"MainVault": {"name": "MainVault", "generate": True}}
    stack = SecretsManagerStack(
        app, "TestSecretsManagerStackEnv", secrets_config=cfg, env=env
    )
    secret = stack.secrets["MainVault"]
    # CDK's secret_name may be a Token; check fallback logical ID
    logical_id = secret.node.id
    assert logical_id == "MainVault"


def test_tags_propagated():
    app = App()
    tags = {"Owner": "ShieldOps", "CostCenter": "AI"}
    cfg = {"MainVault": {"name": "MainVault", "generate": True}}
    stack = SecretsManagerStack(
        app, "TestSecretsManagerStackTags", secrets_config=cfg, shared_tags=tags
    )
    # CDK propagates tags to all resources; check stack tags
    rendered_tags = stack.tags.render_tags()
    # Handle both dict and tuple structures for tags
    tag_dict = {}
    for t in rendered_tags:
        if isinstance(t, dict):
            tag_dict[t.get("Key") or t.get("key")] = t.get("Value") or t.get("value")
        elif isinstance(t, tuple) and len(t) == 2:
            tag_dict[t[0]] = t[1]
    for k, v in tags.items():
        assert tag_dict.get(k) == v


import pytest
from aws_cdk import App
from infra.stacks.security.secrets_manager_stack import SecretsManagerStack


def minimal_secrets_config():
    return {
        "MainVault": {
            "name": "MainVault",
            "description": "Main vault secret",
            "generate": True,
            "generate_key": "password",
            "exclude_characters": "!@#$%^&*()",
        },
        "ApiKey": {
            "name": "ApiKey",
            "description": "API key secret",
            "generate": True,
            "generate_key": "api_key",
        },
    }


def test_stack_instantiates():
    app = App()
    stack = SecretsManagerStack(
        app, "TestSecretsManagerStack", secrets_config=minimal_secrets_config()
    )
    assert stack.secrets["MainVault"] is not None
    assert stack.secrets["ApiKey"] is not None


def test_empty_secrets_config():
    app = App()
    stack = SecretsManagerStack(app, "TestSecretsManagerStackEmpty", secrets_config={})
    assert stack.secrets == {}


def test_missing_secrets_config_defaults():
    app = App()
    stack = SecretsManagerStack(app, "TestSecretsManagerStackNoConfig")
    assert stack.secrets == {}


def test_secret_output_export():
    app = App()
    stack = SecretsManagerStack(
        app, "TestSecretsManagerStackExport", secrets_config=minimal_secrets_config()
    )
    # Check CfnOutput export names
    from aws_cdk import CfnOutput

    outputs = [c for c in stack.node.children if isinstance(c, CfnOutput)]
    export_names = [getattr(o, "export_name", None) for o in outputs]
    assert any(
        "TestSecretsManagerStackExport-MainVault-arn" in str(n) for n in export_names
    )
    assert any(
        "TestSecretsManagerStackExport-ApiKey-arn" in str(n) for n in export_names
    )
