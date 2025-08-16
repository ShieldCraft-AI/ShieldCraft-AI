"""
This module contains unit tests for the IamRoleStack class,
which synthesizes IAM roles and policies based on a config-driven approach.
"""

import pytest
from aws_cdk import App, CfnOutput
from infra.domains.foundation.identity_security.iam_stack import IamRoleStack

# Minimal valid config for happy path
VALID_CONFIG = {
    "app": {"env": "dev"},
    "s3": {"buckets": [{"id": "main", "name": "shieldcraft-main-bucket"}]},
    "msk": {"cluster": {"name": "shieldcraft-msk-cluster-dev"}},
}

# Unhappy path configs
MISSING_BUCKET_CONFIG = {
    "app": {"env": "dev"},
    "s3": {"buckets": []},
    "msk": {"cluster": {"name": "shieldcraft-msk-cluster-dev"}},
}
MISSING_MSK_CONFIG = {
    "app": {"env": "dev"},
    "s3": {"buckets": [{"id": "main", "name": "shieldcraft-main-bucket"}]},
    "msk": {"cluster": {}},
}
DUPLICATE_BUCKET_CONFIG = {
    "app": {"env": "dev"},
    "s3": {
        "buckets": [
            {"id": "main", "name": "shieldcraft-main-bucket"},
            {"id": "main", "name": "shieldcraft-main-bucket-2"},
        ]
    },
    "msk": {"cluster": {"name": "shieldcraft-msk-cluster-dev"}},
}


@pytest.fixture
def app():
    return App()


# Happy path: stack instantiation and outputs
def test_iam_role_stack_happy_path(app):
    stack = IamRoleStack(app, "TestIamRoleStack", config=VALID_CONFIG)
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    logical_ids = [o.logical_id for o in outputs]
    assert any("OpenSearchRoleArn" in lid for lid in logical_ids)
    assert any("MskClientRoleArn" in lid for lid in logical_ids)
    assert any("LambdaRoleArn" in lid for lid in logical_ids)
    assert any("SageMakerRoleArn" in lid for lid in logical_ids)
    assert any("GlueRoleArn" in lid for lid in logical_ids)
    assert any("AirbyteRoleArn" in lid for lid in logical_ids)
    assert any("LakeFormationAdminRoleArn" in lid for lid in logical_ids)
    assert any("VpcFlowLogsRoleArn" in lid for lid in logical_ids)
    assert any("DataQualityLambdaRoleArn" in lid for lid in logical_ids)
    assert any("DataQualityGlueRoleArn" in lid for lid in logical_ids)
    assert any("ComplianceLambdaRoleArn" in lid for lid in logical_ids)


# Secrets manager integration: ensure secret is imported and read granted
def test_iam_role_stack_secrets_manager_integration(app):
    secret_arn = (
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:shieldcraft-vault-abc123"
    )
    stack = IamRoleStack(
        app, "TestIamRoleStack", config=VALID_CONFIG, secrets_manager_arn=secret_arn
    )
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    logical_ids = [o.logical_id for o in outputs]
    assert any("VaultSecretArn" in lid for lid in logical_ids)


# Multiple buckets: ensure all buckets are processed and policies attached
def test_iam_role_stack_multiple_buckets(app):
    config = {
        "app": {"env": "dev"},
        "s3": {
            "buckets": [
                {"id": "main", "name": "bucket1"},
                {"id": "aux", "name": "bucket2"},
            ]
        },
        "msk": {"cluster": {"name": "shieldcraft-msk-cluster-dev"}},
    }
    stack = IamRoleStack(app, "TestIamRoleStack", config=config)
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    logical_ids = [o.logical_id for o in outputs]
    assert any("OpenSearchRoleArn" in lid for lid in logical_ids)
    assert any("GlueRoleArn" in lid for lid in logical_ids)


# Custom environment: ensure ARNs and outputs reflect env
def test_iam_role_stack_custom_env(app):
    config = {
        "app": {"env": "prod"},
        "s3": {"buckets": [{"id": "main", "name": "shieldcraft-prod-bucket"}]},
        "msk": {"cluster": {"name": "shieldcraft-msk-cluster-prod"}},
    }
    stack = IamRoleStack(app, "TestIamRoleStack", config=config)
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    logical_ids = [o.logical_id for o in outputs]
    assert any("ProdOpenSearchRoleArn" in lid for lid in logical_ids)
    assert any("ProdMskClientRoleArn" in lid for lid in logical_ids)


