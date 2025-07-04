import pytest
from aws_cdk import App, assertions
from infra.stacks.storage.s3_stack import S3Stack


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
                    "removal_policy": "DESTROY",
                }
            ],
            "tags": {"Owner": "S3Team"},
        },
        "app": {"env": "test"},
    }


# --- Happy path: S3 bucket creation ---
def test_s3_stack_synthesizes():
    app = App()
    stack = S3Stack(app, "TestS3Stack", config=minimal_s3_config())
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties("AWS::S3::Bucket", {"BucketName": "test-raw"})
    outputs = template.to_json().get("Outputs", {})
    assert "TestS3StackS3BucketRawDataBucketName" in outputs
    assert "TestS3StackS3BucketRawDataBucketArn" in outputs


# --- Happy path: Tagging ---
def test_s3_stack_tags():
    app = App()
    stack = S3Stack(app, "TestS3Stack", config=minimal_s3_config())
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "S3Team" for tag in tags
    )


# --- Happy path: Multiple buckets creation ---
def test_s3_stack_multiple_buckets():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {"id": "RawDataBucket", "name": "test-raw"},
                {"id": "ProcessedDataBucket", "name": "test-processed"},
                {"id": "AnalyticsDataBucket", "name": "test-analytics"},
            ]
        },
        "app": {"env": "test"},
    }
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::S3::Bucket", 3)
    assert set(stack.buckets.keys()) == {
        "RawDataBucket",
        "ProcessedDataBucket",
        "AnalyticsDataBucket",
    }
    assert stack.raw_bucket is not None
    assert stack.processed_bucket is not None
    assert stack.analytics_bucket is not None


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
                {"id": "dup", "name": "bucket2"},
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        S3Stack(app, "TestS3Stack", config=config)


# --- Unhappy path: Missing required fields ---
def test_s3_stack_missing_required_fields():
    app = App()
    config = {"s3": {"buckets": [{"id": "missing"}]}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        S3Stack(app, "TestS3Stack", config=config)


# --- Unhappy path: Invalid bucket name ---
def test_s3_stack_invalid_bucket_name():
    app = App()
    config = {
        "s3": {"buckets": [{"id": "BadBucket", "name": "INVALID_NAME!"}]},
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        S3Stack(app, "TestS3Stack", config=config)


# --- Happy path: CloudWatch alarms created ---
def test_s3_stack_cloudwatch_alarms():
    app = App()
    config = minimal_s3_config()
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::CloudWatch::Alarm")
    assert any("4xxErrorsAlarm" in k or "5xxErrorsAlarm" in k for k in resources)
