import React from 'react';
import Layout from '@theme/Layout';
import BrowserOnly from '@docusaurus/BrowserOnly';
import styles from './architecture.module.css';
// Static import of discovery JSON to avoid runtime fetch + render flash
// (relative path from src/pages to static/data)
// eslint-disable-next-line @typescript-eslint/no-var-requires
const staticDiscovery = require('../../static/data/architecture_discovery.json');

type TierKey = 'starter' | 'growth' | 'enterprise';

type Capability = {
    id: string;
    icon: string;
    title: string;
    description: string;
    // Default AWS services (fallback). Use awsByTier for tier-specific services.
    aws?: string[]; // AWS services involved (canonical names)
    awsByTier?: Record<TierKey, string[]>; // Tier-specific AWS services
    monthly: Record<TierKey, number>;
    section: 'Data & Pipeline' | 'ML & Intelligence' | 'Platform & Governance';
};

const TIERS: Record<TierKey, { label: string; tagline: string }> = {
    starter: { label: 'Starter', tagline: 'Launch-ready essentials at low cost' },
    growth: { label: 'Growth', tagline: 'Scale with confidence and controls' },
    enterprise: { label: 'Enterprise', tagline: 'Mission-critical performance and governance' },
};

const CAPABILITIES: Capability[] = [
    {
        id: 'ingestion',
        icon: '📊',
        title: 'Data Ingestion Pipeline',
        description: 'Reliable batch and streaming capture from SaaS, logs, and sensors.',
        awsByTier: {
            starter: ['Amazon S3', 'Amazon EventBridge', 'AWS Lambda'],
            growth: ['Amazon S3', 'Amazon EventBridge', 'AWS Lambda', 'AWS Glue'],
            enterprise: ['Amazon S3', 'Amazon EventBridge', 'AWS Lambda', 'Amazon MSK'],
        },
        monthly: { starter: 5, growth: 35, enterprise: 180 },
        section: 'Data & Pipeline',
    },
    {
        id: 'processing',
        icon: '⚙️',
        title: 'ML Data Processing',
        description: 'Distributed transforms, feature extraction, and quality checks.',
        awsByTier: {
            starter: ['AWS Glue', 'AWS Lambda'],
            growth: ['AWS Glue', 'AWS Step Functions'],
            enterprise: ['AWS Glue', 'AWS Step Functions', 'Amazon EventBridge'],
        },
        monthly: { starter: 25, growth: 120, enterprise: 650 },
        section: 'Data & Pipeline',
    },
    {
        id: 'lake',
        icon: '🏛️',
        title: 'Data Lake Storage',
        description: 'Secure, tiered storage with lifecycle and encryption at rest.',
        awsByTier: {
            starter: ['Amazon S3'],
            growth: ['Amazon S3', 'AWS Lake Formation'],
            enterprise: ['Amazon S3', 'AWS Lake Formation'],
        },
        monthly: { starter: 125, growth: 420, enterprise: 2100 },
        section: 'Data & Pipeline',
    },
    {
        id: 'dq',
        icon: '✅',
        title: 'Data Quality & Validation',
        description: 'Automated rules, profiling, and remediation gates for data trust.',
        awsByTier: {
            starter: ['AWS Glue DataBrew'],
            growth: ['AWS Glue Data Quality'],
            enterprise: ['AWS Glue Data Quality', 'AWS Glue DataBrew'],
        },
        monthly: { starter: 10, growth: 45, enterprise: 180 },
        section: 'Data & Pipeline',
    },
    {
        id: 'ml',
        icon: '🧠',
        title: 'Model Training & Inference',
        description: 'From quick prototypes to managed, production-grade endpoints.',
        awsByTier: {
            starter: ['Amazon SageMaker'],
            growth: ['Amazon SageMaker'],
            enterprise: ['Amazon SageMaker'],
        },
        monthly: { starter: 50, growth: 480, enterprise: 2800 },
        section: 'ML & Intelligence',
    },
    {
        id: 'orchestration',
        icon: '🎼',
        title: 'Workflow Orchestration',
        description: 'Event-driven pipelines, SLAs, and dependency management.',
        awsByTier: {
            starter: ['Amazon EventBridge', 'AWS Lambda'],
            growth: ['AWS Step Functions', 'Amazon EventBridge'],
            enterprise: ['AWS Step Functions'],
        },
        monthly: { starter: 15, growth: 60, enterprise: 220 },
        section: 'ML & Intelligence',
    },
    {
        id: 'serving',
        icon: '🚀',
        title: 'API Serving & Gateways',
        description: 'Secure, scalable APIs to deliver ML and analytics to apps.',
        awsByTier: {
            starter: ['Amazon API Gateway', 'AWS Lambda'],
            growth: ['Amazon API Gateway', 'AWS Lambda'],
            enterprise: ['Amazon API Gateway', 'AWS Lambda', 'AWS WAF'],
        },
        monthly: { starter: 12, growth: 65, enterprise: 320 },
        section: 'ML & Intelligence',
    },
    {
        id: 'feature-registry',
        icon: '🧩',
        title: 'Feature Store & Registry',
        description: 'Reusable features and versioned artifacts for consistent ML.',
        awsByTier: {
            starter: ['Amazon SageMaker'],
            growth: ['Amazon SageMaker'],
            enterprise: ['Amazon SageMaker'],
        },
        monthly: { starter: 8, growth: 55, enterprise: 240 },
        section: 'ML & Intelligence',
    },
    {
        id: 'batch-scoring',
        icon: '📦',
        title: 'Batch Scoring Pipelines',
        description: 'High-throughput batch inference with robust retries.',
        awsByTier: {
            starter: ['AWS Lambda'],
            growth: ['Amazon SageMaker', 'AWS Step Functions'],
            enterprise: ['Amazon SageMaker', 'AWS Step Functions'],
        },
        monthly: { starter: 14, growth: 80, enterprise: 360 },
        section: 'ML & Intelligence',
    },
    {
        id: 'security',
        icon: '🔒',
        title: 'Security & Compliance',
        description: 'Threat visibility, least privilege, and guardrails by default.',
        awsByTier: {
            starter: ['AWS IAM', 'Amazon GuardDuty', 'AWS Config'],
            growth: ['AWS IAM', 'Amazon GuardDuty', 'AWS Config', 'AWS Security Hub'],
            enterprise: ['AWS IAM', 'Amazon GuardDuty', 'AWS Config', 'AWS Security Hub'],
        },
        monthly: { starter: 20, growth: 70, enterprise: 260 },
        section: 'Platform & Governance',
    },
    {
        id: 'governance',
        icon: '📋',
        title: 'Data Governance & Lineage',
        description: 'Catalog, lineage, and policy enforcement across datasets.',
        awsByTier: {
            starter: ['AWS Glue'],
            growth: ['AWS Glue', 'AWS Lake Formation'],
            enterprise: ['AWS Glue', 'AWS Lake Formation'],
        },
        monthly: { starter: 15, growth: 55, enterprise: 190 },
        section: 'Platform & Governance',
    },
    {
        id: 'observability',
        icon: '👁️',
        title: 'Observability & Intelligence',
        description: 'Metrics, traces, logs, and AI insights for reliability.',
        awsByTier: {
            starter: ['Amazon CloudWatch'],
            growth: ['Amazon CloudWatch', 'Amazon OpenSearch Service'],
            enterprise: ['Amazon CloudWatch', 'Amazon OpenSearch Service'],
        },
        monthly: { starter: 10, growth: 45, enterprise: 170 },
        section: 'Platform & Governance',
    },
    {
        id: 'messaging',
        icon: '📨',
        title: 'Messaging & Eventing',
        description: 'Reliable queues, topics, and event buses for decoupled systems.',
        awsByTier: {
            starter: ['Amazon EventBridge'],
            growth: ['Amazon EventBridge'],
            enterprise: ['Amazon EventBridge', 'Amazon MSK'],
        },
        monthly: { starter: 8, growth: 40, enterprise: 160 },
        section: 'Data & Pipeline',
    },
    {
        id: 'audit',
        icon: '🧾',
        title: 'Audit & Trails',
        description: 'Forensics-ready logs and change tracking everywhere.',
        awsByTier: {
            starter: ['AWS CloudTrail'],
            growth: ['AWS CloudTrail'],
            enterprise: ['AWS CloudTrail'],
        },
        monthly: { starter: 6, growth: 22, enterprise: 75 },
        section: 'Platform & Governance',
    },
    {
        id: 'finops',
        icon: '💸',
        title: 'Cost & FinOps',
        description: 'Budgets, alerts, and actionable cost analytics.',
        awsByTier: {
            starter: ['AWS Budgets'],
            growth: ['AWS Budgets', 'AWS Cost Explorer'],
            enterprise: ['AWS Budgets', 'AWS Cost Explorer', 'AWS Trusted Advisor'],
        },
        monthly: { starter: 5, growth: 18, enterprise: 60 },
        section: 'Platform & Governance',
    },
];