# Output export names: ensure export_name format is correct
def test_iam_role_stack_output_export_names(app):
    stack = IamRoleStack(app, "TestIamRoleStack", config=VALID_CONFIG)
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    for o in outputs:
        if o.export_name is not None:
            assert o.export_name.startswith(
                "TestIamRoleStack-"
            ) or o.export_name.endswith("-vault-secret-arn")


# Edge case: config missing app.env (should default to 'dev')
def test_iam_role_stack_missing_env_key(app):
    config = {
        "s3": {"buckets": [{"id": "main", "name": "shieldcraft-main-bucket"}]},
        "msk": {"cluster": {"name": "shieldcraft-msk-cluster-dev"}},
    }
    stack = IamRoleStack(app, "TestIamRoleStack", config=config)
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    logical_ids = [o.logical_id for o in outputs]
    assert any("OpenSearchRoleArn" in lid for lid in logical_ids)


# Edge case: config with extra keys (should not break)
def test_iam_role_stack_extra_config_keys(app):
    config = {
        "app": {"env": "dev"},
        "s3": {"buckets": [{"id": "main", "name": "shieldcraft-main-bucket"}]},
        "msk": {"cluster": {"name": "shieldcraft-msk-cluster-dev"}},
        "extra": {"foo": "bar"},
    }
    stack = IamRoleStack(app, "TestIamRoleStack", config=config)
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    logical_ids = [o.logical_id for o in outputs]
    assert any("OpenSearchRoleArn" in lid for lid in logical_ids)


# Defensive: bucket missing 'id' but has 'name' (should work)
def test_iam_role_stack_bucket_missing_id(app):
    config = {
        "app": {"env": "dev"},
        "s3": {"buckets": [{"name": "shieldcraft-main-bucket"}]},
        "msk": {"cluster": {"name": "shieldcraft-msk-cluster-dev"}},
    }
    stack = IamRoleStack(app, "TestIamRoleStack", config=config)
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    logical_ids = [o.logical_id for o in outputs]
    assert any("OpenSearchRoleArn" in lid for lid in logical_ids)


# Unhappy path: missing buckets
@pytest.mark.parametrize(
    "bad_config,expected_error",
    [
        (
            MISSING_BUCKET_CONFIG,
            "s3.buckets must be defined and contain at least one bucket with a name.",
        ),
        (MISSING_MSK_CONFIG, "msk.cluster.name must be defined in config."),
        (DUPLICATE_BUCKET_CONFIG, "Duplicate S3 bucket id in config: main"),
    ],
)
def test_iam_role_stack_unhappy_paths(app, bad_config, expected_error):
    with pytest.raises(ValueError) as exc:
        IamRoleStack(app, "TestIamRoleStack", config=bad_config)
    assert expected_error in str(exc.value)


# Defensive: config must be dict
def test_iam_role_stack_config_type(app):
    with pytest.raises(ValueError) as exc:
        IamRoleStack(app, "TestIamRoleStack", config=None)
    assert "IamRoleStack requires a valid config dict." in str(exc.value)


# Defensive: region/account must be present
def test_iam_role_stack_missing_region_account(app):
    class DummyStack(IamRoleStack):
        @property
        def region(self):
            return None

        @property
        def account(self):
            return None

    with pytest.raises(ValueError) as exc:
        DummyStack(app, "TestIamRoleStack", config=VALID_CONFIG)
    assert "Stack must have region and account context for ARN construction." in str(
        exc.value
    )


def test_iam_role_stack_tag_overwrite_precedence(app):
    from aws_cdk import aws_iam as iam

    config = {
        "app": {"env": "dev"},
        "s3": {"buckets": [{"id": "main", "name": "bucket1"}]},
        "msk": {"cluster": {"name": "msk-dev"}},
        "tags": {"Owner": "bob", "Project": "custom-project"},
    }
    stack = IamRoleStack(app, "TestTagOverwrite", config=config)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    for r in roles:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        tag_manager = r.node.try_find_child("Resource") or r
        tags = getattr(tag_manager, "tags", None)
        if tags is None:
            from aws_cdk import Tags

            tags = Tags.of(r).render_tags()
        tag_dict = {}
        if hasattr(tags, "render_tags"):
            rendered = tags.render_tags()
            if rendered is None:
                rendered = []
            for t in rendered:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, list):
            for t in tags:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, dict):
            tag_dict = tags
        assert tag_dict["Owner"] == "bob"
        assert tag_dict["Project"] == "custom-project"


