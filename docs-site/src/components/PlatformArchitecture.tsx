import React, { useState, useCallback, useRef, useLayoutEffect } from 'react';
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
        label: 'Data Plane',
        services: [
            { name: 'S3' }, { name: 'Glue' }, { name: 'Lake Formation' }, { name: 'EventBridge' }, { name: 'MSK' }, { name: 'CloudTrail' }, { name: 'GuardDuty' }, { name: 'API Gateway' }
        ]
    },
    {
        label: 'Intelligence Core',
        services: [
            { name: 'OpenSearch' }, { name: 'pgVector' }, { name: 'Embeddings' }, { name: 'Feature Store' }, { name: 'SageMaker' }
        ]
    },
    {
        label: 'GenAI + Simulation',
        services: [
            { name: 'LLM Loader' }, { name: 'Attack Sim' }, { name: 'Prompt Orchestrator' }
        ]
    },
    {
        label: 'Autonomy & Orchestration',
        services: [
            { name: 'Lambda' }, { name: 'Step Functions' }, { name: 'Playbooks' }, { name: 'Remediation Guardrails' }, { name: 'IAM' }, { name: 'Secrets Manager' }
        ]
    },
    {
        label: 'Governance + Observability',
        services: [
            { name: 'Security Hub' }, { name: 'Config' }, { name: 'Inspector' }, { name: 'Budgets' }, { name: 'Metrics' }, { name: 'Benchmarks' }
        ]
    }
];

