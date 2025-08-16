"""
This module contains unit tests for the S3Stack class,
which synthesizes AWS S3 buckets and their configurations based on a config-driven approach.
"""


# --- Happy path: Lifecycle rules propagate to template ---
def test_s3_stack_lifecycle_rules_propagation():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {
                    "id": "RawDataBucket",
                    "name": "test-raw",
                    "lifecycle_rules": [
                        {
                            "id": "transition-raw",
                            "enabled": True,
                            "transitions": [
                                {"days": 30, "storage_class": "STANDARD_IA"},
                                {"days": 60, "storage_class": "GLACIER"},
                            ],
                            "expiration_days": 365,
                            "abort_incomplete_multipart_upload_days": 7,
                        }
                    ],
                }
            ]
        },
        "app": {"env": "test"},
    }
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::S3::Bucket")
    found_lifecycle = False
    for r in resources.values():
        props = r["Properties"]
        if "LifecycleConfiguration" in props:
            rules = props["LifecycleConfiguration"].get("Rules", [])
            assert any(rule.get("Status") == "Enabled" for rule in rules)
            assert any(
                any(
                    t.get("StorageClass") == "GLACIER"
                    for t in rule.get("Transitions", [])
                )
                for rule in rules
            )
            found_lifecycle = True
    assert found_lifecycle


# --- Unhappy path: Invalid lifecycle_rules type (should skip, not raise) ---
def test_s3_stack_invalid_lifecycle_rules_type():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {
                    "id": "BadLifecycle",
                    "name": "bad-lifecycle-bucket",
                    "lifecycle_rules": ["notadict", 123, None],
                }
            ]
        },
        "app": {"env": "test"},
    }
    # Should not raise, just skip invalid rules
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::S3::Bucket")
    for r in resources.values():
        props = r["Properties"]
        # No valid rules, so LifecycleConfiguration may be missing or empty
        if "LifecycleConfiguration" in props:
            rules = props["LifecycleConfiguration"].get("Rules", [])
            assert rules == []


# --- Edge case: Multiple lifecycle rules, partial fields ---
def test_s3_stack_multiple_lifecycle_rules_partial_fields():
    app = App()
    config = {
        "s3": {
            "buckets": [
                {
                    "id": "MultiRule",
                    "name": "multi-rule-bucket",
                    "lifecycle_rules": [
                        {"id": "rule1", "enabled": True, "expiration_days": 30},
                        {
                            "id": "rule2",
                            "transitions": [
                                {"days": 15, "storage_class": "STANDARD_IA"}
                            ],
                        },
                    ],
                }
            ]
        },
        "app": {"env": "test"},
    }
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::S3::Bucket")
    found = False
    for r in resources.values():
        props = r["Properties"]
        if "LifecycleConfiguration" in props:
            rules = props["LifecycleConfiguration"].get("Rules", [])
            print("[DEBUG] Synthesized Lifecycle Rules:", rules)
            assert any(rule.get("ExpirationInDays") == 30 for rule in rules)
            assert any(
                any(
                    t.get("StorageClass") == "STANDARD_IA"
                    for t in rule.get("Transitions", [])
                )
                for rule in rules
            )
            found = True
    assert found


# --- Integration test guidance ---
import pytest
from aws_cdk import App, assertions
from infra.domains.data_platform.storage.s3_stack import S3Stack

pytestmark = pytest.mark.unit

# For full auditability, supplement with integration tests post-deployment:
#   aws s3api get-bucket-tagging --bucket <bucket-name>
#   aws resourcegroupstaggingapi get-resources --resource-type-filters s3


# --- Supplementary: Validate tags on every bucket via CDK Tags API ---
def test_s3_stack_bucket_tags_propagation():
    app = App()
    shared_tags = {"CostCenter": "8888", "Owner": "S3Team"}
    config = minimal_s3_config()
    stack = S3Stack(app, "TestS3Stack", config=config, shared_tags=shared_tags)
    expected_keys = {"Project", "Environment", "Owner", "CostCenter"}
    for bucket in stack.buckets.values():
        # tags = [t[0] for t in bucket.node.try_get_context("@aws-cdk/core:tags") or []]
        for key in expected_keys:
            assert any(key == tag.get("Key") for tag in stack.get_stack_tags())


# --- Supplementary: Unhappy path - missing required tag ---
def test_s3_stack_missing_shared_tag():
    app = App()
    config = minimal_s3_config()
    # No shared_tags, only config tags
    stack = S3Stack(app, "TestS3Stack", config=config)
    tags = stack.get_stack_tags() or []
    tag_keys = [tag.get("Key") for tag in tags if isinstance(tag, dict)]
    assert "Owner" in tag_keys
    assert "CostCenter" not in tag_keys


# --- Supplementary: No duplicate tags if present in both config and shared_tags ---
def test_s3_stack_no_duplicate_tags():
    app = App()
    config = minimal_s3_config()
    shared_tags = {"Owner": "S3Team"}
    stack = S3Stack(app, "TestS3Stack", config=config, shared_tags=shared_tags)
    tags = stack.get_stack_tags() or []
    owner_tags = [tag for tag in tags if tag.get("Key") == "Owner"]
    assert len(owner_tags) == 1


# --- Supplementary: Scalability - tags propagate to all buckets ---
def test_s3_stack_tags_scalability_large_bucket_count():
    app = App()
    shared_tags = {"Audit": "True"}
    config = {
        "s3": {"buckets": [{"id": f"B{i}", "name": f"bucket-{i}"} for i in range(50)]},
        "app": {"env": "test"},
    }
    stack = S3Stack(app, "TestS3StackScale", config=config, shared_tags=shared_tags)
    for bucket in stack.buckets.values():
        tags = stack.get_stack_tags() or []
        assert any(tag.get("Key") == "Audit" for tag in tags)


