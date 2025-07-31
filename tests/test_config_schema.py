import pytest
from pydantic import ValidationError
from infra.utils.config_schema import ShieldCraftConfig, BeirConfig, MtebConfig


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
