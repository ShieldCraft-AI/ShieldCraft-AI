export type EnvKey = 'dev' | 'staging' | 'prod';

export type ServiceMode = 'none' | 'external' | 'local' | 'inline' | 'managed' | 'ecs_scale_to_zero' | 'ecs_managed';

export interface EnvSummary {
    label: string;
    account: string;
    region: string;
    vpcId?: string;
    buckets: string[];
    subnets: number;
    services: {
        msk: ServiceMode;
        opensearch: ServiceMode;
        airbyte: ServiceMode;
        data_quality: ServiceMode;
        sagemaker: ServiceMode;
    };
    stepfunctionsType: 'express' | 'standard';
    details: {
        msk?: { mode: ServiceMode; externalBootstrap?: string; clusterName?: string; brokerNodes?: number; instanceType?: string };
        opensearch?: { mode: ServiceMode; domainName?: string; instanceType?: string; instanceCount?: number };
        airbyte?: { mode: ServiceMode; deploymentType?: string; minTasks?: number; maxTasks?: number };
        data_quality?: { mode: ServiceMode; framework?: string; schedule?: string };
        sagemaker?: { mode: ServiceMode; trainingInstanceType?: string; inferenceInstanceType?: string; autoscaling?: boolean };
        glue?: { databaseName?: string; crawlerSchedule?: string };
        lakeformation?: { dataLakeLocation?: string };
        eventbridge?: { dataBus?: string; securityBus?: string };
    };
}

export const pipeline: { stage: EnvKey; account: string; region: string }[] = [
    { stage: 'dev', account: '111111111111', region: 'af-south-1' },
    { stage: 'staging', account: '222222222222', region: 'af-south-1' },
    { stage: 'prod', account: '333333333333', region: 'af-south-1' },
];

