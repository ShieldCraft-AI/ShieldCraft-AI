export type CardTone = 'threat' | 'gen' | 'finops' | 'security';

export type PluginChip = { label: string; tone?: 'default' | 'alert'; href?: string };
export type PluginStat = { label: string; value: string; detail: string };

export type PluginConfig = {
    id: string;
    name: string;
    category: string;
    taskType: string;
    summary: string;
    blurb: string;
    tagline: string;
    chips: PluginChip[];
    stats: PluginStat[];
    bullets: string[];
    tone: CardTone;
    price: string;
    detailHref: string;
};

export const PLUGIN_CONFIG: PluginConfig[] = [
    {
        id: 'threat-classifier',
        name: 'Threat-Classifier',
        category: 'Threat Intelligence',
        taskType: 'Threat regression',
        summary: 'Real-time, analyst-in-the-loop threat scoring.',
        blurb: 'Fuses GuardDuty, SaaS telemetry, and SOC feedback to tune heatmaps within guardrails.',
        tagline: 'Production-hardened enrichment and scoring that blends GuardDuty, SaaS telemetry, and analyst feedback into an adaptive threat profile.',
        chips: [
            { label: 'ML Task: Threat regression', href: '/plugins/threat-classifier' },
            { label: 'Status: Production' },
            { label: 'Latency SLA: 250ms P95' },
            { label: 'Auto-tuned retraining windows' },
        ],
        tone: 'threat',
        price: '$2,400/mo platform fee',
        stats: [
            { label: 'Focus', value: 'Threat Intelligence', detail: 'Signals fusion with explainable scoring.' },
            { label: 'Guardrail', value: 'Immutable audit path', detail: 'Security Hub + EventBridge lineage.' },
            { label: 'Outcome', value: '3.2× faster triage', detail: 'Validated in SOC pilot runbooks.' },
        ],
        bullets: [
            'Multi-source feature engineering orchestrated via Step Functions and Lambda keeps enrichment deterministic even as telemetry volume grows.',
            'Scorecards route into Security Hub and EventBridge, preserving traceability for playbooks, approvals, and analyst overrides.',
            'Shadow deployments execute through SageMaker endpoints to validate new detector bundles before promotion.',
        ],
        detailHref: '/plugins/threat-classifier',
    },
    {
        id: 'seq2seq-rag',
        name: 'Seq2Seq Answer Architect',
        category: 'Generative Ops',
        taskType: 'Seq2Seq / generative AI',
        summary: 'Latency-gated RAG answers with citations.',
        blurb: 'Stage-aware prompts, warm-path caching, and guardrails deliver exec-ready narratives that stay inside data compliance envelopes.',
        tagline: 'Retrieval-augmented generation (RAG) pipeline tuned for evidence synthesis, sub-300ms P95 latency, and strict warm-path governance.',
        chips: [
            { label: 'ML Task: Seq2Seq / Generative AI', href: '/plugins/seq2seq-rag' },
            { label: 'Architectural focus: Scale & latency', tone: 'alert' },
        ],
        tone: 'gen',
        price: '$3,800/mo + usage credits',
        stats: [
            { label: 'Focus', value: 'Knowledge Ops', detail: 'Rapid synthesis from governed corpora.' },
            { label: 'Guardrail', value: 'Latency SLOs', detail: 'P95 ≤ 300ms across warm path.' },
            { label: 'Outcome', value: 'Exec-ready answers', detail: 'Narratives cite source snippets.' },
        ],
        bullets: [
            'Three-stage Step Functions workflow batches retrieval, prompt construction, and inference so GPU throughput scales predictably under burst traffic.',
            'Vector lookups leverage pgvector with adaptive k-nearest strategy, prioritising low-latency shards for frequently accessed domains.',
            'Integrated guardrails inspect prompts and completions for policy, cost, and data egress violations before streaming replies back to analysts.',
        ],
        detailHref: '/plugins/seq2seq-rag',
    },
    {
        id: 'resource-forecaster',
        name: 'Resource Forecaster',
        category: 'FinOps',
        taskType: 'Regression forecasting',
        summary: 'Forecast spend, surface actionable savings.',
        blurb: 'Regression envelopes and RMSE monitors flag budget drift early, pairing recommendations with FinOps runbooks.',
        tagline: 'Regression-driven FinOps advisor that validates compute spend against projected demand and codifies budget guardrails before capacity spikes land.',
        chips: [
            { label: 'ML Task: Regression', href: '/plugins/resource-forecaster' },
            { label: 'Domain: FinOps & capacity planning' },
            { label: 'RMSE monitor: Active' },
        ],
        tone: 'finops',
        price: '$1,950/mo fixed',
        stats: [
            { label: 'Focus', value: 'Spend Justification', detail: 'Budget envelopes by environment.' },
            { label: 'Guardrail', value: 'RMSE ≤ 4.7%', detail: 'Auto-alerts on anomaly windows.' },
            { label: 'Outcome', value: 'Savings surfaced', detail: 'Recommends rightsizing + SP buys.' },
        ],
        bullets: [
            'Historical telemetry, tagging metadata, and workload calendars hydrate a regression model that forecasts compute spend envelopes per environment.',
            'RMSE tracking feeds CloudWatch dashboards so FinOps teams can prove model fidelity and trigger retraining when error budgets drift.',
            'Recommendations flow into AWS Budgets and Cost Explorer playbooks, pairing projections with just-in-time savings plan guidance.',
        ],
        detailHref: '/plugins/resource-forecaster',
    },
    {
        id: 'access-anomaly-detector',
        name: 'Access Anomaly Detector',
        category: 'Data Security',
        taskType: 'NER + anomaly detection',
        summary: 'Secure entity-centric audit trails and alerts.',
        blurb: 'NER pipelines transform access logs into compliance artifacts while KMS and VPC guardrails lock down every inference hop.',
        tagline: 'Named-entity recognition (NER) pipeline that transforms unstructured access logs into actionable compliance artifacts and near-real-time alerts.',
        chips: [
            { label: 'ML Task: NER + anomaly detection', href: '/plugins/access-anomaly-detector' },
            { label: 'Domain: Data security & auditability' },
            { label: 'Guardrail: VPC-only & KMS everywhere', tone: 'alert' },
        ],
        tone: 'security',
        price: '$2,250/mo + compliance support',
        stats: [
            { label: 'Focus', value: 'Access Hygiene', detail: 'Entity-linked compliance narratives.' },
            { label: 'Guardrail', value: 'Zero egress', detail: 'Private subnets + customer KMS keys.' },
            { label: 'Outcome', value: 'Audit-ready', detail: 'Exports map directly to IAM approvals.' },
        ],
        bullets: [
            'Step Functions orchestrate log ingestion, entity extraction, and anomaly scoring so sensitive identities remain inside VPC-scoped subnets.',
            'KMS-encrypted feature stores and Secrets Manager rotation keep entity embeddings locked down while preserving audit trails.',
            'Compliance exports map detections to IAM approvals, raising EventBridge signals when access deviates from policy baselines.',
        ],
        detailHref: '/plugins/access-anomaly-detector',
    },
];

export const PLUGIN_SUMMARY = PLUGIN_CONFIG.map(({ id, name, category, taskType, summary, blurb, tone, price }) => ({
    id,
    name,
    category,
    taskType,
    summary,
    blurb,
    tone,
    price,
}));

export const getPluginById = (id: string): PluginConfig | undefined => PLUGIN_CONFIG.find(plugin => plugin.id === id);
