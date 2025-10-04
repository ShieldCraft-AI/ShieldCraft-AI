#!/usr/bin/env python3
"""
Documentation Baseline Review
Compares Proton templates vs discovered architecture vs documentation
to identify gaps and generate update recommendations.
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Set


def load_discovery_data() -> Dict:
    """Load the architecture discovery data"""
    discovery_file = Path("docs-site/static/data/architecture_discovery.json")
    if discovery_file.exists():
        with open(discovery_file, "r") as f:
            return json.load(f)
    return {}


def get_proton_templates() -> Set[str]:
    """Get list of all Proton templates"""
    proton_dir = Path("proton")
    templates = set()

    for template_file in proton_dir.glob("*.yaml"):
        # Extract service name from filename
        name = template_file.stem.replace("-service-template", "").replace(
            "-environment-template", ""
        )
        templates.add(name.upper())

    return templates


def get_discovered_services() -> Set[str]:
    """Get services from discovery data"""
    discovery = load_discovery_data()
    services = set()

    if "service_matrix" in discovery:
        for service_name in discovery["service_matrix"].keys():
            services.add(service_name.upper())

    return services


def analyze_coverage():
    """Analyze coverage between templates, discovery, and docs"""
    templates = get_proton_templates()
    discovered = get_discovered_services()

    print("🔍 DOCUMENTATION BASELINE REVIEW")
    print("=" * 60)

    print(f"\n📋 TEMPLATE INVENTORY ({len(templates)})")
    print("-" * 40)
    for template in sorted(templates):
        status = "✅ ACTIVE" if template in discovered else "❌ MISSING"
        print(f"  {template:<20} {status}")

    print(f"\n🔧 DISCOVERED SERVICES ({len(discovered)})")
    print("-" * 40)
    for service in sorted(discovered):
        template_exists = (
            "✅ HAS TEMPLATE" if service in templates else "❌ NO TEMPLATE"
        )
        print(f"  {service:<20} {template_exists}")

    missing_from_discovery = templates - discovered
    missing_templates = discovered - templates

    print(
        f"\n❌ SERVICES WITH TEMPLATES BUT NOT DISCOVERED ({len(missing_from_discovery)})"
    )
    print("-" * 60)
    for service in sorted(missing_from_discovery):
        print(f"  {service}")
        # Check if it's documented in aws_stack_architecture.md

    print(f"\n❌ DISCOVERED SERVICES WITHOUT TEMPLATES ({len(missing_templates)})")
    print("-" * 60)
    for service in sorted(missing_templates):
        print(f"  {service}")

    # Coverage analysis
    coverage_pct = (len(discovered) / len(templates)) * 100 if templates else 0

    print(f"\n📊 COVERAGE ANALYSIS")
    print("-" * 40)
    print(f"  Templates:        {len(templates)}")
    print(f"  Active Services:  {len(discovered)}")
    print(f"  Coverage:         {coverage_pct:.1f}%")
    print(f"  Missing Services: {len(missing_from_discovery)}")

    return {
        "templates": templates,
        "discovered": discovered,
        "missing_from_discovery": missing_from_discovery,
        "missing_templates": missing_templates,
        "coverage_percent": coverage_pct,
    }


def check_documentation_alignment():
    """Check if aws_stack_architecture.md aligns with actual templates"""

    # Read the current documentation
    doc_file = Path("docs-site/docs/github/aws_stack_architecture.md")
    if not doc_file.exists():
        print("❌ Documentation file not found!")
        return

    with open(doc_file, "r") as f:
        doc_content = f.read()

    templates = get_proton_templates()
    discovered = get_discovered_services()

    print(f"\n📄 DOCUMENTATION ALIGNMENT CHECK")
    print("-" * 50)

    # Check if all discovered services are documented
    services_in_doc = []
    for service in sorted(discovered):
        service_lower = service.lower()
        if service_lower in doc_content.lower():
            services_in_doc.append(service)
            print(f"  ✅ {service:<20} documented")
        else:
            print(f"  ❌ {service:<20} NOT documented")

    print(f"\n📊 DOCUMENTATION COVERAGE")
    print("-" * 40)
    print(f"  Discovered Services:  {len(discovered)}")
    print(f"  Documented Services:  {len(services_in_doc)}")
    print(f"  Documentation Gap:    {len(discovered) - len(services_in_doc)}")


def generate_recommendations():
    """Generate specific recommendations for documentation updates"""

    analysis = analyze_coverage()

    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 60)

    if analysis["missing_from_discovery"]:
        print("\n1. INVESTIGATE MISSING SERVICES:")
        print("   The following templates exist but services aren't active:")
        for service in sorted(analysis["missing_from_discovery"]):
            print(f"   - {service}: Check if this should be enabled in env configs")

    if analysis["missing_templates"]:
        print("\n2. CREATE MISSING TEMPLATES:")
        print("   The following services are active but lack templates:")
        for service in sorted(analysis["missing_templates"]):
            print(f"   - {service}: Create Proton template")

    if analysis["coverage_percent"] < 100:
        print(f"\n3. IMPROVE COVERAGE:")
        print(f"   Current coverage: {analysis['coverage_percent']:.1f}%")
        print(f"   Target: 100% (all templates should have active services)")

    print(f"\n4. UPDATE DOCUMENTATION:")
    print(f"   - Review aws_stack_architecture.md against actual services")
    print(f"   - Ensure dependency matrix reflects current architecture")
    print(f"   - Update service descriptions based on discovery data")


if __name__ == "__main__":
    analyze_coverage()
    check_documentation_alignment()
    generate_recommendations()
