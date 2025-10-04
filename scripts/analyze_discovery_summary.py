#!/usr/bin/env python3
"""
Architecture Discovery Summary Generator

Quick analysis tool to understand the discovered ShieldCraft AI architecture.
"""

import json
from pathlib import Path
from collections import defaultdict


def analyze_discovery():
    """Analyze the architecture discovery results"""
    discovery_file = Path("docs-site/static/data/architecture_discovery.json")

    with open(discovery_file) as f:
        data = json.load(f)

    print("🎯 ShieldCraft AI Architecture Discovery Analysis")
    print("=" * 60)

    # Capabilities Analysis
    print(f"\n📋 CAPABILITIES ({len(data['capabilities'])})")
    print("-" * 40)
    for cap_id, cap in data["capabilities"].items():
        print(f"  {cap_id.upper():<15} {cap['capability_name']}")
        print(f"  {'Category:':<15} {cap['category']}")

        # Cost progression
        costs = cap["cost_progression"]
        dev_cost = costs.get("dev", 0)
        staging_cost = costs.get("staging", 0)
        prod_cost = costs.get("prod", 0)
        print(
            f"  {'Costs:':<15} DEV: ${dev_cost:.0f} → STAGING: ${staging_cost:.0f} → PROD: ${prod_cost:.0f}"
        )
        print()

    # Service Matrix Analysis
    print(f"\n🔧 SERVICE MATRIX ({len(data['service_matrix'])})")
    print("-" * 40)

    service_summary = defaultdict(dict)
    for service, envs in data["service_matrix"].items():
        print(f"  {service.upper():<20}", end="")
        for env in ["dev", "staging", "prod"]:
            if env in envs:
                instance = envs[env]
                mode = instance["mode"]
                cost = instance["estimated_monthly_cost_usd"]
                enabled = "✅" if instance["enabled"] else "❌"
                print(f" {env.upper()}: {enabled} {mode:<8} ${cost:<4.0f}", end="")
                service_summary[service][env] = {
                    "mode": mode,
                    "cost": cost,
                    "enabled": instance["enabled"],
                }
            else:
                print(f" {env.upper()}: ❌ {'none':<8} ${0:<4.0f}", end="")
        print()

    # Cost Analysis by Environment
    print(f"\n💰 COST ANALYSIS BY ENVIRONMENT")
    print("-" * 40)

    env_totals = defaultdict(float)
    for service, envs in service_summary.items():
        for env, details in envs.items():
            if details["enabled"]:
                env_totals[env] += details["cost"]

    for env in ["dev", "staging", "prod"]:
        total = env_totals[env]
        print(f"  {env.upper():<12} ${total:>6.0f} / month")

    # Service Mode Progression
    print(f"\n📈 SERVICE MODE PROGRESSION")
    print("-" * 40)

    for service, envs in service_summary.items():
        modes = []
        for env in ["dev", "staging", "prod"]:
            if env in envs and envs[env]["enabled"]:
                modes.append(f"{env}: {envs[env]['mode']}")
            else:
                modes.append(f"{env}: none")

        progression = " → ".join(modes)
        print(f"  {service:<20} {progression}")

    # Template Coverage
    print(f"\n📄 TEMPLATE COVERAGE")
    print("-" * 40)

    template_count = len(data["template_inventory"])
    active_services = len(
        [
            s
            for s, envs in data["service_matrix"].items()
            if any(inst["enabled"] for inst in envs.values())
        ]
    )

    print(f"  Templates Discovered: {template_count}")
    print(f"  Active Services:      {active_services}")
    print(f"  Coverage:             {(active_services/template_count)*100:.1f}%")

    # Security Features
    print(f"\n🔐 SECURITY POSTURE")
    print("-" * 40)

    for env, features in data["security_posture"].items():
        print(f"  {env.upper():<12} {', '.join(features)}")

    # Dependencies
    print(f"\n🔗 SERVICE DEPENDENCIES")
    print("-" * 40)

    for service, deps in data["dependency_graph"].items():
        if deps:
            print(f"  {service:<20} → {', '.join(deps)}")

    print(f"\n✅ Analysis complete!")


if __name__ == "__main__":
    analyze_discovery()
