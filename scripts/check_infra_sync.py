#!/usr/bin/env python3
"""
Quick check that the services listed in INFRA_BLUEPRINT (pricing.tsx) are actually enabled
in the environment configuration files under `config/` (dev/staging/prod). This is heuristic-based
and intended to catch obvious mismatches (e.g. OpenSearch disabled in dev but shown in Starter).

Run from repo root:
  ./scripts/check_infra_sync.py

No external deps required (uses PyYAML if installed for nicer parsing, but falls back to text search).
"""
import re
import os
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRICING = ROOT / "docs-site" / "src" / "pages" / "pricing.tsx"
CONFIG_DIR = ROOT / "config"
CONFIG_FILES = {
    "dev": CONFIG_DIR / "dev.yml",
    "staging": CONFIG_DIR / "staging.yml",
    "prod": CONFIG_DIR / "prod.yml",
}


def read_pricing_block(path: Path) -> str:
    txt = path.read_text(encoding="utf-8")
    # Find the INFRA_BLUEPRINT block
    m = re.search(r"const\s+INFRA_BLUEPRINT[\s\S]*?=\s*\{", txt)
    if not m:
        # fallback: find the long object literal start
        start = txt.find("const INFRA_BLUEPRINT")
        if start == -1:
            raise SystemExit("Could not locate INFRA_BLUEPRINT in pricing.tsx")
        txt = txt[start:]
    # We want the object literal until the closing '};' that ends the assignment
    m2 = re.search(r"const\s+INFRA_BLUEPRINT[\s\S]*?=\s*(\{[\s\S]*?\})\s*;", txt)
    block = m2.group(1) if m2 else txt
    return block


def extract_services_from_block(block: str):
    # simple approach: find all quoted strings inside the block and filter plausible service labels
    strings = re.findall(r"'([^']+)'|\"([^\"]+)\"", block)
    vals = [a or b for a, b in strings]
    # Filter items that look like service labels (contain space and letters) and ignore keys like 'region'
    services = [
        s.strip()
        for s in vals
        if re.search(r"[A-Za-z].*\s+", s)
        or s.lower().startswith(("amazon", "aws", "application", "attack", "airbyte"))
    ]
    # Deduplicate while preserving order
    seen = set()
    out = []
    for s in services:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def read_config_texts():
    texts = {}
    for env, p in CONFIG_FILES.items():
        if not p.exists():
            texts[env] = ""
        else:
            texts[env] = p.read_text(encoding="utf-8").lower()
    return texts


CHECK_KEYWORDS = {
    # service label -> keywords to look for in config YAML to indicate presence
    "Amazon OpenSearch Service": ["opensearch", "opensearch.mode", "opensearch:"],
    "Amazon SageMaker": ["sagemaker.mode", "sagemaker:"],
    "Amazon MSK": ["msk.mode", "msk:"],
    "Amazon S3": ["s3:", "buckets:", "analyticsdata", "rawdata"],
    "AWS Step Functions": ["stepfunctions", "state_machines", "step_functions"],
    "Amazon EventBridge": ["eventbridge", "data_bus_name", "security_bus_name"],
    "AWS Lambda": ["lambda_", "functions:", "lambda:"],
    "AWS Glue": ["glue:", "crawler", "glue.crawler", "enable_data_quality"],
    "Amazon CloudWatch": ["cloudwatch", "cloudwatch:"],
    "AWS Budgets": ["budgets", "aws budgets", "aws_budgets", "enable_budget"],
    "AWS Cost Explorer": ["cost explorer", "enable_cost_explorer", "cost_explorer"],
    "AWS Backup": ["aws backup", "aws_backup", "backup:"],
    "AWS Resilience Hub": ["resilience hub", "resilience_hub", "resiliencehub"],
    "AWS WAF": ["waf", "aws waf", "aws_waf"],
    "AWS Shield Advanced": ["shield advanced", "shield_advanced", "aws shield"],
    "AWS IAM": ["iam:", "aws iam", "iam_identity_center", "identity center"],
    "AWS IAM Identity Center": [
        "iam identity center",
        "iam_identity_center",
        "identity center",
    ],
    "AWS Security Hub": ["security hub", "security_hub", "aws security hub"],
    "Amazon GuardDuty": ["guardduty", "guard duty", "guard-duty"],
    "Amazon Detective": ["detective", "amazon detective"],
    "Amazon Inspector": ["inspector", "amazon inspector"],
    "AWS Artifact": ["artifact", "aws artifact"],
    "AWS CodePipeline": ["codepipeline", "aws codepipeline"],
    "Amazon API Gateway": ["api gateway", "api_gateway", "amazon api gateway"],
    "Application Load Balancer (ALB)": [
        "alb",
        "application load balancer",
        "load balancer",
    ],
    "Amazon EC2": ["ec2", "amazon ec2", "ec2 auto scaling", "auto scaling"],
    "Amazon OpenSearch Service": ["opensearch"],
    "AWS CloudTrail": ["cloudtrail", "cloud trail", "cloud_trail"],
    "AWS Control Tower": ["control tower", "control_tower", "aws control tower"],
}


