import type { Capability, Env, ServiceRef } from './types';

const svc = (name: string, description?: string, awsLink?: string): ServiceRef => ({ name, description, awsLink });

export const defaultEnv: Env = 'dev';

export const capabilities: Capability[] = [
    {
        id: 'node_ingestion',
        title: 'Ingestion',
        summary: 'Bring signals from cloud and SaaS into the data plane.',
        viewTags: ['data-plane'],
        recommendedByEnv: {
            dev: svc('EventBridge Pipes'),
            staging: svc('Kinesis Data Streams'),
            prod: svc('Kinesis Data Streams'),
        },
        alternatives: [
            { service: 'MSK', whenToChoose: 'Kafka-first enterprises or strict Kafka compatibility' },
            { service: 'AppFlow', whenToChoose: 'SaaS connectors required' },
        ],
        proofLinks: [],
    },
    {
        id: 'node_correlation',
        title: 'Correlation / Stream Processing',
        summary: 'Correlate, enrich, and score events in motion.',
        viewTags: ['data-plane'],
        recommendedByEnv: {
            dev: svc('Lambda'),
            staging: svc('Kinesis Data Analytics'),
            prod: svc('Kinesis Data Analytics'),
        },
        alternatives: [
            { service: 'MSK + Flink', whenToChoose: 'Kafka estate and long-running jobs' },
            { service: 'ECS on Fargate', whenToChoose: 'Custom runtimes or heavy workloads' },
        ],
        proofLinks: [],
    },
    {
        id: 'node_guardrails',
        title: 'Guardrails / Policy',
        summary: 'Prevent unsafe actions with policy and boundaries.',
        viewTags: ['guardrails'],
        recommendedByEnv: {
            dev: svc('SCPs & IAM Boundaries'),
            staging: svc('AWS Config'),
            prod: svc('AWS Config & Control Tower'),
        },
        alternatives: [
            { service: 'Bedrock Guardrails', whenToChoose: 'GenAI actions need content guardrails' },
        ],
        proofLinks: [],
    },
    {
        id: 'node_actions',
        title: 'Actions / Remediation',
        summary: 'Policy-guarded changes applied to cloud assets.',
        viewTags: ['actions'],
        recommendedByEnv: {
            dev: svc('Lambda'),
            staging: svc('SSM Automation'),
            prod: svc('SSM Automation'),
        },
        alternatives: [
            { service: 'CloudFormation StackSets', whenToChoose: 'Org-wide posture updates' },
        ],
        proofLinks: [],
    },
    {
        id: 'node_observability',
        title: 'Observability',
        summary: 'Logs, metrics, traces, and posture aggregation.',
        viewTags: ['observability'],
        recommendedByEnv: {
            dev: svc('CloudWatch'),
            staging: svc('CloudWatch, Security Hub'),
            prod: svc('CloudWatch, Security Hub, GuardDuty'),
        },
        alternatives: [
            { service: 'OpenTelemetry Collector', whenToChoose: 'External observability backends' },
        ],
        proofLinks: [],
    },
];
