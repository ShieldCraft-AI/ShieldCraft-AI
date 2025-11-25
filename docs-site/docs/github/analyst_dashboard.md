The Analyst Dashboard consolidates three evidence groups so teams can review GuardSuite posture without hitting live services:

1. **Risk baseline** &mdash; mirrors the weighted posture table maintained in `docs/github/risk_log.md` and `docs/github/risks_mitigation.md`.
2. **Retrieval spot checks** &mdash; reuses static payloads from `docs/github/retrieval_spotcheck.md` to show quality gates for knowledge retrieval.
3. **Signal drift summaries** &mdash; aligns with the drift report snapshots under `docs/github/drift_reports/`.

## What ships in ATU-1

- `/dashboard` exposes a deterministic `<DashboardSummary />` view rendered entirely on the client with no fetches.
- The view lists the latest annotated findings from the artifacts above so analysts can trace any badge back to documented evidence.
- Each card clearly states the evidence source, the effective date, and the stability flag (steady, watch, investigate).

## Intended workflow

1. Product or infra owners update the source markdown files as controls move.
2. The dashboard summary is re-deployed through the docs pipeline, ensuring the UI and the written artifacts stay in sync.
3. Analysts can reference this page or jump directly into the evidence links without leaving the docs bundle.

No timers, randomness, or network requests exist in this ATU; the dashboard is safe to host in static builds and satisfies the Application Layer requirement SC-APP-UI-001.
