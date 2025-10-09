import React, { useState, useCallback, useRef, useLayoutEffect, useMemo } from 'react';
import useScrollPersistence from '../clientModules/scrollRestoration';
import styles from './PlatformArchitecture.module.css';

type RotationItem = { title: string; body: string };

const rotations: RotationItem[] = [
    {
        title: 'Ingestion → Normalization',
        body: 'Multi-account telemetry lands in governed storage; schemas & tagging enforce lineage before enrichment.'
    },
    {
        title: 'Indexing & Vectorization',
        body: 'Relevant artifacts (findings, identity graph, playbooks) are chunked & embedded behind a retrieval boundary.'
    },
    {
        title: 'Context Augmentation',
        body: 'Queries and events are expanded with top-k semantic + structured context, forming precise augmented prompts.'
    },
    {
        title: 'Generative Reasoning & Simulation',
        body: 'LLM & attack simulators produce response hypotheses, remediation steps, or novel scenario variants.'
    },
    {
        title: 'Autonomous Actions & Feedback',
        body: 'Guardrailed workflows execute; outcomes & validation metrics loop back to refine embeddings & policies.'
    },
];

const layerSpec: { label: string; services: { name: string; icon?: string }[] }[] = [
    {
        label: 'Ingestion & Governance Layer',
        services: [
            { name: 'S3' }, { name: 'Glue' }, { name: 'Glue Data Quality' }, { name: 'Glue DataBrew' }, { name: 'Lake Formation' }, { name: 'EventBridge' }, { name: 'API Gateway' }, { name: 'MSK' }, { name: 'CloudTrail' }, { name: 'VPC' }
        ]
    },
    {
        label: 'GenAI & MLOps Core',
        services: [
            { name: 'OpenSearch' }, { name: 'pgVector' }, { name: 'Embeddings' }, { name: 'Feature Store' }, { name: 'SageMaker' }, { name: 'LLM Loader' }, { name: 'Attack Sim' }, { name: 'Prompt Orchestrator' }
        ]
    },
    {
        label: 'Remediation & Financial Control Plane',
        services: [
            { name: 'Lambda' }, { name: 'Step Functions' }, { name: 'Playbooks' }, { name: 'Remediation Guardrails' }, { name: 'IAM' }, { name: 'Secrets Manager' }, { name: 'Security Hub' }, { name: 'GuardDuty' }, { name: 'Config' }, { name: 'Detective' }, { name: 'WAF' }, { name: 'Budgets' }, { name: 'Cost Explorer' }, { name: 'CloudWatch' }, { name: 'Control Tower' }, { name: 'IAM Identity Center' }, { name: 'Benchmarks' }
        ]
    }
];

