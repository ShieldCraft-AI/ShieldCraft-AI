import pytest
from aws_cdk import App, assertions
from infra.stacks.s3_stack import S3Stack
from aws_cdk import RemovalPolicy

def minimal_s3_config():
    return {
        "s3": {
            "buckets": [
                {
                    "id": "RawDataBucket",
                    "name": "test-raw",
                    "versioned": True,
                    "encryption": "S3_MANAGED",
                    "block_public_access": "BLOCK_ALL",
                    "removal_policy": "DESTROY"
                }
            ],
            "tags": {"Owner": "S3Team"}
        },
        "app": {"env": "test"}
    }

# --- Happy path: S3 bucket creation ---
def test_s3_stack_synthesizes():
    app = App()
    stack = S3Stack(app, "TestS3Stack", config=minimal_s3_config())
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties("AWS::S3::Bucket", {
        "BucketName": "test-raw"
    })
    outputs = template.to_json().get("Outputs", {})
    assert "TestS3StackS3BucketRawDataBucketName" in outputs
    assert "TestS3StackS3BucketRawDataBucketArn" in outputs

# --- Happy path: Tagging ---
def test_s3_stack_tags():
    app = App()
    stack = S3Stack(app, "TestS3Stack", config=minimal_s3_config())
    tags = stack.tags.render_tags()
    assert any(tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI" for tag in tags)
    assert any(tag.get("Key") == "Owner" and tag.get("Value") == "S3Team" for tag in tags)

# --- Unhappy path: buckets not a list or empty ---
def test_s3_stack_buckets_not_list():
    app = App()
    config = {"s3": {"buckets": "notalist"}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        S3Stack(app, "TestS3Stack", config=config)

def test_s3_stack_buckets_empty():
    app = App()
    config = {"s3": {"buckets": []}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        S3Stack(app, "TestS3Stack", config=config)

# --- Unhappy path: Duplicate bucket id ---
def test_s3_stack_duplicate_bucket_id():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {"id": "dup", "name": "bucket1"},
                {"id": "dup", "name": "bucket2"}
            ]
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        S3Stack(app, "TestS3Stack", config=config)

# --- Unhappy path: Missing required fields ---
def test_s3_stack_missing_required_fields():
    app = App()
    config = {"s3": {"buckets": [{"id": "missing"}]}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        S3Stack(app, "TestS3Stack", config=config)
