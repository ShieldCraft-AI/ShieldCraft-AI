# ShieldCraft Drift Reports

ShieldCraft ships a read-only drift automation pipeline so every environment can detect CloudFormation drift, review remediation intent, and acknowledge safe differences without mutating stacks by default.

## Components
- **Detection script**: `scripts/drift_remediation/run_drift_check.py` orchestrates CloudFormation `detect_drift`, `cdk diff`, and SHA-256 hashing of the rendered diff.
- **Remediation planner**: `scripts/drift_remediation/run_drift_remediation.py` turns latest detection artifacts into JSON remediation plans with manual approval steps.
- **Helper modules**: Baselines live in `scripts/drift_remediation/baseline_utils.py`, comparisons in `comparator.py`, and summaries in `summary.py`.
- **Nox sessions**: `nox -s drift_check`, `nox -s drift_acknowledge`, and `nox -s drift_report` wrap the scripts with repo-wide guardrails.
- **Artifacts**:
  - `artifacts/drift/<STACK>/` – detection JSON + `.diff` files
  - `artifacts/drift_remediation/<STACK>/` – remediation plan JSON files
  - `artifacts/drift_summary/latest.json|md` – aggregated output from `nox -s drift_report`
  - `drift_baselines/<stack>.json` – local-only baseline hashes that gate acknowledgements

### Telemetry context
- `[telemetry]` log entries are the only structured source that `drift_report` needs to rebuild JSON/markdown summaries, and they remain read-only.
- Set `SHIELDCRAFT_EMIT_TELEMETRY=1` when you want extra JSON snapshots under `artifacts/drift_telemetry/`; omit it to skip disk writes entirely.

## Guardrails
- `NO_APPLY=1` is enforced by default (CI sets it automatically). Remove it only when explicitly performing approved remediation work.
- Remediation scripts check both `NO_APPLY` and allowlists before calling CloudFormation `update_stack`.
- CI runs the detection job on a read-only IAM role, ensuring zero drift writes happen during scheduled checks.

## Human workflows
1. **Detect** – run `poetry run nox -s drift_check -- --stacks MyStack` (or omit `--stacks` to use config). Review `.json` + `.diff` outputs under `artifacts/drift/`.
2. **Summarize** – `poetry run nox -s drift_report` builds `artifacts/drift_summary/latest.(json|md)` which can be attached to PRs or issues.
3. **Remediate** – `poetry run python scripts/drift_remediation/run_drift_remediation.py --stacks MyStack --artifacts-dir artifacts/drift_remediation` writes structured plans. Because `NO_APPLY=1`, plans default to manual approval steps.
4. **Acknowledge safe drift** – once reviewed, run `poetry run nox -s drift_acknowledge -- MyStack artifacts/drift/MyStack/<timestamp>.diff "Change approved"` to bump `drift_baselines/MyStack.json`.

## CI coverage
- `.github/workflows/ci.yml` defines a nightly `drift_check` job. It installs Poetry, runs `nox -s drift_check -- --post` (best-effort GitHub issue), generates summaries, uploads artifacts, and never executes remediation.
- Scheduled cadence: dev (monthly), staging (weekly), prod (daily) via `config/*.yml` `drift_scan_schedule`. These values inform future automation and documentation.

## References
- `scripts/drift_remediation/run_drift_check.py`
- `scripts/drift_remediation/run_drift_remediation.py`
- `nox_sessions/drift.py`
- `.github/workflows/ci.yml`
- `docs-site/docs/github/deployment_dry_run_rollback.md`
