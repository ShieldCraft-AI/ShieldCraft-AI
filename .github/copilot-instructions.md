## ShieldCraft-AI — Copilot instructions (concise)

Purpose: help an AI coding agent be immediately productive in this repository. The agent should make code changes when appropriate, but report to the human reviewer at the "why" level — architectural intent, scope, risk, and rollback — not low-level mechanics.

- Read these files first (quick shortlist):
  - `infra/app.py` — CDK v2 orchestration, stack ordering, tag application (`apply_standard_tags`) and config loader usage.
  - `ai_core/model_loader.py` — canonical LLM wrapper: supports a zero-cost `stub` backend for dev, prints friendly error strings ("[STUB]", "[ERROR]").
  - `api/app.py` — demo FastAPI endpoints and demo payload wiring (`scripts/demo_vertical_slice`).
  - `config/*.yml` and `config/secrets.<env>.yml` — source-of-truth for infra; infra read these via `infra.utils.config_loader`.
  - `docs-site/` — Docusaurus site and custom plugins (webpack polyfills, og-meta). Use `yarn start` locally.

- Architecture summary to emit with every substantive change (the "why" report):
  1. One-line summary of intent and why the change is needed.
 2. Components affected (files, stacks, services) and the blast radius (dev vs staging vs prod).
 3. Risks and failure modes (data loss, infra costs, OOMs, broken deploys).
 4. Rollback/mitigation plan and required configuration changes.
 5. Minimal validation steps (unit test, smoke command, synth) and which CI job to run.

- Agent behavior rules (repo-specific):
  - Default to non-destructive, dev-safe behavior. Use `ai_core` config `model_name: stub` for local runs and CI to avoid heavy downloads.
  - Do not alter `config/secrets.*.yml` or commit credentials. If secrets are required, list them and where they should be stored (Secrets Manager) instead.
  - For infra changes, preserve `apply_standard_tags` and stack dependency ordering in `infra/app.py`.
  - When updating model behavior, follow `ai_core/model_loader.py` patterns (return friendly error strings instead of raising for expected failures).

- Helpful commands (high-level, for validation):
  - FastAPI demo: set PYTHONPATH and run `uvicorn api.app:app --reload` or `python -m api.app` to exercise demo endpoints.
  - CDK synth/deploy (local synth): `python infra/app.py` (CDK v2 required). Use `env=dev` for safe testing.
  - Docs site: `cd docs-site && yarn && yarn start` (or `yarn build` for static output).
  - Docker build targets: Dockerfile supports `--target=dev|staging|final` and `--build-arg PYTHON_VERSION`.

- Integration points to be careful with:
  - AWS CDK stacks (many Fn.import_value references). Missing config/account/region will break `infra/app.py` — check `config/*.yml` first.
  - Hugging Face / transformers (model downloads may OOM or be large). Prefer `stub` in dev/CI.
  - Custom Docusaurus plugins in `docs-site/plugins` — webpack fallbacks are local; don't assume upstream config works unchanged.

- Reporting template (use this every PR or patch summary):
  - Title: short intent (1 line)
  - Why: architecture-level reason (2–4 lines)
  - Scope: files/stacks/services changed and env impact
  - Risks & mitigations: short bullets
  - How I validated: commands/tests run

- Tests & CI notes:
  - Run pytest for Python changes. Tests use markers such as `integration` and `msk` — avoid heavy integration tests in quick PRs.
  - Prefer small unit tests and smoke synths for infra changes.

If anything about the architecture, environment defaults, or risk model is unclear, ask a single clarifying question before making destructive infra changes. After edits, provide the short "why" report above in the PR description.

## Project-specific details (read these before changing behavior)

- Checklist & progress: `docs-site/docs/github/checklist.md` is the canonical project progress artifact; the helper script `scripts/update_checklist_progress.py` updates the progress bar and README. If you manipulate checklist items, run that script and attach the updated artifact to your PR.
- Proton PaS: local-only Proton templates live under `proton/templates/` and are packaged by `scripts/proton_bundle.py` into `dist/proton/` — these are local scaffolding artifacts and must not trigger AWS deployments.
- Docs portal: `docs-site/` contains custom Docusaurus plugins and interactive components; run `cd docs-site && yarn start` locally to validate visual regressions after UI changes.
- Tests & automation: prefer `nox -s commit_flow` (or `poetry run nox -s commit_flow`) for a full pre-commit pipeline; `pytest` is configured extensively and includes infra contract tests — avoid running heavy integration suites in quick edits.
- Model dev flow: default to `ai_core` config `model_name: stub` for dev/CI; when switching to real models, include a cost and OOM risk statement in the "why" report and prefer quantized configs.

## Communication style (enforced)

- Primary rule: perform necessary code changes autonomously when allowed, but ALWAYS communicate results to the human reviewer at the architectural/impact level (the "why"). Do not dump low-level implementation steps in top-level messages. Show low-level diffs/commands only when explicitly requested.
- Required "why" report (top of PR or patch summary):
  - 1-line intent summary
  - Components changed and blast radius (files, stacks, env impact)
  - Top 3 risks and mitigations (cost, data loss, OOM, deploy failures)
  - Rollback plan (one-line) and guarded config flags to flip
  - Minimal validation steps run (commands and quick pass/fail)

