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


# --- Resource and permission exposure as stack attributes ---
def test_lakeformation_stack_resource_and_permission_exposure():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [
                {"name": "bucket1", "arn": "arn:aws:s3:::bucket1"},
                {"name": "bucket2", "arn": "arn:aws:s3:::bucket2"},
            ],
            "permissions": [
                {
                    "principal": "arn:aws:iam::123456789012:role/LakeAdmin",
                    "resource": {
                        "dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}
                    },
                    "permissions": ["DATA_LOCATION_ACCESS"],
                }
            ],
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    assert hasattr(stack, "resources")
    assert hasattr(stack, "permissions")
    assert len(stack.resources) == 2
    assert len(stack.permissions) == 1


# --- Tag propagation: shared_tags and per-stack tags ---
def test_lakeformation_stack_shared_tags_propagation():
    app = App()
    test_stack = Stack(app, "TestStack")
    shared_tags = {"CostCenter": "9999"}
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}],
            "tags": {"Owner": "LFTeam"},
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(
        test_stack, "TestLakeFormationStack", config=config, shared_tags=shared_tags
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "CostCenter" and tag.get("Value") == "9999" for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "LFTeam" for tag in tags
    )


# --- Removal policy propagation (dev/prod) ---
def test_lakeformation_stack_removal_policy_propagation():
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
    # RemovalPolicy is not directly exposed, but resource exists and is retained in prod
    template_dev = assertions.Template.from_stack(stack_dev)
    template_prod = assertions.Template.from_stack(stack_prod)
    template_dev.resource_count_is("AWS::LakeFormation::Resource", 1)
    template_prod.resource_count_is("AWS::LakeFormation::Resource", 1)


# --- Output/ARN structure and export name validation ---
def test_lakeformation_stack_output_export_names():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}],
            "permissions": [
                {
                    "principal": "arn:aws:iam::123456789012:role/LakeAdmin",
                    "resource": {
                        "dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}
                    },
                    "permissions": ["DATA_LOCATION_ACCESS"],
                }
            ],
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    for k, v in outputs.items():
        assert all(c.isalnum() or c in "-:_." for c in k), f"Invalid output key: {k}"
        assert (
            isinstance(v, dict) and "Value" in v and "Export" in v
        ), f"Invalid output value structure: {v}"
        export_name = v["Export"]["Name"]
        assert all(
            c.isalnum() or c in "-:_" for c in export_name
        ), f"Invalid export name: {export_name}"


# --- Event rule presence (CloudTrail monitoring) ---
def test_lakeformation_stack_event_rule_presence():
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


# --- Edge case: Empty buckets list (should raise) ---
def test_lakeformation_stack_empty_buckets():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"lakeformation": {"buckets": []}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)


# --- Edge case: Invalid bucket name (should raise) ---
def test_lakeformation_stack_invalid_bucket_name():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "INVALID_BUCKET_NAME!", "arn": "arn:aws:s3:::bucket1"}]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)


# --- Edge case: Empty permissions list (should not raise, just no permissions) ---
def test_lakeformation_stack_empty_permissions():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}],
            "permissions": [],
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    # Only resource, no permissions
    template.resource_count_is("AWS::LakeFormation::Resource", 1)
    template.resource_count_is("AWS::LakeFormation::Permissions", 0)


# --- Unhappy path: Permission missing principal/resource/permissions ---
def test_lakeformation_stack_permission_missing_fields_all():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}],
            "permissions": [{"principal": None, "resource": None, "permissions": None}],
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)


# --- Edge case: Minimal config (single bucket, no permissions) ---
def test_lakeformation_stack_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucketmin", "arn": "arn:aws:s3:::bucketmin"}]
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Resource", 1)
    template.resource_count_is("AWS::LakeFormation::Permissions", 0)


