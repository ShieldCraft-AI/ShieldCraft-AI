# Deployment Dry-Run & Rollback Explainer

This guide shows how to validate infrastructure and app changes safely (dry-runs) and how to plan rollbacks. It emphasizes local-only flows first and avoids any AWS activity unless explicitly enabled.

## Goals
- See what would change (plans/diffs) without provisioning anything.
- Understand likely cost surfaces before enabling a deploy.
- Have clear rollback procedures per domain.

## Dry-run workflows (no AWS calls)
- CDK synth (local): generates CloudFormation templates.
- CDK diff (local): shows the plan against last known state (uses previously synthesized/stored context; safe locally).
- Proton bundling (local): packages versioned templates and a manifest; no AWS calls.

Optional, controlled AWS inspection (only when explicitly allowed):
- CDK diff with an AWS account/profile can query stack state. Treat as read-only but still requires credentials; keep this off by default.

## Safety guardrails
- Default to dev config with expensive services disabled (`mode: none` where supported).
- Require an explicit `SC_DEPLOY_ENABLE=1` for any command that might reach AWS.
- Use tags (`project`, `environment`, `cost_center`) for tracing and cost visibility.
- Prefer `DeletionPolicy: Retain` on stateful data stores and S3 buckets.
- Keep Secrets in Secrets Manager; never derive or store secrets from ARNs.

## Rollback strategies
- Immutable blue/green for compute (Lambda/SageMaker): keep last-good alias/endpoint for quick re-point.
- Data stores: Retain policy; reversible schema changes; export before destructive ops.
- Event buses/workflows: version and stage changes behind feature flags/aliases.
- Infra drift: favor small, incremental changes; isolate blast radius by stack/domain.

## Cost surfaces (quick reference)
- SageMaker endpoints: High. Gate behind env toggles and quotas.
- MSK/OpenSearch domains: High. Keep off in dev; stage in controlled envs.
- S3/Glue/Lake Formation: Low–Med. Watch crawler and data scan costs.
- Lambda/Step Functions/EventBridge: Low for typical dev/test usage.
- VPC endpoints/NAT: Med. NAT gateways are recurring.

## Failure modes to anticipate
- Missing bootstrap or permissions (CDK) → fix AWS bootstrap or use local-only synth.
- Resource replacements (diff shows ‘will replace’) → plan data retention/migrations.
- Invalid config (Pydantic failures) → fix `config/*.yml` early; add unhappy-path tests.
- Cross-account KMS/roles not granted → verify principals/conditions in IAM policies.

## Checklists

Pre-flight (always)
- [ ] `poetry run nox -s commit_flow` is green (lint/tests).
- [ ] Config validates (Pydantic) and secrets references resolve.
- [ ] `cd docs-site && npm run typecheck` passes (if docs changed).
- [ ] `python scripts/proton_bundle.py` produces `dist/proton/manifest.json` (when Proton templates change).
- [ ] Review `cdk synth` output for unintended resources.

Dry-run (local-first)
- [ ] `cdk synth` produces templates locally.
- [ ] `cdk diff` runs locally. If you must point to AWS to diff actual state, do it in a sandbox account only.

Rollback plan (per change)
- [ ] Identify stateful resources (buckets/db/topics) and set Retain where needed.
- [ ] Define revert path (alias switch, parameter rollback, template reversion).
- [ ] Confirm monitoring/alarms for deploy and rollback windows.

## Command references (optional)

Local-only (safe)
```bash
# Synthesize CloudFormation locally (no AWS calls)
poetry run cdk synth

# Show logical plan against last context (local)
poetry run cdk diff --no-path-metadata --no-asset-metadata

# Bundle Proton templates locally
python scripts/proton_bundle.py
```

Read-only inspection (use only when explicitly allowed)
```bash
# Compare to live stacks in a sandbox account (requires credentials)
SC_DEPLOY_ENABLE=1 AWS_PROFILE=sandbox poetry run cdk diff --app "python infra/app.py"
```

Rollback patterns (illustrative; adapt to your stacks)
```bash
# Re-point Lambda alias to previous version (example)
aws lambda update-alias --function-name my-fn --name live --function-version $PREV

# Retain+recreate pattern (buckets)
# 1) Set DeletionPolicy: Retain in template
# 2) Recreate stack without destroying bucket; reattach policies
```

## Ownership and cadence
- Platform owns deploy/diff tooling; domain owners own rollback plans for their stacks.
- Review dry-run and rollback design for each PR that changes infra or data.

## References
- `infra/` (CDK app & stacks), `config/` (env YAML), `scripts/proton_bundle.py`, `proton/templates/**`, `tests/` (unhappy-paths), and `docs-site/docs/github/aws_stack_architecture.md`.
