#!/usr/bin/env python3
"""
Demo Vertical Slice (local-only)
Emits a deterministic JSON doc representing:
  Ingest -> Retrieve -> Risk Score -> Remediation Plan
No external services; respects SC_ENV and accepts --finding-id.
"""
from __future__ import annotations
import argparse
import json
import os
from datetime import datetime, timezone


def classify(score: float) -> str:
    if score >= 0.75:
        return "HIGH"
    if score >= 0.4:
        return "MEDIUM"
    return "LOW"


def build_demo_payload(finding_id: str, env: str) -> dict:
    # Deterministic stub evidence; replace later with real retrieval.
    evidence = [
        {
            "source": "guardduty",
            "snippet": "EC2 instance port scan detected",
            "score": 0.61,
        },
        {
            "source": "saas_security",
            "snippet": "Unusual login location for admin user",
            "score": 0.72,
        },
    ]
    # Simple fused score (mean); guardrail-aware strategies come later.
    mean_score = round(sum(e["score"] for e in evidence) / len(evidence), 4)
    payload = {
        "findingId": finding_id,
        "evidence": evidence,
        "risk": {
            "score": mean_score,
            "class": classify(mean_score),
        },
        "remediation": {
            "planId": f"plan-{finding_id[:8]}",
            "steps": [
                {"action": "quarantine-instance", "owner": "secops"},
                {"action": "force-mfa-reset", "owner": "iam-admin"},
            ],
        },
        "meta": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "env": env,
            "version": 1,
        },
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Demo vertical slice JSON emitter (local-only)"
    )
    parser.add_argument("--finding-id", default="fdg-0001", help="Finding identifier")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    env = os.getenv("SC_ENV", "dev")
    payload = build_demo_payload(args.finding_id, env)
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=False))
    else:
        print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
