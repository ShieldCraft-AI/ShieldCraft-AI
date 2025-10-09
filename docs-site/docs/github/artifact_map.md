# Artifact Map - Claims to Code and Tests

This map links key claims in the ShieldCraft AI blueprint to concrete code and tests for quicker verification. It evolves over time-treat it as a living index.

## Environment-aware IaC and Guardrails
- Claim: Environment-aware, multi-account IaC with explicit naming/tagging and guardrails
  - Code: `infra/app.py`, `infra/**/` domain stacks, `infra/utils/`
  - Config: `config/*.yml`, `config/secrets.*.yml`
  - Tests: `tests/infra/` (stack contracts, unhappy paths)

- Claim: Centralized secrets (no static creds in code)
  - Code: `infra/foundation/identity_security/secrets_manager_stack.py`
  - Usage: Secrets referenced via config loader, injected into stacks
  - Tests: `tests/infra/test_secrets_*.py`

## Data, Retrieval, and AI Core
- Claim: Vector store abstraction (pgvector) and retrieval boundary
  - Code: `ai_core/vector_store.py`, `ai_core/embedding/`
  - Tests: `tests/ai_core/test_vector_store_*.py`

- Claim: Model loader hot-swap (stub ↔ Mistral-7B)
  - Code: `ai_core/model_loader.py`
  - Tests: `tests/ai_core/test_model_loader_*.py`

## Benchmarks and Evaluation
- Claim: Baseline MTEB/BEIR signals captured
  - Artifacts: `mteb_benchmark.log`, `mteb_results.json/`
  - Harness: `lambda/beir_benchmark/`, `nox_sessions/beir.py`
  - Tests: `tests/benchmarks/test_beir_*.py`

## Proton PaS (Local-only Scaffolding)
- Claim: Versioned Proton templates with a local bundler
  - Code: `proton/templates/**`, `scripts/proton_bundle.py`
  - Output: `dist/proton/manifest.json` (local only)
  - UI: `docs-site/src/components/Infra/InfraOverview.tsx`

## Demo Vertical Slice (Doc + Script)
- Claim: Finding → retrieve → risk score → remediation plan JSON
  - Doc: `docs-site/docs/github/demo_vertical_slice.md`
  - Script: `scripts/demo_vertical_slice.py` (prints deterministic JSON)

## Documentation and Portal
- Claim: Executive-ready docs portal with plugin catalogue and task badges
  - Code: `docs-site/src/pages/plugins.tsx`, `docs-site/src/pages/plugins/**`
  - Styles: `docs-site/src/pages/plugins.module.css`, `docs-site/src/pages/plugins/plugin-detail.module.css`
  - Infra overview: `docs-site/src/components/Infra/InfraOverview.tsx`

---

Notes
- Path names are stable; some tests may have different exact filenames than shown here. Use repository search if a pointer is missing.
- This map will expand as new ADRs, tests, and features land. PRs welcome.
