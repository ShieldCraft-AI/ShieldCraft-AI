# Config Validation Contract

ShieldCraft environments share a deterministic configuration contract enforced by `config.schema.config_validator.validate_config`. The validator loads a YAML file, verifies the required sections (`app`, `s3`, `glue`), runs the Pydantic `ShieldCraftConfig` schema, and returns a structured `ValidationResult` that captures errors, schema violations, missing sections, and a deterministic structure fingerprint.

## Usage

```bash
# Validate a single file
poetry run python -c "from config.schema.config_validator import validate_config; print(validate_config('config/dev.yml'))"

# Run the full validation suite
nox -s config_validate
```

`config_validate` runs inside the existing Nox registry and will:
- validate `config/dev.yml`, `config/staging.yml`, and `config/prod.yml`
- aggregate schema and required-section errors
- compare structure fingerprints to detect cross-environment drift

Any failure raises a deterministic error message and exits non-zero.

## Integration Points

- CI/CD: add `nox -s config_validate` before deployment to block drift or schema regressions.
- Tests: `tests/config/test_config_validator.py` covers happy-path configs, schema mismatch, missing sections, prod invariants, YAML parse errors, and drift detection logic.
- Tooling: other code can import `validate_config` to gate custom workflows without duplicating schema knowledge.