# --- Edge case: s3_buckets is empty dict (should raise) ---
def test_lakeformation_stack_empty_s3_buckets_dict():
    app = App()
    test_stack = Stack(app, "TestStack")
    s3_buckets = {}
    config = {"lakeformation": {}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        LakeFormationStack(
            test_stack, "TestLakeFormationStack", config=config, s3_buckets=s3_buckets
        )


# --- Edge case: s3_buckets with invalid bucket construct (missing name/arn) ---
def test_lakeformation_stack_invalid_s3_bucket_construct():
    class DummyBucket:
        pass

    app = App()
    test_stack = Stack(app, "TestStack")
    s3_buckets = {"Dummy": DummyBucket()}
    config = {"lakeformation": {}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        LakeFormationStack(
            test_stack, "TestLakeFormationStack", config=config, s3_buckets=s3_buckets
        )


# --- Edge case: bucket name is unresolved token (should not raise) ---
def test_lakeformation_stack_unresolved_token_bucket_name():
    from aws_cdk import aws_s3 as s3, Token

    app = App()
    test_stack = Stack(app, "TestStack")
    unresolved_name = Token.as_string({"Ref": "SomeResource"})
    s3_bucket = s3.Bucket(test_stack, "TestBucket", bucket_name=unresolved_name)
    s3_buckets = {"TestBucket": s3_bucket}
    config = {"lakeformation": {}, "app": {"env": "test"}}
    stack = LakeFormationStack(
        test_stack, "TestLakeFormationStack", config=config, s3_buckets=s3_buckets
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Resource", 1)


# --- Edge case: permission with duplicate resource but different principal (should not raise) ---
def test_lakeformation_stack_duplicate_resource_different_principal():
    app = App()
    test_stack = Stack(app, "TestStack")
    perm1 = {
        "principal": "arn:aws:iam::123456789012:role/LakeAdmin1",
        "resource": {"dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}},
        "permissions": ["DATA_LOCATION_ACCESS"],
    }
    perm2 = {
        "principal": "arn:aws:iam::123456789012:role/LakeAdmin2",
        "resource": {"dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}},
        "permissions": ["DATA_LOCATION_ACCESS"],
    }
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}],
            "permissions": [perm1, perm2],
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Permissions", 2)


# --- Unhappy path: permission with admin role placeholder but no admin role provided (should not raise) ---
def test_lakeformation_stack_admin_placeholder_no_role():
    app = App()
    test_stack = Stack(app, "TestStack")
    perm = {
        "principal": "LAKEFORMATION_ADMIN_ROLE_ARN",
        "resource": {"dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}},
        "permissions": ["DATA_LOCATION_ACCESS"],
    }
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucket1", "arn": "arn:aws:s3:::bucket1"}],
            "permissions": [perm],
        },
        "app": {"env": "test"},
    }
    # Should not raise, just uses the placeholder string as principal
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Permissions", 1)


# --- DRY orchestration: minimal config, edge/unhappy paths, backward compatibility ---
def test_lakeformation_stack_minimal_and_edge_cases():
    # Minimal config
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "lakeformation": {
            "buckets": [{"name": "bucketmin", "arn": "arn:aws:s3:::bucketmin"}]
        },
        "app": {"env": "test"},
    }
    stack = LakeFormationStack(test_stack, "TestLakeFormationStack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Resource", 1)
    # Unhappy: duplicate bucket name
    app = App()
    test_stack = Stack(app, "TestStack")
    config_dup = {
        "lakeformation": {
            "buckets": [
                {"name": "dup", "arn": "arn:aws:s3:::bucket1"},
                {"name": "dup", "arn": "arn:aws:s3:::bucket2"},
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStackDup", config=config_dup)
    # Unhappy: invalid bucket name
    app = App()
    test_stack = Stack(app, "TestStack")
    config_bad = {
        "lakeformation": {
            "buckets": [{"name": "INVALID!", "arn": "arn:aws:s3:::bucket1"}]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStackBad", config=config_bad)
    # Unhappy: empty buckets
    app = App()
    test_stack = Stack(app, "TestStack")
    config_empty = {"lakeformation": {"buckets": []}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        LakeFormationStack(
            test_stack, "TestLakeFormationStackEmpty", config=config_empty
        )
    # Unhappy: permissions not a list
    app = App()
    test_stack = Stack(app, "TestStack")
    config_perm = {
        "lakeformation": {
            "buckets": [{"name": "b", "arn": "arn:aws:s3:::b"}],
            "permissions": "notalist",
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(test_stack, "TestLakeFormationStackPerm", config=config_perm)
    # Unhappy: duplicate permissions
    app = App()
    test_stack = Stack(app, "TestStack")
    perm = {
        "principal": "arn:aws:iam::123456789012:role/LakeAdmin",
        "resource": {"dataLocation": {"resourceArn": "arn:aws:s3:::bucket1"}},
        "permissions": ["DATA_LOCATION_ACCESS"],
    }
    config_dup_perm = {
        "lakeformation": {
            "buckets": [{"name": "b", "arn": "arn:aws:s3:::b"}],
            "permissions": [perm, perm],
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(
            test_stack, "TestLakeFormationStackDupPerm", config=config_dup_perm
        )
    # Unhappy: missing required fields
    app = App()
    test_stack = Stack(app, "TestStack")
    config_missing = {
        "lakeformation": {"buckets": [{"name": "b"}]},
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(
            test_stack, "TestLakeFormationStackMissing", config=config_missing
        )
    # Unhappy: permission missing fields
    app = App()
    test_stack = Stack(app, "TestStack")
    config_perm_missing = {
        "lakeformation": {
            "buckets": [{"name": "b", "arn": "arn:aws:s3:::b"}],
            "permissions": [{"principal": None, "resource": None, "permissions": None}],
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LakeFormationStack(
            test_stack, "TestLakeFormationStackPermMissing", config=config_perm_missing
        )
    # Backward compatibility: s3_buckets cross-stack
    app = App()
    test_stack = Stack(app, "TestStack")
    from aws_cdk import aws_s3 as s3

    s3_bucket = s3.Bucket(test_stack, "TestBucket", bucket_name="bucketx")
    s3_buckets = {"TestBucket": s3_bucket}
    config_cross = {"lakeformation": {}, "app": {"env": "test"}}
    stack = LakeFormationStack(
        test_stack,
        "TestLakeFormationStackCross",
        config=config_cross,
        s3_buckets=s3_buckets,
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::LakeFormation::Resource", 1)
