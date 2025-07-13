"""
Check config intagrity for ShieldCraft AI project.
This script checks referential integrity of networking resources in the config files.
"""

import os
import yaml

CONFIG_DIR = "config"
ENV_FILES = ["dev.yml", "staging.yml", "prod.yml"]


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def check_integrity(config, filename):
    errors = []

    # Gather defined subnets and security groups
    networking = config.get("networking", {})
    defined_subnets = {s["id"] for s in networking.get("subnets", []) if "id" in s}
    defined_sgs = {
        sg["id"] for sg in networking.get("security_groups", []) if "id" in sg
    }

    # Helper to check references
    def check_refs(refs, defined, ref_type, context):
        for ref in refs:
            if ref not in defined:
                errors.append(
                    f"{filename}: {ref_type} '{ref}' referenced in {context} but not defined in networking.{ref_type}s"
                )

    # Check MSK cluster references
    msk = config.get("msk", {})
    cluster = msk.get("cluster", {})
    check_refs(
        cluster.get("vpc_subnet_ids", []),
        defined_subnets,
        "subnet",
        "msk.cluster.vpc_subnet_ids",
    )
    check_refs(
        cluster.get("security_group_ids", []),
        defined_sgs,
        "security_group",
        "msk.cluster.security_group_ids",
    )

    # Check Lambda function references
    lambda_ = config.get("lambda_", {})
    for fn in lambda_.get("functions", []):
        check_refs(
            fn.get("vpc_subnet_ids", []),
            defined_subnets,
            "subnet",
            f"lambda_.functions[{fn.get('id', '?')}].vpc_subnet_ids",
        )
        check_refs(
            fn.get("security_group_ids", []),
            defined_sgs,
            "security_group",
            f"lambda_.functions[{fn.get('id', '?')}].security_group_ids",
        )

    # Check Opensearch security group
    opensearch = config.get("opensearch", {})
    sg_id = opensearch.get("security_group", {}).get("id")
    if sg_id and sg_id not in defined_sgs:
        errors.append(
            f"{filename}: security_group '{sg_id}' referenced in opensearch.security_group.id but not defined in networking.security_groups"
        )

    return errors


def main():
    all_errors = []
    for env_file in ENV_FILES:
        path = os.path.join(CONFIG_DIR, env_file)
        if not os.path.exists(path):
            print(f"Config file not found: {path}")
            continue
        config = load_yaml(path)
        errors = check_integrity(config, env_file)
        if errors:
            all_errors.extend(errors)

    if all_errors:
        print("Referential integrity check FAILED:")
        for err in all_errors:
            print("  -", err)
        exit(1)
    else:
        print("Referential integrity check PASSED: All references are valid.")


if __name__ == "__main__":
    main()
