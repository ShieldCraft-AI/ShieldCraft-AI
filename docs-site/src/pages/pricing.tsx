import Layout from '@theme/Layout';
import React from 'react';
import styles from './pricing.module.css';
const staticDiscovery = require('../../static/data/architecture_discovery.json');

type TierKey = 'starter' | 'growth' | 'enterprise';

type Capability = {
    id: string;
    label: string;
    summary: string;
    monthly: Record<TierKey, number>;
    aws: string[];
    awsByTier?: Partial<Record<TierKey, string[]>>;
};

type HoveredService = {
    label: string;
    tier: TierKey;
};

type InfraGroup = {
    title: string;
    services: string[];
    description?: string;
};

type Subnet = {
    name: string;
    type: 'public' | 'private' | 'isolated' | 'edge' | 'transit';
    cidr?: string;
    notes?: string;
    workloads?: InfraGroup[];
};

type InfraAZ = {
    name: string;
    summary: string;
    groups: InfraGroup[];
    subnets?: Subnet[];
};

type InfraBlueprint = {
    region: string;
    regionWide: InfraGroup[];
    azs: InfraAZ[];
    perimeter?: InfraGroup[];
    failover?: FailoverPlan;
};

type FailoverPlan = {
    title: string;
    description: string;
    services: string[];
    azPath: string[];
    cadence?: string;
};

type DeploymentPoint = {
    heading: string;
    detail: string;
};

type DeploymentOption = {
    key: string;
    label: string;
    badge?: string;
    description: string;
    points: DeploymentPoint[];
    services?: string[];
    icon: string;
    meta?: string;
};

type TierMeta = {
    label: string;
    tagline: string;
};

type TierOverview = {
    badge: string;
};

const TIERS: Record<TierKey, TierMeta> = {
    starter: {
        label: 'Starter',
        tagline: 'Launch GuardDuty-backed telemetry, ingestion, and curated storage.',
    },
    growth: {
        label: 'Growth',
        tagline: 'Scale data plane, ML ops, and cross-account automations.',
    },
    enterprise: {
        label: 'Enterprise',
        tagline: 'Operate with global guardrails, auto-scaling compute, and proactive defenses.',
    },
};

const displayServiceName = (label: string) => label.replace(/^(AWS|Amazon)\s+/, '').trim();

const TIER_OVERVIEW: Record<TierKey, TierOverview> = {
    starter: {
        badge: 'Fastest time-to-value',
    },
    growth: {
        badge: 'Scale telemetry & automation',
    },
    enterprise: {
        badge: 'Global resilience & compliance',
    },
};

const CAPABILITIES: Capability[] = [
    {
        id: 'ingest',
        label: 'Signals ingestion & harmonisation',
        summary: 'Normalize SaaS, endpoint, and network telemetry with managed schemas while Step Functions throttle inference fan-out for cost-aware latency.',
        monthly: { starter: 4200, growth: 7300, enterprise: 11200 },
        aws: ['Amazon EventBridge', 'AWS Lambda', 'AWS Step Functions', 'Amazon S3'],
        awsByTier: {
            starter: ['Amazon EventBridge', 'AWS Lambda', 'AWS Step Functions', 'Amazon S3'],
            growth: ['Amazon EventBridge', 'AWS Lambda', 'AWS Step Functions', 'Amazon S3'],
            enterprise: ['Amazon EventBridge', 'AWS Lambda', 'AWS Step Functions', 'Amazon MSK', 'Amazon S3'],
        },
    },
    {
        id: 'mlops',
        label: 'Model operations & orchestration',
        summary: 'Train, evaluate, and promote detections across environments with approvals.',
        monthly: { starter: 3100, growth: 5200, enterprise: 8800 },
        aws: ['Amazon SageMaker', 'AWS Step Functions', 'AWS Glue'],
        awsByTier: {
            starter: ['Amazon SageMaker'],
            growth: ['Amazon SageMaker', 'AWS Step Functions'],
            enterprise: ['Amazon SageMaker', 'AWS Step Functions', 'AWS Glue'],
        },
    },
    {
        id: 'governance',
        label: 'Security governance & guardrails',
        summary: 'Enforce compliance, identity federation, and detective controls with Identity Center, Security Hub, Config, and Detective.',
        monthly: { starter: 1800, growth: 2400, enterprise: 3600 },
        aws: ['AWS IAM', 'AWS IAM Identity Center', 'AWS Config', 'AWS Security Hub', 'Amazon GuardDuty', 'Amazon Detective'],
        awsByTier: {
            starter: ['AWS IAM', 'Amazon GuardDuty'],
            growth: ['AWS IAM', 'Amazon GuardDuty', 'AWS IAM Identity Center', 'AWS Config', 'AWS Security Hub'],
            enterprise: ['AWS IAM', 'Amazon GuardDuty', 'AWS IAM Identity Center', 'AWS Config', 'AWS Security Hub', 'AWS CloudTrail', 'Amazon Detective', 'Amazon Inspector', 'AWS Artifact', 'AWS CodePipeline'],
        },
    },
    {
        id: 'finops',
        label: 'FinOps & resilience',
        summary: 'Guard spend, automate immutable backups, and validate recovery objectives while hardening ingress for burst workloads.',
        monthly: { starter: 1200, growth: 1950, enterprise: 4200 },
        aws: ['AWS Budgets', 'AWS Cost Explorer', 'AWS Backup', 'AWS Resilience Hub', 'AWS WAF', 'AWS Shield Advanced'],
        awsByTier: {
            starter: ['AWS Budgets', 'AWS Backup'],
            growth: ['AWS Budgets', 'AWS Cost Explorer', 'AWS Backup'],
            enterprise: ['AWS Budgets', 'AWS Cost Explorer', 'AWS Backup', 'AWS Resilience Hub', 'AWS WAF', 'AWS Shield Advanced'],
        },
    },
];