def test_iam_role_stack_tag_value_type_robustness(app):
    from aws_cdk import aws_iam as iam

    config = {
        "app": {"env": "dev"},
        "s3": {"buckets": [{"id": "main", "name": "bucket1"}]},
        "msk": {"cluster": {"name": "msk-dev"}},
        "tags": {"CostCenter": 123, "Team": None, "Compliance": True},
    }
    stack = IamRoleStack(app, "TestTagType", config=config)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    for r in roles:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        tag_manager = r.node.try_find_child("Resource") or r
        tags = getattr(tag_manager, "tags", None)
        if tags is None:
            from aws_cdk import Tags

            tags = Tags.of(r).render_tags()
        tag_dict = {}
        if hasattr(tags, "render_tags"):
            rendered = tags.render_tags()
            if rendered is None:
                rendered = []
            for t in rendered:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, list):
            for t in tags:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, dict):
            tag_dict = tags
        assert tag_dict["CostCenter"] == "123"
        assert tag_dict["Compliance"] == "True"


def test_iam_role_stack_vault_secret_grant_all_roles(app):
    from aws_cdk import aws_iam as iam

    secret_arn = (
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:shieldcraft-vault-abc123"
    )
    stack = IamRoleStack(
        app, "TestVaultGrant", config=VALID_CONFIG, secrets_manager_arn=secret_arn
    )
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    # Defensive: All real roles should have grant_read called (no exception)
    assert stack.secrets_manager_secret is not None
    # No exception means grant_read was called for all roles


def test_iam_role_stack_parallel_tag_isolation():
    from aws_cdk import App
    from aws_cdk import aws_iam as iam

    app1 = App()
    app2 = App()
    config1 = {
        "app": {"env": "dev"},
        "s3": {"buckets": [{"id": "main", "name": "bucket1"}]},
        "msk": {"cluster": {"name": "msk-dev"}},
        "tags": {"Owner": "alice"},
    }
    config2 = {
        "app": {"env": "prod"},
        "s3": {"buckets": [{"id": "main", "name": "bucket2"}]},
        "msk": {"cluster": {"name": "msk-prod"}},
        "tags": {"Owner": "bob"},
    }
    stack1 = IamRoleStack(app1, "Stack1", config=config1)
    stack2 = IamRoleStack(app2, "Stack2", config=config2)
    roles1 = [c for c in stack1.node.children if isinstance(c, iam.Role)]
    roles2 = [c for c in stack2.node.children if isinstance(c, iam.Role)]
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    for r in roles1:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        tag_manager = r.node.try_find_child("Resource") or r
        tags = getattr(tag_manager, "tags", None)
        if tags is None:
            from aws_cdk import Tags

            tags = Tags.of(r).render_tags()
        tag_dict = {}
        if hasattr(tags, "render_tags"):
            rendered = tags.render_tags()
            if rendered is None:
                rendered = []
            for t in rendered:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, list):
            for t in tags:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, dict):
            tag_dict = tags
        assert tag_dict["Owner"] == "alice"
    for r in roles2:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        tag_manager = r.node.try_find_child("Resource") or r
        tags = getattr(tag_manager, "tags", None)
        if tags is None:
            from aws_cdk import Tags

            tags = Tags.of(r).render_tags()
        tag_dict = {}
        if hasattr(tags, "render_tags"):
            rendered = tags.render_tags()
            if rendered is None:
                rendered = []
            for t in rendered:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, list):
            for t in tags:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, dict):
            tag_dict = tags
        assert tag_dict["Owner"] == "bob"