export const envs: Record<EnvKey, EnvSummary> = {
    dev: {
        label: 'Development',
        account: '879584803102',
        region: 'af-south-1',
        vpcId: 'vpc-shieldcraft-dev',
        buckets: ['shieldcraft-dev-raw', 'shieldcraft-dev-processed', 'shieldcraft-dev-analytics'],
        subnets: 3,
        services: {
            msk: 'external',
            opensearch: 'none',
            airbyte: 'ecs_scale_to_zero',
            data_quality: 'inline',
            sagemaker: 'local',
        },
        stepfunctionsType: 'express',
        details: {
            msk: { mode: 'external', externalBootstrap: 'redpanda:9092', clusterName: 'shieldcraft-msk-cluster' },
            opensearch: { mode: 'none', domainName: 'shieldcraft-opensearch-dev' },
            airbyte: { mode: 'ecs_scale_to_zero', deploymentType: 'ecs', minTasks: 1, maxTasks: 3 },
            data_quality: { mode: 'inline', framework: 'deequ', schedule: 'cron(0 3 * * ? *)' },
            sagemaker: { mode: 'local', trainingInstanceType: 'ml.t3.medium', inferenceInstanceType: 'ml.t3.medium', autoscaling: false },
            glue: { databaseName: 'shieldcraft_dev_db', crawlerSchedule: 'cron(0 2 * * ? *)' },
            lakeformation: { dataLakeLocation: 's3://shieldcraft-dev-analytics' },
            eventbridge: { dataBus: 'shieldcraft-dev-data-bus', securityBus: 'shieldcraft-dev-security-bus' },
        },
    },
    staging: {
        label: 'Staging',
        account: '879584803102',
        region: 'af-south-1',
        vpcId: 'vpc-shieldcraft-staging',
        buckets: [
            'shieldcraft-staging-raw',
            'shieldcraft-staging-processed',
            'shieldcraft-staging-analytics',
        ],
        subnets: 3,
        services: {
            msk: 'managed',
            opensearch: 'managed',
            airbyte: 'ecs_managed',
            data_quality: 'managed',
            sagemaker: 'managed',
        },
        stepfunctionsType: 'standard',
        details: {
            msk: { mode: 'managed', clusterName: 'shieldcraft-msk-cluster-staging', brokerNodes: 3, instanceType: 'kafka.m5.large' },
            opensearch: { mode: 'managed', domainName: 'shieldcraft-opensearch-staging', instanceType: 't3.small.search', instanceCount: 2 },
            airbyte: { mode: 'ecs_managed', deploymentType: 'ecs', minTasks: 1, maxTasks: 3 },
            data_quality: { mode: 'managed', framework: 'deequ', schedule: 'cron(0 3 * * ? *)' },
            sagemaker: { mode: 'managed', trainingInstanceType: 'ml.m5.xlarge', inferenceInstanceType: 'ml.m5.large', autoscaling: true },
            glue: { databaseName: 'shieldcraft_staging_db', crawlerSchedule: 'cron(0 2 * * ? *)' },
            lakeformation: { dataLakeLocation: 's3://shieldcraft-staging-analytics' },
            eventbridge: { dataBus: 'shieldcraft-staging-data-bus', securityBus: 'shieldcraft-staging-security-bus' },
        },
    },
    prod: {
        label: 'Production',
        account: '879584803102',
        region: 'af-south-1',
        vpcId: 'vpc-shieldcraft-prod',
        buckets: [
            'shieldcraft-prod-raw',
            'shieldcraft-prod-processed',
            'shieldcraft-prod-analytics',
        ],
        subnets: 4,
        services: {
            msk: 'managed',
            opensearch: 'managed',
            airbyte: 'ecs_managed',
            data_quality: 'managed',
            sagemaker: 'managed',
        },
        stepfunctionsType: 'standard',
        details: {
            msk: { mode: 'managed', clusterName: 'shieldcraft-msk-cluster-prod', brokerNodes: 6, instanceType: 'kafka.m5.large' },
            opensearch: { mode: 'managed', domainName: 'shieldcraft-opensearch-prod', instanceType: 'r6g.large.search', instanceCount: 3 },
            airbyte: { mode: 'ecs_managed', deploymentType: 'ecs', minTasks: 2, maxTasks: 6 },
            data_quality: { mode: 'managed', framework: 'deequ', schedule: 'cron(0 3 * * ? *)' },
            sagemaker: { mode: 'managed', trainingInstanceType: 'ml.m5.xlarge', inferenceInstanceType: 'ml.m5.large', autoscaling: true },
            glue: { databaseName: 'shieldcraft_prod_db', crawlerSchedule: 'cron(0 2 * * ? *)' },
            lakeformation: { dataLakeLocation: 's3://shieldcraft-prod-analytics' },
            eventbridge: { dataBus: 'shieldcraft-prod-data-bus', securityBus: 'shieldcraft-prod-security-bus' },
        },
    },
};

export const serviceDescriptions: Record<keyof EnvSummary['services'], string> = {
    msk: 'Kafka streaming backbone (Amazon MSK or external).',
    opensearch: 'Search and analytics (Amazon OpenSearch Service).',
    airbyte: 'Data ingestion connectors (Airbyte on ECS).',
    data_quality: 'Data quality checks (Deequ / managed).',
    sagemaker: 'Model training/hosting (Amazon SageMaker).',
};

export const dependencyEdges: Array<[string, string]> = [
    ['Networking', 'IAM'],
    ['Networking', 'S3'],
    ['Networking', 'MSK'],
    ['Networking', 'Glue'],
    ['Networking', 'Lambda'],
    ['Networking', 'LakeFormation'],
    ['Networking', 'OpenSearch'],
    ['Networking', 'DataQuality'],
    ['Networking', 'SageMaker'],
    ['Networking', 'CloudNativeHardening'],
    ['IAM', 'Glue'],
    ['IAM', 'Lambda'],
    ['IAM', 'LakeFormation'],
    ['IAM', 'OpenSearch'],
    ['IAM', 'SageMaker'],
    ['S3', 'Glue'],
    ['Glue', 'DataQuality'],
    ['Lambda', 'DataQuality'],
    ['MSK', 'CloudNativeHardening'],
    ['Lambda', 'CloudNativeHardening'],
    ['OpenSearch', 'CloudNativeHardening'],
];