const INFRA_BLUEPRINT: Record<TierKey, InfraBlueprint> = {
    starter: {
        region: 'Primary AWS Region',
        regionWide: [
            {
                title: 'Data Lake & Governance',
                services: ['Amazon S3', 'AWS Lake Formation', 'AWS Glue'],
                description: 'Tiered S3 zones with Lake Formation enforcement and Glue catalog automation keep telemetry governable from the first workload.',
            },
            {
                title: 'Network Fabric & Endpoints',
                services: ['Amazon VPC', 'Amazon S3 Gateway Endpoint'],
                description: 'Dual-AZ VPC, flow logging, and S3 gateway endpoints retain ingest traffic on the AWS backbone while enforcing deterministic egress paths.',
            },
            {
                title: 'Central Observability',
                services: ['Amazon CloudWatch'],
                description: 'Unified metrics, logs, and alarms fuel platform runbooks and highlight latency drifts across the blueprint.',
            },
            {
                title: 'Ingestion workflow orchestration',
                services: ['AWS Step Functions', 'Amazon EventBridge', 'AWS Lambda'],
                description: 'Step Functions state machines micro-batch telemetry enrichment and pace inference hand-offs so GPUs stay warm only when needed while latency stays predictable.',
            },
        ],
        azs: [
            {
                name: 'Availability Zone A',
                summary: 'Edge routing, ingestion, and orchestration (public + private subnets).',
                subnets: [
                    {
                        name: 'Public edge subnet',
                        type: 'public',
                        cidr: '10.0.0.0/24',
                        workloads: [
                            {
                                title: 'Edge routing & TLS termination',
                                services: ['Application Load Balancer (ALB)', 'AWS WAF'],
                                description: 'Public ALB terminates TLS, enforces managed WAF rules, and hands off vetted traffic into private integrations.',
                            },
                        ],
                    },
                    {
                        name: 'Private app subnet',
                        type: 'private',
                        cidr: '10.0.1.0/24',
                        workloads: [
                            {
                                title: 'Ingestion APIs & automation',
                                services: ['Amazon API Gateway', 'Amazon EventBridge', 'AWS Lambda', 'AWS Step Functions'],
                                description: 'API Gateway brokers authenticated intake while EventBridge, Step Functions, and Lambda orchestrate enrichment, buffering, and latency-aware inference triggers.',
                            },
                        ],
                    },
                ],
                groups: [],
            },
            {
                name: 'Availability Zone B',
                summary: 'Processing, hybrid compute, and ML workloads (private subnets).',
                subnets: [
                    {
                        name: 'Private data subnet',
                        type: 'private',
                        cidr: '10.0.2.0/24',
                        workloads: [
                            {
                                title: 'Data processing & quality',
                                services: ['AWS Glue'],
                                description: 'Glue crawlers and ETL pipelines refine raw telemetry into curated lake zones with built-in quality bars.',
                            },
                            {
                                title: 'Burst compute workers',
                                services: ['Amazon EC2', 'Amazon EC2 Auto Scaling'],
                                description: 'Auto Scaling EC2 fleet handles stateful connectors and batch inference bursts without starving ingest pathways.',
                            },
                        ],
                    },
                    {
                        name: 'Isolated ML subnet',
                        type: 'isolated',
                        cidr: '10.0.3.0/24',
                        workloads: [
                            {
                                title: 'Model training & ops',
                                services: ['Amazon SageMaker'],
                                description: 'Notebook, training, and inference resources run in isolation with VPC-only endpoints and encrypted artifacts.',
                            },
                        ],
                    },
                ],
                groups: [],
            },
            {
                name: 'Availability Zone C',
                summary: 'Analytics, observability, and warm standby orchestration.',
                subnets: [
                    {
                        name: 'Private analytics subnet',
                        type: 'private',
                        cidr: '10.0.4.0/24',
                        workloads: [
                            {
                                title: 'Analytics & search',
                                services: ['Amazon OpenSearch Service', 'Amazon CloudWatch'],
                                description: 'OpenSearch dashboards, curated log stores, and CloudWatch telemetry sit away from ingest paths for steady investigations.',
                            },
                        ],
                    },
                    {
                        name: 'Isolated standby subnet',
                        type: 'isolated',
                        cidr: '10.0.5.0/24',
                        workloads: [
                            {
                                title: 'Standby orchestration',
                                services: ['AWS Step Functions', 'AWS Lambda'],
                                description: 'Pre-provisioned runbooks and chaos drills sit isolated to orchestrate regional failover during exercises or incidents.',
                            },
                        ],
                    },
                ],
                groups: [],
            },
        ],
        perimeter: [
            {
                title: 'Identity & security guardrails',
                services: ['AWS IAM', 'AWS IAM Identity Center', 'Amazon GuardDuty', 'AWS Config', 'AWS CloudTrail'],
                description: 'IAM boundaries, Identity Center federation, GuardDuty findings, Config conformance packs, and CloudTrail trails are enforced globally before any regional workload deploys.',
            },
            {
                title: 'Financial governance & backups',
                services: ['AWS Budgets', 'AWS Backup'],
                description: 'Environment-level budgets, proactive alerts, and automated AWS Backup plans notify platform teams when spend drifts while protecting critical telemetry stores.',
            },
            {
                title: 'Secrets & shared services',
                services: ['AWS Secrets Manager'],
                description: 'Centralised secrets rotation for connectors, webhook credentials, and infrastructure artefacts lives outside specific subnets.',
            },
            {
                title: 'Org extensions',
                services: ['AWS Organizations'],
                description: 'Organizations integration links accounts into existing landing zones and propagates service control policies and tagging standards.',
            },
        ],
        failover: {
            title: 'Automated AZ failover drills',
            description: 'CloudWatch alarms and Step Functions shift ingestion and automation workloads from AZ A into standby AZ C while Lambda warms connectors.',
            services: ['Amazon CloudWatch', 'AWS Step Functions', 'AWS Lambda'],
            azPath: ['Availability Zone A', 'Failover orchestration', 'Availability Zone C'],
            cadence: 'Monthly failover exercise with automated rollback validation.',
        },
    },
    growth: {
        region: 'Primary AWS Region',
        regionWide: [
            {
                title: 'Data Lake & Governance',
                services: ['Amazon S3', 'AWS Lake Formation', 'AWS Glue'],
                description: 'Curated S3 zones, Lake Formation governance, and Glue catalog automation converge to manage higher-volume telemetry without sacrificing control.',
            },
            {
                title: 'Search & Observability',
                services: ['Amazon OpenSearch Service', 'Amazon CloudWatch'],
                description: 'Regional OpenSearch domains and CloudWatch dashboards uplift investigations, SLO tracking, and alert routing across accounts.',
            },
            {
                title: 'Network & Endpoints',
                services: ['Amazon VPC', 'Amazon S3 Gateway Endpoint'],
                description: 'Multi-AZ VPC with gateway endpoints and shared services subnets keeps ingestion, analytics, and automation flows on the AWS backbone.',
            },
            {
                title: 'Ingestion → inference choreography',
                services: ['AWS Step Functions', 'Amazon EventBridge', 'AWS Lambda'],
                description: 'State machines batch and prioritise telemetry from EventBridge into inference shards, scaling concurrency by queue depth to shave p99 latency without overspending.',
            },
        ],
        azs: [
            {
                name: 'Availability Zone A',
                summary: 'Edge balancing, orchestration, and streaming.',
                subnets: [
                    {
                        name: 'Public ingress subnet',
                        type: 'public',
                        cidr: '10.1.0.0/24',
                        notes: 'ALB, AWS WAF, NAT gateway',
                        workloads: [
                            {
                                title: 'Edge routing & load balancing',
                                services: ['Application Load Balancer (ALB)', 'AWS WAF'],
                                description: 'ALB terminates TLS, enforces WAF protections, and meters multi-tenant intake before handing traffic to private services.',
                            },
                        ],
                    },
                    {
                        name: 'Private orchestration subnet',
                        type: 'private',
                        cidr: '10.1.1.0/24',
                        notes: 'API Gateway integrations, Lambda, Step Functions',
                        workloads: [
                            {
                                title: 'Event-driven control plane',
                                services: ['Amazon API Gateway', 'Amazon EventBridge', 'AWS Lambda', 'AWS Step Functions'],
                                description: 'API Gateway, EventBridge, Step Functions, and Lambda coordinate ingest fan-out, cooldown windows, and inference batching for balanced latency versus cost.',
                            },
                        ],
                    },
                ],
                groups: [],
            },
            {
                name: 'Availability Zone B',
                summary: 'Processing, ML, stateless compute, and analytics.',
                subnets: [
                    {
                        name: 'Private data subnet',
                        type: 'private',
                        cidr: '10.1.2.0/24',
                        notes: 'Glue ETL, catalog crawlers, quality checks',
                        workloads: [
                            {
                                title: 'Data processing & governance',
                                services: ['AWS Glue'],
                                description: 'Glue ETL, crawlers, and Lake Formation transactions hydrate curated zones and publish dimensional models.',
                            },
                        ],
                    },
                    {
                        name: 'Private compute subnet',
                        type: 'private',
                        cidr: '10.1.3.0/24',
                        notes: 'Auto Scaling workers, streaming enrichers',
                        workloads: [
                            {
                                title: 'Stateless compute tier',
                                services: ['Amazon EC2', 'Amazon EC2 Auto Scaling'],
                                description: 'Auto Scaling EC2 pools run streaming enrichers, near-real-time inference, and partner connectors inside private networking.',
                            },
                        ],
                    },
                    {
                        name: 'Isolated ML subnet',
                        type: 'isolated',
                        cidr: '10.1.4.0/24',
                        notes: 'SageMaker notebooks, training, endpoints',
                        workloads: [
                            {
                                title: 'Model operations',
                                services: ['Amazon SageMaker'],
                                description: 'Managed notebooks, training jobs, and inference endpoints scale out under isolation with private-only access.',
                            },
                        ],
                    },
                    {
                        name: 'Private analytics subnet',
                        type: 'private',
                        cidr: '10.1.5.0/24',
                        notes: 'OpenSearch dashboards and APIs',
                        workloads: [
                            {
                                title: 'Investigations & observability',
                                services: ['Amazon OpenSearch Service', 'Amazon CloudWatch'],
                                description: 'OpenSearch domains, Kibana dashboards, and CloudWatch metrics power analyst searches and platform observability.',
                            },
                        ],
                    },
                ],
                groups: [],
            },
        ],
        perimeter: [
            {
                title: 'Identity & posture guardrails',
                services: ['AWS IAM', 'AWS IAM Identity Center', 'AWS Security Hub', 'AWS Config', 'AWS CloudTrail', 'Amazon Detective'],
                description: 'IAM boundaries, Identity Center federation, Security Hub scoring, Config conformance packs, CloudTrail trails, and Detective investigations remain global so every workload inherits zero-trust guardrails.',
            },
            {
                title: 'Financial insights & protection',
                services: ['AWS Budgets', 'AWS Cost Explorer', 'AWS Backup'],
                description: 'Budgets and Cost Explorer views align to each environment while AWS Backup enforces immutable restore points for analytics and ingest datasets.',
            },
            {
                title: 'Regional shared services',
                services: ['AWS Secrets Manager'],
                description: 'Rotation-ready secrets for partner connectors, SaaS API keys, and shared pipelines stay centralized yet VPC-accessible.',
            },
            {
                title: 'Quality & compliance add-ons',
                services: ['Data Quality'],
                description: 'Optional Proton templates seed Glue Data Quality monitors and scorecards against crown-jewel tables.',
            },
            {
                title: 'Proactive security checks',
                services: ['Amazon Inspector', 'AWS Artifact'],
                description: 'Inspector agents, ECR scans, and Artifact audit bundles prep the org for customer questionnaires and compliance attestation.',
            },
        ],
        failover: {
            title: 'Coordinated multi-AZ failover',
            description: 'EventBridge routes alarms into Step Functions and Resilience Hub playbooks to drain traffic from AZ A, trigger AWS Backup restores if needed, and restart streaming plus analytics workers in AZ B within minutes.',
            services: ['Amazon CloudWatch', 'Amazon EventBridge', 'AWS Step Functions', 'AWS Lambda', 'AWS Resilience Hub', 'AWS Backup'],
            azPath: ['Availability Zone A', 'Event bus & runbooks', 'Availability Zone B'],
            cadence: 'Bi-weekly chaos drills validate streaming and analytics continuity.',
        },
    },
    enterprise: {
        region: 'Primary AWS Region',
        regionWide: [
            {
                title: 'Data Lake & Governance',
                services: ['Amazon S3', 'AWS Lake Formation', 'AWS Glue'],
                description: 'Production-grade S3 tiers, Lake Formation policies, and Glue pipelines orchestrate governed data products across regions.',
            },
            {
                title: 'Network Fabric',
                services: ['Amazon VPC', 'Amazon S3 Gateway Endpoint'],
                description: 'Multi-AZ VPC with centralized ingress, gateway endpoints, transit attachments, and shared services subnets connects hybrid estates securely.',
            },
            {
                title: 'Operational Resilience',
                services: ['Amazon CloudWatch', 'AWS Step Functions', 'AWS Resilience Hub'],
                description: 'Cross-region observability streams, Resilience Hub blueprints, and automation state machines keep runbooks reliable during audits and chaos testing.',
            },
            {
                title: 'Global ingestion orchestrator',
                services: ['AWS Step Functions', 'Amazon EventBridge', 'Amazon MSK'],
                description: 'Step Functions spans regions to pace MSK ingestion bursts into inference fleets, aligning concurrency windows with GPU scale-out to protect latency and cost envelopes.',
            },
        ],
        azs: [
            {
                name: 'Availability Zone A',
                summary: 'Global ingress, streaming, and automation with layered edge protection.',
                subnets: [
                    {
                        name: 'Public edge subnet',
                        type: 'public',
                        cidr: '10.2.0.0/24',
                        notes: 'ALB, Shield Advanced, WAF, NAT',
                        workloads: [
                            {
                                title: 'Global edge & threat protection',
                                services: ['Application Load Balancer (ALB)', 'Amazon API Gateway', 'AWS WAF', 'AWS Shield Advanced'],
                                description: 'Layered ingress with Shield Advanced telemetry, managed WAF rules, and custom auth protects traffic before it reaches private runtimes.',
                            },
                        ],
                    },
                    {
                        name: 'Private control subnet',
                        type: 'private',
                        cidr: '10.2.1.0/24',
                        workloads: [
                            {
                                title: 'Orchestration & event fabric',
                                services: ['Amazon MSK', 'Amazon EventBridge', 'AWS Step Functions', 'AWS Lambda'],
                                description: 'MSK, EventBridge, Step Functions, and Lambda compose long-running automations, approvals, and cross-account streaming while throttling inference spins so GPU time maps to real signal volume.',
                            },
                        ],
                    },
                ],
                groups: [],
            },
            {
                name: 'Availability Zone B',
                summary: 'Core data lake processing, Airbyte mesh, and production ML endpoints.',
                subnets: [
                    {
                        name: 'Private data subnet',
                        type: 'private',
                        cidr: '10.2.2.0/24',
                        notes: 'Glue ETL, Lake Formation transactions',
                        workloads: [
                            {
                                title: 'Data & feature engineering',
                                services: ['AWS Glue', 'AWS Lake Formation'],
                                description: 'Glue pipelines and Lake Formation transactions manage feature stores, curated zones, and compliance artefacts.',
                            },
                        ],
                    },
                    {
                        name: 'Private compute subnet',
                        type: 'private',
                        cidr: '10.2.3.0/24',
                        notes: 'EC2 Auto Scaling, Airbyte, MSK consumers',
                        workloads: [
                            {
                                title: 'Auto-scaling compute mesh',
                                services: ['Amazon EC2', 'Amazon EC2 Auto Scaling', 'Airbyte (ECS)'],
                                description: 'Horizontal EC2 and ECS fleets run Airbyte connectors, inference workers, and data-plane services with managed scaling.',
                            },
                        ],
                    },
                    {
                        name: 'Isolated ML subnet',
                        type: 'isolated',
                        cidr: '10.2.4.0/24',
                        notes: 'SageMaker endpoints and batch transforms',
                        workloads: [
                            {
                                title: 'Model ops',
                                services: ['Amazon SageMaker'],
                                description: 'Multi-model endpoints, shadow deployments, and pipelines execute within isolated, encrypted ML subnets.',
                            },
                        ],
                    },
                ],
                groups: [],
            },
            {
                name: 'Availability Zone C',
                summary: 'Observability, advanced analytics, and cyber range automation.',
                subnets: [
                    {
                        name: 'Private analytics subnet',
                        type: 'private',
                        cidr: '10.2.5.0/24',
                        notes: 'OpenSearch, CloudWatch metrics, dashboards',
                        workloads: [
                            {
                                title: 'Observability & search',
                                services: ['Amazon OpenSearch Service', 'Amazon CloudWatch'],
                                description: 'Unified telemetry, dashboards, and threat hunting search domains are hosted away from ingress to stay resilient.',
                            },
                        ],
                    },
                    {
                        name: 'Isolated cyber-range subnet',
                        type: 'isolated',
                        cidr: '10.2.6.0/24',
                        notes: 'Attack Simulation, chaos engineering lab',
                        workloads: [
                            {
                                title: 'Adversarial validation & DR drills',
                                services: ['Attack Simulation', 'AWS Step Functions'],
                                description: 'AWS FIS experiments and orchestrated disaster recovery drills validate coverage and keep playbooks fresh.',
                            },
                        ],
                    },
                    {
                        name: 'Transit automation subnet',
                        type: 'transit',
                        cidr: '10.2.7.0/28',
                        notes: 'Hub for cross-region failover runbooks',
                        workloads: [
                            {
                                title: 'Governance automation',
                                services: ['AWS Config', 'AWS Security Hub'],
                                description: 'Config conformance packs and Security Hub aggregation coordinate with transit routing to push governance signals globally.',
                            },
                        ],
                    },
                ],
                groups: [],
            },
        ],
        perimeter: [
            {
                title: 'Identity & security command plane',
                services: ['AWS IAM', 'AWS IAM Identity Center', 'AWS Security Hub', 'AWS Config', 'Amazon GuardDuty', 'Amazon Detective', 'AWS CloudTrail', 'AWS Trusted Advisor'],
                description: 'Global IAM federation, Identity Center workforce access, Security Hub aggregation, Config compliance packs, GuardDuty telemetry, Detective investigations, CloudTrail audit trails, and Trusted Advisor checks govern every environment.',
            },
            {
                title: 'Edge & cost resilience',
                services: ['AWS Budgets', 'AWS Cost Explorer', 'AWS WAF', 'AWS Shield Advanced', 'AWS Resilience Hub'],
                description: 'FinOps analytics combine with Resilience Hub runbooks plus managed WAF and Shield Advanced to enforce spend guardrails while hardening the enterprise perimeter.',
            },
            {
                title: 'Regional shared services',
                services: ['AWS Secrets Manager', 'Cloud Native Hardening'],
                description: 'Secrets Manager rotation and hardened baselines provide shared services that stay outside workload subnets yet remain VPC reachable.',
            },
            {
                title: 'Data protection & backups',
                services: ['AWS Backup'],
                description: 'AWS Backup orchestrates immutable, cross-account backup plans with vault locking to maintain compliance-heavy retention objectives.',
            },
            {
                title: 'Governance extensions',
                services: ['AWS Control Tower', 'AWS Organizations'],
                description: 'Proton pipelines tie into Control Tower and Organizations so guardrails, tagging, and account vending stay consistent across regions.',
            },
            {
                title: 'Continuous assurance & release',
                services: ['Amazon Inspector', 'AWS Artifact', 'AWS CodePipeline'],
                description: 'Inspector scans, Artifact audit bundles, and CodePipeline gating keep every infrastructure and ML release audit-ready.',
            },
        ],
        failover: {
            title: 'Self-healing multi-AZ mesh',
            description: 'Transit automation triggers Step Functions and Resilience Hub blueprints to reassign global ingress, restart MSK consumers, warm SageMaker endpoints, and invoke AWS Backup restores when any AZ degrades.',
            services: ['Amazon CloudWatch', 'AWS Step Functions', 'Amazon MSK', 'AWS Lambda', 'AWS Resilience Hub', 'AWS Backup'],
            azPath: ['Availability Zone A', 'Transit automation subnet', 'Availability Zone C'],
            cadence: 'Continuous game-day automation with cross-region handshakes.',
        },
    },
};

