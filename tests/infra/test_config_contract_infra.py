import pytest
from infra.utils.config_loader import get_config_loader


@pytest.mark.parametrize("env", ["dev", "staging", "prod"])
def test_msk_config_contract(env):
    cfg = get_config_loader(env=env).export()
    msk = cfg.get("msk", {})
    assert "cluster" in msk
    cluster = msk["cluster"]
    for key in [
        "id",
        "name",
        "kafka_version",
        "number_of_broker_nodes",
        "instance_type",
    ]:
        assert key in cluster, f"Missing {key} in msk.cluster for env {env}"


import pathlib
from infra.utils.config_loader import ConfigLoader, LocalYamlBackend

CONFIG_DIR = str(pathlib.Path(__file__).parent.parent.parent / "config")


@pytest.mark.parametrize("env", ["dev", "staging", "prod"])
def test_lakeformation_buckets_contract(env):
    loader = ConfigLoader(env=env, backend=LocalYamlBackend(CONFIG_DIR))
    cfg = loader.export()
    lf = cfg.get("lakeformation", {})
    assert "buckets" in lf
    assert isinstance(lf["buckets"], list)
    for bucket in lf["buckets"]:
        assert "id" in bucket and "name" in bucket