const SECTIONS: Array<{ name: Capability['section']; blurb: string }> = [
    { name: 'Data & Pipeline', blurb: 'Ingest, move, and transform your data with reliable pipelines.' },
    { name: 'ML & Intelligence', blurb: 'Train, deploy, and serve models with enterprise-grade MLOps.' },
    { name: 'Platform & Governance', blurb: 'Secure, govern, and observe your platform at scale.' },
];

export default function ArchitectureVisualization(): React.JSX.Element {
    // State for hover highlighting
    const [hoveredColumn, setHoveredColumn] = React.useState<TierKey | null>(null);
    const [hoveredService, setHoveredService] = React.useState<{ label: string; tier: TierKey } | null>(null);

    // Helper to read CSS variables so charts and inline styles follow theme
    const getCssVar = (name: string, fallback: string) => {
        if (typeof document === 'undefined') return fallback;
        const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
        return v || fallback;
    };
    const themeVars = React.useMemo(() => ({
        text: 'var(--ifm-font-color-base)',
        link: 'var(--ifm-link-color)',
        border: 'var(--ifm-color-emphasis-300)',
        panelBg: 'var(--ifm-background-surface-color)',
        sectionBg: 'var(--ifm-background-surface-color)',
        cardBg: 'var(--ifm-background-surface-color)',
        titleAccentStart: 'var(--ifm-color-primary)',
        titleAccentEnd: 'var(--ifm-color-success)',
        successChipBg: 'rgba(34,197,94,.15)',
        successChipBorder: 'rgba(34,197,94,.35)',
        successChipText: 'var(--ifm-color-success)',
        tooltipBg: 'var(--ifm-background-surface-color)',
        tooltipBorder: 'var(--ifm-color-emphasis-300)',
    }), []);
    const fmtInt = React.useMemo(() => new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }), []);
    const toUSD = React.useCallback((n: number) => `$${fmtInt.format(Math.round(n))}`, [fmtInt]);
    const [tier, setTier] = React.useState<TierKey>('starter');
    const envForTier: Record<TierKey, 'dev' | 'staging' | 'prod'> = {
        starter: 'dev',
        growth: 'staging',
        enterprise: 'prod',
    };
    const TIER_KEYS: TierKey[] = ['starter', 'growth', 'enterprise'];

    type Discovery = {
        capabilities: Record<string, {
            cost_progression: Record<'dev' | 'staging' | 'prod', number>;
            active_services_by_env?: Record<'dev' | 'staging' | 'prod', string[]>;
            per_service_costs_by_env?: Record<'dev' | 'staging' | 'prod', Record<string, number>>;
        }>;
        cost_analysis?: Record<string, Record<'dev' | 'staging' | 'prod', number>>;
    } | null;

    const [discovery] = React.useState<Discovery>(staticDiscovery as Discovery);
    const [chartType, setChartType] = React.useState<'stacked' | 'line'>('stacked');

    // Removed runtime fetch (data is static). If in future this needs to be dynamic,
    // reintroduce effect with SWR-style caching to avoid hydration flashes.

    // Totals computed from discovery (preferred) with static fallback
    const total = React.useMemo(() => {
        const env = envForTier[tier];
        if (discovery?.cost_analysis) {
            const sum = Object.values(discovery.cost_analysis).reduce((acc, perEnv) => acc + (perEnv[env] || 0), 0);
            return Math.round(sum);
        }
        return CAPABILITIES.reduce((s, c) => s + c.monthly[tier], 0);
    }, [tier, discovery]);

    const totalsByTier = React.useMemo(() => {
        if (discovery?.cost_analysis) {
            const envs: Array<'dev' | 'staging' | 'prod'> = ['dev', 'staging', 'prod'];
            const totals = envs.map(env => Object.values(discovery.cost_analysis!).reduce((acc, perEnv) => acc + (perEnv[env] || 0), 0));
            return { starter: Math.round(totals[0]), growth: Math.round(totals[1]), enterprise: Math.round(totals[2]) };
        }
        const sum = (t: TierKey) => CAPABILITIES.reduce((s, c) => s + c.monthly[t], 0);
        return { starter: sum('starter'), growth: sum('growth'), enterprise: sum('enterprise') };
    }, [discovery]);
    const ICONS: Record<string, string> = {
        'Amazon S3': '/aws-icons/Arch_Amazon-Simple-Storage-Service_48.svg',
        'Amazon EventBridge': '/aws-icons/Arch_Amazon-EventBridge_48.svg',
        'AWS Lambda': '/aws-icons/Arch_AWS-Lambda_48.svg',
        'AWS Glue': '/aws-icons/Arch_AWS-Glue_48.svg',
        'AWS Step Functions': '/aws-icons/Arch_AWS-Step-Functions_48.svg',
        'AWS Lake Formation': '/aws-icons/Arch_AWS-Lake-Formation_48.svg',
        'Amazon SageMaker': '/aws-icons/Arch_Amazon-SageMaker_48.svg',
        'Amazon API Gateway': '/aws-icons/Arch_Amazon-API-Gateway_48.svg',
        'Amazon CloudWatch': '/aws-icons/Arch_Amazon-CloudWatch_48.svg',
        'Amazon OpenSearch Service': '/aws-icons/Arch_Amazon-OpenSearch-Service_48.svg',
        'AWS IAM': '/aws-icons/Arch_AWS-Identity-and-Access-Management_48.svg',
        'Amazon GuardDuty': '/aws-icons/Arch_Amazon-GuardDuty_48.svg',
        'AWS Config': '/aws-icons/Arch_AWS-Config_48.svg',
        'AWS Glue Data Quality': '/aws-icons/Res_AWS-Glue_Data-Quality_48.svg',
        'AWS Glue DataBrew': '/aws-icons/Arch_AWS-Glue-DataBrew_48.svg',
        'AWS CloudTrail': '/aws-icons/Arch_AWS-CloudTrail_48.svg',
        'AWS Cost Explorer': '/aws-icons/Arch_AWS-Cost-Explorer_48.svg',
        'AWS Budgets': '/aws-icons/Arch_AWS-Budgets_48.svg',
        'AWS Trusted Advisor': '/aws-icons/Res_AWS-Trusted-Advisor_Checklist-Cost_48.svg',
        'Amazon MSK': '/aws-icons/Arch_Amazon-Managed-Streaming-for-Apache-Kafka_48.svg',
        'AWS WAF': '/aws-icons/Arch_AWS-WAF_48.svg',
        'AWS Security Hub': '/aws-icons/Arch_AWS-Security-Hub_48.svg',
        'AWS Secrets Manager': '/aws-icons/Arch_AWS-Secrets-Manager_48.svg',
        'Amazon VPC': '/aws-icons/Res_Amazon-VPC_Virtual-private-cloud-VPC_48.svg',
        // Airbyte is not an AWS service; use the custom Airbyte icon
        'Airbyte (ECS)': '/aws-icons/airbyte.png',
    };

    const SERVICE_LABELS: Record<string, string> = {
        eventbridge: 'Amazon EventBridge',
        msk: 'Amazon MSK',
        opensearch: 'Amazon OpenSearch Service',
        sagemaker: 'Amazon SageMaker',
        glue: 'AWS Glue',
        stepfunctions: 'AWS Step Functions',
        lambda: 'AWS Lambda',
        s3: 'Amazon S3',
        lakeformation: 'AWS Lake Formation',
        iam: 'AWS IAM',
        security: 'AWS Security Hub',
        secrets_manager: 'AWS Secrets Manager',
        budget: 'AWS Budgets',
        compliance: 'AWS Config',
        controltower: 'AWS Control Tower',
        airbyte: 'Airbyte (ECS)',
        attack_simulation: 'Attack Simulation',
        cloud_native_hardening: 'Cloud Native Hardening',
        dataquality: 'Data Quality',
        networking: 'Amazon VPC',
    };

    const SERVICE_LINKS: Record<string, string> = {
        'Amazon EventBridge': 'https://aws.amazon.com/eventbridge/',
        'Amazon MSK': 'https://aws.amazon.com/msk/',
        'Amazon OpenSearch Service': 'https://aws.amazon.com/opensearch-service/',
        'Amazon SageMaker': 'https://aws.amazon.com/sagemaker/',
        'AWS Glue': 'https://aws.amazon.com/glue/',
        'AWS Step Functions': 'https://aws.amazon.com/step-functions/',
        'AWS Lambda': 'https://aws.amazon.com/lambda/',
        'Amazon S3': 'https://aws.amazon.com/s3/',
        'AWS Lake Formation': 'https://aws.amazon.com/lake-formation/',
        'AWS IAM': 'https://aws.amazon.com/iam/',
        'AWS Security Hub': 'https://aws.amazon.com/security-hub/',
        'AWS Secrets Manager': 'https://aws.amazon.com/secrets-manager/',
        'AWS Budgets': 'https://aws.amazon.com/aws-cost-management/aws-budgets/',
        'AWS Cost Explorer': 'https://aws.amazon.com/aws-cost-management/aws-cost-explorer/',
        'AWS Trusted Advisor': 'https://aws.amazon.com/premiumsupport/technology/trusted-advisor/',
        'AWS CloudTrail': 'https://aws.amazon.com/cloudtrail/',
        'Amazon CloudWatch': 'https://aws.amazon.com/cloudwatch/',
        'AWS WAF': 'https://aws.amazon.com/waf/',
        'AWS Config': 'https://aws.amazon.com/config/',
        'Amazon API Gateway': 'https://aws.amazon.com/api-gateway/',
        'Amazon VPC': 'https://aws.amazon.com/vpc/',
        'Airbyte (ECS)': 'https://airbyte.com/',
        'Data Quality': 'https://docs.aws.amazon.com/glue/latest/dg/data-quality.html',
        'Cloud Native Hardening': 'https://aws.amazon.com/architecture/well-architected/',
        'Attack Simulation': 'https://aws.amazon.com/fis/',
        'AWS Control Tower': 'https://aws.amazon.com/controltower/',
    };

    const SERVICE_DESC: Record<string, string> = {
        'Amazon EventBridge': 'Decoupled event buses for ingest and orchestration across ShieldCraft pipelines.',
        'Amazon MSK': 'Managed Kafka for high-throughput, durable streaming of security telemetry.',
        'Amazon OpenSearch Service': 'Search and analytics for logs and detections; fast, schema-on-read queries.',
        'Amazon SageMaker': 'Training, endpoints, and MLOps for risk scoring and generative AI.',
        'AWS Glue': 'ETL jobs, crawlers, and data quality checks to shape the lake.',
        'AWS Step Functions': 'Resilient workflow orchestration with retries and compensations.',
        'AWS Lambda': 'Serverless glue code for triggers, transforms, and lightweight compute.',
        'Amazon S3': 'Durable, encrypted data lake storage with lifecycle and tiers.',
        'AWS Lake Formation': 'Fine-grained access controls and governance for the lake.',
        'AWS IAM': 'Least-privilege identity and role boundaries across the platform.',
        'AWS Security Hub': 'Centralized security findings and continuous posture monitoring.',
        'AWS Secrets Manager': 'Managed secrets rotation for connectors and workloads.',
        'AWS Budgets': 'Cost guardrails and alerts mapped to project tags.',
        'AWS Cost Explorer': 'Spend analytics and trends for FinOps insights.',
        'AWS Trusted Advisor': 'Automated checks for cost, performance, and security.',
        'AWS CloudTrail': 'Immutable audit trails for governance and forensics.',
        'Amazon CloudWatch': 'Metrics and logs powering SLOs and alerts.',
        'AWS WAF': 'Layer-7 protections for APIs and web surfaces.',
        'AWS Config': 'Resource compliance and drift detection at scale.',
        'Amazon API Gateway': 'Secure API ingress for serving and control planes.',
        'Amazon VPC': 'Network isolation, subnets, and routing for data planes.',
        'Airbyte (ECS)': 'SaaS data connectors orchestrated on ECS for ingestion.',
        'Data Quality': 'Profiling and rules to keep the lake trustworthy.',
        'Cloud Native Hardening': 'Baseline guardrails and controls baked into the stack.',
        'Attack Simulation': 'Probes and chaos to validate defenses and runbooks.',
        'AWS Control Tower': 'Guardrails and blueprints for multi-account governance at scale.',
    };

    // Stacked per-service breakdown, aggregated across capabilities for each env
    const stackedServiceData = React.useMemo(() => {
        const envs: Array<'dev' | 'staging' | 'prod'> = ['dev', 'staging', 'prod'];
        const perEnv: Record<'dev' | 'staging' | 'prod', Record<string, number>> = { dev: {}, staging: {}, prod: {} };
        if (discovery?.capabilities) {
            for (const cap of Object.values(discovery.capabilities)) {
                for (const env of envs) {
                    const perSvc = cap.per_service_costs_by_env?.[env];
                    if (!perSvc) continue;
                    for (const [svcKey, val] of Object.entries(perSvc)) {
                        const label = SERVICE_LABELS[svcKey] || svcKey;
                        const v = typeof val === 'number' ? val : 0;
                        if (v > 0) perEnv[env][label] = (perEnv[env][label] || 0) + v;
                    }
                }
            }
        }
        const allLabels = Array.from(new Set<string>([
            ...Object.keys(perEnv.dev),
            ...Object.keys(perEnv.staging),
            ...Object.keys(perEnv.prod),
        ]));
        const ranked = allLabels.map(l => ({
            l,
            avg: ((perEnv.dev[l] || 0) + (perEnv.staging[l] || 0) + (perEnv.prod[l] || 0)) / 3,
        })).sort((a, b) => b.avg - a.avg);
        const TOP_N = 6;
        const top = ranked.slice(0, TOP_N).map(x => x.l);
        const datasets: Array<{ name: string; y: number[] }> = [];
        for (const svc of top) {
            datasets.push({ name: svc, y: [perEnv.dev[svc] || 0, perEnv.staging[svc] || 0, perEnv.prod[svc] || 0] });
        }
        if (ranked.length > TOP_N) {
            const totals = {
                dev: Object.values(perEnv.dev).reduce((s, v) => s + v, 0),
                staging: Object.values(perEnv.staging).reduce((s, v) => s + v, 0),
                prod: Object.values(perEnv.prod).reduce((s, v) => s + v, 0),
            };
            const otherY = [
                Math.max(0, totals.dev - top.reduce((s, l) => s + (perEnv.dev[l] || 0), 0)),
                Math.max(0, totals.staging - top.reduce((s, l) => s + (perEnv.staging[l] || 0), 0)),
                Math.max(0, totals.prod - top.reduce((s, l) => s + (perEnv.prod[l] || 0), 0)),
            ];
            if (otherY.some(v => v > 0)) datasets.push({ name: 'Other', y: otherY });
        }
        return { datasets };
    }, [discovery]);

    const ServiceRow: React.FC<{ label: string; iconSrc?: string; priceUsdPerMonth?: number; tier: TierKey }>
        = ({ label, iconSrc, priceUsdPerMonth, tier }) => {
            const [imgOk, setImgOk] = React.useState(true);
            const isServiceHovered = hoveredService?.label === label && hoveredService?.tier === tier;
            // Only dim if another service in ANY tier is hovered (not this one)
            const isOtherServiceHovered = hoveredService !== null && !(hoveredService.label === label && hoveredService.tier === tier);
            const link = SERVICE_LINKS[label];
            const desc = SERVICE_DESC[label];
            // Inline brief (succinct) shown in row; fall back to desc
            const brief = desc;
            const initials = React.useMemo(() => {
                const cleaned = label.replace(/\(.*?\)/g, '').trim();
                const words = cleaned.split(/\s+/).filter(Boolean);
                const letters = words.slice(0, 2).map(w => w[0]?.toUpperCase() ?? '').join('');
                return letters || 'SC';
            }, [label]);
            const RowTag: any = link ? 'a' : 'div';

            const handleMouseEnter = () => {
                setHoveredService({ label, tier });
                // Also ensure the column knows it's hovered
                setHoveredColumn(tier);
            };

            const handleMouseLeave = () => {
                // Only clear if this specific service is the one being tracked
                if (hoveredService?.label === label && hoveredService?.tier === tier) {
                    setHoveredService(null);
                }
            };

            return (
                <RowTag
                    className="svc-row"
                    href={link || undefined}
                    target={link ? '_blank' : undefined}
                    rel={link ? 'noopener noreferrer' : undefined}
                    aria-label={link ? `${label} – open AWS page` : label}
                    onMouseEnter={handleMouseEnter}
                    onMouseLeave={handleMouseLeave}
                    style={{
                        position: 'relative',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 16,
                        padding: 14,
                        borderRadius: 12,
                        textDecoration: 'none',
                        color: 'inherit',
                        cursor: link ? 'pointer' : 'default',
                        border: '1px solid transparent',
                        opacity: isOtherServiceHovered ? 0.4 : 1,
                        transition: 'all 0.2s ease'
                    }}
                >
                    <div style={{ flex: '0 0 auto' }}>
                        {iconSrc && imgOk ? (
                            <img
                                src={iconSrc}
                                alt={label}
                                onError={() => setImgOk(false)}
                                style={{ width: 36, height: 36, objectFit: 'contain', verticalAlign: 'middle' }}
                            />
                        ) : (
                            <span title={label} style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 36, height: 36, borderRadius: '9999px', border: `1px solid ${themeVars.border}`, background: 'linear-gradient(135deg, var(--ifm-color-primary), var(--ifm-color-success))', color: '#fff', fontWeight: 800, fontSize: '.85rem', letterSpacing: .3 }}>
                                {initials}
                            </span>
                        )}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 600, lineHeight: 1.2, fontSize: '.98rem' }}>{label}</div>
                        {brief && (
                            <div style={{ fontSize: '.9rem', opacity: .9, lineHeight: 1.4, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' }}>
                                {brief}
                            </div>
                        )}
                    </div>
                    <div style={{ flex: '0 0 auto', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 10, minWidth: 128 }}>
                        {typeof priceUsdPerMonth === 'number' && priceUsdPerMonth > 0 && (
                            <span className="price-chip" title="Approximate monthly cost" style={{
                                display: 'inline-block',
                                background: 'transparent',
                                border: `1px solid ${getCssVar('--ifm-color-emphasis-200', 'rgba(0,0,0,.08)')}`,
                                color: 'inherit',
                                fontWeight: 600,
                                padding: '6px 10px',
                                borderRadius: 9999,
                                fontSize: '.86rem',
                                opacity: .95,
                                lineHeight: 1.1,
                                whiteSpace: 'nowrap'
                            }}>
                                {toUSD(priceUsdPerMonth)}
                            </span>
                        )}
                    </div>
                </RowTag>
            );
        };

    const TierColumn: React.FC<{ t: TierKey }> = ({ t }) => {
        const env = envForTier[t];
        const isColumnHovered = hoveredColumn === t;
        const isOtherColumnHovered = hoveredColumn !== null && hoveredColumn !== t;
        const capKeyMap: Record<string, string> = {
            ingestion: 'ingestion',
            processing: 'processing',
            lake: 'storage',
            ml: 'ml',
            orchestration: 'orchestration',
            security: 'security',
            governance: 'governance',
            observability: 'observability',
        };
        const reverseMap: Record<string, string> = Object.entries(SERVICE_LABELS)
            .reduce((acc, [key, val]) => { acc[val] = key; return acc; }, {} as Record<string, string>);
        // Total for this tier
        const tierTotal = React.useMemo(() => {
            if (discovery?.cost_analysis) {
                const sum = Object.values(discovery.cost_analysis).reduce((acc, perEnv) => acc + (perEnv[env] || 0), 0);
                return Math.round(sum);
            }
            const sum = (t0: TierKey) => CAPABILITIES.reduce((s, c) => s + c.monthly[t0], 0);
            return sum(t);
        }, [discovery, env, t]);

        // Aggregate all services used in this tier/env across capabilities
        const entries = React.useMemo(() => {
            const set = new Set<string>();
            if (discovery?.capabilities) {
                for (const cap of Object.values(discovery.capabilities)) {
                    const svcs = cap.active_services_by_env?.[env] ?? [];
                    svcs.forEach(k => set.add(SERVICE_LABELS[k] || k));
                }
            }
            // Fallback to static mapping if discovery isn't present or empty
            if (set.size === 0) {
                CAPABILITIES.forEach(c => (c.awsByTier?.[t] ?? c.aws ?? []).forEach(lbl => set.add(lbl)));
            }
            // For the most expensive tier (Enterprise), include all not-enabled Proton services as part of the main list
            if (t === 'enterprise') {
                NOT_ENABLED_KEYS.forEach(k => set.add(SERVICE_LABELS[k] || k));
            }
            const labels = Array.from(set).sort((a, b) => a.localeCompare(b));
            return labels.map(label => {
                const key = reverseMap[label];
                // Prefer detailed per-service costs aggregated across capabilities
                let priceSum = 0;
                if (key && discovery?.capabilities) {
                    for (const cap of Object.values(discovery.capabilities)) {
                        const perSvc = cap.per_service_costs_by_env?.[env];
                        if (perSvc && typeof perSvc[key] === 'number') {
                            priceSum += perSvc[key];
                        }
                    }
                }
                const price = priceSum > 0 ? priceSum : undefined;
                return { label, price } as { label: string; price?: number };
            });
        }, [discovery, env, t]);

        // Compute add-ons for this tier with env-aware pricing
        const addOns = React.useMemo(() => {
            return NOT_ENABLED_KEYS.map(k => {
                const label = SERVICE_LABELS[k] || k;
                const costs = costForServiceByTier(k);
                const price = costs[t];
                return { key: k, label, price };
            });
        }, [t, costForServiceByTier]);

        return (
            <div
                className="tier-card"
                onMouseEnter={() => {
                    setHoveredColumn(t);
                    // Clear any stale service hover when entering a new column
                    if (hoveredService && hoveredService.tier !== t) {
                        setHoveredService(null);
                    }
                }}
                onMouseLeave={() => {
                    setHoveredColumn(null);
                    // Clear service hover when leaving the column entirely
                    setHoveredService(null);
                }}
                style={{
                    display: 'flex', flexDirection: 'column', gap: 16,
                    border: `1px solid ${themeVars.border}`,
                    borderRadius: 16,
                    padding: 18,
                    boxShadow: isColumnHovered ? '0 20px 50px rgba(34, 211, 238, 0.25)' : '0 18px 40px rgba(0,0,0,.07)',
                    opacity: isOtherColumnHovered ? 0.5 : 1,
                    transition: 'all 0.2s ease'
                }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', paddingBottom: 8, borderBottom: `1px solid ${getCssVar('--ifm-color-emphasis-200', 'rgba(0,0,0,.08)')}` }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        <div style={{ fontWeight: 800, fontSize: '1.12rem', letterSpacing: '.1px' }}>{TIERS[t].label}</div>
                        <div style={{ fontSize: '.86rem', opacity: .8 }}>{TIERS[t].tagline}</div>
                    </div>
                    <div style={{ fontWeight: 800, fontSize: '1.02rem' }}>
                        <span className="price-chip" style={{
                            display: 'inline-block',
                            padding: '6px 12px',
                            borderRadius: 9999,
                            border: `1px solid ${getCssVar('--ifm-color-emphasis-200', 'rgba(0,0,0,.08)')}`,
                            background: 'transparent',
                            minWidth: 96,
                            textAlign: 'center',
                            whiteSpace: 'nowrap'
                        }}>{toUSD(tierTotal)}</span>
                    </div>
                </div>
                <div className="svc-list" style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                    {entries.map(({ label, price }) => (
                        <ServiceRow key={`${t}-svc-${label}`} label={label} iconSrc={ICONS[label]} priceUsdPerMonth={typeof price === 'number' ? price : undefined} tier={t} />
                    ))}
                </div>

                {/* Available add-ons (not enabled yet) - hidden for Enterprise since all services are included */}
                {t !== 'enterprise' && (
                    <div style={{ marginTop: 14, paddingTop: 10, borderTop: `1px solid ${getCssVar('--ifm-color-emphasis-200', 'rgba(0,0,0,.08)')}` }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                            <div style={{ fontWeight: 700, fontSize: '.92rem', opacity: .9 }}>Available add‑ons</div>
                            <span style={{ border: `1px solid ${getCssVar('--ifm-color-emphasis-200', 'rgba(0,0,0,.08)')}`, borderRadius: 9999, padding: '2px 8px', fontSize: '.75rem', opacity: .85 }}>Not enabled</span>
                        </div>
                        <div className="svc-list" style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                            {addOns.map(({ key, label, price }) => (
                                <ServiceRow key={`addon-${t}-${key}`} label={label} iconSrc={ICONS[label]} priceUsdPerMonth={price > 0 ? price : undefined} tier={t} />
                            ))}
                        </div>
                    </div>
                )}
            </div>
        );
    };

    // Optional icon mapping for Control Tower; falls back to monogram if missing in assets
    ICONS['AWS Control Tower'] = ICONS['AWS Control Tower'] || '/aws-icons/Arch_AWS-Control-Tower_48.svg';

    // Compute per-tier costs for a given service key across all capabilities
    const costForServiceByTier = React.useCallback((svcKey: string): { starter: number; growth: number; enterprise: number } => {
        const envs: Array<'dev' | 'staging' | 'prod'> = ['dev', 'staging', 'prod'];
        const sums = { dev: 0, staging: 0, prod: 0 } as Record<'dev' | 'staging' | 'prod', number>;
        if (discovery?.capabilities) {
            for (const cap of Object.values(discovery.capabilities)) {
                for (const env of envs) {
                    const perSvc = cap.per_service_costs_by_env?.[env];
                    if (perSvc && typeof perSvc[svcKey] === 'number') sums[env] += perSvc[svcKey] as number;
                }
            }
        }
        return { starter: Math.round(sums.dev), growth: Math.round(sums.staging), enterprise: Math.round(sums.prod) };
    }, [discovery]);

    // The six Proton templates available but not enabled in env YAMLs
    const NOT_ENABLED_KEYS = ['attack_simulation', 'budget', 'compliance', 'controltower', 'dataquality', 'secrets_manager'] as const;
    const notEnabledServices = React.useMemo(() => {
        return NOT_ENABLED_KEYS.map(k => {
            const label = SERVICE_LABELS[k] || k;
            const costs = costForServiceByTier(k);
            return { key: k, label, costs };
        });
    }, [costForServiceByTier]);

    // Removed old Card/grid layout and sectionCards to simplify structure

    return (
        <Layout>
            <div className={styles.architecturePageWrapper}>
                <div className={styles.architectureInner}>
                    <h1 className={styles.pageTitle}>ShieldCraft AI Architecture</h1>
                    <p className={styles.pageSubtitle}>Compare tiers to preview scope and monthly run-rate</p>

                    <div className={styles.tierGridWrap}>
                        <div className={styles.tierGrid}>
                            {TIER_KEYS.map(t => (
                                <TierColumn key={`col-${t}`} t={t} />
                            ))}
                        </div>
                    </div>

                    <div className={styles.chartCardWrap}>
                        <div className={styles.chartCard}>
                            <div className={styles.chartCardHeader}>
                                <div>
                                    <h3 className={styles.chartCardTitle}>Tier Cost Comparison</h3>
                                    <p className={styles.chartCardSubtitle}>{chartType === 'stacked' ? 'Breakdown by top services across Starter, Growth, and Enterprise.' : 'Top services per tier (line chart).'}</p>
                                </div>
                                <div className={styles.chartCardControls}>
                                    <label htmlFor="chartType" className={styles.selectLabel}>View:</label>
                                    <select id="chartType" value={chartType} onChange={(e) => setChartType(e.target.value as any)} className={styles.selectEl}>
                                        <option value="stacked">Stacked bars</option>
                                        <option value="line">Line</option>
                                    </select>
                                </div>
                            </div>
                            <div className={styles.chartCardBody}>
                                <BrowserOnly>
                                    {() => {
                                        const Plot = require('react-plotly.js').default;
                                        const theme = document.documentElement.getAttribute('data-theme');
                                        const isDark = theme === 'dark';
                                        const fontColor = getCssVar('--ifm-font-color-base', isDark ? '#e5e7eb' : '#111827');
                                        const gridColor = isDark ? 'rgba(148,163,184,.25)' : 'rgba(17,24,39,.12)';
                                        const tiers = ['Starter', 'Growth', 'Enterprise'] as const;
                                        const totalsMap: Record<typeof tiers[number], number> = {
                                            'Starter': totalsByTier.starter,
                                            'Growth': totalsByTier.growth,
                                            'Enterprise': totalsByTier.enterprise,
                                        };
                                        // Order tiers by total cost descending so bars/lines decrease left to right
                                        const ordered = tiers.map((label, idx) => ({ label, idx, total: totalsMap[label] }))
                                            .sort((a, b) => (b.total ?? 0) - (a.total ?? 0));
                                        const orderedLabels = ordered.map(o => o.label);
                                        const idxOrder = ordered.map(o => o.idx); // indices 0=dev,1=staging,2=prod
                                        const stacks = stackedServiceData.datasets || [];
                                        const hasStacks = stacks.length > 0;

                                        let data: any[] = [];
                                        if (chartType === 'line') {
                                            if (hasStacks) {
                                                // One line per top service across ordered tiers
                                                data = stacks.map((ds: any) => ({
                                                    type: 'scatter',
                                                    mode: 'lines+markers',
                                                    x: orderedLabels,
                                                    y: idxOrder.map(i => ds.y[i] || 0),
                                                    name: ds.name,
                                                    hovertemplate: `<b>%{x}</b><br>%{fullData.name}: $%{y:,.0f}<extra></extra>`
                                                }));
                                            } else {
                                                // Fallback: totals only if no per-service data available
                                                const totalsOrdered = ordered.map(o => totalsMap[o.label]);
                                                data = [{
                                                    type: 'scatter',
                                                    mode: 'lines+markers',
                                                    x: orderedLabels,
                                                    y: totalsOrdered,
                                                    name: 'Total',
                                                    hovertemplate: `<b>%{x}</b><br>Total: $%{y:,.0f}<extra></extra>`
                                                }];
                                            }
                                        } else if (hasStacks) {
                                            data = stacks.map((ds: any) => ({
                                                type: 'bar',
                                                x: orderedLabels,
                                                y: idxOrder.map(i => ds.y[i] || 0),
                                                name: ds.name,
                                                hovertemplate: `<b>%{x}</b><br>%{fullData.name}: $%{y:,.0f}<extra></extra>`
                                            }));
                                        } else {
                                            data = [{
                                                type: 'bar',
                                                x: orderedLabels,
                                                y: ordered.map(o => totalsMap[o.label]),
                                                name: 'Total',
                                                hovertemplate: `<b>%{x}</b><br>Total: $%{y:,.0f}<extra></extra>`
                                            }];
                                        }
                                        return (
                                            <Plot
                                                data={data}
                                                layout={{
                                                    paper_bgcolor: 'rgba(0,0,0,0)',
                                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                                    barmode: chartType === 'stacked' && hasStacks ? 'stack' : undefined,
                                                    margin: { t: 24, r: 12, b: 40, l: 56 },
                                                    xaxis: { tickfont: { color: fontColor } },
                                                    yaxis: { tickfont: { color: fontColor }, gridcolor: gridColor, tickprefix: '$' },
                                                    font: { color: fontColor },
                                                    height: 360,
                                                    showlegend: chartType === 'stacked' && hasStacks,
                                                    legend: chartType === 'stacked' && hasStacks ? { orientation: 'h', y: -0.2 } : undefined,
                                                }}
                                                config={{ displayModeBar: false, responsive: true }}
                                                style={{ width: '100%', height: '100%' }}
                                            />
                                        );
                                    }}
                                </BrowserOnly>
                            </div>
                        </div>
                    </div>

                    <div className={styles.deployGridWrap}>
                        <div className={styles.deployGrid}>
                            <div className="tier-card">
                                <div className={styles.deployCardHeader}><h3>Deploy to Your AWS</h3></div>
                                <p className={styles.deployBody}>Seamlessly integrate ShieldCraft into your existing AWS org and accounts—no data leaves your boundary. We work with your tags, IAM, and guardrails for a non‑disruptive rollout across regions and accounts.</p>
                                <ul className={styles.deployList}>
                                    <li>Multi‑account, multi‑region ready</li>
                                    <li>Least‑privilege IAM and encrypted-by-default</li>
                                    <li>Control Tower/Organizations compatible</li>
                                </ul>
                            </div>
                            <div className="tier-card">
                                <div className={styles.deployCardHeader}><h3>On‑Premises / Air‑Gapped</h3></div>
                                <p className={styles.deployBody}>Bring ShieldCraft to where your data lives. Deploy on Kubernetes or VMware with S3‑compatible storage and Kafka/OpenSearch equivalents. Hardened images and offline updates included.</p>
                                <ul className={styles.deployList}>
                                    <li>Kubernetes or VMware deployment</li>
                                    <li>S3‑compatible and on‑prem Kafka support</li>
                                    <li>Offline updates for disconnected sites</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
}