export default function PlatformArchitecture() {
    // Mount scroll persistence to continuously save scroll during interaction
    useScrollPersistence();
    const [idx, setIdx] = useState(0);
    const [selectedKey, setSelectedKey] = useState<string | null>('S3');
    // Preserve vertical scroll position relative to the component container when content height shifts
    const containerRef = useRef<HTMLElement | null>(null);
    const preserveRef = useRef<{ top: number; scrollY: number } | null>(null);

    // Map specific layer/service clicks to the most relevant lifecycle narrative index
    const narrativeMap: Record<string, number> = {
        'Data & Integration': 0,
        'Intelligence & Simulation': 3,
        'Orchestration & Governance': 4,
        // service level (fallback to closest concept)
        'S3': 0, 'Glue': 0, 'Glue Data Quality': 0, 'Glue DataBrew': 0, 'Lake Formation': 0, 'EventBridge': 0, 'API Gateway': 0, 'MSK': 0, 'CloudTrail': 0, 'VPC': 0,
        'OpenSearch': 2, 'pgVector': 1, 'Embeddings': 1, 'Feature Store': 1, 'SageMaker': 1,
        'LLM Loader': 3, 'Attack Sim': 3, 'Prompt Orchestrator': 3,
        'Lambda': 4, 'Step Functions': 4, 'Playbooks': 4, 'Remediation Guardrails': 4, 'IAM': 4, 'Secrets Manager': 4,
        'Security Hub': 0, 'GuardDuty': 0, 'Config': 0, 'Detective': 0, 'WAF': 4, 'Budgets': 0, 'Cost Explorer': 0, 'CloudWatch': 4, 'Control Tower': 0, 'IAM Identity Center': 4, 'Benchmarks': 4
    };

    // Detail copy for each selectable entity
    const entityDetails: Record<string, { type: 'Layer' | 'Service'; blurb: string; }> = {
        'Data & Integration': { type: 'Layer', blurb: 'Governed ingestion and contracts-first integration across accounts, with lineage, retention, and access enforced at the edge.' },
        'Intelligence & Simulation': { type: 'Layer', blurb: 'Hybrid retrieval (structured + semantic) and safe generative simulation to test hypotheses and pressure-test controls.' },
        'Orchestration & Governance': { type: 'Layer', blurb: 'Guardrailed automation, policy enforcement, and continuous evaluation closing the loop safely.' },
        // Services
        'S3': { type: 'Service', blurb: 'Buckets instantiated via Proton & CDK constructs, parameterized per environment (dev → prod). SSE-KMS and block public access are default guardrails.' },
        'Glue': { type: 'Service', blurb: 'ETL & schema enforcement normalizing multi-source telemetry.' },
        'Glue Data Quality': { type: 'Service', blurb: 'Rule-based and statistical checks ensure datasets remain trustworthy.' },
        'Glue DataBrew': { type: 'Service', blurb: 'Visual data prep for quick transforms and profile-driven cleanup.' },
        'Lake Formation': { type: 'Service', blurb: 'Fine-grained access controls across the governed data lake.' },
        'EventBridge': { type: 'Service', blurb: 'Event routing fabric decoupling producers from autonomous workflows.' },
        'API Gateway': { type: 'Service', blurb: 'Managed API entrypoint enabling secure control & integration interfaces.' },
        'MSK': { type: 'Service', blurb: 'Streaming backbone handling high-volume telemetry fan-in.' },
        'CloudTrail': { type: 'Service', blurb: 'Authoritative audit + API activity feed for enrichment and detection.' },
        'VPC': { type: 'Service', blurb: 'Isolated networking, endpoints, and routing boundaries for secure traffic.' },
        'GuardDuty': { type: 'Service', blurb: 'Managed threat findings feeding enrichment + prioritization.' },
        'OpenSearch': { type: 'Service', blurb: 'Low-latency indexed search over normalized findings + logs.' },
        'pgVector': { type: 'Service', blurb: 'Relational + vector hybrid store enabling structured + semantic joins.' },
        'Embeddings': { type: 'Service', blurb: 'Dense representations capturing semantic security context.' },
        'Feature Store': { type: 'Service', blurb: 'Versioned security features powering model & rule hybrids.' },
        'SageMaker': { type: 'Service', blurb: 'Managed model hosting / inference endpoints powering retrieval-augmented reasoning.' },
        'LLM Loader': { type: 'Service', blurb: 'Abstraction over foundation + tuned model endpoints.' },
        'Attack Sim': { type: 'Service', blurb: 'Generative adversary harness crafting multi-stage scenarios.' },
        'Prompt Orchestrator': { type: 'Service', blurb: 'Composable prompt + tool chain assembly with policy guards.' },
        'Lambda': { type: 'Service', blurb: 'Stateless micro-automations driving remediation + enrichment.' },
        'Step Functions': { type: 'Service', blurb: 'Deterministic state machine orchestration for response flows.' },
        'Playbooks': { type: 'Service', blurb: 'Codified conditional response logic with evaluation checkpoints.' },
        'Remediation Guardrails': { type: 'Service', blurb: 'Policy & safety checks gating autonomous actions.' },
        'IAM': { type: 'Service', blurb: 'Identity + permission boundaries governing least-privilege execution.' },
        'Secrets Manager': { type: 'Service', blurb: 'Secret material lifecycle (rotation & tight-scoped retrieval).' },
        'Security Hub': { type: 'Service', blurb: 'Unified control & finding aggregation for compliance posture.' },
        'Config': { type: 'Service', blurb: 'Resource state timeline & conformance signal source.' },
        'Detective': { type: 'Service', blurb: 'Investigation service that helps analyze, identify, and root-cause issues quickly.' },
        'WAF': { type: 'Service', blurb: 'Layer-7 protection and managed rules acting as an external safety brake.' },
        'Budgets': { type: 'Service', blurb: 'Cost guardrails + alerting feeding autonomy safety decisions.' },
        'Cost Explorer': { type: 'Service', blurb: 'Spend analytics driving decisions and accountability.' },
        'CloudWatch': { type: 'Service', blurb: 'Operational metrics, logs, and alarms for visibility and control.' },
        'Control Tower': { type: 'Service', blurb: 'Landing zone governance and guardrails across accounts.' },
        'IAM Identity Center': { type: 'Service', blurb: 'Centralized workforce identity and SSO for platform access.' },
        'Benchmarks': { type: 'Service', blurb: 'Evaluation suites measuring model & workflow quality.' },
    };

    // Map service display names to icon asset filenames in /aws-icons
    const serviceIconMap: Record<string, string> = {
        // Data Plane
        'S3': 'Arch_Amazon-Simple-Storage-Service_48.svg',
        'Glue': 'Arch_AWS-Glue_48.svg',
        'Glue Data Quality': 'Res_AWS-Glue_Data-Quality_48.svg',
        'Glue DataBrew': 'Arch_AWS-Glue-DataBrew_48.svg',
        'Lake Formation': 'Arch_AWS-Lake-Formation_48.svg',
        'EventBridge': 'Arch_Amazon-EventBridge_48.svg',
        'API Gateway': 'Arch_Amazon-API-Gateway_48.svg',
        'MSK': 'Arch_Amazon-Managed-Streaming-for-Apache-Kafka_48.svg',
        'CloudTrail': 'Arch_AWS-CloudTrail_48.svg',
        'VPC': 'Res_Amazon-VPC_Virtual-private-cloud-VPC_48.svg',
        'GuardDuty': 'Arch_Amazon-GuardDuty_48.svg',
        // Intelligence Core
        'OpenSearch': 'Arch_Amazon-OpenSearch-Service_48.svg',
        'pgVector': 'Arch_Amazon-RDS_48.svg', // relational best-fit
        'Embeddings': 'Res_Amazon-SageMaker_Model_48.svg',
        'Feature Store': 'Arch_Amazon-SageMaker_48.svg',
        'SageMaker': 'Arch_Amazon-SageMaker_48.svg',
        // GenAI + Simulation
        'LLM Loader': 'Res_Amazon-SageMaker_Model_48.svg',
        'Attack Sim': 'Arch_AWS-WAF_48.svg', // security control stand-in
        'Prompt Orchestrator': 'Arch_Amazon-CloudWatch_48.svg', // orchestration/observability proxy
        // Autonomy & Orchestration
        'Lambda': 'Arch_AWS-Lambda_48.svg',
        'Step Functions': 'Arch_AWS-Step-Functions_48.svg',
        'Playbooks': 'Arch_Amazon-CloudWatch_48.svg', // using CloudWatch for operational run-books
        'Remediation Guardrails': 'Arch_AWS-WAF_48.svg',
        'IAM': 'Arch_AWS-Identity-and-Access-Management_48.svg',
        'Secrets Manager': 'Arch_AWS-Secrets-Manager_48.svg',
        // Governance + Observability
        'Security Hub': 'Arch_AWS-Security-Hub_48.svg',
        'Config': 'Arch_AWS-Config_48.svg',
        'Detective': 'Arch_Amazon-Detective_48.svg',
        'WAF': 'Arch_AWS-WAF_48.svg',
        'Budgets': 'Arch_AWS-Budgets_48.svg',
        'Cost Explorer': 'Arch_AWS-Cost-Explorer_48.svg',
        'CloudWatch': 'Arch_Amazon-CloudWatch_48.svg',
        'Control Tower': '', // fallback
        'IAM Identity Center': 'Arch_AWS-IAM-Identity-Center_48.svg',
        'Benchmarks': 'Res_AWS-Trusted-Advisor_Checklist-Cost_48.svg'
    };

    const genericFallbackIcon = 'Arch_Amazon-CloudWatch_48.svg';

    const selectItem = useCallback((key: string) => {
        // measure pre-change position
        if (containerRef.current) {
            preserveRef.current = {
                top: containerRef.current.getBoundingClientRect().top,
                scrollY: window.scrollY
            };
        }
        const mapped = narrativeMap[key];
        if (typeof mapped === 'number') {
            setIdx(mapped);
            setSelectedKey(key);
        }
    }, []);

    // After any idx/selection update, adjust scroll to keep section anchored
    useLayoutEffect(() => {
        if (preserveRef.current && containerRef.current) {
            const before = preserveRef.current;
            const newTop = containerRef.current.getBoundingClientRect().top;
            const delta = newTop - before.top;
            if (Math.abs(delta) > 1) {
                window.scrollTo({ top: before.scrollY + delta });
            }
            preserveRef.current = null;
        }
    }, [idx, selectedKey]);

    const active = rotations[idx];
    const detail = selectedKey ? entityDetails[selectedKey] : null;
    // Prefer a service icon when a service is selected; for layers, use fallback; for no selection, show nothing.
    const displayedIcon = useMemo(() => {
        if (!selectedKey) return null;
        if (detail?.type === 'Service') {
            return serviceIconMap[selectedKey] || genericFallbackIcon;
        }
        // Layer or unknown selection → fallback icon
        return genericFallbackIcon;
    }, [detail, selectedKey]);

    // Build a concise narrative when an entity is selected; fall back to lifecycle text otherwise
    const selectedStageIdx = useMemo(() => {
        if (!selectedKey) return idx;
        const mapped = narrativeMap[selectedKey];
        return typeof mapped === 'number' ? mapped : idx;
    }, [selectedKey, idx]);

    const personalizedBody = useMemo(() => {
        if (!selectedKey || !detail) return active.body;
        const stage = rotations[selectedStageIdx]?.title || active.title;
        // Short, punchy body incorporating the selection and stage
        const base = detail.blurb;
        // Tailor a crisp second clause depending on layer vs service
        const clause = detail.type === 'Service'
            ? `Deployed as code, gated by budgets and policy. Stage: ${stage}.`
            : `Contracts-first, failure-aware, and observable end-to-end. Stage: ${stage}.`;
        return `${base} ${clause}`;
    }, [selectedKey, detail, selectedStageIdx, active.body, active.title]);

    // Key tags to highlight properties per selection
    const tagsMap: Record<string, string[]> = {
        // Data Plane
        'S3': ['Encrypted', 'Lifecycle', 'Versioned'],
        'Glue': ['Schemas', 'ETL', 'Governed'],
        'Glue Data Quality': ['DQ', 'Rules', 'Profiles'],
        'Glue DataBrew': ['Visual', 'Profiles', 'Transform'],
        'Lake Formation': ['LF‑Tags', 'Fine‑grained', 'Governed'],
        'EventBridge': ['Fan‑out', 'Retries', 'DLQ'],
        'API Gateway': ['Private', 'IAM', 'Throttled'],
        'MSK': ['Streaming', 'Partitions', 'SSE'],
        'CloudTrail': ['Org‑wide', 'Immutable', 'Audit'],
        'VPC': ['Endpoints', 'Subnets', 'Routes'],
        'GuardDuty': ['Findings', 'Managed', 'Priority'],
        // Intelligence Core
        'OpenSearch': ['Low‑latency', 'FGAC', 'ILM'],
        'pgVector': ['Hybrid', 'ANN', 'SQL'],
        'Embeddings': ['Vectors', 'Batchable', 'Reproducible'],
        'Feature Store': ['Versioned', 'Schemas', 'Drift'],
        'SageMaker': ['Managed', 'Autoscale', 'GPU'],
        // GenAI + Simulation
        'LLM Loader': ['Hot‑swap', 'Quantized', 'Device‑aware'],
        'Attack Sim': ['Safe', 'Multi‑stage', 'Signals'],
        'Prompt Orchestrator': ['Policy', 'Budgets', 'Composable'],
        // Autonomy & Orchestration
        'Lambda': ['Idempotent', 'DLQ', 'Least‑privilege'],
        'Step Functions': ['Retries', 'Timeouts', 'Approvals'],
        'Playbooks': ['Conditional', 'Reversible', 'Auditable'],
        'Remediation Guardrails': ['Budgets', 'Config', 'Safety'],
        'IAM': ['Least‑privilege', 'Boundaries', 'Tagged'],
        'Secrets Manager': ['Centralized', 'Rotatable', 'Scoped'],
        // Governance + Observability
        'Security Hub': ['Aggregated', 'Standards', 'Routing'],
        'Config': ['Conformance', 'Recorders', 'Remediation'],
        'Detective': ['Investigate', 'Graph', 'Root-cause'],
        'WAF': ['Rules', 'Managed', 'L7'],
        'Budgets': ['Alarms', 'Thresholds', 'Tags'],
        'Cost Explorer': ['Curves', 'Forecast', 'Tags'],
        'CloudWatch': ['Dashboards', 'Alarms', 'TraceIDs'],
        'Control Tower': ['Guardrails', 'Accounts', 'Landing Zone'],
        'IAM Identity Center': ['SSO', 'SCIM', 'SAML'],
        'Benchmarks': ['MTEB', 'BEIR', 'Gates'],
        // Layers (generic tags)
        'Data & Integration': ['Governed', 'Encrypted', 'Tagged'],
        'Intelligence & Simulation': ['Hybrid', 'Reasoning', 'Retrieval'],
        'Orchestration & Governance': ['Guardrailed', 'Auditable', 'Policy']
    };
    const activeTags = selectedKey ? tagsMap[selectedKey] : undefined;

    return (
        <section ref={containerRef} className={styles.archSection} aria-labelledby="platform-arch-title">
            <h2 id="platform-arch-title" className={styles.archTitle}>Unified Security Data Plane &amp; Governed Deployment Engine on AWS</h2>
            <p className={styles.archSubtitle}>The platform utilizes <strong>AWS Proton and CDK Constructs</strong> to ingest, enrich, and correlate security telemetry. Actionable insights are delivered into workflows, fortified by policy-grade guardrails and deterministic cost control.</p>

            <div className={styles.archGridWrapper}>
                <div className={styles.diagramCard} aria-label="Layered architecture diagram">
                    <div className={styles.layersGrid}>
                        {layerSpec.map(layer => (
                            <div key={layer.label} className={styles.layerGroup}>
                                <button
                                    type="button"
                                    className={`${styles.layerHeaderBtn || styles.layerHeader} ${selectedKey === layer.label ? styles.servicePillActive : ''}`}
                                    onClick={() => selectItem(layer.label)}
                                    aria-pressed={idx === narrativeMap[layer.label]}
                                >
                                    {layer.label}
                                </button>
                                <div className={styles.servicesRow}>
                                    {layer.services.map(s => (
                                        <button
                                            key={s.name}
                                            type="button"
                                            className={`${styles.servicePillBtn || styles.servicePill} ${selectedKey === s.name ? styles.servicePillActive : ''}`}
                                            onClick={() => selectItem(s.name)}
                                            aria-label={`Focus lifecycle narrative for ${s.name}`}
                                            aria-pressed={idx === narrativeMap[s.name]}
                                        >{s.name}</button>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className={styles.archNote}>Traceability: each layer enforces contracts (schemas, policies, embedding boundaries) enabling safe autonomous actions. <strong>Platform extensibility is provided via versioned CDK SDK constructs.</strong></div>
                </div>
                <div className={styles.rotatingPanel} aria-live="polite">
                    <div className={styles.rightSplit}>
                        {/* Top: Service overview */}
                        <div
                            key={`svc-${idx}-${selectedKey || 'auto'}`}
                            className={`${styles.rightCard} ${styles.infoPane} ${styles.fadeSwap}`}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'nowrap' }}>
                                {displayedIcon && (
                                    <div className={styles.selectionIconWrap}>
                                        <img
                                            src={`/aws-icons/${displayedIcon}`}
                                            alt={`${selectedKey ?? 'Selected'} icon`}
                                            className={styles.selectionIcon}
                                            loading="lazy"
                                            width={68}
                                            height={68}
                                        />
                                    </div>
                                )}
                                <div style={{ minWidth: 0 }}>
                                    {detail && (
                                        <div className={styles.selectionMeta}>
                                            <span className={styles.selectionTag}>{detail.type}</span>
                                            <span className={styles.selectionName}>{selectedKey}</span>
                                        </div>
                                    )}
                                    <h3 className={styles.rotationHeadline}>{selectedKey ? rotations[selectedStageIdx].title : active.title}</h3>
                                </div>
                            </div>
                            <p className={styles.rotationBody}>{personalizedBody}</p>
                            {activeTags && (
                                <div className={styles.metaTags}>
                                    {activeTags.map(t => (
                                        <span key={t} className={styles.metaTag}>{t}</span>
                                    ))}
                                </div>
                            )}
                            {!detail && (
                                <p className={styles.selectionHint}>Select any layer or service on the left for contextual implementation details. Lifecycle stages adjust automatically.</p>
                            )}
                        </div>

                        {/* Bottom: ShieldCraft implementation */}
                        <div key={`impl-${idx}-${selectedKey || 'auto'}`} className={`${styles.rightCard} ${styles.implPane}`}>
                            <UsageEmbedded selectedKey={selectedKey} />
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

// Embedded usage details component
function UsageEmbedded({ selectedKey }: { selectedKey: string | null }) {
    const baseIntro = 'Instantiated via Proton + CDK, parameterized per environment (dev → prod), with guardrails baked in.';
    const usageBullets: Record<string, string[]> = {
        'Data & Integration': [
            'Ingest once, govern always: KMS, tags, and LF enforce lineage and access.',
            'Event-driven patterns (EB/MSK) decouple producers and consumers safely.',
            'APIs and trails are private by default; network paths are explicit via VPC.'
        ],
        // Data Plane services
        'S3': [
            'Buckets instantiated via Proton & CDK constructs, parameterized per environment (dev → prod).',
            'Default guardrails: SSE-KMS encryption, block public access, access logging, and lifecycle policies tuned per env.',
            'Explicit naming and prefixing by domain; parameterized retention and lifecycle tiers (dev→prod).'
        ],
        'Glue': [
            'Crawlers scheduled per source; tables tagged for Lake Formation.',
            'ETL jobs enforced by schema; failures surface to metrics/alerts.',
            'Contracts-first catalogs drive downstream features and embedding shapes.'
        ],
        'Glue Data Quality': [
            'Data quality rules run per dataset; thresholds enforce promotion gates.',
            'Profiles tracked over time to catch drift and anomalies.',
            'Failures route to EventBridge for triage and remediation.'
        ],
        'Glue DataBrew': [
            'Quick profiling and visual transforms for exploratory pipelines.',
            'Recipes versioned; export back to Glue ETL for productionization.',
            'Used sparingly in prod; heavier use in dev for speed.'
        ],
        'Lake Formation': [
            'LF-tags map to domains/teams; grants managed via IaC only.',
            'Fine-grained permissions before any compute touches data.',
            'Auditable grants/Revokes; row/column filters ready when needed.'
        ],
        'EventBridge': [
            'Event patterns route findings/changes to Step Functions/Lambda.',
            'Dead-letter SQS for resiliency; retries with backoff.',
            'Schema registry optional; detail-type normalized for consumers.'
        ],
        'API Gateway': [
            'Private IAM-auth endpoints for control-plane hooks (no public surface by default).',
            'Stage variables and throttles are env-tuned.',
            'Access logs to CloudWatch with request IDs for traceability.'
        ],
        'MSK': [
            'Dev: external or disabled; Prod: MSK with per-domain topics + SSE.',
            'Producers enforce schemas; consumers idempotent with offset tracking.',
            'Topic naming with env suffix; partitioning sized by throughput.'
        ],
        'CloudTrail': [
            'Org trail into S3 (immutable via bucket policies); multi-account coverage.',
            'EventBridge rules fan-out high-value API events to workflows.',
            'Retention aligned with compliance; access via LF-governed tables.'
        ],
        'VPC': [
            'Private subnets and VPC endpoints for AWS services (no public egress).',
            'Security groups least-privilege; NACLs for coarse segmenting.',
            'Route tables explicitly defined; flow logs enabled to S3/CloudWatch.'
        ],
        'GuardDuty': [
            'Enabled across accounts; findings aggregated and deduped.',
            'EventBridge routes P1/P2 findings to response playbooks.',
            'Findings mirrored to storage for search and correlation.'
        ],
        'Intelligence & Simulation': [
            'Hybrid retrieval (OpenSearch + vectors) ensures both recall and precision.',
            'Generative simulation validates assumptions before automation acts.',
            'Features, models, and prompts are versioned and observable.'
        ],
        // Intelligence Core services
        'OpenSearch': [
            'Dev toggle off (cost save); Prod domain with encryption + fine-grained access.',
            'Indices per domain; ILM policies keep hot/warm storage efficient.',
            'Used for findings/logs search in hybrid with vectors for recall.'
        ],
        'pgVector': [
            'Postgres with pgvector; ANN search via <-> operator.',
            'Connection via env (container in dev, managed Postgres in higher envs).',
            'Migrations create tables; embedding dims/version stored with docs.'
        ],
        'Embeddings': [
            'Batch size + device configurable; CPU stub locally, GPU when available.',
            'Model ID + dim persisted for reproducibility.',
            'Backpressure + retries avoid hot-spotting during bulk loads.'
        ],
        'Feature Store': [
            'Versioned features with explicit schemas; drift surfaces to metrics.',
            'Backed by governed storage (S3/Glue); SM Feature Store optional.',
            'Feature contracts pin prompt inputs across model revisions.'
        ],
        'SageMaker': [
            'Optional managed endpoints; roles via ExecutionRoleArn (no secret anti-patterns).',
            'Autoscaling + instance types are env-gated; cost controls on.',
            'Local inference path exists to avoid costs in dev.'
        ],
        'GenAI + Simulation': [
            'Loader picks the right model per task (stub → 7B Q4).',
            'Attack sim generates multi‑step paths to pressure‑test controls.',
            'Orchestrator composes tools with policy + token budgets.'
        ],
        // GenAI + Simulation services
        'LLM Loader': [
            'Abstraction over stub and HF models; optional 4‑bit quantization.',
            'Device auto-detect (CUDA/CPU); graceful OOM guidance.',
            'Swappable without breaking retrieval/prompt contracts.'
        ],
        'Attack Sim': [
            'Generates realistic multi-stage scenarios to validate controls.',
            'Outputs tagged and fed into metrics and tuning loops.',
            'Safe by design: no destructive actions in lower envs.'
        ],
        'Prompt Orchestrator': [
            'Composes tools and prompts with policy and spend limits.',
            'Token budgets enforced per request; logs for audit.',
            'Reusable chains with guardrails and redaction where needed.'
        ],
        'Orchestration & Governance': [
            'State machines with retries/timeouts and human-in-the-loop stops.',
            'Budgets, WAF, and policy-as-code gate risky flows and costs.',
            'Security/Config/Detective provide posture and investigation signals.'
        ],
        // Autonomy & Orchestration services
        'Lambda': [
            'Idempotent functions with retries and DLQs (SQS).',
            'Least-privilege roles; inputs validated; outputs traced.',
            'Deployed via IaC with env-aware names and tags.'
        ],
        'Step Functions': [
            'Sagas with retries/timeouts and optional manual approvals.',
            'Per-step metrics + structured logs for investigations.',
            'Clear failure paths and reversible compensations.'
        ],
        'Playbooks': [
            'Runbooks as code: conditional steps + evaluation gates.',
            'Every change is auditable and designed to be undoable.',
            'Tied to findings and budgets to throttle risky flows.'
        ],
        'Remediation Guardrails': [
            'Budget/Config/Security posture required before action.',
            'Pre-flight checks ensure least-privilege + blast radius safe.',
            'Approvals or dry-runs in lower envs by default.'
        ],
        'IAM': [
            'Explicit managed policies; boundary/conditions enforce least privilege.',
            'Standardized tags and names for auditability.',
            'Cross-stack role outputs imported by consumers.'
        ],
        'Secrets Manager': [
            'Centralized secrets by env; ARNs injected via config.',
            'Tight-scoped retrieval in code; rotation policies where needed.',
            'No derived-secret anti-patterns; secrets never store ARNs.'
        ],
        'Governance + Observability': [
            'Cost + retention scale up in prod; tags everywhere.',
            'BEIR/MTEB + DQ become gates, not suggestions.',
            'Metrics close the loop to tune thresholds + embeddings.'
        ],
        // Governance + Observability services
        'Security Hub': [
            'Aggregated findings across accounts; filters drive priorities.',
            'EventBridge routes criticals to orchestrations.',
            'Posture trends tracked; exceptions documented.'
        ],
        'Config': [
            'Recorders on; rules enforce guardrails and conformance.',
            'Noncompliance triggers remediation playbooks.',
            'Retention tuned per env and compliance needs.'
        ],
        'Budgets': [
            'Monthly budgets with SNS/email alerts per env.',
            'Hard-stops for unsafe autonomy when thresholds trip.',
            'Tags drive chargeback/showback visibility.'
        ],
        'CloudWatch': [
            'Metrics and dashboards across ingestion/orchestration pipelines.',
            'Structured logs with correlation IDs wired from producers.',
            'Alarms with actionable runbooks and suppression windows.'
        ],
        'Benchmarks': [
            'MTEB/BEIR harness; artifacts committed to repo.',
            'Gated in prod; informative in dev/staging.',
            'Signals tune embeddings, rerankers, and thresholds.'
        ],
        'Detective': [
            'Findings and logs stitched into graphs to accelerate investigations.',
            'Pivot from entities to relationships to uncover root cause.',
            'Access controlled via roles; artifacts exported for correlation.'
        ],
        'WAF': [
            'Managed rule sets applied to public edges; custom rules for control endpoints.',
            'Used as an external kill-switch/safety-brake for autonomy.',
            'Metrics feed into budgets/policy to throttle risky flows.'
        ],
        'Cost Explorer': [
            'Spend visibility per env with tags; forecasts drive scaling decisions.',
            'Detect anomalies and attribute to services/workloads.',
            'Reports exported and surfaced alongside posture/quality.'
        ],
        'Control Tower': [
            'Landing zone with guardrails and audited account vending.',
            'Baseline controls ensure Config/CloudTrail are always on.',
            'Integrates with Security/Identity for consistent posture.'
        ],
        'IAM Identity Center': [
            'Workforce SSO with SCIM/SAML; groups map to least-privilege roles.',
            'Account/app assignments codified; no ad-hoc grants.',
            'Central audit of access with periodic reviews.'
        ],
    };

    // Service level fallback mapping to its parent layer bullets
    const serviceToLayer: Record<string, string> = {
        'S3': 'Data & Integration', 'Glue': 'Data & Integration', 'Lake Formation': 'Data & Integration', 'EventBridge': 'Data & Integration', 'API Gateway': 'Data & Integration', 'MSK': 'Data & Integration', 'CloudTrail': 'Data & Integration', 'VPC': 'Data & Integration', 'Glue Data Quality': 'Data & Integration', 'Glue DataBrew': 'Data & Integration',
        'OpenSearch': 'Intelligence & Simulation', 'pgVector': 'Intelligence & Simulation', 'Embeddings': 'Intelligence & Simulation', 'Feature Store': 'Intelligence & Simulation', 'SageMaker': 'Intelligence & Simulation', 'LLM Loader': 'Intelligence & Simulation', 'Attack Sim': 'Intelligence & Simulation', 'Prompt Orchestrator': 'Intelligence & Simulation',
        'Lambda': 'Orchestration & Governance', 'Step Functions': 'Orchestration & Governance', 'Playbooks': 'Orchestration & Governance', 'Remediation Guardrails': 'Orchestration & Governance', 'IAM': 'Orchestration & Governance', 'Secrets Manager': 'Orchestration & Governance', 'Security Hub': 'Orchestration & Governance', 'GuardDuty': 'Orchestration & Governance', 'Config': 'Orchestration & Governance', 'Detective': 'Orchestration & Governance', 'WAF': 'Orchestration & Governance', 'Budgets': 'Orchestration & Governance', 'Cost Explorer': 'Orchestration & Governance', 'CloudWatch': 'Orchestration & Governance', 'Control Tower': 'Orchestration & Governance', 'IAM Identity Center': 'Orchestration & Governance', 'Benchmarks': 'Orchestration & Governance'
    };

    let key = selectedKey || '';
    let bullets: string[] = [];
    if (key) {
        if (usageBullets[key]) bullets = usageBullets[key];
        else if (serviceToLayer[key] && usageBullets[serviceToLayer[key]]) bullets = usageBullets[serviceToLayer[key]];
    }
    const showFallback = !key;
    const fallbackBullets = [
        'Dev for speed; prod for scale (managed streaming, OpenSearch, GPU).',
        'Config, not code, flips retention, concurrency, and models.',
        'Benchmarks + DQ continuously sharpen embeddings and policy.'
    ];

    return (
        <div className={styles.usageBlockEmbedded}>
            <div className={styles.usageHeading}>ShieldCraft Implementation</div>
            <ul className={styles.usageList}>
                {(showFallback ? fallbackBullets : bullets).map(line => (
                    <li key={line} className={styles.usageItem}>{line}</li>
                ))}
            </ul>
            <div className={styles.usageFooterMini}>{baseIntro}</div>
        </div>
    );
}