## Enforcement options (choose and document)

- If a change touches `infra/` or `config/secrets.*.yml`, require explicit human approval in the PR description and attach a successful `python infra/app.py` synth output (use `env=dev` by default).
- For model changes (non-stub), include a note listing the extra CI cost (approx. GPU download/infra) and prefer a staged feature branch that disables heavy downloads in CI unless maintainer opt-in is present.

If you'd like these enforcement options toggled (e.g., mandatory human approval for any infra edits), tell me which to enforce and I will update this instruction file accordingly.
## ShieldCraft-AI — Copilot instructions

These instructions give an AI coding assistant the minimum, actionable context
to be productive in this repository. Read these before making edits.

- Purpose: ShieldCraft-AI is a GenAI-driven cloud cybersecurity reference
  platform (Python + AWS CDK v2 + Docusaurus). Key subsystems live under
  `infra/` (CDK stacks), `ai_core/` (LLM wrappers), `api/` (FastAPI demo), and
  `docs-site/` (Docusaurus documentation).

- High-level architecture:
  - infra/: AWS CDK v2 stacks — networking, S3, Glue, MSK, Lambda, Lake
    Formation, SageMaker, OpenSearch, etc. `infra/app.py` is the CDK entrypoint
    and uses `config/*.yml` to set region/account and stack config.
  - ai_core/: Model loader and inference contract. `ai_core/model_loader.py`
    supports a zero-cost `stub` model and Hugging Face models (see
    MODEL_NAME/defaults). Use `stub` for dev to avoid downloads.
  - api/: FastAPI demo endpoints (quick vertical-slice payloads used by the
    docs-site dashboard). `api/app.py` is minimal — keep changes backward
    compatible with demo payload shape (see `scripts/demo_vertical_slice.py`).
  - docs-site/: Docusaurus site and developer docs. `docs-site/docusaurus.config.ts`
    contains important build-time quirks (meta tags injected via local plugin).

- Config and conventions:
  - Config loader: infra uses `infra.utils.config_loader.get_config_loader()`.
    `infra/app.py` reads `config/*.yml` and `config/secrets.<env>.yml`.
  - Environments: `app`/CDK relies on `env` (dev/staging/prod). Many modules
    branch on `env`; prefer defaults when adding features and keep `dev` safe
    (no real cloud calls).
  - Model dev flow: set `ai_core` config `model_name: stub` to run locally
    without large downloads. See `ai_core/model_loader.py` for error handling
    patterns.
  - Packaging: Python project uses Poetry (`pyproject.toml`). Tests use
    pytest; CI scripts live in `.github/workflows` (see README badge).

- Developer workflows and quick commands:
  - Run FastAPI demo: set PYTHONPATH and run `uvicorn api.app:app --reload` or
    use `python -m api.app` if provided. Keep payload shapes stable.
  - Build site: `cd docs-site && yarn && yarn start` for local preview;
    `yarn build` for static build. Docs site uses local webpack polyfills plugin.
  - CDK deploy flow: `python infra/app.py` is the entrypoint; CDK v2 and
    IAM Identity Center (SSO) are expected. Do not assume static AWS creds.
    For edits to infra, update `config/*.yml` and test `app.synth()` locally.

- Patterns and pitfalls observed (use these to guide fixes):
  - Avoid introducing runtime secrets in code — infra reads `config/secrets.*.yml`.
  - Many stacks import Fn.import_value values; keep stack dependencies and
    apply_standard_tags() calls consistent with `infra/app.py` ordering.
  - Model loader prints info and returns friendly error strings (not
    exceptions). When integrating, check for strings like "[ERROR]" or
    "[STUB]" rather than assuming an exception is raised.
  - Docusaurus config uses local plugins instead of top-level fields; prefer
    reading `docs-site/plugins/` when changing meta, webpack fallbacks, or
    clientModules.

- When changing code, follow these repo-specific rules:
  - Keep `dev` safe: ensure changes default to non-destructive behavior when
    env=dev or model_name=stub.
  - Merge, don’t overwrite: If editing infra configs, preserve tag handling in
    `infra/app.py` (`apply_standard_tags` and `get_shared_tags`).
  - Small reproducible tests: add a pytest under `tests/` targeting the
    smallest module changed (e.g., ai_core or scripts). Use `pytest -k <name>`.

- Files worth reading when addressing tasks (examples):
  - `infra/app.py` — CDK orchestration, config, tags, stack ordering
  - `ai_core/model_loader.py` — model selection, stub behavior, error strings
  - `api/app.py` — demo API endpoints and expected demo payloads
  - `docs-site/docusaurus.config.ts` and `docs-site/README.md` — doc build quirks
  - `pyproject.toml` — dependency constraints and tools (Poetry, pytest)
  - `Dockerfile` — multi-stage build targets dev/staging/final and HEALTHCHECK

- If you need to make a risky or large infra change:
  - Prefer writing a small RFC/ADR under `docs-site/docs/github/` describing
    why and include a rollback plan. Update `docs-site/docs/github/checklist.md`
    where relevant.

If anything here is unclear or you'd like extra examples (commands, test
templates, or a short ADR example), tell me which area and I'll expand.