export default function PlatformArchitecture() {
    const [idx, setIdx] = useState(0);
    const [selectedKey, setSelectedKey] = useState<string | null>(null);
    // Preserve vertical scroll position relative to the component container when content height shifts
    const containerRef = useRef<HTMLElement | null>(null);
    const preserveRef = useRef<{ top: number; scrollY: number } | null>(null);

    // Map specific layer/service clicks to the most relevant lifecycle narrative index
    const narrativeMap: Record<string, number> = {
        'Data Plane': 0,
        'Intelligence Core': 1,
        'GenAI + Simulation': 3,
        'Autonomy & Orchestration': 4,
        'Governance + Observability': 0,
        // service level (fallback to closest concept)
        'S3': 0, 'Glue': 0, 'Lake Formation': 0, 'EventBridge': 0, 'API Gateway': 0, 'MSK': 0, 'CloudTrail': 0, 'GuardDuty': 0,
        'OpenSearch': 2, 'pgVector': 1, 'Embeddings': 1, 'Feature Store': 1, 'SageMaker': 1,
        'LLM Loader': 3, 'Attack Sim': 3, 'Prompt Orchestrator': 3,
        'Lambda': 4, 'Step Functions': 4, 'Playbooks': 4, 'Remediation Guardrails': 4, 'IAM': 4, 'Secrets Manager': 4,
        'Security Hub': 0, 'Config': 0, 'Inspector': 0, 'Budgets': 0, 'Metrics': 4, 'Benchmarks': 4
    };

    // Detail copy for each selectable entity
    const entityDetails: Record<string, { type: 'Layer' | 'Service'; blurb: string; }> = {
        'Data Plane': { type: 'Layer', blurb: 'Unified multi-account ingestion, normalization, tagging & retention establishing deterministic lineage.' },
        'Intelligence Core': { type: 'Layer', blurb: 'Feature + embedding pipelines and vector indices powering precise hybrid retrieval.' },
        'GenAI + Simulation': { type: 'Layer', blurb: 'Reasoning + adversarial generation engines producing hypotheses, attack paths & response drafts.' },
        'Autonomy & Orchestration': { type: 'Layer', blurb: 'Guardrailed execution fabric converting hypotheses into reversible, auditable change.' },
        'Governance + Observability': { type: 'Layer', blurb: 'Policy, compliance & evaluation signals enforcing safe continuous improvement.' },
        // Services
        'S3': { type: 'Service', blurb: 'Durable object storage for raw + curated security artifacts.' },
        'Glue': { type: 'Service', blurb: 'ETL & schema enforcement normalizing multi-source telemetry.' },
        'Lake Formation': { type: 'Service', blurb: 'Fine-grained access controls across the governed data lake.' },
        'EventBridge': { type: 'Service', blurb: 'Event routing fabric decoupling producers from autonomous workflows.' },
        'API Gateway': { type: 'Service', blurb: 'Managed API entrypoint enabling secure control & integration interfaces.' },
        'MSK': { type: 'Service', blurb: 'Streaming backbone handling high-volume telemetry fan-in.' },
        'CloudTrail': { type: 'Service', blurb: 'Authoritative audit + API activity feed for enrichment and detection.' },
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
        'Inspector': { type: 'Service', blurb: 'Vulnerability & exposure scanning feeding prioritization.' },
        'Budgets': { type: 'Service', blurb: 'Cost guardrails + alerting feeding autonomy safety decisions.' },
        'Metrics': { type: 'Service', blurb: 'Operational + effect metrics exposing drift & saturation.' },
        'Benchmarks': { type: 'Service', blurb: 'Evaluation suites measuring model & workflow quality.' },
    };

    // Map service display names to icon asset filenames in /aws-icons
    const serviceIconMap: Record<string, string> = {
        // Data Plane
        'S3': 'Res_Amazon-Simple-Storage-Service_S3-On-Outposts_48.svg',
        'Glue': 'Res_AWS-Glue_Data-Quality_48.svg',
        'Lake Formation': 'Arch_AWS-Lake-Formation_48.svg',
        'EventBridge': 'Arch_Amazon-EventBridge_48.svg',
        'API Gateway': 'Arch_Amazon-API-Gateway_48.svg',
        'MSK': 'Arch_Amazon-Managed-Streaming-for-Apache-Kafka_48.svg',
        'CloudTrail': 'Arch_AWS-CloudTrail_48.svg',
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
        'Inspector': 'Arch_Amazon-Detective_48.svg', // investigative posture
        'Budgets': 'Arch_AWS-Budgets_48.svg',
        'Metrics': 'Arch_Amazon-CloudWatch_48.svg',
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
    const activeServiceIcon = detail?.type === 'Service' && selectedKey
        ? (serviceIconMap[selectedKey] || genericFallbackIcon)
        : null;

    return (
        <section ref={containerRef} className={styles.archSection} aria-labelledby="platform-arch-title">
            <h2 id="platform-arch-title" className={styles.archTitle}>Platform Architecture</h2>
            <p className={styles.archSubtitle}>From raw telemetry to autonomous, validated remediation. A governed intelligence loop.</p>

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
                    <div className={styles.archNote}>Traceability: each layer enforces contracts (schemas, policies, embedding boundaries) enabling safe autonomous actions.</div>
                </div>
                <div className={styles.rotatingPanel} aria-live="polite">
                    <div className={styles.iconStage}>
                        {activeServiceIcon && (
                            <img
                                src={`/aws-icons/${activeServiceIcon}`}
                                alt={`${selectedKey} icon`}
                                className={styles.selectionIcon}
                                loading="lazy"
                                width={56}
                                height={56}
                            />
                        )}
                    </div>
                    <div
                        key={`${idx}-${selectedKey || 'auto'}`}
                        className={`${styles.rotationContent} ${styles.fadeSwap}`}
                    >
                        {detail && (
                            <div className={styles.selectionMeta}>
                                <span className={styles.selectionTag}>{detail.type}</span>
                                <span className={styles.selectionName}>{selectedKey}</span>
                            </div>
                        )}
                        <h3 className={styles.rotationHeadline}>{active.title}</h3>
                        <p className={styles.rotationBody}>{active.body}</p>
                        {detail && (
                            <p className={styles.selectionBlurb}>{detail.blurb}</p>
                        )}
                        {!detail && (
                            <p className={styles.selectionHint}>Select any layer or service on the left for contextual implementation details. Lifecycle stages adjust automatically.</p>
                        )}
                        <UsageEmbedded selectedKey={selectedKey} />
                    </div>
                </div>
            </div>
        </section>
    );
}

// Embedded usage details component
function UsageEmbedded({ selectedKey }: { selectedKey: string | null }) {
    const baseIntro = 'ShieldCraft instantiates each layer via declarative Proton + CDK templates parameterized by environment (dev → prod).';
    const usageBullets: Record<string, string[]> = {
        'Data Plane': [
            'S3 (raw / processed / analytics) bucket set from config with env-specific lifecycle (30→60→GLACIER dev vs 90→180 prod).',
            'Glue + Lake Formation: crawler schedules + fine-grained permissions scaffold governed read domains.',
            'Event sources (CloudTrail, GuardDuty) normalized & tagged before feature/embedding pipelines.'
        ],
        'Intelligence Core': [
            'pgVector + embeddings batch size & device toggle (CPU stub → quantized GPU).',
            'OpenSearch disabled in dev (cost save) → managed domain in prod for low-latency hybrid retrieval.',
            'Feature store schemas versioned to keep prompts deterministic across model revisions.'
        ],
        'GenAI + Simulation': [
            'Model loader abstraction selects stub / small / quantized 7B via config flags.',
            'Attack simulation harness generates multi-stage adversary paths feeding drift + control gap metrics.',
            'Prompt Orchestrator assembles tool-augmented chains with guardrails (policy + token budgets).'
        ],
        'Autonomy & Orchestration': [
            'Step Functions orchestrate ingest/validate + benchmark flows with explicit failure handling.',
            'Lambda remediation & playbooks execute reversible changes gated by guardrail policies.',
            'Budget + Config + Security Hub signals short‑circuit unsafe autonomy transitions.'
        ],
        'Governance + Observability': [
            'Cost/governance toggles (budgets, tagging, retention) scale up in prod.',
            'BEIR/MTEB + data quality shift from pass‑through (dev) to enforced validation gates (prod).',
            'Metrics + benchmarks refine embeddings & policy thresholds continuously.'
        ],
    };

    // Service level fallback mapping to its parent layer bullets
    const serviceToLayer: Record<string, string> = {
        'S3': 'Data Plane', 'Glue': 'Data Plane', 'Lake Formation': 'Data Plane', 'EventBridge': 'Data Plane', 'MSK': 'Data Plane', 'CloudTrail': 'Data Plane', 'GuardDuty': 'Data Plane',
        'OpenSearch': 'Intelligence Core', 'pgVector': 'Intelligence Core', 'Embeddings': 'Intelligence Core', 'Feature Store': 'Intelligence Core',
        'LLM Loader': 'GenAI + Simulation', 'Attack Sim': 'GenAI + Simulation', 'Prompt Orchestrator': 'GenAI + Simulation',
        'Lambda': 'Autonomy & Orchestration', 'Step Functions': 'Autonomy & Orchestration', 'Playbooks': 'Autonomy & Orchestration', 'Remediation Guardrails': 'Autonomy & Orchestration',
        'Security Hub': 'Governance + Observability', 'Config': 'Governance + Observability', 'Inspector': 'Governance + Observability', 'Metrics': 'Governance + Observability', 'Benchmarks': 'Governance + Observability'
    };

    let key = selectedKey || '';
    let bullets: string[] = [];
    if (key) {
        if (usageBullets[key]) bullets = usageBullets[key];
        else if (serviceToLayer[key] && usageBullets[serviceToLayer[key]]) bullets = usageBullets[serviceToLayer[key]];
    }
    const showFallback = !key;
    const fallbackBullets = [
        'Dev optimizes velocity (external MSK, stub models); prod enables managed streaming, OpenSearch, GPU inference.',
        'Config files drive retention, concurrency, model selection, and validation depth with no code branching.',
        'Benchmarks + data quality feed continuous embedding + policy refinement loops.'
    ];

    return (
        <div className={styles.usageBlockEmbedded}>
            <div>ShieldCraft Implementation</div>
            <ul className={styles.usageList}>
                {(showFallback ? fallbackBullets : bullets).map(line => (
                    <li key={line} className={styles.usageItem}>{line}</li>
                ))}
            </ul>
            <div className={styles.usageFooterMini}>{baseIntro}</div>
        </div>
    );
}
