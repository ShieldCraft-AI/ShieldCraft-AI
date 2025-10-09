# Demo Vertical Slice - Ingest → Retrieve → Risk Score → Remediation JSON

This vertical slice demonstrates the end-to-end narrative in a minimal, cost-safe way. It emits a deterministic JSON document you can paste into tools or dashboards.

## Output shape
```json
{
  "findingId": "...",
  "evidence": [
    { "source": "...", "snippet": "...", "score": 0.0 }
  ],
  "risk": { "score": 0.0, "class": "LOW|MEDIUM|HIGH" },
  "remediation": {
    "planId": "...",
    "steps": [ { "action": "...", "owner": "..." } ]
  },
  "meta": { "generatedAt": "ISO-8601", "env": "dev|staging|prod" }
}
```

## How to run (local)
- Script: `scripts/demo_vertical_slice.py`
- It requires no external services. It reads optional `SC_ENV` to set the env in the output.

## Next steps
- Swap stub retrieval with a tiny local pgvector query when dev DB is running.
- Add an option to include guardrail metrics and latency envelopes in `meta`.

## Try the Analyst Dashboard Mock
A lightweight mock dashboard is available in the docs site at `/analyst-dashboard` that renders the demo vertical slice as a visual card. Run the docs dev server to preview.
