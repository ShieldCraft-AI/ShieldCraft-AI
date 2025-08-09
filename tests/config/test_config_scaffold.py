"""
Test suite for configuration loading and validation.
"""

import pytest
import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"


@pytest.mark.parametrize(
    "filename",
    [
        "dev.yml",
        "staging.yml",
        "prod.yml",
    ],
)
def test_yaml_loads_without_error(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"YAML error in {filename}: {e}")


@pytest.mark.parametrize(
    "filename",
    [
        "dev.yml",
        "staging.yml",
        "prod.yml",
    ],
)
def test_stepfunctions_state_machines_present(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert "stepfunctions" in config, f"Missing 'stepfunctions' in {filename}"
    assert (
        "state_machines" in config["stepfunctions"]
    ), f"Missing 'state_machines' in stepfunctions for {filename}"
    assert any(
        sm["id"] == "BenchmarkAndValidate"
        for sm in config["stepfunctions"]["state_machines"]
    ), f"BenchmarkAndValidate state machine missing in {filename}"


@pytest.mark.parametrize("filename", ["staging.yml", "prod.yml"])
def test_parallelization_max_workers(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert (
        config["orchestrator"]["max_workers"] > 1
    ), f"max_workers should be >1 for {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_glue_lakeformation_schema(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert "database_name" in config.get(
        "glue", {}
    ), f"Missing glue.database_name in {filename}"
    assert (
        "buckets" in config["lakeformation"]
    ), f"Missing lakeformation.buckets in {filename}"
    assert (
        "permissions" in config["lakeformation"]
    ), f"Missing lakeformation.permissions in {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_model_embedding_config(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    for section in ["ai_core", "embedding"]:
        for key in ["model_name", "quantize", "device"]:
            assert key in config[section], f"Missing {section}.{key} in {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_s3_bucket_naming_convention(filename):
    config_path = CONFIG_DIR / filename
    env = filename.split(".")[0]
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    for bucket in config["s3"]["buckets"]:
        assert (
            env in bucket["name"]
        ), f"Bucket {bucket['id']} name missing env in {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_security_group_outbound_policy(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    for sg in config["networking"]["security_groups"]:
        assert (
            sg["allow_all_outbound"] is True
        ), f"Security group {sg['id']} must allow outbound in {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_lambda_timeout_memory(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    for fn in config["lambda_"]["functions"]:
        assert fn["timeout"] >= 30, f"Lambda {fn['id']} timeout too low in {filename}"
        assert (
            fn["memory_size"] >= 128
        ), f"Lambda {fn['id']} memory_size too low in {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_opensearch_encryption(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    domain = config["opensearch"]["domain"]
    assert (
        domain["node_to_node_encryption_options"]["enabled"] is True
    ), f"Node-to-node encryption not enabled in {filename}"
    assert (
        domain["encryption_at_rest_options"]["enabled"] is True
    ), f"At-rest encryption not enabled in {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_airbyte_task_count(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    airbyte = config["airbyte"]
    assert airbyte["min_task_count"] >= 1, f"min_task_count < 1 in {filename}"
    assert (
        airbyte["max_task_count"] >= airbyte["min_task_count"]
    ), f"max_task_count < min_task_count in {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_eventbridge_bus_names(filename):
    config_path = CONFIG_DIR / filename
    env = filename.split(".")[0]
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert (
        env in config["eventbridge"]["data_bus_name"]
    ), f"data_bus_name missing env in {filename}"
    assert (
        env in config["eventbridge"]["security_bus_name"]
    ), f"security_bus_name missing env in {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_lakeformation_bucket_reference(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    s3_bucket_names = {b["name"] for b in config["s3"]["buckets"]}
    for bucket in config["lakeformation"]["buckets"]:
        assert (
            bucket["name"] in s3_bucket_names
        ), f"LakeFormation bucket {bucket['name']} not found in S3 buckets for {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_stepfunctions_end_state_present(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    for sm in config["stepfunctions"]["state_machines"]:
        assert any(
            step.get("end", False) for step in sm["definition"]
        ), f"No end state in state machine {sm['id']} for {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_vector_store_credentials(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    vs = config["vector_store"]
    assert vs["db_user"], f"vector_store.db_user missing or empty in {filename}"
    assert vs["db_password"], f"vector_store.db_password missing or empty in {filename}"


@pytest.mark.parametrize("filename", ["dev.yml", "staging.yml", "prod.yml"])
def test_cloud_native_hardening(filename):
    config_path = CONFIG_DIR / filename
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    hardening = config["cloud_native_hardening"]
    assert (
        hardening["enable_cloudwatch_alarms"] is True
    ), f"CloudWatch alarms not enabled in {filename}"
    assert hardening["alarm_email"], f"alarm_email missing in {filename}"
