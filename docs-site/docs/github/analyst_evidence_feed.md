---
id: analyst_evidence_feed
slug: /github/analyst-evidence-feed
title: Analyst Evidence Feed Placeholder
sidebar_label: Evidence Feed
---

SC-APP-UI-002 expands the Analyst Dashboard by exposing a deterministic evidence feed. The current implementation is static and
mirrors the JSON envelope that the future ingestion pipeline will publish, allowing reviewers to validate formatting before
any live data flows.

## JSON Envelope

```json
{
  "id": "EV-001",
  "artifact_type": "drift_summary",
  "priority": "watch",
  "ingested_at": "2025-11-18T07:10:00Z",
  "evidence_source": "docs/github/drift_reports/README.md#summary",
  "summary": "Short analyst-facing description",
  "payload": {
    "stack": "vectorguard-control-plane",
    "comparison_status": "acknowledged",
    "diff_sha": "6c7fd1c8",
    "pending_actions": ["confirm-log-retention"]
  }
}
```

Field notes:

- `id` keeps the human-friendly identifier that downstream tickets reuse.
- `artifact_type` flags which subsystem (drift, retrieval, risk) generated the item.
- `priority` controls the badge color rendered by the UI (`info`, `watch`, `investigate`).
- `ingested_at` documents when the evidence snapshot was written.
- `evidence_source` links directly to the supporting markdown artifact.
- `summary` is a single-sentence analyst explainer.
- `payload` is an arbitrary JSON object that the analyst desk can expand for future automation.

## Sample Items

The static feed defined in `docs-site/src/components/Dashboard/EvidenceFeed.tsx` ships three items:

1. **EV-001** captures the vectorguard drift snapshot referencing `docs/github/drift_reports/README.md`.
2. **EV-002** reuses the retrieval spot-check ticket enrichment payload for RSC-148.
3. **EV-003** references the risk register entry covering ML guardrails.

Because the placeholders are pure JSON, Docusaurus can host them safely without network calls, timers, or build-time side effects.
