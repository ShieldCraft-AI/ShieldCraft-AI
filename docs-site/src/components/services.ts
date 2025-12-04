// Single source of truth for AWS services used by the selector and platform components.
// Icon paths are absolute within docs-site static folder: /aws-icons/<name>.svg

export type AwsServiceId =
    | 's3' | 'glue' | 'glueDataQuality' | 'glueDataBrew' | 'lakeFormation' | 'eventbridge' | 'apiGateway' | 'msk' | 'cloudTrail' | 'vpc'
    | 'opensearch' | 'sagemaker' | 'stepFunctions' | 'lambda'
    | 'iam' | 'secretsManager' | 'guardDuty' | 'securityHub' | 'config' | 'detective' | 'waf'
    | 'budgets' | 'costExplorer' | 'cloudWatch' | 'controlTower' | 'identityCenter';

export type AwsService = {
    id: AwsServiceId;
    title: string;
    summary: string;
    shieldcraftUse: string;
    details?: string;
    icon: string; // path under /aws-icons/
};

export type AwsServiceGroup = { id: 'ingestion' | 'mlops' | 'remediation' | 'finops'; label: string; services: AwsService[] };

// Full 26-service catalog matching the landing page architecture diagram
export const SERVICE_GROUPS: AwsServiceGroup[] = [
    {
        id: 'ingestion',
        label: 'Ingestion & Governance',
        services: [
            {
                id: 's3',
                title: 'Amazon S3',
                summary: 'Durable object storage for immutable artifacts and audit evidence.',
                shieldcraftUse: 'Canonical archive for snapshots, telemetry, and model artifacts with SSE-KMS and lifecycle policies.',
                details: 'Block public access, enforce TLS-only access points, replicate to DR regions when needed.',
                icon: '/aws-icons/Arch_Amazon-Simple-Storage-Service_48.svg',
            },
            {
                id: 'glue',
                title: 'AWS Glue',
                summary: 'Schema-governed ETL for ingestion and feature prep.',
                shieldcraftUse: 'Crawlers and jobs drive deterministic transforms and catalog-driven contracts.',
                details: 'Jobs run in private subnets with checkpointing and data quality checks.',
                icon: '/aws-icons/Arch_AWS-Glue_48.svg',
            },
            {
                id: 'lakeFormation',
                title: 'AWS Lake Formation',
                summary: 'Unified data permissions and lineage enforcement.',
                shieldcraftUse: 'LF-tags and grants map to domains to enforce column-level controls before compute.',
                details: 'Grants only via IaC for a clean audit trail.',
                icon: '/aws-icons/Arch_AWS-Lake-Formation_48.svg',
            },
            {
                id: 'eventbridge',
                title: 'Amazon EventBridge',
                summary: 'Event bus for normalized telemetry and async workflows.',
                shieldcraftUse: 'Routes posture, detections, and approvals into Step Functions and replayable workflows.',
                details: 'DLQs + schema registry prevent silent drops.',
                icon: '/aws-icons/Arch_Amazon-EventBridge_48.svg',
            },
            {
                id: 'glueDataQuality',
                title: 'AWS Glue Data Quality',
                summary: 'Automated data quality checks and rules.',
                shieldcraftUse: 'Validates telemetry schemas before ML ingestion; blocks bad data.',
                details: 'Rule-based validation with anomaly detection.',
                icon: '/aws-icons/Arch_AWS-Glue_48.svg',
            },
            {
                id: 'glueDataBrew',
                title: 'AWS Glue DataBrew',
                summary: 'Visual data preparation and cleaning.',
                shieldcraftUse: 'Normalizes log formats and enriches context fields.',
                details: 'No-code transforms for security analysts.',
                icon: '/aws-icons/Arch_AWS-Glue-DataBrew_48.svg',
            },
            {
                id: 'apiGateway',
                title: 'Amazon API Gateway',
                summary: 'Managed API proxy with auth and throttling.',
                shieldcraftUse: 'Exposes ShieldCraft APIs for external integrations.',
                details: 'OAuth2 + API key auth; rate limiting per consumer.',
                icon: '/aws-icons/Arch_Amazon-API-Gateway_48.svg',
            },
            {
                id: 'msk',
                title: 'Amazon MSK',
                summary: 'Managed Kafka for high-volume streaming.',
                shieldcraftUse: 'Streams raw telemetry for replay and feature backfills.',
                details: 'Multi-AZ with encryption; retention configurable.',
                icon: '/aws-icons/Arch_Amazon-Managed-Streaming-for-Apache-Kafka_48.svg',
            },
            {
                id: 'cloudTrail',
                title: 'AWS CloudTrail',
                summary: 'Immutable API audit logs for every account.',
                shieldcraftUse: 'Forensics, approvals and evidence for automation actions.',
                details: 'Org trails to S3; analysis via event pipelines.',
                icon: '/aws-icons/Arch_AWS-CloudTrail_48.svg',
            },
            {
                id: 'vpc',
                title: 'Amazon VPC',
                summary: 'Network isolation and segmentation.',
                shieldcraftUse: 'Private subnets for compute; VPC Flow Logs feed network analysis.',
                details: 'Multi-AZ with NAT gateways and security groups.',
                icon: '/aws-icons/Arch_Amazon-Virtual-Private-Cloud_48.svg',
            },
        ],
    },
    {
        id: 'mlops',
        label: 'GenAI & MLOps Core',
        services: [
            {
                id: 'opensearch',
                title: 'Amazon OpenSearch',
                summary: 'Low-latency search for logs, findings and hybrid retrieval.',
                shieldcraftUse: 'Search + vectors for analyst pivoting and historical context recall.',
                details: 'ILM policies and fine-grained access control.',
                icon: '/aws-icons/Arch_Amazon-OpenSearch-Service_48.svg',
            },
            {
                id: 'sagemaker',
                title: 'Amazon SageMaker',
                summary: 'Managed training and guarded inference for GenAI workloads.',
                shieldcraftUse: 'Hosts LLM endpoints for threat analysis; trains custom detectors.',
                details: 'Execution roles scoped tightly; autoscaling gated by budgets.',
                icon: '/aws-icons/Arch_Amazon-SageMaker_48.svg',
            },
        ],
    },
    {
        id: 'remediation',
        label: 'Remediation & Control Plane',
        services: [
            {
                id: 'lambda',
                title: 'AWS Lambda',
                summary: 'Serverless glue for enrichment and lightweight orchestration.',
                shieldcraftUse: 'Executes playbook actions: credential revocation, isolation, snapshots.',
                details: 'Least-privilege roles; private VPC attachments.',
                icon: '/aws-icons/Arch_AWS-Lambda_48.svg',
            },
            {
                id: 'stepFunctions',
                title: 'AWS Step Functions',
                summary: 'Deterministic orchestration for remediation and ML pipelines.',
                shieldcraftUse: 'Coordinates multi-step playbooks with approvals and rollback.',
                details: 'State history for audit + manual pause hooks.',
                icon: '/aws-icons/Arch_AWS-Step-Functions_48.svg',
            },
            {
                id: 'iam',
                title: 'AWS IAM',
                summary: 'Identity and access guardrails.',
                shieldcraftUse: 'Revokes compromised credentials; enforces least privilege.',
                details: 'No inline policies; versioned IaC only.',
                icon: '/aws-icons/Arch_AWS-Identity-and-Access-Management_48.svg',
            },
            {
                id: 'secretsManager',
                title: 'AWS Secrets Manager',
                summary: 'Centralized secret rotation and retrieval controls.',
                shieldcraftUse: 'Rotates leaked credentials automatically.',
                details: 'Audit and rotation events to EventBridge.',
                icon: '/aws-icons/Arch_AWS-Secrets-Manager_48.svg',
            },
            {
                id: 'securityHub',
                title: 'AWS Security Hub',
                summary: 'Normalized posture signals and standards mapping.',
                shieldcraftUse: 'Aggregates findings from GuardDuty, Config, Inspector.',
                details: 'Exception tracking with owners and expiry.',
                icon: '/aws-icons/Arch_AWS-Security-Hub_48.svg',
            },
            {
                id: 'guardDuty',
                title: 'Amazon GuardDuty',
                summary: 'Managed threat detection and signals.',
                shieldcraftUse: 'Detects initial anomalies; ShieldCraft analyzes intent and acts.',
                details: 'Delegated admin for multi-account centralization.',
                icon: '/aws-icons/Arch_Amazon-GuardDuty_48.svg',
            },
            {
                id: 'config',
                title: 'AWS Config',
                summary: 'Resource compliance snapshots wired to remediation.',
                shieldcraftUse: 'Validates remediation actions; enforces compliance rules.',
                details: 'Recorders and aggregated snapshots across accounts.',
                icon: '/aws-icons/Arch_AWS-Config_48.svg',
            },
            {
                id: 'detective',
                title: 'Amazon Detective',
                summary: 'Security investigation with behavior graphs.',
                shieldcraftUse: 'Enriches LLM context with entity relationship graphs.',
                details: 'Auto-ingestion of GuardDuty, VPC Flow, CloudTrail.',
                icon: '/aws-icons/Arch_Amazon-Detective_48.svg',
            },
            {
                id: 'waf',
                title: 'AWS WAF',
                summary: 'Web application firewall.',
                shieldcraftUse: 'Blocks malicious IPs detected during incident response.',
                details: 'Rate-based rules and geo-blocking.',
                icon: '/aws-icons/Arch_AWS-WAF_48.svg',
            },
            {
                id: 'controlTower',
                title: 'AWS Control Tower',
                summary: 'Landing zone and account vending.',
                shieldcraftUse: 'Enforces baseline guardrails across accounts.',
                details: 'Integrates with IAM Identity Center.',
                icon: '/aws-icons/Arch_AWS-Control-Tower_48.svg',
            },
            {
                id: 'identityCenter',
                title: 'IAM Identity Center',
                summary: 'Centralized workforce authentication.',
                shieldcraftUse: 'SSO for analyst access to portal and AWS console.',
                details: 'SAML federation with corporate IdP.',
                icon: '/aws-icons/Arch_AWS-IAM-Identity-Center_48.svg',
            },
        ],
    },
    {
        id: 'finops',
        label: 'FinOps & Observability',
        services: [
            {
                id: 'budgets',
                title: 'AWS Budgets',
                summary: 'Cost and usage budget tracking.',
                shieldcraftUse: 'Gates autonomous actions when spend exceeds thresholds.',
                details: 'SNS alerts to ops team; CloudWatch integration.',
                icon: '/aws-icons/Arch_AWS-Budgets_48.svg',
            },
            {
                id: 'costExplorer',
                title: 'AWS Cost Explorer',
                summary: 'Cost analysis and forecasting.',
                shieldcraftUse: 'Surfaces cost trends for remediation planning.',
                details: 'API access for programmatic queries.',
                icon: '/aws-icons/Arch_AWS-Cost-Explorer_48.svg',
            },
            {
                id: 'cloudWatch',
                title: 'Amazon CloudWatch',
                summary: 'Metrics, logs, and alarms powering evidence loops.',
                shieldcraftUse: 'Monitors model drift, ingestion latency, remediation rates.',
                details: 'Structured logs and correlation IDs.',
                icon: '/aws-icons/Arch_Amazon-CloudWatch_48.svg',
            },
        ],
    },
];

export const FLAT_SERVICES: AwsService[] = SERVICE_GROUPS.flatMap((g) => g.services);
export const DEFAULT_SERVICE_ID: AwsService['id'] = FLAT_SERVICES[0].id;

export const SERVICE_INDEX: Record<AwsService['id'], number> = FLAT_SERVICES.reduce((acc, s, idx) => {
    acc[s.id] = idx;
    return acc;
}, {} as Record<AwsService['id'], number>);
