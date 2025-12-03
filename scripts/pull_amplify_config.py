#!/usr/bin/env python3
"""
DOCUMENTED DEPLOY HELPER  -  Reviewed
Purpose: fetch runtime Amplify config from AWS Secrets Manager for docs usage.
This script reads secrets and writes to a local docs file; do not run in CI
without secure credentials. Changes require reviewer approval.

Fetch the Amplify runtime config secret and write docs-site/static/amplify-config.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

DEFAULT_REGION = "af-south-1"
DEFAULT_SECRET_NAME = "shieldcraft/amplify-config"
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[1] / "docs-site" / "static" / "amplify-config.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pull Amplify config from AWS Secrets Manager"
    )
    parser.add_argument(
        "--region", default=DEFAULT_REGION, help="AWS region for the secret"
    )
    parser.add_argument(
        "--secret-name", default=DEFAULT_SECRET_NAME, help="Secrets Manager name"
    )
    parser.add_argument(
        "--output", default=str(DEFAULT_OUTPUT), help="Output file path"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite output if it exists"
    )
    parser.add_argument(
        "--preview", action="store_true", help="Print the downloaded JSON"
    )
    return parser.parse_args()


def fetch_secret(region: str, secret_name: str) -> dict:
    client = boto3.client("secretsmanager", region_name=region)
    try:
        resp = client.get_secret_value(SecretId=secret_name)
    except ClientError as exc:
        raise SystemExit(
            f"Failed to fetch secret {secret_name} in {region}: {exc}"
        ) from exc
    body = resp.get("SecretString")
    if not body:
        raise SystemExit("SecretString was empty or binary")
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Secret payload is not valid JSON: {exc}") from exc


def write_config(data: dict, output_path: Path, overwrite: bool) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not overwrite:
        raise SystemExit(f"{output_path} already exists. Pass --force to overwrite.")
    output_path.write_text(json.dumps(data, indent=2))
    return output_path


def main() -> int:
    args = parse_args()
    config = fetch_secret(args.region, args.secret_name)
    out_path = write_config(config, Path(args.output).resolve(), args.force)
    print(f"Wrote {out_path}")
    print(
        "docs-site/static/amplify-config.json is gitignored; commit the secret only via CI."
    )
    if args.preview:
        print(json.dumps(config, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
