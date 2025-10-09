# Threat Model Summary (Initial Draft)

This document distills key residual risks and mitigations for ShieldCraft AI across environments (dev, staging, prod). It complements the Architecture Spec and Security & Governance checklist.

## Scope and Assumptions
- Scope: data ingestion, governance, retrieval/AI core, docs portal, and IaC (CDK/Proton) as deployed or scaffolded today.
- Assumptions:
  - Dev minimizes managed services to control cost; staging/prod introduce managed services behind guardrails.
  - Secrets are centralized in AWS Secrets Manager; no static credentials in code.
  - All resources receive consistent tags and environment-suffixed names.

## System Context and Trust Boundaries
- Trust boundaries: internet → portal, analyst access → API, AWS account per environment, VPC private subnets, KMS-encrypted storage, Secrets Manager.
- Data classes: telemetry (low/med), credentials/keys (high), model artifacts (med), benchmark logs (low), identity data (high).

## Key Assets
- Identity and access: IAM roles/policies, Cognito (auth stack).
- Data stores: S3 buckets (raw/processed/analytics), pgvector database, Glue/LF catalog.
- Compute and control plane: Lambda, Step Functions (scaffolded), EventBridge, CDK Pipelines (optional), Proton bundles (local-only).
- Secrets: Credentials in Secrets Manager with least privilege access.

## Threat Surfaces (by domain)
- Ingestion and Storage: data exfiltration via misconfigured buckets, schema poisoning, ungoverned PII ingestion.
- Retrieval and Vector Store: prompt injection via retrieved context, vector poisoning, embedding model drift.
- AI Inference: hallucination leading to bad recommendations, toxicity, or jailbreak prompts.
- Control Plane / IaC: misconfiguration drift, privilege escalation via overly broad IAM, secret sprawl.
- Docs Portal: XSS via MDX content, auth/z misconfig for preview features.

## Controls (implemented)
- S3 encryption + lifecycle policies; public access blocks.
- GuardDuty, Security Hub, Detective enabled; Inspector optional.
- Centralized Secrets Manager; Pydantic config validation; CDK tagging and naming.
- Event-driven patterns (DLQs, retries) and explicit IAM boundaries (scoped roles).
- Cost guardrails: Budgets, tagging, retention.

## Residual Risks and Mitigations
| ID     | Risk                                    | Likelihood | Impact | Residual | Mitigation/Backlog                                                                      | Owner    | Target |
| ------ | --------------------------------------- | ---------- | ------ | -------- | --------------------------------------------------------------------------------------- | -------- | ------ |
| TR-001 | Prompt injection via retrieved context  | Med        | Med    | Med      | Add retrieval spot-check harness; sanitize/score context; introduce allow/deny patterns | AI       | Q4     |
| TR-002 | Vector poisoning from untrusted sources | Low        | High   | Med      | Establish data source allowlist and signed ingestion; add provenance in embeddings      | Data     | Q4     |
| TR-003 | Hallucination/toxicity in responses     | Med        | Med    | Med      | Add evaluation loop w/ toxicity/QA scoring; guardrail prompts and filters               | AI       | Q4     |
| TR-004 | IAM policy creep / privilege escalation | Low        | High   | Med      | Automated IAM review cadence; policy lints; boundary policies                           | SecOps   | Q4     |
| TR-005 | Drift/misconfiguration in IaC           | Med        | Med    | Med      | Drift remediation pipeline; CI checks for config schema                                 | Platform | Q4     |
| TR-006 | PII leakage in ingestion                | Low        | High   | Med      | DLP rules and redaction; Lake Formation governance tightening                           | Data     | Q4     |

## Review Cadence
- Monthly risk review in dev/staging; quarterly in prod.
- Triggered review on material architecture change (new domain/service) or incident.

## Evidence and References
- Architecture Spec, Checklist progress, Security & Governance section.
- Benchmarks: `mteb_benchmark.log`, `mteb_results.json/`.
- IaC repos: `infra/`, config schema and loader in `infra/utils/`.

> Status: Initial draft. Will evolve alongside the spot-check harness and dry-run/rollback explainer.