const DEPLOYMENT_OPTIONS: DeploymentOption[] = [
    {
        key: 'aws-managed',
        label: 'Deploy to Your AWS',
        badge: 'Landing zone native',
        description: 'Seamlessly integrate ShieldCraft into existing AWS accounts while data stays inside your boundary. We layer onto your tagging model, guardrails, and security controls for a non-disruptive rollout.',
        points: [
            {
                heading: 'Multi-account, multi-region ready',
                detail: 'Proton blueprints coordinate dev/staging/prod accounts in parallel with cross-region replication and audit-ready logging.',
            },
            {
                heading: 'Least-privilege & encrypted-by-default',
                detail: 'IAM boundaries, KMS policies, and automated drift detection keep the control plane secure without slowing shipping velocity.',
            },
            {
                heading: 'Control Tower & Organizations aligned',
                detail: 'Supports account factories, SCPs, and shared logging buckets so you inherit your existing landing zone baselines.',
            },
        ],
        services: ['AWS Control Tower', 'AWS Organizations', 'AWS IAM', 'Amazon EventBridge'],
        icon: '/aws-icons/Arch_AWS-Control-Tower_48.svg',
        meta: 'Launch window: 2–4 weeks including security and tagging workshops.',
    },
    {
        key: 'airgapped',
        label: 'On-Premises / Air-Gapped',
        badge: 'Disconnected ready',
        description: 'Bring ShieldCraft to where your data resides. Deploy on Kubernetes or VMware with S3-compatible storage and Kafka/OpenSearch equivalents, backed by hardened images and offline updates.',
        points: [
            {
                heading: 'Kubernetes or VMware footprint',
                detail: 'Validated Helm charts and OVA bundles fit into regulated DMZ or factory zones with limited egress.',
            },
            {
                heading: 'S3-compatible & Kafka integrations',
                detail: 'Adapters sync with MinIO, Ceph, or Confluent so pipelines run without rewriting ingestion flows.',
            },
            {
                heading: 'Offline update pipeline',
                detail: 'Signed update bundles, artifact mirrors, and hardware key support keep air-gapped estates current.',
            },
        ],
        services: ['Amazon S3', 'Amazon MSK', 'Amazon OpenSearch Service', 'AWS Lambda'],
        icon: '/aws-icons/Arch_Amazon-S3-on-Outposts_48.svg',
        meta: 'Delivery kit includes hardened container registry exports and detached CI/CD playbooks.',
    },
];

