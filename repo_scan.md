# ShieldCraft AI – Repository Audit (2025-11-24)

## Inputs Reviewed
- `ShieldCraft-AI-Context.txt` – spec snapshot updated 2025-10-17 covering secrets-scanner rollout, Proton scaffolding, OAuth scope, and the canonical architecture narrative.
- `checklist.md` – architect-facing execution checklist at the repo root reporting 85 % completion with Application, GuardSuite, Infra, and AI items still unchecked.
- `docs-site/docs/github/checklist.md` – docs-site mirror of the checklist (also 85 %) that enumerates 55 complete vs 10 remaining items (2 active, 8 deferred).

## Deterministic Findings by Capability

### 1. Foundation & Planning  -  COMPLETE
- `infra/app.py` composes networking, data, ML, security, compliance, and budget stacks per environment, enforcing shared tags and dependency ordering.
- `infra/utils/config_loader.py` provides the typed, single-source configuration loader with Secrets Manager indirection, validating sections before CDK synthesis.
- `infra/stacks/cost/budget_service.py` (invoked via `BudgetStack` inside `infra/app.py`) wires deterministic per-environment spend guardrails required by the spec.

### 2. Data Preparation & Retrieval  -  COMPLETE
- `ai_core/model_loader.py` (and sibling chunking/vector modules) implements the hot-swappable model abstraction with stub-vs-real selection required for guarded experimentation.
- `ai_core/vector_store.py` and `ai_core/embedding/` house the pgvector-backed retrieval layer that the spec calls for.
- `scripts/retrieval_spotcheck.py` plus `docs-site/docs/github/retrieval_spotcheck.md` capture the deterministic spot-check harness and evidence artifacts backing the checklist items.

### 3. AWS Cloud Foundation  -  COMPLETE WITH DEFERRED MULTI-REGION
- `infra/stacks/networking/networking.py` provisions the segmented VPC, subnets, and flow-log plumbing consumed by the other stacks.
- `infra/stacks/security/secrets_manager_service.py` and `infra/stacks/cost/budget_service.py` confirm centralized secrets + cost guardrails are codified.
- `infra/stacks/cloud_native/cloud_native_hardening_service.py` enables GuardDuty, Security Hub, Detective, and Config hooks per the security baseline.
- No automation or scripts exist for multi-region failover rehearsals (SC-INFRA-STACK-002 remains open as listed in both checklists).

### 4. AI Core Development & Experimentation  -  PARTIAL
- `ai_core/model_loader.py` and `docs-site/docs/github/retrieval_spotcheck.md` satisfy the baseline loader + benchmark requirements.
- Missing: multi-agent orchestration, prompt-governance registry, approval workflow, and the automated hallucination/toxicity loop (checklist items SC-AI-AGENT-001/002/003 and SC-AI-DRIFT-001 remain unimplemented anywhere in the repo).

### 5. Application Layer & Integration  -  PARTIAL
- `docs-site/src/pages/dashboard/index.tsx` (plus `docs-site/src/components/Dashboard/DashboardSummary.tsx`) implements the static Analyst Dashboard requested by SC-APP-UI-001 with deterministic evidence pulled from docs artifacts.
- `docs-site/src/pages/dashboard/evidence.tsx` and `docs-site/src/components/Dashboard/EvidenceFeed.tsx` fulfill SC-APP-UI-002 by exposing a placeholder evidence feed.
- `docs-site/tests/test_dashboard_route.js` adds Jest coverage for both dashboard routes.
- `api/app.py` exposes a demo `/demo-vertical-slice` endpoint but no public dashboard API contract; SC-APP-UI-003 and the SC-APP-PUBLIC-API-* items still lack concrete implementation or documentation.

### 6. GuardSuite Integration Layer  -  PARTIAL
- `docs/Guard Suite.txt`, `ShieldCraft-AI-Context.txt`, and `docs-site/docs/github/artifact_map.md` collectively describe the integration narrative and evidence map.
- The GuardSuite CLI contract (SC-GS-CLI-001), model governance integration (SC-GS-MODEL-001), and full docs parity (SC-GS-DOCS-002) have no code, scripts, or docs in the repo.

### 7. Security & Governance  -  PARTIAL
- `scripts/check-secrets.js` + `scripts/scan-secrets.json` implement the deterministic secrets scanner wired into `scripts/commit-script.sh`.
- `docs-site/docs/github/threat_model_summary.md` and `docs-site/docs/github/risk_log.md` capture the documented risk baseline cited by the dashboard components.
- SBOM generation/signing and automated IAM access-review cadence (SC-INFRA-STACK-003/004) are still theoretical; no scripts or CI hooks exist for them.

