#!/usr/bin/env python3
"""
Retrieval relevance spot-check harness (local-only)

Runs a tiny set of query cases against a provided retriever function.
By default, uses a built-in in-memory retriever seeded with 3 docs.

Usage:
  python scripts/retrieval_spotcheck.py --pretty --threshold 0.5

This script is dependency-free and safe to run locally.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

# Ensure repository root is on sys.path for local execution
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ai_core.eval.spotcheck import QueryCase, evaluate_cases


def default_corpus() -> Dict[str, str]:
    return {
        "guardduty port scan": "EC2 instance port scan detected on VPC subnet",
        "identity anomaly": "Unusual login location for admin user in SaaS app",
        "budget drift": "Forecast indicates overspend; consider savings plan",
    }


def in_memory_retriever(corpus: Dict[str, str]):
    # Simple exact-key fallback; otherwise return a best-effort match by overlap.
    def _retrieve(query: str) -> str:
        if query in corpus:
            return corpus[query]
        # naive overlap with keys
        tokens = set(query.lower().split())
        best = ""
        best_score = -1
        for k, v in corpus.items():
            score = len(tokens & set(k.split()))
            if score > best_score:
                best_score = score
                best = v
        return best

    return _retrieve


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Retrieval spot-check harness (local-only)"
    )
    parser.add_argument(
        "--threshold", type=float, default=0.3, help="Pass threshold (0-1)"
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )
    args = parser.parse_args()

    cases: List[QueryCase] = [
        QueryCase(query="guardduty port scan", expected="port scan detected"),
        QueryCase(query="identity anomaly", expected="unusual login location"),
        QueryCase(query="budget drift", expected="overspend forecast"),
    ]
    retriever = in_memory_retriever(default_corpus())
    results, pct = evaluate_cases(cases, retriever, threshold=args.threshold)

    payload = {
        "threshold": args.threshold,
        "passedPct": round(pct, 4),
        "total": len(results),
        "passed": sum(1 for r in results if r.passed),
        "cases": [
            {
                "query": r.query,
                "expected": r.expected,
                "retrieved": r.retrieved,
                "score": r.score,
                "passed": r.passed,
            }
            for r in results
        ],
    }

    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