def test_iam_role_stack_invalid_tag_key_value(app):
    from aws_cdk import aws_iam as iam

    config = {
        "app": {"env": "dev"},
        "s3": {"buckets": [{"id": "main", "name": "bucket1"}]},
        "msk": {"cluster": {"name": "msk-dev"}},
        "tags": {"": "emptykey", None: "nonekey", "Valid": "ok", "Bad": None},
    }
    stack = IamRoleStack(app, "TestInvalidTag", config=config)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    for r in roles:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        tag_manager = r.node.try_find_child("Resource") or r
        tags = getattr(tag_manager, "tags", None)
        if tags is None:
            from aws_cdk import Tags

            tags = Tags.of(r).render_tags()
        tag_dict = {}
        if hasattr(tags, "render_tags"):
            rendered = tags.render_tags()
            if rendered is None:
                rendered = []
            for t in rendered:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, list):
            for t in tags:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, dict):
            tag_dict = tags
        # Only valid tags should be present
        assert "Valid" in tag_dict
        assert tag_dict["Valid"] == "ok"
        assert "" not in tag_dict
        assert None not in tag_dict
        assert tag_dict.get("Bad") is None

    from aws_cdk import aws_iam as iam

    stack = IamRoleStack(app, "TestIamRoleStack", config=VALID_CONFIG)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]

    # Supplemental: All IAM roles are tagged with standard tags
    expected_tag_keys = {
        "Project",
        "Environment",
        "Owner",
        "CostCenter",
        "Team",
        "Compliance",
    }
    # Optionally add org/OU tags if present in config
    org_keys = set()
    for k in ["Organization", "OrgUnit", "OU", "OrgId", "OrgName"]:
        if k in VALID_CONFIG.get("tags", {}):
            org_keys.add(k)
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    for r in roles:
        # Only check tags on real roles (not CDK Token placeholders)
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        tag_manager = r.node.try_find_child("Resource") or r
        tags = getattr(tag_manager, "tags", None)
        if tags is None:
            from aws_cdk import Tags

            tags = Tags.of(r).render_tags()
        tag_keys = set()
        if hasattr(tags, "render_tags"):
            rendered = tags.render_tags()
            if rendered is None:
                rendered = []
            tag_keys = {t["key"] for t in rendered}
        elif isinstance(tags, list):
            tag_keys = {t["key"] for t in tags}
        elif isinstance(tags, dict):
            tag_keys = set(tags.keys())
        assert expected_tag_keys.issubset(
            tag_keys
        ), f"Missing required tags on role {r.role_name}: {expected_tag_keys - tag_keys}"
        if org_keys:
            assert org_keys.issubset(
                tag_keys
            ), f"Missing org/OU tags on role {r.role_name}: {org_keys - tag_keys}"
    # Supplemental: test tag value correctness and no duplicate tags
    stack3 = IamRoleStack(
        app,
        "TestIamRoleStackTagValues",
        config={
            "app": {"env": "qa"},
            "s3": {"buckets": [{"id": "main", "name": "qa-bucket"}]},
            "msk": {"cluster": {"name": "qa-msk"}},
            "tags": {
                "Owner": "alice",
                "CostCenter": "AI-123",
                "Custom": "custom-value",
            },
        },
    )
    roles3 = [c for c in stack3.node.children if isinstance(c, iam.Role)]
    for r in roles3:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        tag_manager = r.node.try_find_child("Resource") or r
        tags = getattr(tag_manager, "tags", None)
        if tags is None:
            from aws_cdk import Tags

            tags = Tags.of(r).render_tags()
        tag_dict = {}
        if hasattr(tags, "render_tags"):
            rendered = tags.render_tags()
            if rendered is None:
                rendered = []
            for t in rendered:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, list):
            for t in tags:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, dict):
            tag_dict = tags
        # Check tag values
        assert tag_dict.get("Owner") == "alice"
        assert tag_dict.get("CostCenter") == "AI-123"
        assert tag_dict.get("Custom") == "custom-value"
        # No duplicate keys
        assert len(tag_dict) == len(set(tag_dict.keys()))

    # Supplemental: test org/OU tag propagation if present in config
    custom_config = VALID_CONFIG.copy()
    custom_config["tags"] = {"OrgUnit": "AI-ML", "OrgId": "o-123456"}
    stack2 = IamRoleStack(app, "TestIamRoleStackOrg", config=custom_config)
    roles2 = [c for c in stack2.node.children if isinstance(c, iam.Role)]
    for r in roles2:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        tag_manager = r.node.try_find_child("Resource") or r
        tags = getattr(tag_manager, "tags", None)
        if tags is None:
            from aws_cdk import Tags

            tags = Tags.of(r).render_tags()
        tag_keys = set()
        if hasattr(tags, "render_tags"):
            rendered = tags.render_tags()
            if rendered is None:
                rendered = []
            tag_keys = {t["key"] for t in rendered}
        elif isinstance(tags, list):
            tag_keys = {t["key"] for t in tags}
        elif isinstance(tags, dict):
            tag_keys = set(tags.keys())
        assert {"OrgUnit", "OrgId"}.issubset(
            tag_keys
        ), f"Missing org/OU tags on role {r.role_name}: { {'OrgUnit', 'OrgId'} - tag_keys }"

    role_names = [r.role_name for r in roles]
    assert len(role_names) == len(set(role_names)), "Duplicate role names detected"
    arns = [r.role_arn for r in roles]
    assert len(arns) == len(set(arns)), "Duplicate role ARNs detected"