### 8. Documentation & Enablement  -  COMPLETE
- `docs-site/docs/github/demo_vertical_slice.md`, `docs-site/docs/github/artifact_map.md`, and `docs-site/docs/github/checklist.md` provide the evidence, artifact crosswalk, and automation described in the spec.
- `ShieldCraft-AI-Context.txt` is up to date (Oct 17 snapshot) and captures the secrets scanner work plus Proton scaffolding.

## Checklist Drift & Open Items

| Checklist ID                  | Observed Status                                     | Evidence / Gap                                                                                                                                                                               |
| ----------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SC-APP-UI-001                 | **Complete in repo, still open in both checklists** | `docs-site/src/pages/dashboard/index.tsx`, `docs-site/src/components/Dashboard/DashboardSummary.tsx`, and `docs-site/tests/test_dashboard_route.js` implement and test the static dashboard. |
| SC-APP-UI-002                 | **Complete in repo, still open in both checklists** | `docs-site/src/pages/dashboard/evidence.tsx` + `docs-site/src/components/Dashboard/EvidenceFeed.tsx` + matching docs `docs-site/docs/github/analyst_evidence_feed.md`.                       |
| SC-APP-UI-003                 | Not started                                         | No chart/UX polish beyond static cards; no routes, docs, or tests reference finalized UX.                                                                                                    |
| SC-APP-PUBLIC-API-001/002/003 | Not started                                         | Only `api/app.py` demo endpoints exist; no documented public API surface, auth contract, or evidence pipeline wiring for dashboard data.                                                     |
| SC-GS-DOCS-002                | Not started                                         | GuardSuite documentation parity is incomplete; only high-level `docs/Guard Suite.txt` exists.                                                                                                |
| SC-GS-CLI-001                 | Not started                                         | No CLI contract, schema, or integration hooks observed under `src/`, `cli.py`, or docs.                                                                                                      |
| SC-GS-MODEL-001               | Not started                                         | No governance registry or GuardSuite model integration artifacts in repo.                                                                                                                    |
| SC-INFRA-STACK-002            | Deferred / not implemented                          | No multi-region failover rehearsal scripts, docs, or tests.                                                                                                                                  |
| SC-INFRA-STACK-003            | Not started                                         | No SBOM generation/signing pipeline in `scripts/`, CI configs, or docs.                                                                                                                      |
| SC-INFRA-STACK-004            | Not started                                         | No automated IAM access review cadence implemented.                                                                                                                                          |
| SC-AI-AGENT-001/002/003       | Not started                                         | No multi-agent orchestration, prompt registry, or approval workflow code.                                                                                                                    |
| SC-AI-DRIFT-001               | Not started                                         | Drift monitoring exists as manual reports, but no automated alerting loop or CI hook is present.                                                                                             |

## Risks & Recommendations
- **Checklist accuracy drift (Medium):** SC-APP-UI-001 and SC-APP-UI-002 are implemented but remain unchecked; this can cause the Architect workflow to reschedule already-complete work. _Recommendation:_ Update both checklists with the implemented evidence paths before issuing further UI instructions.
- **Application/API surface gap (High):** No implementation exists for SC-APP-UI-003 or the public API tasks, blocking downstream integrations. _Recommendation:_ Scope the charting/UX work and design the API envelope that will back the dashboard before moving to GuardSuite CLI/model items.
- **GuardSuite integration debt (Medium):** Documentation parity, CLI contract, and model governance hooks lack any committed artifacts. _Recommendation:_ Produce at least stubs (schema + doc) so future instructions have concrete targets.
- **Security automation gap (Medium):** SBOM generation/signing and IAM review cadence remain aspirational. _Recommendation:_ Add deterministic scripts in `scripts/` plus CI wiring to generate SBOMs and capture IAM findings.
- **AI governance gap (Medium):** Multi-agent orchestration, prompt registry, approval flows, and continuous drift monitoring have no code. _Recommendation:_ Treat these as a focused follow-on tranche once the UI/API surface is locked.

## Suggested Next Actions
1. Update `checklist.md` and `docs-site/docs/github/checklist.md` to mark SC-APP-UI-001 and SC-APP-UI-002 complete with links to the dashboard routes, EvidenceFeed component, docs, and Jest tests.
2. Design and implement SC-APP-UI-003 (finalized UX + charts) plus the supporting public API envelope so that subsequent evidence ingest work has an executable surface.
3. Stand up stubs for GuardSuite CLI and model governance integration (schema, doc, and placeholder entry points) to unblock Architect sequencing.
4. Add deterministic automation for SBOM generation/signing and IAM access reviews, wiring them into the existing `nox`/CI toolchain.
5. Plan the AI governance tranche (multi-agent orchestration, prompt registry, approval workflow, drift monitoring) with clear ownership and evidence artifacts.
