# IaC & Proton PaS Roadmap Checklist

Date: 2025-10-17

IMPORTANT: Under no circumstances should any automated job or script deploy cloud resources. All work is synthesis / lint / test only.

Use this file to mark progress on infra hardening, Proton PaS, and test coverage. Each item builds on the previous.

- [ ] P0  -  Lock safety: add repo "no-deploy" guard and CI enforcement
  - Why: Prevent accidental, costly deploys.
  - Quick local check: run a repo grep for deploy commands.

- [ ] P0  -  Baseline static analysis (cfn-lint, cdk-nag, Checkov, flake8/bandit)
  - Why: catch infra anti-patterns early in PRs.
  - Quick: synth + cfn-lint on templates.

- [ ] P0  -  Synthesis smoke harness & contract tests
  - Why: ensure CDK App.synth() completes and critical CfnOutputs exist.
  - Quick: pytest -m "not integration" (unit infra tests)

- [ ] P0  -  Proton PaS: run & validate `scripts/proton_bundle.py` (local-only)
  - Why: ensure manifest.json + zips are produced for docs/UI.
  - Quick: python scripts/proton_bundle.py && ls -la dist/proton

- [ ] P1  -  Proton schema & manifest tests
  - Why: ensure per-template schemas contain required keys.

- [ ] P0  -  CI: wire safety test + synth + linters + unit tests + proton bundle
  - Why: fail fast on PRs before merge to `main`.

- [ ] P1  -  Secrets workflow hardening (allowlist + CI scanning)
  - Why: reduce false positives while blocking real secrets.
  - Quick: node scripts/check-secrets.js -> inspect scripts/scan-secrets.json

- [ ] P1  -  Policy-as-code (CDK-Nag / Checkov rules) & tuning
  - Why: enforce encryption, logging, least privilege IAM.

- [ ] P2  -  Expand infra unit coverage & opt-in integration tests
  - Why: exercise edge cases; keep heavy tests gated and manual.

- [ ] P2  -  Nightly drift/contract validation (Proton manifest vs CDK synth)
  - Why: detect drift early and open issues/PRs automatically.

- [ ] P1  -  Proton dry-run publisher (prints `aws proton` commands only)
  - Why: transition from docs-only PaS to production-ready template lifecycle without execution.

- [ ] P0  -  PR protections: require CI checks + approver + artifact generation
  - Why: ensure deploy-readiness and prevent accidental merges.

- [ ] P3  -  Deploy-readiness audit & cost estimator (manual approval gate)
  - Why: before any human-triggered deploy, understand cost and approvals needed.

Notes:
- Mark each checkbox when complete. Keep `main` protected until P0 items pass in CI.
- Integration tests that call real AWS must be opt-in and run in a controlled environment with explicit approvals.

If you want, I can add small unit test files (synth smoke + critical outputs + proton bundle test) and a CI workflow that runs the P0 pipeline (synth + linters + tests)  -  pick "create tests" or "create CI" and I'll implement next.

--

## Platform services to evaluate & potentially add
We should consider adding or validating the following AWS services (examples). For each service: add a stack module, unit tests (schema + synth), cfn-lint rules, and policy-as-code checks.

- AWS Config (resource recording, rules)
  - Why: continuous compliance, drift detection. Verify recorder, delivery channel (+ S3 bucket encryption), and an initial rule pack.

- AWS Systems Manager (Parameter Store / Automation)
  - Why: runtime configuration, patch automation, Run Command for remedial actions. Verify parameter hierarchy and KMS encryption.

- AWS Inspector / Detective
  - Why: runtime vulnerability scanning (Inspector) and investigative graph/detections (Detective). Verify enabling toggles and least-privilege roles.

- AWS Config Remediation + Guardrails (remediation runbooks)
  - Why: automated corrective actions for some rule violations (non-destructive defaults only).

- AWS Artifact & Audit (or use external auditing storage)
  - Why: store compliance artifacts and reports for audits; verify S3 lifecycle and access controls.

- Amazon Macie / S3 Data Classification
  - Why: detect sensitive data in S3 buckets (PII, keys). Validate via sample buckets in dev.

- AWS CloudTrail + Lake (central logging) + OpenSearch integration
  - Why: ensure audit logs are centrally stored, encrypted, and searchable; verify KMS and retention.

- Amazon Inspector ECR/Image Scanning (CI integration)
  - Why: ensure container images are scanned before deployment (local image scanning recommended).

- SageMaker Model Monitor / Model Registry
  - Why: monitor drift, data/label quality for models; register versions in a model catalog. Add as optional stack behind flag.

- EventBridge Schema Registry / Observability hooks
  - Why: track event contracts; make schemas first-class to catch drift.

- AWS Security Hub (aggregation) + custom action hooks
  - Why: aggregate findings across GuardDuty / Inspector / Macie; verify SNS/SQS integration.

Notes on adding services:
- Add incrementally. For each new service: (1) minimal stack, (2) unit tests that validate config errors, (3) cfn-lint and checkov policies, (4) add to `config/dev.yml` toggles.
- Keep costs low in `dev` by defaulting to disabled or local/stubbed alternatives (e.g., model monitor = stub, Macie disabled in dev).
- Ensure all stacks have a `enabled` flag in config and that resources in dev are off by default.