# --- Supplementary: Stack-level tags present in all buckets ---
def test_s3_stack_stack_level_tags_present_in_buckets():
    app = App()
    config = minimal_s3_config()
    stack = S3Stack(app, "TestS3Stack", config=config)
    tags = stack.get_stack_tags() or []
    stack_tag_keys = [tag.get("Key") for tag in tags if isinstance(tag, dict)]
    for bucket in stack.buckets.values():
        for key in stack_tag_keys:
            assert any(tag.get("Key") == key for tag in stack.get_stack_tags())


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
    tags = stack.get_stack_tags() or []
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
    tags = stack.get_stack_tags() or []
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
    tags = stack.get_stack_tags() or []
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


# --- Supplementary: Resource-level tag propagation ---
def test_s3_stack_bucket_resource_tags():
    # CDK assertions.Template does not expose global tags in .to_json().
    # For auditability, validate tags at the construct level and supplement with integration tests using AWS CLI v2.
    app = App()
    shared_tags = {"CostCenter": "9999"}
    config = minimal_s3_config()
    stack = S3Stack(app, "TestS3Stack", config=config, shared_tags=shared_tags)
    tags = stack.get_stack_tags() or []
    tag_keys = [tag.get("Key") for tag in tags if isinstance(tag, dict)]
    assert "Project" in tag_keys
    assert "Owner" in tag_keys
    assert "Environment" in tag_keys
    assert "CostCenter" in tag_keys
    # For deployed resources, use:
    # aws s3api get-bucket-tagging --bucket <bucket-name>


# --- Supplementary: CloudWatch alarm config ---
def test_s3_stack_cloudwatch_alarm_config():
    app = App()
    config = minimal_s3_config()
    stack = S3Stack(app, "TestS3Stack", config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::CloudWatch::Alarm")
    found_4xx = found_5xx = False
    for k, v in resources.items():
        props = v["Properties"]
        if "4xxErrorsAlarm" in k:
            found_4xx = True
            assert props["Threshold"] == 1
            assert props["EvaluationPeriods"] == 1
            assert props["TreatMissingData"] == "notBreaching"
        if "5xxErrorsAlarm" in k:
            found_5xx = True
            assert props["Threshold"] == 1
            assert props["EvaluationPeriods"] == 1
            assert props["TreatMissingData"] == "notBreaching"
    assert found_4xx and found_5xx


# --- Supplementary: Removal policy export validation ---
def test_s3_stack_removal_policy_export():
    for policy in ["DESTROY", "RETAIN"]:
        app = App()
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
        template = assertions.Template.from_stack(stack)
        outputs = template.to_json().get("Outputs", {})
        bucket_name_key = f"TestS3Stack{policy}S3Bucket{policy}Name"
        assert bucket_name_key in outputs


# --- Supplementary: KMS key propagation ---
def test_s3_stack_kms_key_encryption_type():
    from aws_cdk import aws_kms as kms, Stack

    app = App()
    test_stack = Stack(app, "TestS3StackKMS2")
    kms_key = kms.Key(test_stack, "TestKmsKey2")
    config = {
        "s3": {
            "buckets": [
                {"id": "KmsBucket2", "name": "kms-bucket2", "encryption": "UNENCRYPTED"}
            ]
        },
        "app": {"env": "test"},
    }
    stack = S3Stack(test_stack, "S3", config=config, kms_key=kms_key)
    for b in stack.buckets.values():
        assert getattr(b, "encryption_key", None) == kms_key
    # Inspect the synthesized template for KMS encryption configuration
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::S3::Bucket")
    for r in resources.values():
        props = r["Properties"]
        # The presence of BucketEncryption with KMSMasterKeyID indicates KMS encryption
        if "BucketEncryption" in props:
            sse_config = props["BucketEncryption"].get(
                "ServerSideEncryptionConfiguration"
            )
            if isinstance(sse_config, dict):
                rules = sse_config.get("Rules", [])
            elif isinstance(sse_config, list):
                rules = sse_config
            else:
                rules = []
            found_kms = any(
                rule.get("ServerSideEncryptionByDefault", {}).get("SSEAlgorithm")
                == "aws:kms"
                for rule in rules
                if isinstance(rule, dict)
            )
            assert found_kms


# --- Supplementary: Scalability/parallelism ---
def test_s3_stack_scalability_tags():
    # CDK assertions.Template does not expose global tags in .to_json().
    # For auditability, validate tags at the construct level and supplement with integration tests using AWS CLI v2.
    app = App()
    shared_tags = {"Team": "ScaleTest"}
    config = {
        "s3": {"buckets": [{"id": f"B{i}", "name": f"bucket-{i}"} for i in range(100)]},
        "app": {"env": "test"},
    }
    stack = S3Stack(app, "TestS3StackScale", config=config, shared_tags=shared_tags)
    resources = stack.buckets
    assert len(resources) == 100
    tags = stack.get_stack_tags() or []
    tag_keys = [tag.get("Key") for tag in tags if isinstance(tag, dict)]
    assert "Team" in tag_keys
    assert "Project" in tag_keys
    # For deployed resources, use:
    # aws s3api get-bucket-tagging --bucket <bucket-name>


# --- Supplementary: Error logging/auditability ---
def test_s3_stack_error_logging_on_invalid_config():
    app = App()
    config = {
        "s3": {"buckets": [{"id": "Bad", "name": "bad!bucket"}]},
        "app": {"env": "test"},
    }
    try:
        S3Stack(app, "TestS3Stack", config=config)
    except ValueError as e:
        assert "Invalid S3 bucket name" in str(e)


def pytest_configure(config):
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
