"""
Audit script for ShieldCraft AI config files.
Scans for plaintext secrets in fields that should be vault references.
Usage:
    poetry run python scripts/audit_secrets.py /path/to/config.yml
"""

import sys
import re
import yaml
from pathlib import Path


def find_plaintext_secrets(config: dict, secret_fields):
    vault_pattern = re.compile(r"^(aws-vault:|arn:aws:secretsmanager:)")
    issues = []
    for field in secret_fields:
        value = config.get(field)
        if value is not None and not vault_pattern.match(str(value)):
            issues.append((field, value))
    return issues


def audit_config_file(config_path: str):
    secret_fields = ["sns_topic_secret_arn", "external_api_key_arn"]
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    issues = find_plaintext_secrets(config.get("app", {}), secret_fields)
    # Check top-level fields, handle missing or null config sections
    issues = find_plaintext_secrets(
        (
            config.get("app", {})
            if config and isinstance(config.get("app", {}), dict)
            else {}
        ),
        secret_fields,
    )
    # Check hardening section if present
    hardening = config.get("cloud_native_hardening") if config else None
    if isinstance(hardening, dict):
        issues += find_plaintext_secrets(hardening, secret_fields)
    if issues:
        print(f"[!] Plaintext secrets found in {config_path}:")
        for field, value in issues:
            print(f"    - {field}: {value}")
        return 1
    print(f"[✓] No plaintext secrets found in {config_path}.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: poetry run python scripts/audit_secrets.py /path/to/config.yml")
        sys.exit(2)
    config_path = sys.argv[1]
    if not Path(config_path).is_file():
        print(f"Config file not found: {config_path}")
        sys.exit(2)
    sys.exit(audit_config_file(config_path))