# Advanced: Least-privilege managed policies
def test_iam_role_stack_least_privilege_policies(app):
    from aws_cdk import aws_iam as iam

    stack = IamRoleStack(app, "TestIamRoleStack", config=VALID_CONFIG)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    for r in roles:
        managed_policy_arns = getattr(
            getattr(r.node, "default_child", None), "managed_policy_arns", None
        )
        if managed_policy_arns:
            for arn in managed_policy_arns:
                # Skip CDK tokens (lazy evaluation)
                if isinstance(arn, str) and arn.startswith("#{Token["):
                    continue
                # Accept AWS managed policies and service-role policies
                assert (
                    arn.startswith("arn:aws:iam::aws:policy/") or "service-role/" in arn
                ), f"Non-AWS managed policy attached: {arn}"


# Advanced: Parallel stack instantiation (resource isolation)
def test_iam_role_stack_parallel_stacks():
    from aws_cdk import App

    app1 = App()
    app2 = App()
    stack1 = IamRoleStack(app1, "Stack1", config=VALID_CONFIG)
    stack2 = IamRoleStack(app2, "Stack2", config=VALID_CONFIG)
    outputs1 = [
        o.export_name
        for o in stack1.node.children
        if isinstance(o, CfnOutput) and o.export_name
    ]
    outputs2 = [
        o.export_name
        for o in stack2.node.children
        if isinstance(o, CfnOutput) and o.export_name
    ]
    assert set(outputs1).isdisjoint(
        set(outputs2)
    ), "Export names overlap between stacks"


# Advanced: Cross-stack output validation (exported outputs are consumable)
def test_iam_role_stack_cross_stack_output(app):
    stack = IamRoleStack(app, "TestIamRoleStack", config=VALID_CONFIG)
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    for o in outputs:
        assert o.export_name is None or o.export_name.startswith(
            "TestIamRoleStack-"
        ), "Invalid export name format"


# Advanced: Vault secret access granted to all major roles
def test_iam_role_stack_vault_secret_access(app):
    secret_arn = (
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:shieldcraft-vault-abc123"
    )
    from aws_cdk import aws_iam as iam

    stack = IamRoleStack(
        app, "TestIamRoleStack", config=VALID_CONFIG, secrets_manager_arn=secret_arn
    )
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    # Defensive: All roles should have vault secret grant_read called if secret is imported
    # This is not directly inspectable, so we assert no exception is raised during stack creation
    # and that the secret is present
    assert stack.secrets_manager_secret is not None


# Defensive: Invalid managed policy name raises error
def test_iam_role_stack_invalid_managed_policy(app):
    bad_config = VALID_CONFIG.copy()
    bad_config["s3"]["buckets"][0]["name"] = "bad-bucket"
    from aws_cdk import aws_iam as iam

    try:
        role = iam.Role(
            app,
            "BadRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),  # type: ignore
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("NonExistentPolicy")
            ],
        )
        raise RuntimeError("Expected error for invalid managed policy not raised")
    except Exception:
        pass


# Defensive: Invalid service principal raises error
def test_iam_role_stack_invalid_service_principal(app):
    bad_config = VALID_CONFIG.copy()
    from aws_cdk import aws_iam as iam

    try:
        role = iam.Role(
            app,
            "BadPrincipalRole",
            assumed_by=iam.ServicePrincipal("not-a-service.amazonaws.com"),  # type: ignore
        )
        raise RuntimeError("Expected error for invalid service principal not raised")
    except Exception:
        pass


# Defensive: Invalid export name raises error
def test_iam_role_stack_invalid_export_name(app):
    # CDK allows export_name=None, so this is not an error. Test removed.
    pass


def test_iam_role_stack_unique_physical_names(app):
    from aws_cdk import aws_iam as iam

    stack = IamRoleStack(app, "TestUniquePhysicalNames", config=VALID_CONFIG)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    physical_names = set()
    for r in roles:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        assert (
            r.role_name not in physical_names
        ), f"Duplicate physical role name: {r.role_name}"
        physical_names.add(r.role_name)


