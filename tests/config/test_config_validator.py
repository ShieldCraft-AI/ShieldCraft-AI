from __future__ import annotations

from pathlib import Path
from typing import Dict

import pytest
import yaml

from config.schema.config_validator import ValidationResult, validate_config

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


def _write_temp_config(tmp_path: Path, payload: Dict) -> Path:
    target = tmp_path / "tmp.yml"
    with target.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle)
    return target


def _update_existing_config(tmp_path: Path, source_name: str, mutate) -> Path:
    target = tmp_path / f"{source_name}.yml"
    target.write_text((CONFIG_DIR / f"{source_name}.yml").read_text(), encoding="utf-8")
    mutate(target)
    return target


class TestValidateConfig:
    def test_valid_configs(self):
        for env in ("dev", "staging", "prod"):
            result = validate_config(str(CONFIG_DIR / f"{env}.yml"))
            assert isinstance(result, ValidationResult)
            assert result.valid is True
            assert not result.errors
            assert not result.schema_errors
            assert not result.missing_sections

    def test_prod_config_required_invariants(self, tmp_path: Path):
        def mutate(path: Path) -> None:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            data["s3"]["buckets"][0]["removal_policy"] = "DESTROY"
            path.write_text(yaml.safe_dump(data), encoding="utf-8")

        path = _update_existing_config(tmp_path, "prod", mutate)
        result = validate_config(str(path))
        assert result.valid is False
        assert any("RETAIN" in err for err in result.schema_errors)

    def test_schema_mismatch(self, tmp_path: Path):
        path = _write_temp_config(
            tmp_path,
            {
                "app": {"env": "dev"},
                "s3": {},
                "glue": {},
                "lambda_": {"functions": [{}]},
            },
        )
        result = validate_config(str(path))
        assert result.valid is False
        assert any("lambda_.functions" in err for err in result.schema_errors)

    def test_missing_required_sections(self, tmp_path: Path):
        path = _write_temp_config(tmp_path, {"app": {}, "glue": {}})
        result = validate_config(str(path))
        assert result.valid is False
        assert set(result.missing_sections) == {"app", "s3"}

    def test_cross_environment_structure_drift(self):
        dev_fp = validate_config(str(CONFIG_DIR / "dev.yml")).structure_fingerprint
        stage_fp = validate_config(
            str(CONFIG_DIR / "staging.yml")
        ).structure_fingerprint
        assert dev_fp == stage_fp

    def test_yaml_parse_error(self, tmp_path: Path):
        malformed = tmp_path / "bad.yml"
        malformed.write_text("app: [\n  -", encoding="utf-8")
        result = validate_config(str(malformed))
        assert result.valid is False
        assert result.errors

    def test_environment_resolves_from_filename(self, tmp_path: Path):
        original = _write_temp_config(
            tmp_path, {"app": {"env": ""}, "s3": {}, "glue": {}}
        )
        path = original.with_name("qa.yml")
        path.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")
        result = validate_config(str(path))
        assert result.environment == "qa"
