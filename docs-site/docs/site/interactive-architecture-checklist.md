---
title: Interactive Architecture Checklist
---

Goal: Ship a clickable, interview-ready architecture diagram with inline SVG hotspots (hybrid: ID-based + overlay), environment presets (dev, staging, prod), and claim-to-proof links.

## 0) Decisions (locked)
- Environments: dev, staging, prod (see /config/*.yml)
- Hotspot strategy: Hybrid ID-based where SVG ids are stable, overlay zones where layout changes
- Progressive disclosure: Keep services in the side panel; canvas shows capabilities only

## 1) Scaffolding (files + page)
- [ ] Page: docs-site/docs/site/interactive-architecture.mdx (client-only wrapper if needed)
- [ ] Component folder: docs-site/src/components/HotspotDiagram/
  - [ ] HotspotDiagram.tsx (SVG + pan/zoom + hotspot wiring)
  - [ ] HotspotDrawer.tsx (right panel: Why, Services, Proof)
  - [ ] HotspotTooltip.tsx (hover summary)
  - [ ] hotspotData.ts (capabilities + service mapping)
  - [ ] types.ts (Capability, ServiceRef, Env = 'dev' | 'staging' | 'prod')
  - [ ] idMapCheck.ts (validate SVG ids against hotspotData)
  - [ ] HotspotDiagram.module.css
- [ ] Dependency: react-zoom-pan-pinch (wrap SVG)

## 2) Diagram asset workflow
- [ ] Author: diagrams/interactive_hotspots.drawio
- [ ] Export SVG (embed ids; do not embed diagram data)
- [ ] Optimize: svgo pass
- [ ] Place: docs-site/static/img/diagrams/interactive_hotspots.svg
- [ ] Pre-commit: run idMapCheck to verify ids exist in SVG

## 3) Data model (single source of truth)
- [ ] Capability shape:
```ts
type Capability = {
  id: string;
  title: string;
  summary?: string;
  viewTags: Array<'data-plane'|'guardrails'|'actions'|'observability'>;
  recommendedByEnv: { dev: ServiceRef; staging: ServiceRef; prod: ServiceRef };
  alternatives?: Array<{ service: string; whenToChoose: string }>;
  finops?: { costTier: 'low'|'med'|'high'; notes?: string };
  tradeoffs?: string[];
  failureModes?: string[];
  proofLinks: Array<{ label: string; href: string; kind: 'code'|'diagram'|'test'|'runbook' }>;
}
```
- [ ] ServiceRef shape:
```ts
type ServiceRef = { name: string; description?: string; awsLink?: string; opsNotes?: string };
```
- [ ] Env union:
```ts
type Env = 'dev' | 'staging' | 'prod';
```

## 4) First 5 hotspots (capabilities only)
- [ ] Ingestion (id: node_ingestion)
- [ ] Correlation/Stream Processing (id: node_correlation)
- [ ] Guardrails/Policy (id: node_guardrails)
- [ ] Actions/Remediation (id: node_actions)
- [ ] Observability (id: node_observability)

## 5) Services by function (succinct defaults + alternates)
- Ingestion
  - Defaults: dev=EventBridge Pipes; staging=Kinesis; prod=Kinesis
  - Alternates: MSK (Kafka-first org), AppFlow (SaaS)
- Stream Processing
  - Defaults: dev=Lambda; staging=Kinesis Data Analytics; prod=Kinesis Data Analytics
  - Alternates: MSK + Flink; ECS tasks for custom runners
- Storage
  - Defaults: S3 (all); DynamoDB (state); OpenSearch (indexed)
  - Alternates: Aurora Serverless (relational), EFS (shared POSIX)
- Orchestration
  - Defaults: Step Functions; EventBridge Scheduler
  - Alternates: ECS for batch; MWAA if DAG-first
- Compute
  - Defaults: Lambda; ECS on Fargate
  - Alternates: EKS only if already operated
- Actions/Remediation
  - Defaults: Lambda; SSM Automation (fleet)
  - Alternates: CloudFormation StackSets (org-wide)
- Policy/Guardrails
  - Defaults: SCPs; IAM boundaries; AWS Config; Control Tower
  - Alternates: Bedrock Guardrails/Agent policies (if GenAI actions)
- Observability
  - Defaults: CloudWatch logs/metrics; X-Ray; Security Hub; GuardDuty; CloudTrail
  - Alternates: OTel collector to external
- Identity
  - Defaults: IAM roles; IAM Identity Center
  - Alternates: External IdP federation
- Networking/Edge
  - Defaults: VPC; Subnets; NAT; ALB/NLB; PrivateLink; API Gateway; CloudFront
- Queues/Buses
  - Defaults: SQS; SNS; EventBridge buses
- Data Products/Analytics
  - Defaults: Athena; Glue Data Catalog; Lake Formation
  - Alternates: EMR Serverless (heavy processing)

## 6) Minimal UI features (Phase 1)
- [ ] Pan/zoom container around SVG
- [ ] Hover tooltip (title + 1-liner)
- [ ] Click opens drawer with 3 tabs: Why, Services, Proof
- [ ] URL deep link: ?node=capabilityId&env=dev|staging|prod
- [ ] Environment selector: dev / staging / prod

## 7) Overlay fallback (for unstable ids)
- [ ] Overlay layer with viewBox-aligned hit zones for 1–2 nodes likely to move
- [ ] Map overlay ids in hotspotData alongside SVG ids

## 8) Quality gates
- [ ] Typecheck (docs-site)
- [ ] Docs build
- [ ] idMapCheck in pre-commit
- [ ] Proof link validator (paths must exist)
- [ ] One UI smoke test: click Ingestion → drawer title matches; URL updates

## 9) Phase 2 (optional, after demo)
- [ ] Add view modes: Data Plane / Guardrails / Actions / Observability (filter nodes)
- [ ] Add scenarios: Real-time detection / Burst ingestion / Batch enrichment (highlight path)
- [ ] Add tabs: Tradeoffs, Failure Modes, FinOps
- [ ] Expand to 10–12 capabilities

Notes
- Keep canvas service-free; services live in the drawer with env-specific defaults.
- Use concise copy designed, every claim links to proof.
