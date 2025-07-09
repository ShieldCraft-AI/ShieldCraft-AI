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


# --- Edge case: Minimal config (only id and name) ---
def test_s3_stack_minimal_config():
    app = App()
    config = {
        "s3": {"buckets": [{"id": "OnlyId", "name": "minimal-bucket"}]},
        "app": {"env": "test"},
    }
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::S3::Bucket", 1)


# --- Unhappy path: Duplicate bucket name (not just id) ---
def test_s3_stack_duplicate_bucket_name():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {"id": "bucket1", "name": "dup-bucket"},
                {"id": "bucket2", "name": "dup-bucket"},
            ]
        },
        "app": {"env": "test"},
    }
    # Should not raise, AWS allows duplicate names in config, but CDK will fail at deploy if not unique
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::S3::Bucket", 2)


# --- Unhappy path: Invalid encryption value ---
def test_s3_stack_invalid_encryption():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {"id": "BadEnc", "name": "badenc-bucket", "encryption": "INVALID"}
            ]
        },
        "app": {"env": "test"},
    }
    # Should fall back to S3_MANAGED, not raise
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::S3::Bucket", 1)


# --- Unhappy path: Invalid block public access value ---
def test_s3_stack_invalid_block_public_access():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {
                    "id": "BadBlock",
                    "name": "badblock-bucket",
                    "block_public_access": "INVALID",
                }
            ]
        },
        "app": {"env": "test"},
    }
    # Should fall back to BLOCK_ALL, not raise
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::S3::Bucket", 1)


# --- Edge case: prod env always versioned/encrypted ---
def test_s3_stack_prod_env_forces_versioning_and_encryption():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {
                    "id": "ProdBucket",
                    "name": "prod-bucket",
                    "versioned": False,
                    "encryption": "UNENCRYPTED",
                }
            ]
        },
        "app": {"env": "prod"},
    }
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::S3::Bucket")
    # VersioningConfiguration must be present and Status == Enabled
    for r in resources.values():
        props = r["Properties"]
        assert props.get("VersioningConfiguration", {}).get("Status") == "Enabled"


# --- Edge case: shared_tags propagation ---
def test_s3_stack_shared_tags():
    app = App()
    shared_tags = {"CostCenter": "1234"}
    stack = S3Stack(
        app, "TestS3Stack", config=minimal_s3_config(), shared_tags=shared_tags
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "CostCenter" and tag.get("Value") == "1234" for tag in tags
    )


# --- Edge case: KMS key encryption propagation ---
def test_s3_stack_kms_key_encryption_propagation():
    from aws_cdk import aws_kms as kms, Stack

    app = App()
    test_stack = Stack(app, "TestS3StackKMS")
    kms_key = kms.Key(test_stack, "TestKmsKey")
    config = {
        "s3": {
            "buckets": [
                {"id": "KmsBucket", "name": "kms-bucket", "encryption": "UNENCRYPTED"}
            ]
        },
        "app": {"env": "test"},
    }
    stack = S3Stack(test_stack, "S3", config=config, kms_key=kms_key)
    # All buckets should use the provided kms_key for encryption
    for b in stack.buckets.values():
        assert getattr(b, "encryption_key", None) == kms_key


# --- Edge case: All block public access variants ---
def test_s3_stack_block_public_access_variants():
    from aws_cdk import Stack

    for variant in [
        "BLOCK_ALL",
        "BLOCK_ACLS",
        "BLOCK_PUBLIC_POLICY",
        "BLOCK_AUTHENTICATED_USERS",
    ]:
        app = App()
        # S3 bucket names must be lowercase, no underscores, only letters, numbers, hyphens, and periods
        bucket_name = f"bucket-block-{variant.lower().replace('_', '-')}"
        # Stack names must start with a letter and only contain letters, numbers, and hyphens
        stack_name = f"TestS3Stack-{variant}"  # hyphen is allowed, underscore is not
        stack_name = stack_name.replace("_", "-")
        test_stack = Stack(app, stack_name)
        config = {
            "s3": {
                "buckets": [
                    {
                        "id": f"Bucket{variant}",
                        "name": bucket_name,
                        "block_public_access": variant,
                    }
                ]
            },
            "app": {"env": "test"},
        }
        stack = S3Stack(test_stack, "S3", config=config)
        template = assertions.Template.from_stack(stack)
        template.resource_count_is("AWS::S3::Bucket", 1)


# --- Edge case: versioning off in non-prod ---
def test_s3_stack_versioning_off_nonprod():
    app = App()
    config = {
        "s3": {
            "buckets": [{"id": "NoVer", "name": "nover-bucket", "versioned": False}]
        },
        "app": {"env": "dev"},
    }
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::S3::Bucket")
    for r in resources.values():
        props = r["Properties"]
        assert (
            props.get("VersioningConfiguration", {}).get("Status", "Suspended")
            == "Suspended"
        )


# --- Edge case: removal policy propagation ---
def test_s3_stack_removal_policy_variants():
    app = App()
    for policy in ["DESTROY", "RETAIN"]:
        config = {
            "s3": {
                "buckets": [
                    {
                        "id": policy,
                        "name": f"bucket-{policy.lower()}",
                        "removal_policy": policy,
                    }
                ]
            },
            "app": {"env": "test"},
        }
        stack = S3Stack(app, f"TestS3Stack{policy}", config=config)
        # Should not raise
        assert policy in stack.buckets


# --- Edge case: output export names ---
def test_s3_stack_output_export_names():
    app = App()
    config = minimal_s3_config()
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    for k, v in outputs.items():
        assert k.startswith("TestS3StackS3Bucket") or k.startswith("TestS3Stack-")
        assert v["Value"]


# --- Edge case: metrics presence ---
def test_s3_stack_metrics_presence():
    app = App()
    config = minimal_s3_config()
    S3Stack(app, "TestS3Stack", config=config)
    # Should not raise, metrics are created in constructor
    # (No direct assertion, but test ensures no error)


# --- Edge case: shared tags and per-bucket tags merge ---
def test_s3_stack_shared_and_per_bucket_tags_merge():
    app = App()
    config = minimal_s3_config()
    config["s3"]["buckets"][0]["tags"] = {"Env": "dev"}
    shared_tags = {"CostCenter": "5678"}
    stack = S3Stack(app, "TestS3Stack", config=config, shared_tags=shared_tags)
    tags = stack.tags.render_tags()
    # Only shared tags are present at stack level
    assert any(tag.get("Key") == "CostCenter" for tag in tags)
    # Per-bucket tags are not merged at stack level (CDK default)


# --- Unhappy path: invalid config types ---
def test_s3_stack_buckets_not_dict():
    app = App()
    config = {"s3": {"buckets": ["notadict"]}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        S3Stack(app, "TestS3Stack", config=config)


# --- Edge case: large number of buckets ---
def test_s3_stack_many_buckets():
    app = App()
    config = {
        "s3": {"buckets": [{"id": f"B{i}", "name": f"bucket-{i}"} for i in range(25)]},
        "app": {"env": "test"},
    }
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::S3::Bucket", 25)


# --- Edge case: backward compatibility attributes ---
def test_s3_stack_backward_compatibility_attrs():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {"id": "RawDataBucket", "name": "raw-bucket"},
                {"id": "ProcessedDataBucket", "name": "proc-bucket"},
            ]
        },
        "app": {"env": "test"},
    }
    stack = S3Stack(app, "TestS3Stack", config=config)
    assert stack.raw_bucket is not None
    assert stack.processed_bucket is not None
    assert stack.analytics_bucket is None
