"""
Test cases for ShieldCraftConfig schema validation
"""

import pytest
from pydantic import ValidationError
from infra.utils.config_schema import ShieldCraftConfig, BeirConfig, MtebConfig


def test_prod_multi_az_enforced_fail():
    # Should fail: only one subnet in prod
    config = {
        "app": {
            "env": "prod",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-prod",
        },
        "s3": {
            "buckets": [{"id": "b1", "name": "bucket1", "removal_policy": "RETAIN"}]
        },
        "glue": {"database_name": "db1"},
        "networking": {
            "vpc_id": "vpc-1",
            "cidr": "10.0.0.0/16",
            "subnets": [{"id": "subnet-1", "cidr": "10.0.1.0/24", "type": "PUBLIC"}],
            "security_groups": [{"id": "sg-1", "description": "default sg"}],
        },
    }
    with pytest.raises(ValidationError) as exc:
        ShieldCraftConfig(**config)
    assert "at least two subnets for multi-AZ" in str(exc.value)


def test_prod_multi_az_enforced_pass():
    # Should pass: two subnets in prod
    config = {
        "app": {
            "env": "prod",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-prod",
        },
        "s3": {
            "buckets": [{"id": "b1", "name": "bucket1", "removal_policy": "RETAIN"}]
        },
        "glue": {"database_name": "db1"},
        "networking": {
            "vpc_id": "vpc-1",
            "cidr": "10.0.0.0/16",
            "subnets": [
                {"id": "subnet-1", "cidr": "10.0.1.0/24", "type": "PUBLIC"},
                {"id": "subnet-2", "cidr": "10.0.2.0/24", "type": "PRIVATE"},
            ],
            "security_groups": [{"id": "sg-1", "description": "default sg"}],
        },
    }
    scfg = ShieldCraftConfig(**config)
    assert scfg.app.env == "prod"
    assert len(scfg.networking.subnets) == 2


def test_beir_config_valid():
    cfg = BeirConfig(
        datasets=["scifact", "trec-covid"],
        data_path="/tmp/beir",
        output_path="/tmp/beir_results.json",
        batch_size=16,
    )
    assert cfg.datasets == ["scifact", "trec-covid"]
    assert cfg.data_path == "/tmp/beir"
    assert cfg.output_path == "/tmp/beir_results.json"
    assert cfg.batch_size == 16


def test_mteb_config_valid():
    cfg = MtebConfig(
        tasks=["STSBenchmark", "TREC"],
        output_path="/tmp/mteb_results.json",
        batch_size=8,
    )
    assert cfg.tasks == ["STSBenchmark", "TREC"]
    assert cfg.output_path == "/tmp/mteb_results.json"
    assert cfg.batch_size == 8


def test_beir_config_defaults():
    cfg = BeirConfig()
    assert cfg.datasets == ["scifact"]
    assert cfg.data_path == "./beir_datasets"
    assert cfg.output_path == "beir_results.json"
    assert cfg.batch_size == 32


def test_mteb_config_defaults():
    cfg = MtebConfig()
    assert cfg.tasks is None
    assert cfg.output_path == "mteb_results.json"
    assert cfg.batch_size == 32


def test_shieldcraft_config_minimal():
    # Minimal config with required fields only
    config = {
        "app": {
            "env": "dev",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-dev",
        },
        "s3": {"buckets": [{"id": "b1", "name": "bucket1"}]},
        "glue": {"database_name": "db1"},
    }
    scfg = ShieldCraftConfig(**config)
    assert scfg.app.env == "dev"
    assert scfg.s3.buckets[0].id == "b1"
    assert scfg.glue.database_name == "db1"


def test_shieldcraft_config_with_beir_mteb():
    config = {
        "app": {
            "env": "dev",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-dev",
        },
        "s3": {"buckets": [{"id": "b1", "name": "bucket1"}]},
        "glue": {"database_name": "db1"},
        "beir": {"datasets": ["scifact"], "batch_size": 16},
        "mteb": {"tasks": ["STSBenchmark"], "batch_size": 8},
    }
    scfg = ShieldCraftConfig(**config)
    assert scfg.beir.datasets == ["scifact"]
    assert scfg.beir.batch_size == 16
    assert scfg.mteb.tasks == ["STSBenchmark"]
    assert scfg.mteb.batch_size == 8


