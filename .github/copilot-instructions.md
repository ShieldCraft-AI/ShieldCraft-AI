## ShieldCraft-AI - Copilot instructions (concise)

Purpose: help an AI coding agent be immediately productive in this repository. The agent should make code changes when appropriate, but report to the human reviewer at the "why" level - architectural intent, scope, risk, and rollback - not low-level mechanics.

- Read these files first (quick shortlist):
  - `infra/app.py` - CDK v2 orchestration, stack ordering, tag application (`apply_standard_tags`) and config loader usage.
  - `ai_core/model_loader.py` - canonical LLM wrapper: supports a zero-cost `stub` backend for dev, prints friendly error strings ("[STUB]", "[ERROR]").
  - `api/app.py` - demo FastAPI endpoints and demo payload wiring (`scripts/demo_vertical_slice`).
  - `config/*.yml` and `config/secrets.<env>.yml` - source-of-truth for infra; infra read these via `infra.utils.config_loader`.
  - `docs-site/` - Docusaurus site and custom plugins (webpack polyfills, og-meta). Use `yarn start` locally.

- Architecture summary to emit with every substantive change (the "why" report):
  1. One-line summary of intent and why the change is needed.
 2. Components affected (files, stacks, services) and the blast radius (dev vs staging vs prod).
 3. Risks and failure modes (data loss, infra costs, OOMs, broken deploys).
 4. Rollback/mitigation plan and required configuration changes.
 5. Minimal validation steps (unit test, smoke command, synth) and which CI job to run.
```instructions
## ShieldCraft-AI - Copilot instructions (concise)

Purpose: Quickly enable an AI coding agent to be productive in this repo. Keep changes
non-destructive by default and always provide the short "why" report (intent, blast
radius, risks, rollback, validation) with substantive edits.

- Quick-read files (first): `infra/app.py`, `ai_core/model_loader.py`, `api/app.py`,
  `config/*.yml`, `config/secrets.<env>.yml`, and `docs-site/docusaurus.config.ts`.

- One-line operational rules:
  - Default to `env=dev` behavior and `ai_core` config `model_name: stub` for local/CI.
  - Never commit secrets: do not edit `config/secrets.*.yml` in commits.
  - For infra edits, preserve `infra/app.py` stack ordering and `apply_standard_tags()`.

- Short "Why" report (include in PR/patch):
  1. Intent (1 line).
  2. Components changed and blast radius (files/stacks/env).
  3. Top risks & mitigations (cost/OOM/data loss/deploy failure).
  4. Rollback plan and guarded flags to flip.
  5. Minimal validation commands or CI job to run.

- Developer workflows (concrete commands):
  - FastAPI demo: `PYTHONPATH=. uvicorn api.app:app --reload` or `python -m api.app`.
  - CDK local synth: `python infra/app.py` (reads `config/*.yml`; `env` defaults to `dev`).
  - Docs local: `cd docs-site && yarn && yarn start` (or `yarn build`).
  - Pre-commit flow: `poetry run nox -s commit_flow` or `nox -s commit_flow`.
  - Tests: use `pytest -k <name>` for focused checks; avoid heavy integration markers like
    `integration` or `msk` in quick PRs.

- Repo-specific conventions & examples:
  - Config: `infra/utils/config_loader` is authoritative. `infra/app.py` sets `AWS_DEFAULT_REGION`
    and reads `config/secrets.<env>.yml` before running-ensure `account` and `region` exist.
  - Model loader: `ai_core/model_loader.py` returns friendly strings (`[STUB]`, `[ERROR]`).
    Check for those instead of catching exceptions when integrating.
  - Checklist script: when updating `docs-site/docs/github/checklist.md`, run
    `python scripts/update_checklist_progress.py` and attach the updated artifact to PR.
  - Proton templates: local templates live in `proton/templates/`; packaging uses
    `scripts/proton_bundle.py` and should not trigger AWS resources.

- Integration & risk hotspots to check before edits:
  - CDK stacks use `Fn.import_value` extensively-missing imports or config will break `infra/app.py`.
  - Model downloads (Hugging Face/transformers) can OOM or be large-prefer `stub` in CI/dev.
  - Docs: `docs-site/plugins` contain local webpack fallbacks; changes may break builds.
  - Docker: `Dockerfile` supports `--target=dev|staging|final` and `--build-arg PYTHON_VERSION`.

- When changing infra or secrets:
  - Require explicit human approval for edits touching `infra/` or `config/secrets.*.yml`.
  - Validate with `python infra/app.py` (dev env) and include synth output in PR.

- Small testing guidance:
  - Add minimal unit tests under `tests/` targeting the smallest changed module (e.g., `ai_core`).
  - Use `pytest -k <name>` locally; reserve full integration suites for CI jobs.

- Files to read for common patterns:
  - `infra/app.py` - config loader, stack ordering, tagging patterns.
  - `ai_core/model_loader.py` - stub/real model contract and error strings.
  - `api/app.py` and `scripts/demo_vertical_slice.py` - demo payload shapes.
  - `docs-site/docusaurus.config.ts` and `docs-site/plugins/` - docs build quirks.

If any part of the architecture or environment defaults is unclear, ask a single clarifying question before making destructive infra changes. After edits, include the short "why" report in the PR description.

```
- For model changes (non-stub), include a note listing the extra CI cost (approx. GPU download/infra) and prefer a staged feature branch that disables heavy downloads in CI unless maintainer opt-in is present.
