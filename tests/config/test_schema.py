"""
Unit tests for ShieldCraft config schema (config_schema.py).
Covers strict validation, edge cases, and semantic rules.
"""

import pytest
from pydantic import ValidationError
from infra.utils.config_schema import (
    ShieldCraftConfig,
    BucketConfig,
    S3Config,
    AppConfig,
    SubnetConfig,
    SecurityGroupConfig,
    NetworkingConfig,
    GlueConfig,
)


def test_bucket_removal_policy_valid():
    bucket = BucketConfig(id="test-bucket", name="test", removal_policy="DESTROY")
    assert bucket.removal_policy == "DESTROY"


def test_bucket_removal_policy_invalid():
    with pytest.raises(ValidationError):
        BucketConfig(id="test-bucket", name="test", removal_policy="INVALID")


def test_subnet_cidr_valid():
    subnet = SubnetConfig(id="subnet-1", cidr="10.0.0.0/24", type="private")
    assert subnet.cidr == "10.0.0.0/24"


def test_subnet_cidr_invalid():
    with pytest.raises(ValidationError):
        SubnetConfig(id="subnet-1", cidr="bad-cidr", type="private")


def test_networking_unique_ids():
    networking = NetworkingConfig(
        vpc_id="vpc-1",
        cidr="10.0.0.0/16",
        subnets=[
            SubnetConfig(id="a", cidr="10.0.1.0/24", type="private"),
            SubnetConfig(id="b", cidr="10.0.2.0/24", type="private"),
        ],
        security_groups=[
            SecurityGroupConfig(id="sg-1"),
            SecurityGroupConfig(id="sg-2"),
        ],
    )
    assert networking.vpc_id == "vpc-1"


def test_networking_duplicate_subnet_ids():
    with pytest.raises(ValidationError):
        NetworkingConfig(
            vpc_id="vpc-1",
            cidr="10.0.0.0/16",
            subnets=[
                SubnetConfig(id="a", cidr="10.0.1.0/24", type="private"),
                SubnetConfig(id="a", cidr="10.0.2.0/24", type="private"),
            ],
            security_groups=[
                SecurityGroupConfig(id="sg-1"),
                SecurityGroupConfig(id="sg-2"),
            ],
        )


def test_networking_duplicate_sg_ids():
    with pytest.raises(ValidationError):
        NetworkingConfig(
            vpc_id="vpc-1",
            cidr="10.0.0.0/16",
            subnets=[
                SubnetConfig(id="a", cidr="10.0.1.0/24", type="private"),
                SubnetConfig(id="b", cidr="10.0.2.0/24", type="private"),
            ],
            security_groups=[
                SecurityGroupConfig(id="sg-1"),
                SecurityGroupConfig(id="sg-1"),
            ],
        )


def test_app_config_valid():
    app = AppConfig(env="dev", region="af-south-1", resource_prefix="shieldcraft-dev")
    assert app.env == "dev"


def test_s3_config_valid():
    s3 = S3Config(
        buckets=[BucketConfig(id="b1", name="bucket1", removal_policy="DESTROY")]
    )
    assert s3.buckets[0].id == "b1"


def test_bucket_removal_policy_prod_enforced():
    """Ensure RETAIN is enforced for prod buckets."""
    with pytest.raises(ValidationError):
        ShieldCraftConfig(
            app=AppConfig(env="prod", region="us-east-1", resource_prefix="prefix"),
            s3=S3Config(
                buckets=[
                    BucketConfig(
                        id="prod-bucket", name="prod", removal_policy="DESTROY"
                    )
                ]
            ),
            glue=GlueConfig(database_name="db"),
            networking=NetworkingConfig(
                vpc_id="vpc-1",
                cidr="10.0.0.0/16",
                subnets=[SubnetConfig(id="a", cidr="10.0.1.0/24", type="private")],
                security_groups=[SecurityGroupConfig(id="sg-1")],
            ),
        )


# Test for valid and invalid principal in LakeFormationPermissionConfig
def test_lakeformation_permission_principal_valid():
    from infra.utils.config_schema import LakeFormationPermissionConfig

    perm = LakeFormationPermissionConfig(
        principal="arn:aws:iam::123456789012:role/Admin",
        resource_type="table",
        resource={"name": "my_table"},
    )
    assert perm.principal.startswith("arn:aws:iam")


def test_lakeformation_permission_principal_invalid():
    from infra.utils.config_schema import LakeFormationPermissionConfig

    with pytest.raises(ValidationError):
        LakeFormationPermissionConfig(
            principal=None,
            resource_type="table",
            resource={"name": "my_table"},
        )


# Test for extra fields ignored in AppConfig
def test_appconfig_extra_fields_ignored():
    app = AppConfig(
        env="dev",
        region="us-east-1",
        resource_prefix="prefix",
        extra_field="ignored",
    )
    assert app.env == "dev"
    assert not hasattr(app, "extra_field")


# Test for invalid CIDR in SubnetConfig (edge case)
def test_subnet_cidr_empty():
    with pytest.raises(ValidationError):
        SubnetConfig(id="subnet-2", cidr="", type="private")


# Test for duplicate IDs in NetworkingConfig with dicts
def test_networking_duplicate_ids_with_dicts():
    with pytest.raises(ValidationError):
        NetworkingConfig(
            vpc_id="vpc-2",
            cidr="10.1.0.0/16",
            subnets=[
                {"id": "x", "cidr": "10.1.1.0/24", "type": "private"},
                {"id": "x", "cidr": "10.1.2.0/24", "type": "private"},
            ],
            security_groups=[{"id": "sg-x"}, {"id": "sg-x"}],
        )


# Test for valid and invalid model_registry in SageMakerConfig
def test_sagemaker_model_registry_valid():
    from infra.utils.config_schema import SageMakerConfig

    sm = SageMakerConfig(
        training_instance_type="ml.m5.large",
        inference_instance_type="ml.m5.large",
        model_registry="my-model-registry",
    )
    assert sm.model_registry == "my-model-registry"


def test_sagemaker_model_registry_none():
    from infra.utils.config_schema import SageMakerConfig

    sm = SageMakerConfig(
        training_instance_type="ml.m5.large",
        inference_instance_type="ml.m5.large",
        model_registry=None,
    )
    assert sm.model_registry is None
