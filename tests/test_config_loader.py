# Advanced/production-grade tests
import threading
import time


def test_thread_safety_singleton(monkeypatch, tmp_path):
    # Singleton should be thread-safe and always return the same instance
    config = {"app": {"env": "dev"}, "s3": {}, "glue": {}, "msk": {}}
    config_path = tmp_path / "dev.yml"
    import yaml

    with open(config_path, "w") as f:
        yaml.dump(config, f)
    # Patch CONFIG_DIR in the loader module to point to tmp_path
    import sys

    loader_mod = sys.modules["infra.utils.config_loader"]
    old_config_dir = loader_mod.CONFIG_DIR
    loader_mod.CONFIG_DIR = str(tmp_path)
    try:
        monkeypatch.setenv("CONFIG_BACKEND", "local")
        monkeypatch.setenv("ENV", "dev")
        from infra.utils.config_loader import get_config_loader

        results = []

        def load():
            results.append(get_config_loader())

        threads = [threading.Thread(target=load) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert all(r is results[0] for r in results)
    finally:
        loader_mod.CONFIG_DIR = old_config_dir


def test_large_config_performance(tmp_path):
    # Simulate a large config file
    big_section = {f"key{i}": i for i in range(10000)}
    config = {"app": {"env": "dev"}, "s3": big_section, "glue": {}, "msk": {}}
    config_path = tmp_path / "dev.yml"
    import yaml

    with open(config_path, "w") as f:
        yaml.dump(config, f)
    backend = LocalYamlBackend(str(tmp_path))
    start = time.time()
    loader = ConfigLoader(env="dev", backend=backend)
    elapsed = time.time() - start
    assert loader.get("app.env") == "dev"
    assert elapsed < 3  # Should load quickly and reliably in CI


def test_secret_resolution_extension_point():
    # Simulate a future AWS Secrets Manager integration
    class SecretBackend:
        def load(self, env):
            return {
                "app": {"env": "dev", "secret": "aws-vault:my-secret"},
                "s3": {},
                "glue": {},
                "msk": {},
            }

    loader = ConfigLoader(env="dev", backend=SecretBackend())
    val = loader.get("app.secret")
    assert val.startswith("[REDACTED:")


def test_cloud_native_env_vars(monkeypatch):
    # Simulate running in a container with S3 backend env vars
    monkeypatch.setenv("CONFIG_BACKEND", "s3")
    monkeypatch.setenv("CONFIG_S3_BUCKET", "dummy-bucket")
    monkeypatch.setenv("CONFIG_S3_PREFIX", "test/")

    # Use a dummy backend to avoid real AWS calls
    class DummyS3:
        def load(self, env):
            return {"app": {"env": env}, "s3": {}, "glue": {}, "msk": {}}

    loader = ConfigLoader(env="prod", backend=DummyS3())
    assert loader.get("app.env") == "prod"


def test_reload_consistency():
    # Simulate hot reload
    config1 = {"app": {"env": "dev", "foo": "bar"}, "s3": {}, "glue": {}, "msk": {}}
    config2 = {"app": {"env": "dev", "foo": "baz"}, "s3": {}, "glue": {}, "msk": {}}

    class ReloadBackend:
        def __init__(self):
            self._config = config1

        def load(self, env):
            return self._config

    backend = ReloadBackend()
    loader = ConfigLoader(env="dev", backend=backend)
    assert loader.get("app.foo") == "bar"
    backend._config = config2
    loader.reload()
    assert loader.get("app.foo") == "baz"


# Additional comprehensive tests for config loader and backends

import pytest
from infra.utils.config_loader import ConfigLoader
from infra.utils.config_backends import LocalYamlBackend


class DummyBackend:
    def __init__(self, config):
        self._config = config

    def load(self, env):
        return self._config


def test_strict_mode_missing_section():
    config = {"app": {}, "s3": {}, "glue": {}}
    with pytest.raises(Exception):
        ConfigLoader(env="dev", backend=DummyBackend(config), strict=True)


def test_strict_mode_invalid_type():
    config = {"app": [], "s3": {}, "glue": {}, "msk": {}}
    with pytest.raises(Exception):
        ConfigLoader(env="dev", backend=DummyBackend(config), strict=True)


def test_backend_selection_env(monkeypatch, tmp_path):
    config = {"app": {"env": "dev"}, "s3": {}, "glue": {}, "msk": {}}
    config_path = tmp_path / "dev.yml"
    import yaml

    with open(config_path, "w") as f:
        yaml.dump(config, f)
    backend = LocalYamlBackend(str(tmp_path))
    loader = ConfigLoader(env="dev", backend=backend)
    assert loader.get("app.env") == "dev"


def test_secret_resolution_nonmatch():
    config = {
        "app": {"env": "dev", "notsecret": "plain"},
        "s3": {},
        "glue": {},
        "msk": {},
    }
    loader = ConfigLoader(env="dev", backend=DummyBackend(config))
    assert loader.get("app.notsecret") == "plain"


def test_export_redacts_nested_secrets():
    config = {
        "app": {"env": "dev", "secrets": ["aws-vault:foo", "bar"]},
        "s3": {},
        "glue": {},
        "msk": {},
    }
    loader = ConfigLoader(env="dev", backend=DummyBackend(config))
    exported = loader.export()
    assert exported["app"]["secrets"][0] == "[REDACTED]"
    assert exported["app"]["secrets"][1] == "bar"


def test_env_override_precedence(monkeypatch):
    config = {"app": {"env": "dev", "foo": "bar"}, "s3": {}, "glue": {}, "msk": {}}
    loader = ConfigLoader(env="dev", backend=DummyBackend(config))
    monkeypatch.setenv("APP_FOO", "baz")
    assert loader.get("app.foo") == "baz"


def test_env_override_missing(monkeypatch):
    config = {"app": {"env": "dev", "foo": "bar"}, "s3": {}, "glue": {}, "msk": {}}
    loader = ConfigLoader(env="dev", backend=DummyBackend(config))
    monkeypatch.delenv("APP_FOO", raising=False)
    assert loader.get("app.foo") == "bar"


def test_reload_logic(tmp_path):
    config1 = {"app": {"env": "dev", "foo": "bar"}, "s3": {}, "glue": {}, "msk": {}}
    config2 = {"app": {"env": "dev", "foo": "baz"}, "s3": {}, "glue": {}, "msk": {}}

    class ReloadBackend:
        def __init__(self):
            self._config = config1

        def load(self, env):
            return self._config

    backend = ReloadBackend()
    loader = ConfigLoader(env="dev", backend=backend)
    assert loader.get("app.foo") == "bar"
    backend._config = config2
    loader.reload()
    assert loader.get("app.foo") == "baz"


def test_singleton_behavior(monkeypatch, tmp_path):
    # Singleton only applies when no backend is provided
    config = {"app": {"env": "dev"}, "s3": {}, "glue": {}, "msk": {}}
    config_path = tmp_path / "dev.yml"
    import yaml

    with open(config_path, "w") as f:
        yaml.dump(config, f)
    backend = LocalYamlBackend(str(tmp_path))
    loader1 = ConfigLoader(env="dev", backend=backend)
    loader2 = ConfigLoader(env="dev", backend=backend)
    assert loader1 is not loader2
    # But with backend, always new instance
    loader3 = ConfigLoader(env="dev", backend=DummyBackend(config))
    loader4 = ConfigLoader(env="dev", backend=DummyBackend(config))
    assert loader3 is not loader4


def test_optional_sections():
    config = {"app": {"env": "dev"}, "s3": {}, "glue": {}, "msk": {}}
    loader = ConfigLoader(env="dev", backend=DummyBackend(config), strict=True)
    # Optional sections should be missing but not raise
    assert "lambda_" not in loader.config or loader.config["lambda_"] is None


def test_extra_keys_ignored():
    config = {"app": {"env": "dev"}, "s3": {}, "glue": {}, "msk": {}, "extra": 123}
    loader = ConfigLoader(env="dev", backend=DummyBackend(config), strict=True)
    assert loader.get("app.env") == "dev"


def test_empty_config_raises():
    with pytest.raises(Exception):
        ConfigLoader(env="dev", backend=DummyBackend({}), strict=True)


def test_malformed_yaml(tmp_path):
    bad_yaml = "app: [unclosed"
    config_path = tmp_path / "dev.yml"
    with open(config_path, "w") as f:
        f.write(bad_yaml)
    backend = LocalYamlBackend(str(tmp_path))
    with pytest.raises(Exception):
        ConfigLoader(env="dev", backend=backend, strict=True)


def test_nonexistent_env():
    class FailingBackend:
        def load(self, env):
            raise FileNotFoundError(f"Config for env {env} not found")

    with pytest.raises(Exception):
        ConfigLoader(env="nonexistent", backend=FailingBackend(), strict=True)


import os
import tempfile
import yaml
from infra.utils.config_backends import S3Backend, SSMBackend


class DummyS3Backend(S3Backend):
    def __init__(self, config_dict):
        self._config_dict = config_dict

    def load(self, env: str):
        return self._config_dict


class DummySSMBackend(SSMBackend):
    def __init__(self, config_dict):
        self._config_dict = config_dict

    def load(self, env: str):
        return self._config_dict


def make_temp_yaml(config: dict) -> str:
    fd, path = tempfile.mkstemp(suffix=".yml")
    with os.fdopen(fd, "w") as f:
        yaml.dump(config, f)
    return path


def test_local_yaml_backend():
    config = {"app": {"env": "dev"}, "s3": {}, "glue": {}, "msk": {}}
    path = make_temp_yaml(config)
    config_dir = os.path.dirname(path)
    env = os.path.splitext(os.path.basename(path))[0]
    os.rename(path, os.path.join(config_dir, f"{env}.yml"))
    backend = LocalYamlBackend(config_dir)
    loaded = backend.load(env)
    assert loaded["app"]["env"] == "dev"


def test_config_loader_local(monkeypatch):
    config = {"app": {"env": "dev"}, "s3": {}, "glue": {}, "msk": {}}
    path = make_temp_yaml(config)
    config_dir = os.path.dirname(path)
    env = os.path.splitext(os.path.basename(path))[0]
    os.rename(path, os.path.join(config_dir, f"{env}.yml"))
    loader = ConfigLoader(env=env, backend=LocalYamlBackend(config_dir))
    assert loader.get("app.env") == "dev"
    assert loader.get_section("app")["env"] == "dev"


def test_config_loader_s3():
    config = {"app": {"env": "prod"}, "s3": {}, "glue": {}, "msk": {}}
    loader = ConfigLoader(env="prod", backend=DummyS3Backend(config))
    assert loader.get("app.env") == "prod"


def test_config_loader_ssm():
    config = {"app": {"env": "staging"}, "s3": {}, "glue": {}, "msk": {}}
    loader = ConfigLoader(env="staging", backend=DummySSMBackend(config))
    assert loader.get("app.env") == "staging"


def test_schema_validation_error():
    config = {"app": {}, "s3": {}}  # missing glue, msk
    with pytest.raises(Exception):
        ConfigLoader(env="dev", backend=DummyS3Backend(config), strict=True)


def test_env_override(monkeypatch):
    config = {"app": {"env": "dev", "foo": "bar"}, "s3": {}, "glue": {}, "msk": {}}
    loader = ConfigLoader(env="dev", backend=DummyS3Backend(config))
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("APP_FOO", "baz")
    assert loader.get("app.foo") == "baz"


def test_secret_resolution():
    config = {
        "app": {"env": "dev", "secret": "aws-vault:my-secret"},
        "s3": {},
        "glue": {},
        "msk": {},
    }
    loader = ConfigLoader(env="dev", backend=DummyS3Backend(config))
    val = loader.get("app.secret")
    assert val.startswith("[REDACTED:")


def test_export_redacts_secrets():
    config = {
        "app": {"env": "dev", "secret": "aws-vault:my-secret"},
        "s3": {},
        "glue": {},
        "msk": {},
    }
    loader = ConfigLoader(env="dev", backend=DummyS3Backend(config))
    exported = loader.export()
    assert exported["app"]["secret"] == "[REDACTED]"
