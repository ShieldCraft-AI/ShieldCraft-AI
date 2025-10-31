import os
import glob
import pytest

yaml = pytest.importorskip("yaml")

CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config"))

REQUIRED_CONFIG_SECTIONS = [
    "ai_core",
    "airbyte",
    "app",
    "beir",
    "chunking",
    "cloud_native_hardening",
    "data_quality",
    "drift_scan_schedule",
    "embedding",
    "eventbridge",
    "glue",
    "lakeformation",
    "msk",
    "mteb",
    "networking",
]


@pytest.mark.parametrize("config_file", glob.glob(os.path.join(CONFIG_DIR, "*.yml")))
def test_config_file_loads(config_file):
    with open(config_file) as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict)


@pytest.mark.parametrize("config_file", glob.glob(os.path.join(CONFIG_DIR, "*.yml")))
def test_config_sections_present(config_file):
    with open(config_file) as f:
        data = yaml.safe_load(f)
    for section in REQUIRED_CONFIG_SECTIONS:
        assert section in data, f"Missing section {section} in {config_file}"


@pytest.mark.parametrize(
    "section,required_keys",
    [
        ("msk", ["cluster"]),
        ("app", ["account", "env", "region"]),
        ("glue", ["database_name"]),
        ("lakeformation", ["admin_role", "buckets"]),
    ],
)
@pytest.mark.parametrize("config_file", glob.glob(os.path.join(CONFIG_DIR, "*.yml")))
def test_config_section_keys(config_file, section, required_keys):
    with open(config_file) as f:
        data = yaml.safe_load(f)
    if section in data:
        for key in required_keys:
            assert (
                key in data[section]
            ), f"Missing key {key} in section {section} of {config_file}"


@pytest.mark.parametrize("config_file", glob.glob(os.path.join(CONFIG_DIR, "*.yml")))
def test_no_secrets_in_config(config_file):
    import yaml as _yaml

    with open(config_file) as f:
        data = _yaml.safe_load(f)
    forbidden = ["aws_secret_access_key", "password", "private_key", "token"]

    def scan_values(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                yield from scan_values(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from scan_values(v)
        elif isinstance(obj, str):
            yield obj

    for value in scan_values(data):
        for word in forbidden:
            # Only fail if forbidden word is in a value (not a key)
            if word in value.lower():
                raise AssertionError(
                    f"Forbidden secret value '{word}' found in {config_file}: {value}"
                )
