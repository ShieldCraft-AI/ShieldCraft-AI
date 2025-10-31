import os
import warnings
import pytest

try:
    from aws_cdk import App
except ImportError:
    App = None
from infra.shieldcraft_app_stage import ShieldcraftAppStage

pytestmark = pytest.mark.filterwarnings("ignore::Warning")


@pytest.mark.unit
def test_app_synths_without_deploy(monkeypatch):
    if App is None:
        pytest.skip("aws_cdk is not installed; skipping CDK synth test.")
    monkeypatch.setenv("ENV", "dev")
    from infra.utils import config_loader

    orig_get_config_loader = config_loader.get_config_loader

    def fake_loader(*a, **kw):
        loader = orig_get_config_loader(*a, **kw)

        def get_section(section):
            cfg = loader.export()
            if "msk" not in cfg or not isinstance(cfg["msk"], dict):
                cfg["msk"] = {}
            if "cluster" not in cfg["msk"] or not isinstance(
                cfg["msk"]["cluster"], dict
            ):
                cfg["msk"]["cluster"] = {
                    "id": "test-msk-id",
                    "name": "test-msk",
                    "kafka_version": "3.5.1",
                    "number_of_broker_nodes": 1,
                    "instance_type": "kafka.m5.large",
                }

                def fake_loader(*a, **kw):
                    class Loader:
                        def get_section(self, section):
                            if section == "msk":
                                return {
                                    "cluster": {
                                        "id": "test-msk-id",
                                        "name": "test-msk",
                                        "kafka_version": "3.5.1",
                                        "number_of_broker_nodes": 1,
                                        "instance_type": "kafka.m5.large",
                                    }
                                }
                            return {}

                        def export(self):
                            return {
                                "msk": {
                                    "cluster": {
                                        "id": "test-msk-id",
                                        "name": "test-msk",
                                        "kafka_version": "3.5.1",
                                        "number_of_broker_nodes": 1,
                                        "instance_type": "kafka.m5.large",
                                    }
                                },
                                "app": {"env": "dev"},
                                "lakeformation": {},
                            }

                    return Loader()