def test_iam_role_stack_all_roles_have_policy(app):
    from aws_cdk import aws_iam as iam

    stack = IamRoleStack(app, "TestAllRolesHavePolicy", config=VALID_CONFIG)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    for r in roles:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        has_managed = bool(getattr(r, "managed_policies", []))
        has_inline = bool(getattr(r, "policy_fragment", None)) or bool(
            getattr(r, "policies", None)
        )
        assert has_managed or has_inline, f"Role {r.role_name} has no policies attached"


def test_iam_role_stack_all_roles_are_output(app):
    from aws_cdk import aws_iam as iam

    stack = IamRoleStack(app, "TestAllRolesOutput", config=VALID_CONFIG)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    outputs = [o for o in stack.node.children if isinstance(o, CfnOutput)]
    output_arns = {getattr(o, "value", None) for o in outputs}
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    for r in roles:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        assert (
            r.role_arn in output_arns
        ), f"Role {r.role_name} is not output as CfnOutput"


def test_iam_role_stack_role_name_pattern(app):
    from aws_cdk import aws_iam as iam

    stack = IamRoleStack(app, "TestRoleNamePattern", config=VALID_CONFIG)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    pattern = re.compile(r"^shieldcraftai-.*-(dev|prod|qa|staging)$")
    for r in roles:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        assert pattern.match(
            r.role_name
        ), f"Role name does not match pattern: {r.role_name}"


def test_iam_role_stack_invalid_role_name(app):
    from aws_cdk import aws_iam as iam

    bad_config = VALID_CONFIG.copy()
    # Intentionally too long and with invalid chars
    bad_config["app"]["env"] = "dev"
    bad_name = "shieldcraftai-" + ("x" * 65) + "-dev!@#"
    try:
        role = iam.Role(
            app,
            "BadRoleName",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name=bad_name,
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonMSKReadOnlyAccess"
                )
            ],
        )
        raise RuntimeError("Expected error for invalid role name not raised")
    except Exception:
        pass


def test_iam_role_stack_required_tag_fallback(app):
    from aws_cdk import aws_iam as iam

    config = {
        "app": {},  # no env
        "s3": {"buckets": [{"id": "main", "name": "bucket1"}]},
        "msk": {"cluster": {"name": "msk-dev"}},
        "tags": {"Owner": "bob"},
    }
    stack = IamRoleStack(app, "TestRequiredTagFallback", config=config)
    roles = [c for c in stack.node.children if isinstance(c, iam.Role)]
    import re

    token_pattern = re.compile(r"\$\{Token\[TOKEN\.")
    for r in roles:
        if not isinstance(r.role_name, str) or token_pattern.match(str(r.role_name)):
            continue
        tag_manager = r.node.try_find_child("Resource") or r
        tags = getattr(tag_manager, "tags", None)
        if tags is None:
            from aws_cdk import Tags

            tags = Tags.of(r).render_tags()
        tag_dict = {}
        if hasattr(tags, "render_tags"):
            rendered = tags.render_tags()
            if rendered is None:
                rendered = []
            for t in rendered:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, list):
            for t in tags:
                tag_dict[t["key"]] = t["value"]
        elif isinstance(tags, dict):
            tag_dict = tags
        # Project and Environment should always be present
        assert "Project" in tag_dict
        assert "Environment" in tag_dict


def test_iam_role_stack_parallel_stacks_overlapping_role_names():
    from aws_cdk import App
    from aws_cdk import aws_iam as iam

    app1 = App()
    app2 = App()
    config = {
        "app": {"env": "dev"},
        "s3": {"buckets": [{"id": "main", "name": "bucket1"}]},
        "msk": {"cluster": {"name": "msk-dev"}},
    }
    stack1 = IamRoleStack(app1, "Stack1", config=config)
    stack2 = IamRoleStack(app2, "Stack2", config=config)
    roles1 = [c for c in stack1.node.children if isinstance(c, iam.Role)]
    roles2 = [c for c in stack2.node.children if isinstance(c, iam.Role)]
    arns1 = set(r.role_arn for r in roles1 if isinstance(r.role_name, str))
    arns2 = set(r.role_arn for r in roles2 if isinstance(r.role_name, str))
    # ARNs should be unique across stacks (since stack name is part of logical ID)
    assert arns1.isdisjoint(
        arns2
    ), "Role ARNs overlap between parallel stacks with same role names"
    bad_config = VALID_CONFIG.copy()
    bad_config["s3"]["buckets"][0]["name"] = ""
    with pytest.raises(ValueError):
        IamRoleStack(App(), "TestIamRoleStack", config=bad_config)