def test_prod_bucket_removal_policy_enforced():
    config = {
        "app": {
            "env": "prod",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-prod",
        },
        "s3": {
            "buckets": [{"id": "b1", "name": "bucket1", "removal_policy": "DESTROY"}]
        },
        "glue": {"database_name": "db1"},
    }
    with pytest.raises(ValidationError) as exc:
        ShieldCraftConfig(**config)
    assert "removal_policy must be RETAIN" in str(exc.value)


def test_s3_bucket_encryption_optional():
    config = {
        "app": {
            "env": "dev",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-dev",
        },
        "s3": {"buckets": [{"id": "b1", "name": "bucket1", "encryption": "SSE-S3"}]},
        "glue": {"database_name": "db1"},
    }
    scfg = ShieldCraftConfig(**config)
    assert scfg.s3.buckets[0].encryption == "SSE-S3"


def test_duplicate_subnet_ids_fails():
    config = {
        "app": {
            "env": "dev",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-dev",
        },
        "s3": {"buckets": [{"id": "b1", "name": "bucket1"}]},
        "glue": {"database_name": "db1"},
        "networking": {
            "vpc_id": "vpc-1",
            "cidr": "10.0.0.0/16",
            "subnets": [
                {"id": "subnet-1", "cidr": "10.0.1.0/24", "type": "PUBLIC"},
                {"id": "subnet-1", "cidr": "10.0.2.0/24", "type": "PRIVATE"},
            ],
            "security_groups": [{"id": "sg-1", "description": "default sg"}],
        },
    }
    with pytest.raises(ValidationError) as exc:
        ShieldCraftConfig(**config)
    assert "Duplicate subnet IDs found" in str(exc.value)


def test_invalid_cidr_fails():
    config = {
        "app": {
            "env": "dev",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-dev",
        },
        "s3": {"buckets": [{"id": "b1", "name": "bucket1"}]},
        "glue": {"database_name": "db1"},
        "networking": {
            "vpc_id": "vpc-1",
            "cidr": "10.0.0.0/16",
            "subnets": [
                {"id": "subnet-1", "cidr": "bad-cidr", "type": "PUBLIC"},
                {"id": "subnet-2", "cidr": "10.0.2.0/24", "type": "PRIVATE"},
            ],
            "security_groups": [{"id": "sg-1", "description": "default sg"}],
        },
    }
    with pytest.raises(ValidationError) as exc:
        ShieldCraftConfig(**config)
    assert "Invalid CIDR format" in str(exc.value)


def test_missing_required_fields_fails():
    config = {
        "app": {
            "env": "dev",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-dev",
        }
    }
    with pytest.raises(ValidationError) as exc:
        ShieldCraftConfig(**config)
    assert "Field required" in str(exc.value)


def test_referential_integrity_lambda_subnet():
    config = {
        "app": {
            "env": "dev",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-dev",
        },
        "s3": {"buckets": [{"id": "b1", "name": "bucket1"}]},
        "glue": {"database_name": "db1"},
        "networking": {
            "vpc_id": "vpc-1",
            "cidr": "10.0.0.0/16",
            "subnets": [
                {"id": "subnet-1", "cidr": "10.0.1.0/24", "type": "PUBLIC"},
                {"id": "subnet-2", "cidr": "10.0.2.0/24", "type": "PRIVATE"},
            ],
            "security_groups": [{"id": "sg-1", "description": "default sg"}],
        },
        "lambda_": {
            "functions": [
                {
                    "id": "fn1",
                    "handler": "main.handler",
                    "runtime": "python3.9",
                    "memory_size": 128,
                    "timeout": 30,
                    "vpc_subnet_ids": ["subnet-1", "subnet-x"],
                    "security_group_ids": ["sg-1"],
                }
            ]
        },
    }
    with pytest.raises(ValidationError) as exc:
        ShieldCraftConfig(**config)
    assert "Subnet ID 'subnet-x' in lambda_.functions[fn1] does not exist" in str(
        exc.value
    )


def test_secret_field_validation():
    # Should fail if secret fields are not vault references
    config = {
        "app": {
            "env": "dev",
            "region": "af-south-1",
            "account": "123",
            "resource_prefix": "shieldcraft-dev",
        },
        "s3": {"buckets": [{"id": "b1", "name": "bucket1"}]},
        "glue": {"database_name": "db1"},
        "cloud_native_hardening": {
            "sns_topic_secret_arn": "not-a-vault-ref",
            "external_api_key_arn": "arn:aws:secretsmanager:region:acct:secret:mysecret",
        },
    }
    with pytest.raises(ValidationError) as exc:
        ShieldCraftConfig(**config)
    assert "must be a vault reference" in str(exc.value)