export default function PricingPage() {
    const blueprintSectionRef = React.useRef<HTMLDivElement | null>(null);
    const [infraTier, setInfraTier] = React.useState<TierKey>('starter');
    const [hoveredService, setHoveredService] = React.useState<HoveredService | null>(null);

    React.useEffect(() => {
        if (typeof document === 'undefined') return undefined;
        document.body.classList.add('pricing-page');
        document.body.classList.add('aurora-surface');
        return () => {
            document.body.classList.remove('pricing-page');
            document.body.classList.remove('aurora-surface');
        };
    }, []);

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

    const navigateToBlueprint = (targetTier: TierKey) => {
        setInfraTier(targetTier);
        if (typeof window !== 'undefined') {
            const scroll = () => blueprintSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            if (typeof window.requestAnimationFrame === 'function') {
                window.requestAnimationFrame(scroll);
            } else {
                scroll();
            }
        }
    };

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
        'AWS IAM Identity Center': '/aws-icons/Arch_AWS-IAM-Identity-Center_48.svg',
        'AWS Cost Explorer': '/aws-icons/Arch_AWS-Cost-Explorer_48.svg',
        'AWS Budgets': '/aws-icons/Arch_AWS-Budgets_48.svg',
        'AWS Trusted Advisor': '/aws-icons/Res_AWS-Trusted-Advisor_Checklist-Cost_48.svg',
        'Amazon MSK': '/aws-icons/Arch_Amazon-Managed-Streaming-for-Apache-Kafka_48.svg',
        'AWS WAF': '/aws-icons/Arch_AWS-WAF_48.svg',
        'AWS Security Hub': '/aws-icons/Arch_AWS-Security-Hub_48.svg',
        'AWS Secrets Manager': '/aws-icons/Arch_AWS-Secrets-Manager_48.svg',
        'AWS Control Tower': '/aws-icons/Arch_AWS-Control-Tower_48.svg',
        'AWS Shield Advanced': '/aws-icons/Arch_AWS-Shield-Advanced_48.svg',
        'Amazon VPC': '/aws-icons/Res_Amazon-VPC_Virtual-private-cloud-VPC_48.svg',
        'Airbyte (ECS)': '/aws-icons/airbyte.png',
        'Amazon Detective': '/aws-icons/Arch_Amazon-Detective_48.svg',
        'Amazon Inspector': '/aws-icons/Arch_Amazon-Inspector_48.png',
        'AWS Artifact': '/aws-icons/Arch_AWS-CodeArtifact_48.png',
        'AWS CodePipeline': '/aws-icons/Arch_AWS-CodePipeline_48.png',
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
        shield_advanced: 'AWS Shield Advanced',
        airbyte: 'Airbyte (ECS)',
        attack_simulation: 'Attack Simulation',
        cloud_native_hardening: 'Cloud Native Hardening',
        dataquality: 'Data Quality',
        networking: 'Amazon VPC',
        inspector: 'Amazon Inspector',
        artifact: 'AWS Artifact',
        codepipeline: 'AWS CodePipeline',
        iam_identity_center: 'AWS IAM Identity Center',
        detective: 'Amazon Detective',
        resilience_hub: 'AWS Resilience Hub',
        backup: 'AWS Backup',
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
        'AWS Shield Advanced': 'https://aws.amazon.com/shield/',
        'Airbyte (ECS)': 'https://airbyte.com/',
        'Data Quality': 'https://docs.aws.amazon.com/glue/latest/dg/data-quality.html',
        'Cloud Native Hardening': 'https://aws.amazon.com/architecture/well-architected/',
        'Attack Simulation': 'https://aws.amazon.com/fis/',
        'AWS Control Tower': 'https://aws.amazon.com/controltower/',
        'AWS Organizations': 'https://aws.amazon.com/organizations/',
        'Amazon Inspector': 'https://aws.amazon.com/inspector/',
        'AWS Artifact': 'https://aws.amazon.com/artifact/',
        'AWS CodePipeline': 'https://aws.amazon.com/codepipeline/',
        'AWS IAM Identity Center': 'https://aws.amazon.com/iam/identity-center/',
        'Amazon Detective': 'https://aws.amazon.com/detective/',
        'AWS Resilience Hub': 'https://aws.amazon.com/resilience-hub/',
        'AWS Backup': 'https://aws.amazon.com/backup/',
    };

    const SERVICE_DESC: Record<string, string> = {
        'Amazon EventBridge': 'ShieldCraft broadcasts normalized detections and lifecycle signals on EventBridge so ingest pipelines, automations, and analytics stay loosely coupled.',
        'Amazon MSK': 'ShieldCraft streams high-volume telemetry through MSK for durable replay, feature backfills, and cross-account consumers.',
        'Amazon OpenSearch Service': 'ShieldCraft indexes enriched findings and behavioral baselines in OpenSearch to power threat hunts, dashboards, and analyst search.',
        'Amazon SageMaker': 'ShieldCraft trains, evaluates, and serves detection plus generative models on SageMaker pipelines with managed endpoints.',
        'AWS Glue': 'ShieldCraft runs Glue jobs and crawlers to structure lake zones, publish the catalog, and hydrate feature stores from raw feeds.',
        'AWS Step Functions': 'ShieldCraft choreographs remediation, data, and ML pipelines as Step Functions state machines, micro-batching ingestion events to keep inference latency tight and costs predictable.',
        'AWS Lambda': 'ShieldCraft deploys Lambda workers for connectors, lightweight transforms, and near-real-time automations triggered from events or APIs.',
        'Amazon S3': 'ShieldCraft persists landing, curated, and feature data in S3 with versioning, encryption by default, and lifecycle tuning per tier.',
        'AWS Lake Formation': 'ShieldCraft applies Lake Formation grants to enforce persona-based access paths while keeping governance auditable.',
        'AWS IAM': 'ShieldCraft provisions scoped IAM roles, boundary policies, and federation hooks to maintain least-privilege workloads.',
        'Amazon GuardDuty': 'ShieldCraft ingests GuardDuty findings to enrich detections, prioritize response playbooks, and refresh risk scoring.',
        'AWS IAM Identity Center': 'ShieldCraft centralizes workforce access through Identity Center, mapping your IdP groups into least-privilege permission sets across accounts.',
        'AWS Security Hub': 'ShieldCraft consolidates posture checks and curated detections in Security Hub to drive scoring, suppression, and compliance evidence.',
        'AWS Config': 'ShieldCraft runs Config conformance packs and custom rules to spot drift, feeding governance dashboards and auto-remediation.',
        'Amazon Detective': 'ShieldCraft pivots GuardDuty findings and CloudTrail trails into Detective to accelerate graph-based investigations and root-cause analysis.',
        'AWS Glue Data Quality': 'ShieldCraft deploys Glue Data Quality rule sets on mission datasets so bad feeds are quarantined before downstream propagation.',
        'AWS Glue DataBrew': 'ShieldCraft analysts iterate cleansing recipes in DataBrew to triage anomalies and promote hardened quality rules.',
        'AWS CloudTrail': 'ShieldCraft archives CloudTrail events for forensics, correlates them with detections, and baselines privileged activity.',
        'Amazon CloudWatch': 'ShieldCraft centralizes metrics, logs, and alarms in CloudWatch to track SLOs and trigger automated escalations.',
        'AWS WAF': 'ShieldCraft shields public ingress with managed WAF rule sets tuned by telemetry and attack-simulation feedback loops.',
        'Amazon API Gateway': 'ShieldCraft serves secured APIs through API Gateway with custom authorizers, throttling, and request validation.',
        'Application Load Balancer (ALB)': 'ShieldCraft uses ALB to terminate TLS, enforce listener rules, and distribute traffic into API Gateway and VPC services.',
        'Amazon EC2': 'ShieldCraft runs stateful collectors, inference runners, and scaling jobs on EC2 instances inside isolated subnets.',
        'Amazon EC2 Auto Scaling': 'ShieldCraft pairs EC2 fleets with Auto Scaling policies to burst for ingest spikes while keeping runtime costs predictable.',
        'Amazon S3 Gateway Endpoint': 'ShieldCraft routes S3 access through gateway endpoints so data stays on the AWS backbone without traversing the internet.',
        'AWS Secrets Manager': 'ShieldCraft rotates connector credentials, inference keys, and shared secrets in Secrets Manager with full audit trails.',
        'AWS Budgets': 'ShieldCraft wires Budgets alerts into FinOps dashboards and runbooks to enforce per-tier spend guardrails.',
        'AWS Cost Explorer': 'ShieldCraft mines Cost Explorer analytics to surface anomalies, forecast spend, and recommend automated savings actions.',
        'AWS Trusted Advisor': 'ShieldCraft reviews Trusted Advisor insights to confirm resilience, security, and cost baselines before promotions.',
        'AWS Backup': 'ShieldCraft orchestrates immutable backups for crown-jewel datasets, enforcing retention policies aligned with your compliance posture.',
        'AWS Shield Advanced': 'ShieldCraft leans on Shield Advanced for managed DDoS detection, telemetry, and rapid escalation into the global SOC.',
        'Amazon VPC': 'ShieldCraft segments workloads inside dedicated VPCs with flow logging, egress controls, and transit routing for hybrid reach.',
        'Airbyte (ECS)': 'ShieldCraft runs Airbyte on ECS to sync SaaS, ticketing, and telemetry sources into the lake with containerized connectors.',
        'Data Quality': 'ShieldCraft’s Proton add-on seeds Glue Data Quality monitors and scorecards across high-value tables to keep pipelines trustworthy.',
        'Cloud Native Hardening': 'ShieldCraft applies hardened baselines and Well-Architected controls through reusable infrastructure modules.',
        'Attack Simulation': 'ShieldCraft executes AWS FIS-based attack simulations to validate coverage, runbooks, and blast-radius assumptions.',
        'AWS Control Tower': 'ShieldCraft integrates with Control Tower guardrails and account vending to align environments with enterprise landing zones.',
        'AWS Organizations': 'ShieldCraft hooks into Organizations for SCP guardrails, consolidated billing, and delegated administration workflows.',
        'AWS Resilience Hub': 'ShieldCraft models recovery objectives within Resilience Hub, continuously validating that automation meets RTO/RPO targets as architectures evolve.',
        'Amazon Inspector': 'ShieldCraft automates Inspector agent assessments and ECR/CWPP scans on every deployment cycle to surface drift or CVEs.',
        'AWS Artifact': 'ShieldCraft curates compliance evidence and AWS Artifact audit packages so GRC teams can respond to questionnaires instantly.',
        'AWS CodePipeline': 'ShieldCraft’s landing zone and model updates flow through CodePipeline with security gating, canary deploys, and manual approvals.',
    };

    const SERVICE_DESC_COMPACT: Record<string, string> = {
        'Amazon EventBridge': 'Broadcasts normalized detections to decoupled pipelines.',
        'Amazon MSK': 'Streams telemetry with durable replay and backpressure.',
        'Amazon OpenSearch Service': 'Indexes enriched findings for hunts and dashboards.',
        'Amazon SageMaker': 'Runs model training, evaluation, and managed endpoints.',
        'AWS Glue': 'Automates curation jobs and catalog hydration.',
        'AWS Step Functions': 'Orchestrates ingestion and remediation state machines.',
        'AWS Lambda': 'Executes connectors and automations on demand.',
        'Amazon S3': 'Stores landing, curated, and feature data securely.',
        'AWS Lake Formation': 'Enforces table-level governance with auditable grants.',
        'AWS IAM': 'Delivers least-privilege roles and boundaries.',
        'Amazon GuardDuty': 'Surfaces managed threat findings for enrichment.',
        'AWS IAM Identity Center': 'Centralizes workforce SSO and permission sets.',
        'AWS Security Hub': 'Aggregates posture controls and curated detections.',
        'AWS Config': 'Continuously evaluates resource drift and compliance.',
        'Amazon Detective': 'Graphs telemetry to accelerate root-cause analysis.',
        'AWS Glue Data Quality': 'Scores datasets with Glue Data Quality rules.',
        'AWS Glue DataBrew': 'Lets analysts refine data recipes visually.',
        'AWS CloudTrail': 'Captures API activity for forensics and audits.',
        'Amazon CloudWatch': 'Centralizes metrics, logs, and alerting.',
        'AWS WAF': 'Protects ingress with managed firewall rules.',
        'Amazon API Gateway': 'Secures external APIs with throttling and auth.',
        'Application Load Balancer (ALB)': 'Terminates TLS and routes traffic intelligently.',
        'Amazon EC2': 'Runs stateful collectors and batch inference jobs.',
        'Amazon EC2 Auto Scaling': 'Scales EC2 capacity for bursty workloads.',
        'Amazon S3 Gateway Endpoint': 'Keeps S3 access on the AWS backbone.',
        'AWS Secrets Manager': 'Rotates application and connector secrets automatically.',
        'AWS Budgets': 'Alerts on spend drift against guardrails.',
        'AWS Cost Explorer': 'Visualizes usage trends and cost anomalies.',
        'AWS Trusted Advisor': 'Flags resilience, cost, and security opportunities.',
        'AWS Backup': 'Delivers immutable backups with policy-driven retention.',
        'AWS Shield Advanced': 'Provides managed DDoS detection and response.',
        'Amazon VPC': 'Segments workloads with controlled ingress and egress.',
        'Airbyte (ECS)': 'Syncs SaaS sources via containerized connectors.',
        'Data Quality': 'Extends Glue quality monitors to mission datasets.',
        'Cloud Native Hardening': 'Bundles hardened baselines for AWS workloads.',
        'Attack Simulation': 'Exercises failure modes with AWS FIS campaigns.',
        'AWS Control Tower': 'Aligns accounts with enterprise guardrails and vending.',
        'AWS Organizations': 'Manages accounts, SCPs, and delegated admins.',
        'AWS Resilience Hub': 'Models and validates recovery objectives continuously.',
        'Amazon Inspector': 'Automates vulnerability scans across fleets.',
        'AWS Artifact': 'Delivers compliance evidence on demand.',
        'AWS CodePipeline': 'Automates deployments with gated promotion stages.',
    };

    const STATIC_SERVICE_COSTS: Record<string, { starter: number; growth: number; enterprise: number }> = {
        shield_advanced: { starter: 0, growth: 0, enterprise: 3000 },
        inspector: { starter: 0, growth: 120, enterprise: 260 },
        artifact: { starter: 0, growth: 25, enterprise: 60 },
        codepipeline: { starter: 0, growth: 45, enterprise: 110 },
        iam_identity_center: { starter: 180, growth: 0, enterprise: 0 },
        detective: { starter: 220, growth: 260, enterprise: 380 },
        backup: { starter: 140, growth: 220, enterprise: 420 },
        resilience_hub: { starter: 0, growth: 190, enterprise: 420 },
    };

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
        const costs = { starter: Math.round(sums.dev), growth: Math.round(sums.staging), enterprise: Math.round(sums.prod) };
        if (costs.starter === 0 && costs.growth === 0 && costs.enterprise === 0 && svcKey in STATIC_SERVICE_COSTS) {
            return STATIC_SERVICE_COSTS[svcKey];
        }
        return costs;
    }, [discovery]);

    const ADD_ON_SERVICE_KEYS = ['attack_simulation', 'budget', 'compliance', 'controltower', 'dataquality', 'secrets_manager', 'shield_advanced', 'inspector', 'artifact', 'codepipeline', 'iam_identity_center', 'detective'] as const;

    type AddOnServiceKey = typeof ADD_ON_SERVICE_KEYS[number];

    const NOT_ENABLED_KEYS: AddOnServiceKey[] = [...ADD_ON_SERVICE_KEYS];

    type AddOnGroupDefinition = {
        id: string;
        title: string;
        description?: string;
        services: Array<{ key: AddOnServiceKey; tiers?: TierKey[] }>;
    };

    type ResolvedAddOnGroup = {
        id: string;
        title: string;
        description?: string;
        services: Array<{ key: AddOnServiceKey; label: string; price?: number; summary?: string; icon?: string; link?: string }>;
    };

    const ADD_ON_SERVICE_DETAILS: Record<AddOnServiceKey, { summary: string }> = {
        controltower: {
            summary: 'Tie add-on workloads into Control Tower guardrails, account vending, and SCP baselines.',
        },
        compliance: {
            summary: 'Extend Config conformance packs and audit findings coverage without promoting entire tiers.',
        },
        budget: {
            summary: 'Layer proactive AWS Budgets alerting and anomaly notifications onto growth tiers.',
        },
        secrets_manager: {
            summary: 'Centralise connector credentials and API keys without upgrading the entire environment blueprint.',
        },
        iam_identity_center: {
            summary: 'Enable SSO-backed workforce access control with least-privilege permission sets per environment.',
        },
        shield_advanced: {
            summary: 'Activate managed DDoS detection, advanced telemetry, and rapid escalation with AWS Shield Advanced.',
        },
        inspector: {
            summary: 'Scan container and instance fleets for critical CVEs and misconfigurations before promotion.',
        },
        artifact: {
            summary: 'Pull compliance evidence bundles for customer questionnaires and audits directly from AWS Artifact.',
        },
        detective: {
            summary: 'Graph-powered investigation trails that pivot from GuardDuty findings into root-cause analysis.',
        },
        attack_simulation: {
            summary: 'Run chaos drills and FIS experiments to validate runbooks and perimeter controls on schedule.',
        },
        dataquality: {
            summary: 'Deploy Glue Data Quality monitors and scorecards against crown-jewel data tables.',
        },
        codepipeline: {
            summary: 'Add gated release pipelines for infrastructure and model artifacts with approval flows.',
        },
    };

    const ADD_ON_GROUPS: AddOnGroupDefinition[] = [
        {
            id: 'guardrails',
            title: 'Guardrails & governance extensions',
            description: 'Layer in Control Tower guardrails, Identity Center federation, proactive budget alerts, and federated secrets once foundational telemetry is stable.',
            services: [
                { key: 'controltower', tiers: ['starter', 'growth'] },
                { key: 'compliance', tiers: ['starter'] },
                { key: 'budget', tiers: ['starter'] },
                { key: 'secrets_manager', tiers: ['starter', 'growth'] },
                { key: 'iam_identity_center', tiers: ['starter'] },
            ],
        },
        {
            id: 'security',
            title: 'Security posture accelerators',
            description: 'Harden the perimeter and satisfy audit readiness with managed detection, threat hunting, chaos drills, and evidence bundles.',
            services: [
                { key: 'shield_advanced', tiers: ['starter', 'growth'] },
                { key: 'inspector', tiers: ['starter', 'growth'] },
                { key: 'artifact', tiers: ['starter', 'growth'] },
                { key: 'detective', tiers: ['starter', 'growth'] },
                { key: 'attack_simulation', tiers: ['growth'] },
            ],
        },
        {
            id: 'ops-automation',
            title: 'Operational automation add-ons',
            description: 'Inject automation, quality bars, and release rigor once ingestion throughput and detections mature.',
            services: [
                { key: 'dataquality', tiers: ['starter', 'growth'] },
                { key: 'codepipeline', tiers: ['growth'] },
            ],
        },
    ];

    const ServiceRow: React.FC<{ label: string; iconSrc?: string; priceUsdPerMonth?: number; tier: TierKey }>
        = ({ label, iconSrc, priceUsdPerMonth, tier }) => {
            const [imgOk, setImgOk] = React.useState(true);
            const isServiceHovered = hoveredService?.label === label && hoveredService?.tier === tier;
            const isOtherServiceHovered = hoveredService !== null && !(hoveredService.label === label && hoveredService.tier === tier);
            const link = SERVICE_LINKS[label];
            const desc = SERVICE_DESC[label];
            const displayLabel = React.useMemo(() => displayServiceName(label), [label]);
            const summary = desc ?? SERVICE_DESC_COMPACT[label] ?? displayLabel;
            const iconSurface = getCssVar('--pricing-icon-surface', 'rgba(59,130,246,0.12)');
            const iconBorder = getCssVar('--pricing-icon-border', 'rgba(59,130,246,0.22)');
            const hoverGlow = '0 18px 32px rgba(15,23,42,0.14)';
            const initials = React.useMemo(() => {
                const cleaned = displayLabel.replace(/\(.*?\)/g, '').trim();
                const words = cleaned.split(/\s+/).filter(Boolean);
                const letters = words.slice(0, 2).map(w => w[0]?.toUpperCase() ?? '').join('');
                return letters || 'SC';
            }, [displayLabel]);
            const RowTag: any = link ? 'a' : 'div';

            const handleMouseEnter = () => {
                setHoveredService({ label, tier });
            };

            const handleMouseLeave = () => {
                if (hoveredService?.label === label && hoveredService?.tier === tier) {
                    setHoveredService(null);
                }
            };

            return (
                <RowTag
                    className={`${styles.serviceRow} svc-row`}
                    href={link || undefined}
                    target={link ? '_blank' : undefined}
                    rel={link ? 'noopener noreferrer' : undefined}
                    aria-label={link ? `${displayLabel} – open AWS page` : displayLabel}
                    data-hovered={isServiceHovered || undefined}
                    onMouseEnter={handleMouseEnter}
                    onMouseLeave={handleMouseLeave}
                    style={{
                        cursor: link ? 'pointer' : 'default',
                        opacity: isOtherServiceHovered ? 0.4 : 1,
                        zIndex: isServiceHovered ? 3 : 1,
                        boxShadow: isServiceHovered ? hoverGlow : undefined,
                        borderColor: isServiceHovered ? iconBorder : undefined,
                        background: isServiceHovered ? 'linear-gradient(135deg, rgba(59,130,246,0.12), rgba(16,185,129,0.10))' : undefined,
                        textDecoration: 'none'
                    }}
                >
                    <div className={styles.serviceRowHeader}>
                        <div className={styles.serviceRowIdentity}>
                            <span
                                className={styles.serviceRowIconWrap}
                                style={{ background: iconSurface, borderColor: iconBorder }}
                            >
                                {iconSrc && imgOk ? (
                                    <img
                                        src={iconSrc}
                                        alt={displayLabel}
                                        onError={() => setImgOk(false)}
                                    />
                                ) : (
                                    <span className={styles.serviceRowIconFallback}>{initials}</span>
                                )}
                            </span>
                            <div className={styles.serviceRowTitle}>{displayLabel}</div>
                        </div>
                        {typeof priceUsdPerMonth === 'number' && priceUsdPerMonth > 0 ? (
                            <div className={styles.serviceRowPrice}>
                                <span className={`${styles.serviceRowPriceChip} price-chip`} data-tooltip="Approximate monthly cost">
                                    {toUSD(priceUsdPerMonth)}
                                </span>
                            </div>
                        ) : null}
                    </div>
                    <div className={styles.serviceRowDescription}>
                        {summary}
                    </div>
                </RowTag>
            );
        };

    const AddOnGroupSection: React.FC<{ group: ResolvedAddOnGroup }> = ({ group }) => (
        <div className={styles.addOnsGroup}>
            <div className={styles.addOnsGroupHeader}>
                <div className={styles.addOnsGroupTitle}>{group.title}</div>
                {group.description ? <p className={styles.addOnsGroupDescription}>{group.description}</p> : null}
            </div>
            <div className={styles.addOnsGroupList}>
                {group.services.map(service => (
                    <div key={`${group.id}-${service.key}`} className={styles.addOnServiceRow}>
                        <div className={styles.addOnServiceIcon} aria-hidden>
                            {service.icon ? (
                                <img src={service.icon} alt="" />
                            ) : (
                                <span className={styles.addOnServiceFallback}>{service.label.slice(0, 2).toUpperCase()}</span>
                            )}
                        </div>
                        <div className={styles.addOnServiceBody}>
                            <div className={styles.addOnServiceHeading}>
                                {service.link ? (
                                    <a href={service.link} target="_blank" rel="noopener noreferrer">{service.label}</a>
                                ) : (
                                    <span>{service.label}</span>
                                )}
                                {typeof service.price === 'number' && service.price > 0 ? (
                                    <span className={styles.addOnPriceChip}>{toUSD(service.price)}</span>
                                ) : null}
                            </div>
                            {service.summary ? <p className={styles.addOnServiceSummary}>{service.summary}</p> : null}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

    const ServicePill: React.FC<{ label: string }> = ({ label }) => {
        const iconSrc = ICONS[label];
        const desc = SERVICE_DESC[label];
        const displayLabel = React.useMemo(() => displayServiceName(label), [label]);
        const tooltip = desc || displayLabel;
        const initials = React.useMemo(() => {
            const cleaned = displayLabel.replace(/\(.*?\)/g, '').trim();
            const words = cleaned.split(/\s+/).filter(Boolean);
            const letters = words.slice(0, 2).map(w => w[0]?.toUpperCase() ?? '').join('');
            return letters || 'SC';
        }, [displayLabel]);
        const pillRef = React.useRef<HTMLSpanElement | null>(null);
        const [tooltipAlign, setTooltipAlign] = React.useState<'center' | 'start' | 'end'>('center');

        const evaluateAlignment = React.useCallback(() => {
            const node = pillRef.current;
            if (!node) return;
            const host = node.closest(`.${styles.vpcFrame}`)
                ?? node.closest(`.${styles.regionCanvas}`)
                ?? node.closest('.tier-card')
                ?? node.closest(`.${styles.pricingInner}`)
                ?? document.querySelector(`.${styles.pricingInner}`);
            const hostRect = host instanceof HTMLElement ? host.getBoundingClientRect() : { left: 0, right: window.innerWidth };
            const rect = node.getBoundingClientRect();
            const leftSpace = rect.left - hostRect.left;
            const rightSpace = hostRect.right - rect.right;
            const nextAlign: 'center' | 'start' | 'end' = (() => {
                const threshold = 160;
                if (leftSpace < threshold && rightSpace >= leftSpace) {
                    return 'start';
                }
                if (rightSpace < threshold && rightSpace < leftSpace) {
                    return 'end';
                }
                return 'center';
            })();
            setTooltipAlign(prev => (prev === nextAlign ? prev : nextAlign));
        }, []);

        React.useEffect(() => {
            const node = pillRef.current;
            if (!node) return undefined;

            const handleEnter = () => evaluateAlignment();
            const handleFocus = () => evaluateAlignment();
            const handleLeave = () => setTooltipAlign('center');
            const handleResize = () => {
                if (!node) return;
                if (node.matches(':hover') || node === document.activeElement) {
                    evaluateAlignment();
                }
            };

            node.addEventListener('mouseenter', handleEnter);
            node.addEventListener('focus', handleFocus);
            node.addEventListener('mouseleave', handleLeave);
            node.addEventListener('blur', handleLeave);
            window.addEventListener('resize', handleResize);

            return () => {
                node.removeEventListener('mouseenter', handleEnter);
                node.removeEventListener('focus', handleFocus);
                node.removeEventListener('mouseleave', handleLeave);
                node.removeEventListener('blur', handleLeave);
                window.removeEventListener('resize', handleResize);
            };
        }, [evaluateAlignment]);

        return (
            <span
                ref={pillRef}
                className={styles.servicePill}
                data-tooltip={tooltip}
                data-tooltip-align={tooltipAlign === 'center' ? undefined : tooltipAlign}
                aria-label={tooltip}
            >
                {iconSrc ? (
                    <img src={iconSrc} alt="" aria-hidden style={{ width: 26, height: 26, objectFit: 'contain', borderRadius: 8, padding: 3, background: 'rgba(59,130,246,0.12)', border: '1px solid rgba(59,130,246,0.22)' }} />
                ) : (
                    <span className={styles.servicePillInitials}>{initials}</span>
                )}
                <span>{displayLabel}</span>
            </span>
        );
    };

    const SubnetPill: React.FC<Subnet> = ({ name, type, cidr, notes }) => (
        <span className={styles.subnetPill} data-subnet-type={type} title={notes || cidr || name}>
            <span className={styles.subnetDot} aria-hidden />
            <span className={styles.subnetName}>{name}</span>
            {cidr ? <span className={styles.subnetCidr}>{cidr}</span> : null}
        </span>
    );

    const DeploymentCard: React.FC<{ option: DeploymentOption }> = ({ option }) => (
        <div className={styles.deploymentCard}>
            <div className={styles.deploymentHeadingRow}>
                <div className={styles.deploymentIcon} aria-hidden>
                    <img src={option.icon} alt="" />
                </div>
                {option.badge ? <span className={styles.deploymentBadge}>{option.badge}</span> : null}
            </div>
            <div className={styles.deploymentTitle}>{option.label}</div>
            <p className={styles.deploymentDescription}>{option.description}</p>
            <ul className={styles.deploymentList}>
                {option.points.map(point => (
                    <li key={`${option.key}-${point.heading}`} className={styles.deploymentListItem}>
                        <div className={styles.deploymentListMarker} aria-hidden />
                        <div>
                            <div className={styles.deploymentPointHeading}>{point.heading}</div>
                            <div className={styles.deploymentPointDetail}>{point.detail}</div>
                        </div>
                    </li>
                ))}
            </ul>
            {option.services?.length ? (
                <div className={styles.deploymentServices}>
                    {option.services.map(service => (
                        <ServicePill key={`${option.key}-svc-${service}`} label={service} />
                    ))}
                </div>
            ) : null}
            {option.meta ? <div className={styles.deploymentMeta}>{option.meta}</div> : null}
        </div>
    );

    const TierColumn: React.FC<{ t: TierKey; onViewBlueprint: (tier: TierKey) => void; isBlueprintActive: boolean }> = ({ t, onViewBlueprint, isBlueprintActive }) => {
        const env = envForTier[t];
        const reverseMap: Record<string, string> = Object.entries(SERVICE_LABELS)
            .reduce((acc, [key, val]) => { acc[val] = key; return acc; }, {} as Record<string, string>);

        const tierTotal = React.useMemo(() => {
            if (discovery?.cost_analysis) {
                const sum = Object.values(discovery.cost_analysis).reduce((acc, perEnv) => acc + (perEnv[env] || 0), 0);
                return Math.round(sum);
            }
            const sum = (t0: TierKey) => CAPABILITIES.reduce((s, c) => s + c.monthly[t0], 0);
            return sum(t);
        }, [discovery, env, t]);

        const entries = React.useMemo(() => {
            const set = new Set<string>();
            if (discovery?.capabilities) {
                for (const cap of Object.values(discovery.capabilities)) {
                    const svcs = cap.active_services_by_env?.[env] ?? [];
                    svcs.forEach(k => set.add(SERVICE_LABELS[k] || k));
                }
            }
            if (set.size === 0) {
                CAPABILITIES.forEach(c => (c.awsByTier?.[t] ?? c.aws ?? []).forEach(lbl => set.add(lbl)));
            }
            if (t === 'enterprise') {
                NOT_ENABLED_KEYS.forEach(k => set.add(SERVICE_LABELS[k] || k));
            }
            const labels = Array.from(set).sort((a, b) => a.localeCompare(b));
            return labels.map(label => {
                const key = reverseMap[label];
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


        const overview = TIER_OVERVIEW[t];

        return (
            <div
                className="tier-card"
                onMouseLeave={() => {
                    setHoveredService(null);
                }}
                style={{
                    display: 'flex', flexDirection: 'column', gap: 16,
                    border: `1px solid ${themeVars.border}`,
                    borderRadius: 16,
                    padding: 18,
                    boxShadow: '0 18px 40px rgba(0,0,0,.07)',
                    transition: 'all 0.2s ease'
                }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, paddingBottom: 8, borderBottom: `1px solid ${getCssVar('--ifm-color-emphasis-200', 'rgba(0,0,0,.08)')}` }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        <div style={{ fontWeight: 800, fontSize: '1.12rem', letterSpacing: '.1px' }}>{TIERS[t].label}</div>
                        <div style={{ fontSize: '.86rem', opacity: .8 }}>{TIERS[t].tagline}</div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6 }}>
                        <span className="price-chip" style={{
                            display: 'inline-block',
                            padding: '6px 12px',
                            borderRadius: 9999,
                            border: `1px solid ${getCssVar('--ifm-color-emphasis-200', 'rgba(0,0,0,.08)')}`,
                            background: 'transparent',
                            minWidth: 96,
                            textAlign: 'center',
                            whiteSpace: 'nowrap',
                            fontWeight: 800,
                            fontSize: '1.02rem'
                        }}>{toUSD(tierTotal)}</span>
                        <a
                            href="#infra-blueprint"
                            className={`${styles.viewArchitectureLink} ${isBlueprintActive ? styles.viewArchitectureLinkActive : ''}`}
                            onClick={(event) => {
                                event.preventDefault();
                                onViewBlueprint(t);
                            }}
                        >
                            View infrastructure
                        </a>
                    </div>
                </div>
                <div className={styles.tierOverview}>
                    <div className={styles.tierBadge}>{overview.badge}</div>
                </div>
                <div className="svc-list" style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                    {entries.map(({ label, price }) => (
                        <ServiceRow key={`${t}-svc-${label}`} label={label} iconSrc={ICONS[label]} priceUsdPerMonth={typeof price === 'number' ? price : undefined} tier={t} />
                    ))}
                </div>
            </div>
        );
    };

    const InfraRegionMap: React.FC<{ blueprint: InfraBlueprint }> = ({ blueprint }) => (
        <div className={styles.infraRegionMap}>
            {blueprint.perimeter?.length ? (
                <section className={styles.globalPerimeter} aria-label="Global guardrails and shared services">
                    <div className={styles.perimeterConnector} aria-hidden>
                        <span className={styles.perimeterConnectorLine} />
                    </div>
                    <div className={styles.perimeterStrip}>
                        <div className={styles.perimeterTitle}>Global services</div>
                        <div className={styles.perimeterGroups}>
                            {blueprint.perimeter.map(group => (
                                <div key={`perimeter-${group.title}`} className={styles.infraGroup}>
                                    <div className={styles.groupTitle}>{group.title}</div>
                                    {group.description && <p className={styles.groupDescription}>{group.description}</p>}
                                    <div className={styles.servicePillRow}>
                                        {group.services.map(service => (
                                            <ServicePill key={`perimeter-${group.title}-${service}`} label={service} />
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            ) : null}
            <div className={styles.regionCanvas}>
                <div className={styles.regionHeader}>
                    <div>
                        <h3 className={styles.regionTitle}>{blueprint.region}</h3>
                    </div>
                </div>
                {blueprint.regionWide?.length ? (
                    <div className={styles.regionWideSection}>
                        <div className={styles.regionWideTitle}>Regional platforms &amp; data services</div>
                        <div className={styles.regionWideGroups}>
                            {blueprint.regionWide.map(group => (
                                <div key={`region-${group.title}`} className={styles.infraGroup}>
                                    <div className={styles.groupTitle}>{group.title}</div>
                                    {group.description && <p className={styles.groupDescription}>{group.description}</p>}
                                    <div className={styles.servicePillRow}>
                                        {group.services.map(service => (
                                            <ServicePill key={`region-${group.title}-${service}`} label={service} />
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : null}
                <div className={styles.vpcFrame}>
                    <div className={styles.vpcBadge}>VPC</div>
                    <div className={styles.azWrapper}>
                        {blueprint.azs.map(az => (
                            <div key={az.name} className={styles.azCard}>
                                <div className={styles.azHeader}>
                                    <div className={styles.azName}>{az.name}</div>
                                    <p className={styles.azSummary}>{az.summary}</p>
                                </div>
                                {az.subnets?.length ? (
                                    <div className={styles.subnetCluster}>
                                        <div className={styles.subnetTitle}>Subnets &amp; workloads</div>
                                        <div className={styles.subnetList}>
                                            {az.subnets.map(subnet => (
                                                <div
                                                    key={`${az.name}-${subnet.name}`}
                                                    className={styles.subnetCard}
                                                    data-subnet-type={subnet.type}
                                                >
                                                    <div className={styles.subnetHeader}>
                                                        <SubnetPill {...subnet} />
                                                        {subnet.notes ? <span className={styles.subnetNotes}>{subnet.notes}</span> : null}
                                                    </div>
                                                    {subnet.workloads?.length ? (
                                                        <div className={styles.subnetWorkloads}>
                                                            {subnet.workloads.map(group => (
                                                                <div key={`${az.name}-${subnet.name}-${group.title}`} className={styles.infraGroup}>
                                                                    <div className={styles.groupTitle}>{group.title}</div>
                                                                    {group.description && <p className={styles.groupDescription}>{group.description}</p>}
                                                                    <div className={styles.servicePillRow}>
                                                                        {group.services.map(service => (
                                                                            <ServicePill key={`${az.name}-${subnet.name}-${group.title}-${service}`} label={service} />
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    ) : null}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ) : null}
                                {az.groups?.length ? (
                                    <div className={styles.azGroups}>
                                        {az.groups.map(group => (
                                            <div key={`${az.name}-${group.title}`} className={styles.infraGroup}>
                                                <div className={styles.groupTitle}>{group.title}</div>
                                                {group.description && <p className={styles.groupDescription}>{group.description}</p>}
                                                <div className={styles.servicePillRow}>
                                                    {group.services.map(service => (
                                                        <ServicePill key={`${az.name}-${group.title}-${service}`} label={service} />
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : null}
                            </div>
                        ))}
                    </div>
                    {blueprint.failover ? (
                        <div className={styles.failoverRibbon}>
                            <div className={styles.failoverHeader}>
                                <div className={styles.failoverHeadingGroup}>
                                    <span className={styles.failoverBadge}>Multi-AZ failover</span>
                                    <div className={styles.failoverTitle}>{blueprint.failover.title}</div>
                                </div>
                                {blueprint.failover.cadence ? (
                                    <div className={styles.failoverCadence}>{blueprint.failover.cadence}</div>
                                ) : null}
                            </div>
                            {blueprint.failover.azPath?.length ? (
                                <div className={styles.failoverVector} aria-hidden>
                                    {blueprint.failover.azPath.map((label, idx) => (
                                        <React.Fragment key={`failover-path-${label}-${idx}`}>
                                            <div className={styles.failoverNode}>{label}</div>
                                            {idx !== blueprint.failover.azPath.length - 1 ? (
                                                <div className={styles.failoverArrow}>
                                                    <span className={styles.failoverArrowBody} />
                                                    <span className={styles.failoverArrowHead} />
                                                </div>
                                            ) : null}
                                        </React.Fragment>
                                    ))}
                                </div>
                            ) : null}
                            <p className={styles.failoverDescription}>{blueprint.failover.description}</p>
                            <div className={styles.servicePillRow}>
                                {blueprint.failover.services.map(service => (
                                    <ServicePill key={`failover-${service}`} label={service} />
                                ))}
                            </div>
                        </div>
                    ) : null}
                </div>
            </div>
        </div>
    );

    return (
        <Layout title="Pricing" description="ShieldCraft AI pricing tiers, add-ons, and infrastructure blueprint.">
            <div className={`${styles.pricingPageWrapper} pricing-page-wrapper`}>
                <div className={styles.pricingInner}>
                    <h1 className={styles.pageTitle}>ShieldCraft AI Pricing</h1>
                    <p className={styles.pageSubtitle}>Compare tiers to preview scope, monthly run-rate, and the AWS services each IaC template activates.</p>
                    <div className={styles.tierGridWrap}>
                        <div className={styles.tierGrid}>
                            {TIER_KEYS.map(t => (
                                <TierColumn
                                    key={`col-${t}`}
                                    t={t}
                                    onViewBlueprint={navigateToBlueprint}
                                    isBlueprintActive={infraTier === t}
                                />
                            ))}
                        </div>
                    </div>

                    <div ref={blueprintSectionRef} id="infra-blueprint" className={styles.infraSection}>
                        <div className={styles.infraHeader}>
                            <div className={styles.infraTierToggle} role="radiogroup" aria-label="Select infrastructure tier">
                                {TIER_KEYS.map(t => (
                                    <button
                                        key={`infra-toggle-${t}`}
                                        type="button"
                                        role="radio"
                                        aria-checked={infraTier === t}
                                        className={`${styles.infraToggleButton} ${infraTier === t ? styles.infraToggleButtonActive : ''}`}
                                        onClick={() => setInfraTier(t)}
                                    >
                                        {TIERS[t].label}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <InfraRegionMap blueprint={INFRA_BLUEPRINT[infraTier]} />
                    </div>

                    <div className={styles.deployGridWrap}>
                        <div className={styles.deployIntro}>
                            <div>
                                <h2 className={styles.deployTitle}>Deployment playbooks</h2>
                            </div>
                            <div className={styles.deployMetaRow}>
                                <span className={styles.deployMetaChip}>No shared tenancy</span>
                                <span className={styles.deployMetaChip}>You keep the encryption keys</span>
                                <span className={styles.deployMetaChip}>Runbook-driven cutovers</span>
                            </div>
                        </div>
                        <div className={styles.deployGrid}>
                            {DEPLOYMENT_OPTIONS.map(option => (
                                <DeploymentCard key={option.key} option={option} />
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
}