def check_presence(service: str, config_texts: dict):
    keys = CHECK_KEYWORDS.get(service, [service.lower()])
    result = {}
    for env, txt in config_texts.items():
        found = False
        for k in keys:
            if k.lower() in txt:
                # Special-case opensearch: ensure not 'mode: none'
                if "opensearch" in k.lower():
                    # if 'mode: none' present near opensearch, treat as disabled
                    m = re.search(r"opensearch[:\s\n\r\S]*mode\s*:\s*(\w+)", txt)
                    if m and m.group(1).strip() == "none":
                        found = False
                        continue
                found = True
                break
        result[env] = found
    return result


def build_blueprint_tier_map(block: str):
    # Robust parsing: locate each tier key and extract its brace-balanced block
    tiers = ["starter", "growth", "enterprise"]
    mapping = {t: set() for t in tiers}

    for t in tiers:
        pattern = re.compile(rf"{t}\s*:\s*\{{", re.I)
        m = pattern.search(block)
        if not m:
            continue
        start = m.end() - 1  # position of the opening '{'
        # find matching closing brace
        depth = 0
        i = start
        end = None
        while i < len(block):
            ch = block[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
            i += 1
        section = block[start + 1 : end] if end else ""
        # Extract quoted strings within section
        strings = re.findall(r"'([^']+)'|\"([^\"]+)\"", section)
        vals = [a or b for a, b in strings]
        for v in vals:
            if re.search(
                r"\b(Amazon|AWS|Application|Attack|Airbyte|S3|EC2|ALB|Lambda|Glue|SageMaker|MSK|OpenSearch)\b",
                v,
                re.I,
            ):
                mapping[t].add(v.strip())
    return mapping


def main():
    parser = argparse.ArgumentParser(
        description="Check INFRA_BLUEPRINT vs config files"
    )
    parser.add_argument(
        "--finops",
        action="store_true",
        help="Run focused FinOps/Governance service scan",
    )
    args = parser.parse_args()

    block = read_pricing_block(PRICING)
    config_texts = read_config_texts()
    tier_map = build_blueprint_tier_map(block)

    # Focused FinOps/Governance service names (canonical labels matching CHECK_KEYWORDS keys when possible)
    FINOPS_SERVICES = [
        "AWS Budgets",
        "AWS Cost Explorer",
        "AWS Backup",
        "AWS CloudTrail",
        "AWS Config",
        "Amazon GuardDuty",
        "Amazon Inspector",
        "AWS Security Hub",
        "AWS Artifact",
        "AWS Control Tower",
    ]

    if args.finops:
        services = FINOPS_SERVICES
    else:
        services = extract_services_from_block(block)

    print("\nInfrastructure sync check\n" + ("-" * 60))

    # Check per-service presence heuristics
    pres_map = {s: check_presence(s, config_texts) for s in services}

    # If running focused FinOps scan, print a concise table and exit
    if args.finops:
        print("\nFinOps / Governance summary:\n")
        header = (
            "Service".ljust(40) + "dev".rjust(8) + "staging".rjust(10) + "prod".rjust(8)
        )
        print(header)
        print("-" * len(header))
        for s in services:
            pm = pres_map.get(s, {})
            d = "YES" if pm.get("dev") else "NO"
            st = "YES" if pm.get("staging") else "NO"
            pr = "YES" if pm.get("prod") else "NO"
            print(f"{s.ljust(40)}{d.rjust(8)}{st.rjust(10)}{pr.rjust(8)}")
        return

    # Print a summary table for the blueprint tiers vs config presence
    for tier, env in [
        ("starter", "dev"),
        ("growth", "staging"),
        ("enterprise", "prod"),
    ]:
        print(f"\nTier '{tier}' -> environment '{env}':")
        print("-" * 40)
        expected = sorted(tier_map.get(tier, []))
        if not expected:
            print("  (no services parsed for this tier)")
            continue
        for svc in expected:
            presence = False
            # try to find normalized match in pres_map keys
            key = None
            for candidate in pres_map:
                if candidate.lower() in svc.lower() or svc.lower() in candidate.lower():
                    key = candidate
                    break
            if key:
                presence = pres_map[key].get(env, False)
            else:
                # fallback: check if svc keyword appears in config text
                presence = any(svc.lower() in config_texts[e] for e in [env])
            print(f" - {svc:40} => present in {env}: {presence}")

    # Report services that appear in blueprint but are missing in their target env
    print("\nSummary mismatches:")
    mismatches = []
    for tier, env in [
        ("starter", "dev"),
        ("growth", "staging"),
        ("enterprise", "prod"),
    ]:
        for svc in sorted(tier_map.get(tier, [])):
            key = None
            for candidate in pres_map:
                if candidate.lower() in svc.lower() or svc.lower() in candidate.lower():
                    key = candidate
                    break
            present = False
            if key:
                present = pres_map[key].get(env, False)
            else:
                present = svc.lower() in config_texts[env]
            if not present:
                mismatches.append((tier, env, svc))

    if mismatches:
        print(
            "\nThe following blueprint items appear to be NOT present in the corresponding environment configs:"
        )
        for tier, env, svc in mismatches:
            print(f" - tier={tier.ljust(8)} env={env.ljust(8)} service={svc}")
    else:
        print("\nNo mismatches detected by heuristic scan.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error during check:", e)
        sys.exit(2)
