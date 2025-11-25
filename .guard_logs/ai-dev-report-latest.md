# GuardSuite AI Dev Report
Repo: shieldcraft-ai
Source of structure: `tree.txt` snapshot dated 2025-11-21

ANALYSIS_COMPLETE: true
Summary of repo health: ShieldCraft-AI hosts a mature infra/AI/docs platform, but none of the GuardSuite-mandated subsystems (evaluator, rules pipeline, fixpacks, CLI, canonical schemas) exist beyond marketing copy under `docs/` and `docs-site/`. The codebase therefore fails every deterministic GuardSuite requirement.
Deterministic structure statement: All findings below are derived directly from `tree.txt`, which enumerates the repository layout down to file level; no inferred or hypothetical files are referenced.

## Findings
1. **Evaluator isolation missing.** The GuardSuite template expects a dedicated `evaluator/` (or `src/<pillar>/evaluator`) path, yet `tree.txt` only shows general-purpose modules (`ai_core/eval/spotcheck.py`, `src/ingestion`, `src/api`, `src/shieldcraft_ai`). There is no deterministic evaluator entrypoint, no multi-env separation, and no way to enforce evaluator-only dependencies.
2. **No rule pipeline directories.** GuardSuite requires a `rules/` or equivalent pipeline tree. The repository contains data ingestion scaffolding (`data_prep/<domain>/schema.py` + `ingest.py`) but zero `rules/` directories anywhere in `tree.txt`, leaving no place for rule definitions, bundling, or promotion stages.
3. **Fixpack implementation absent.** While the docs site references FixPack concepts (`docs-site/src/data/guardSuitePricing.ts`, `docs-site/src/pages/guard-suite.tsx`), the code tree lacks any `fixpack/`, `remediation/`, or metadata folders. No runtime pack manifests or executors exist under `src/`, `scripts/`, or `lambda/`.
4. **CLI contract undefined.** GuardSuite expects a deterministic CLI (`cli/` or `src/cli.py`) with commands for evaluator, rules, and fixpacks. The root `src/` tree only contains `ingestion`, `api`, and `shieldcraft_ai` packages plus `src/main.py`, with zero CLI scaffolding or packaging instructions, so there is no contract to exercise or test.
5. **Issue schema (#ISSUEDICT_SCHEMA) missing.** A repo-wide search of `tree.txt` shows no files or directories referencing `ISSUEDICT_SCHEMA` or any canonical issue dict. The scattered `data_prep/*/schema.py` modules describe ingestion payloads, not GuardSuite issue documents, meaning findings cannot be serialized deterministically.
6. **Canonical schema + adapters undefined.** GuardSuite calls for `schemas/` and `adapters/` layers. `tree.txt` shows neither path; instead schema logic is embedded per data source and there are no adapter modules at all, so downstream consumers cannot rely on a stable schema contract.
7. **Snapshot/golden coverage absent.** No `__snapshots__` folders, `.snap` files, or other golden artifacts appear anywhere in `tree.txt`. Jest snapshot dependencies in `package-lock.json` therefore have no matching assets, leaving GuardSuite UI/CLI output unverified.
8. **CI workflows missing.** GuardSuite compliance depends on automated checks, yet the repository tree contains no `.github/workflows` (tree lists `.gitignore` and other dotfiles, so their absence is authoritative). Without CI definitions, there is no coverage for evaluator, CLI, or docs regressions.
9. **Tests ignore GuardSuite subsystems.** The sizeable `tests/` hierarchy covers `model`, `scripts`, `proton`, `infra`, and `config`, but there is no `tests/guard_suite`, `tests/cli`, or evaluator-specific suite. Consequently, GuardSuite pathways have zero unit, integration, or snapshot tests.
10. **Docs describe GuardSuite without backing implementation.** Files like `docs/Guard Suite.txt` and `docs-site/src/pages/guard-suite.tsx` lay out product, pricing, and UX expectations, but the runtime tree (src/, ai_core/, lambda/, scripts/) never instantiates those services. This divergence signals documentation drift and a missing architecture hand-off.
11. **Orphaned subsystems unrelated to GuardSuite.** Large directories (`lambda/*`, `proton/*`, `analysis/lighthouse/*`, `docs-site/analysis/*`) operate independently of GuardSuite concepts and lack adapters into any evaluator/CLI contract, indicating the repo has diverged entirely from the GuardSuite template and contains multiple untracked execution surfaces.
12. **Deterministic evaluator path validation fails.** Without `evaluator/` or referenced pipelines, there is no way to trace a finding from ingestion to issue dict, violating the deterministic-path guarantee GuardSuite mandates.

## Validation Checklist
- Evaluator isolation: FAIL
- Rule pipeline: FAIL
- Fixpack metadata: FAIL
- CLI contract: FAIL
- Snapshot/golden assets: FAIL
- Test coverage for evaluator/CLI: FAIL
- CI workflows present: FAIL
- Issue schema alignment (#ISSUEDICT_SCHEMA): FAIL
- Canonical schema + adapters: FAIL
- Docs vs implementation parity: FAIL
