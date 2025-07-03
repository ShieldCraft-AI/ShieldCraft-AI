
import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.lakeformation_stack import LakeFormationStack

# --- Happy path: S3 Resource creation ---
def test_lakeformation_stack_resource_creation():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [
                {"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}
            ]
        },
        "app": {"env": "test"}
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Resource", 1)
    outputs = template.to_json().get("Outputs", {})
    assert "TestLakeFormationStackLakeFormationResourcebucket1Arn" in outputs

# --- Happy path: Permissions creation ---
def test_lakeformation_stack_permissions_creation():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [
                {"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}
            ],
            "permissions": [
                {"principal": "arn:aws:iam::123456789012:role/LakeAdmin", "resource": {"dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}}, "permissions": ["DATA_LOCATION_ACCESS"]}
            ]
        },
        "app": {"env": "test"}
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Permissions", 1)
    outputs = template.to_json().get("Outputs", {})
    assert any("Principal" in k for k in outputs.keys())

# --- Happy path: Tagging ---
def test_lakeformation_stack_tags():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {"buckets": [], "tags": {"Owner": "DataTeam"}},
        "app": {"env": "test"}
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    tags = stack.tags.render_tags()
    assert any(tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI" for tag in tags)
    assert any(tag.get("Key") == "Owner" and tag.get("Value") == "DataTeam" for tag in tags)

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
                {"name": "dup", "arn": "arn:aws:s3:::bucket2"}
            ]
        },
        "app": {"env": "test"}
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
    perm = {"principal": "arn:aws:iam::123456789012:role/LakeAdmin", "resource": {"dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}}, "permissions": ["DATA_LOCATION_ACCESS"]}
    config = {
        "lakeformation": {
            "buckets": [
                {"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}
            ],
            "permissions": [perm, perm]
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)

# --- Unhappy path: Missing required fields in bucket ---
def test_lakeformation_stack_bucket_missing_fields():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"lakeformation": {"buckets": [{"name": "bucket1"}]}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)

# --- Unhappy path: Missing required fields in permission ---
def test_lakeformation_stack_permission_missing_fields():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"lakeformation": {"permissions": [{"principal": "arn:aws:iam::123456789012:role/LakeAdmin"}]}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
