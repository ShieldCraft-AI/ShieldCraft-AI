export type AwsServiceId =
    | 's3'
    | 'glue'
    | 'lakeFormation'
    | 'eventbridge'
    | 'opensearch'
    | 'sagemaker'
    | 'stepFunctions'
    | 'lambda'
    | 'iam'
    | 'secretsManager'
    | 'guardDuty'
    | 'securityHub'
    | 'config'
    | 'cloudTrail'
    | 'cloudWatch'
    | 'controlTower';

export type AwsService = {
    id: AwsServiceId;
    title: string;
    summary: string;
    shieldcraftUse: string;
    details?: string;
    icon: string;
};

export type AwsServiceGroup = {
    id: 'core' | 'integration' | 'security' | 'governance';
    label: string;
    services: AwsService[];
};

export const SERVICE_GROUPS: AwsServiceGroup[] = [
    {
        id: 'core',
        label: 'Core Data Services',
        services: [
            {
                id: 's3',
                title: 'Amazon S3',
                summary: 'Durable object storage for immutable artifacts and audit evidence.',
                shieldcraftUse:
                    'Holds telemetry, investigation snapshots, and model checkpoints with KMS-encrypted buckets and lifecycle policies per environment.',
                details: 'Block public access, enforce TLS-only access points, replicate to disaster recovery regions.',
                icon: '/aws-icons/Arch_Amazon-Simple-Storage-Service_48.svg',
            },
            {
                id: 'glue',
                title: 'AWS Glue',
                summary: 'Schema-governed ETL for ingestion and feature prep.',
                shieldcraftUse:
                    'Crawlers tag sources for Lake Formation, while jobs orchestrate governed pipelines before data hits downstream services.',
                details: 'Jobs run inside private subnets with checkpointing and alerting back to Guard Suite.',
                icon: '/aws-icons/Arch_AWS-Glue_48.svg',
            },
            {
                id: 'lakeFormation',
                title: 'AWS Lake Formation',
                summary: 'Unified data permissions and lineage enforcement.',
                shieldcraftUse:
                    'LF-tags map to business domains so only approved orchestration steps can access sensitive columns or partitions.',
                details: 'All grants and revokes flow through IaC for a clean audit trail.',
                icon: '/aws-icons/Arch_AWS-Lake-Formation_48.svg',
            },
            {
                id: 'eventbridge',
                title: 'Amazon EventBridge',
                summary: 'Event bus for normalized telemetry and async workflows.',
                shieldcraftUse:
                    'Routes posture changes, detections, and approvals into Step Functions or Lambda responders with replay support.',
                details: 'Dead-letter queues and schema registry ensure no event is dropped silently.',
                icon: '/aws-icons/Arch_Amazon-EventBridge_48.svg',
            },
        ],
    },
    {
        id: 'integration',
        label: 'Integration & MLOps',
        services: [
            {
                id: 'opensearch',
                title: 'Amazon OpenSearch',
                summary: 'Low-latency search over findings, vectors, and docs.',
                shieldcraftUse:
                    'Combines with embeddings for hybrid retrieval so analysts can pivot from threat context to remediation history instantly.',
                details: 'Domains run with fine-grained access, dedicated master nodes, and ILM to manage cost.',
                icon: '/aws-icons/Arch_Amazon-OpenSearch-Service_48.svg',
            },
            {
                id: 'sagemaker',
                title: 'Amazon SageMaker',
                summary: 'Managed training/inference for governed AI workloads.',
                shieldcraftUse:
                    'Executes BEIR/MTEB benchmarking and guarded inference endpoints for autonomy loops when GPU acceleration is justified.',
                details: 'Execution roles scoped tightly; endpoints auto-scale with budget controls.',
                icon: '/aws-icons/Arch_Amazon-SageMaker_48.svg',
            },
            {
                id: 'stepFunctions',
                title: 'AWS Step Functions',
                summary: 'Deterministic pipelines for remediation and ML gates.',
                shieldcraftUse:
                    'Playbooks enforce approvals, retries, and policy-as-code before any action hits production accounts.',
                details: 'State history stored for audit, with hooks for manual pause or rollback.',
                icon: '/aws-icons/Arch_AWS-Step-Functions_48.svg',
            },
            {
                id: 'lambda',
                title: 'AWS Lambda',
                summary: 'Serverless glue for detectors, enrichers, and tooling.',
                shieldcraftUse:
                    'Executes lightweight evaluators, policy checks, and data prep tasks close to the pipeline without managing fleets.',
                details: 'Functions ship with DLQs, structured logging, and env-aware IAM roles.',
                icon: '/aws-icons/Arch_AWS-Lambda_48.svg',
            },
        ],
    },
    {
        id: 'security',
        label: 'Security & Identity',
        services: [
            {
                id: 'iam',
                title: 'AWS IAM',
                summary: 'Guardrails for least-privilege automation.',
                shieldcraftUse:
                    'Managed policies and SCPs scope every detector, model, and remediation path; drift detection highlights risky grants.',
                details: 'No inline policies; everything flows through versioned IaC.',
                icon: '/aws-icons/Arch_AWS-Identity-and-Access-Management_48.svg',
            },
            {
                id: 'secretsManager',
                title: 'AWS Secrets Manager',
                summary: 'Centralized credential storage with rotation hooks.',
                shieldcraftUse:
                    'Feeds connectors and RAG tooling without leaking secrets to config files or notebooks.',
                details: 'Rotation events push into EventBridge and Step Functions for approvals.',
                icon: '/aws-icons/Arch_AWS-Secrets-Manager_48.svg',
            },
            {
                id: 'guardDuty',
                title: 'Amazon GuardDuty',
                summary: 'Managed threat intel to seed simulations and responses.',
                shieldcraftUse:
                    'High-severity findings auto-open playbooks; lower tiers train gen-AI simulations and scoring models.',
                details: 'Multi-account delegated admin centralizes triage signals.',
                icon: '/aws-icons/Arch_Amazon-GuardDuty_48.svg',
            },
            {
                id: 'securityHub',
                title: 'AWS Security Hub',
                summary: 'Unified security posture with standards mapping.',
                shieldcraftUse:
                    'Normalizes findings into ShieldCraft guardrails so automation respects CIS/NIST gates.',
                details: 'Exceptions tracked with expiry dates and owners.',
                icon: '/aws-icons/Arch_AWS-Security-Hub_48.svg',
            },
        ],
    },
    {
        id: 'governance',
        label: 'Governance & Observability',
        services: [
            {
                id: 'config',
                title: 'AWS Config',
                summary: 'Resource compliance snapshots wired to remediation.',
                shieldcraftUse:
                    'Rules gate high-risk autonomy; drifts halt deployments until remediation passes.',
                details: 'Recorders run in every account with data aggregated centrally.',
                icon: '/aws-icons/Arch_AWS-Config_48.svg',
            },
            {
                id: 'cloudTrail',
                title: 'AWS CloudTrail',
                summary: 'Immutable API audit logs for every account.',
                shieldcraftUse:
                    'Feeds anomaly detection, forensics, and human-in-the-loop approvals before Step Functions continue.',
                details: 'Organization trails land in S3 with CloudWatch insights enabled.',
                icon: '/aws-icons/Arch_AWS-CloudTrail_48.svg',
            },
            {
                id: 'cloudWatch',
                title: 'Amazon CloudWatch',
                summary: 'Metrics, logs, and alarms powering evidence loops.',
                shieldcraftUse:
                    'Correlates ingestion throughput, model drift, and remediation latency into runbooks.',
                details: 'Dashboards tracked per environment; alarms link to PagerDuty + Guard Suite.',
                icon: '/aws-icons/Arch_Amazon-CloudWatch_48.svg',
            },
            {
                id: 'controlTower',
                title: 'AWS Control Tower',
                summary: 'Landing zone + guardrails for every tenant account.',
                shieldcraftUse:
                    'Ensures security services (Config, CloudTrail, Security Hub) stay enabled and tagged as new accounts land.',
                details: 'Blueprint ties into IAM Identity Center for workforce onboarding.',
                icon: '/aws-icons/Arch_AWS-Control-Tower_48.svg',
            },
        ],
    },
];

export const FLAT_SERVICES: AwsService[] = SERVICE_GROUPS.flatMap((group) => group.services);

export const DEFAULT_SERVICE_ID = FLAT_SERVICES[0].id;

export const SERVICE_INDEX: Record<AwsServiceId, number> = FLAT_SERVICES.reduce(
    (acc, service, idx) => {
        acc[service.id] = idx;
        return acc;
    },
    {} as Record<AwsServiceId, number>
);
