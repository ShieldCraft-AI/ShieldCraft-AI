#!/usr/bin/env python3
"""
update_msk_arn.py

After a CDK deploy, use this script to update the MSK cluster ARN in the correct environment YAML config.
Usage:
  python update_msk_arn.py --env dev --arn <MSK_CLUSTER_ARN>

This ensures integration tests and automation always use the correct cluster for the environment.
"""
import argparse
import sys
import os
import yaml

def update_arn(config_path, arn):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    if "msk" not in config or "cluster" not in config["msk"]:
        print(f"ERROR: Could not find msk.cluster section in {config_path}")
        sys.exit(1)
    config["msk"]["cluster"]["arn"] = arn
    with open(config_path, 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
    print(f"Updated {config_path} with MSK cluster ARN.")


def extract_arn_from_cdk_output(output_path, export_name=None):
    """
    Extract the MSK cluster ARN from a CDK output file (JSON or YAML).
    If export_name is provided, use it to find the correct output key.
    """
    import json
    import yaml as yamllib
    if not os.path.exists(output_path):
        print(f"ERROR: CDK output file not found: {output_path}")
        sys.exit(1)
    with open(output_path, 'r') as f:
        if output_path.endswith('.json'):
            outputs = json.load(f)
        else:
            outputs = yamllib.safe_load(f)
    # Try to find the ARN by export name or by guessing
    arn = None
    if export_name:
        # CDK CLI output format
        arn = outputs.get(export_name)
        if arn:
            return arn
    # Try common keys
    for k, v in outputs.items():
        if isinstance(v, dict) and 'Export' in v and 'Value' in v:
            if export_name and v['Export'].get('Name') == export_name:
                return v['Value']
            if 'msk' in k.lower() and 'arn' in k.lower():
                return v['Value']
        if export_name and k == export_name:
            return v
        if 'msk' in k.lower() and 'arn' in k.lower():
            return v
    print(f"ERROR: Could not find MSK cluster ARN in CDK output {output_path}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Update MSK cluster ARN in environment config YAML.")
    parser.add_argument('--env', required=True, help='Environment name (dev, staging, prod)')
    parser.add_argument('--arn', help='MSK cluster ARN to set (overrides --cdk-output)')
    parser.add_argument('--cdk-output', help='Path to CDK output file (JSON or YAML)')
    parser.add_argument('--export-name', help='CDK export name for the MSK cluster ARN (optional)')
    parser.add_argument('--config-dir', default='config', help='Path to config directory (default: ./config)')
    args = parser.parse_args()

    config_path = os.path.join(args.config_dir, f"{args.env}.yml")
    if not os.path.exists(config_path):
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)

    arn = args.arn
    if not arn:
        if not args.cdk_output:
            print("ERROR: Must provide either --arn or --cdk-output")
            sys.exit(1)
        arn = extract_arn_from_cdk_output(args.cdk_output, args.export_name)
    update_arn(config_path, arn)

if __name__ == "__main__":
    main()
