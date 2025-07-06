import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.storage.lakeformation_stack import LakeFormationStack


# --- Happy path: S3 Resource creation (config-based) ---
def test_lakeformation_stack_resource_creation_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}]
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Resource", 1)
    outputs = template.to_json().get("Outputs", {})
    assert "TestLakeFormationStackLakeFormationResourcebucket1Arn" in outputs


# --- Happy path: S3 Resource creation (cross-stack S3 bucket constructs) ---
def test_lakeformation_stack_resource_creation_s3_buckets():
    from aws_cdk import aws_s3 as s3

    app = App()
    test_stack = Stack(app, "TestStack")
    s3_bucket = s3.Bucket(test_stack, "TestBucket", bucket_name="bucket2")
    s3_buckets = {"TestBucket": s3_bucket}
    config = {"lakeformation": {}, "app": {"env": "test"}}
    stack = LakeFormationStack(
        test_stack, "TestLakeFormationStack", config=config, s3_buckets=s3_buckets
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Resource", 1)
    outputs = template.to_json().get("Outputs", {})
    assert "TestLakeFormationStackLakeFormationResourceTestBucketArn" in outputs


# --- Happy path: Permissions creation ---
def test_lakeformation_stack_permissions_creation():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}],
            "permissions": [
                {
                    "principal": "LAKEFORMATION_ADMIN_ROLE_ARN",
                    "resource": {
                        "dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}
                    },
                    "permissions": ["DATA_LOCATION_ACCESS"],
                }
            ],
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(
        test_stack,
        "TestLakeFormationStack",
        config=config,
        lakeformation_admin_role_arn="arn:aws:iam::123456789012:role/MockLakeFormationAdminRole",
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Permissions", 1)
    outputs = template.to_json().get("Outputs", {})
    assert any("Principal" in k for k in outputs.keys())


# --- Happy path: Tagging ---
def test_lakeformation_stack_tags():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}],
            "tags": {"Owner": "DataTeam"},
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "DataTeam" for tag in tags
    )


# --- Happy path: Removal policy (dev vs prod) ---
def test_lakeformation_stack_removal_policy():
    app = App()
    test_stack = Stack(app, "TestStack")
    config_dev = {
        "lakeformation": {
            "buckets": [
                {
                    "name": "bucketdev",
                    "arn": "arn:aws:s3:::bucketdev",
                    "removal_policy": "DESTROY",
                }
            ]
        },
        "app": {"env": "dev"},
    }
    config_prod = {
        "lakeformation": {
            "buckets": [{"name": "bucketprod", "arn": "arn:aws:s3:::bucketprod"}]
        },
        "app": {"env": "prod"},
    }
    stack_dev = LakeFormationStack(
        test_stack, "TestLakeFormationStackDev", config=config_dev
    )
    stack_prod = LakeFormationStack(
        test_stack, "TestLakeFormationStackProd", config=config_prod
    )
    template_dev = assertions.Template.from_stack(stack_dev)
    template_prod = assertions.Template.from_stack(stack_prod)
    # RemovalPolicy is not directly exposed, but we can check resource exists
    template_dev.resource_count_is("AWS::LakeFormation::Resource", 1)
    template_prod.resource_count_is("AWS::LakeFormation::Resource", 1)


# --- Happy path: Monitoring event rule present ---
def test_lakeformation_stack_monitoring_event_rule():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}]
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Events::Rule")
    assert any("LakeFormationFailureRule" in k for k in resources)


# --- Unhappy path: Buckets not a list ---
def test_lakeformation_stack_buckets_not_list():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"lakeformation": {"buckets": "notalist"}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)


# --- Unhappy path: Duplicate bucket names ---
def test_lakeformation_stack_duplicate_bucket_names():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [
                {"name": "dup", "arn": "arn:aws:s3:::bucket1"},
                {"name": "dup", "arn": "arn:aws:s3:::bucket2"},
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)


# --- Unhappy path: Permissions not a list ---
def test_lakeformation_stack_permissions_not_list():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"lakeformation": {"permissions": "notalist"}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)


# --- Unhappy path: Duplicate permissions ---
def test_lakeformation_stack_duplicate_permissions():
    app = App()
    test_stack = Stack(app, "TestStack")
    perm = {
        "principal": "arn:aws:iam::123456789012:role/LakeAdmin",
        "resource": {"dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}},
        "permissions": ["DATA_LOCATION_ACCESS"],
    }
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}],
            "permissions": [perm, perm],
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)


# --- Unhappy path: Missing required fields in bucket ---
def test_lakeformation_stack_bucket_missing_fields():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {"buckets": [{"name": "bucket1"}]},
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)


# --- Unhappy path: Missing required fields in permission ---
def test_lakeformation_stack_permission_missing_fields():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "permissions": [{"principal": "arn:aws:iam::123456789012:role/LakeAdmin"}]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
