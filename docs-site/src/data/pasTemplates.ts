export type PaSTemplate = {
    id: string;
    kind: 'environment' | 'service';
    name: string;
    file: string;
    description?: string;
    domain?: string;
};

export const pasTemplates: PaSTemplate[] = [
    { id: 'networking-environment', kind: 'environment', name: 'Networking Environment', file: 'proton/networking-environment-template.yaml', description: 'VPC, subnets, and base networking used by service templates.' },
    { id: 'airbyte-service', kind: 'service', name: 'Airbyte', file: 'proton/airbyte-service-template.yaml', domain: 'ingestion/connectors' },
    { id: 'attack-simulation-service', kind: 'service', name: 'Attack Simulation', file: 'proton/attack_simulation-service-template.yaml', domain: 'security/testing' },
    { id: 'budget-service', kind: 'service', name: 'Budget', file: 'proton/budget-service-template.yaml', domain: 'finops' },
    { id: 'cloud-native-hardening-service', kind: 'service', name: 'Cloud Native Hardening', file: 'proton/cloud_native_hardening-service-template.yaml', domain: 'security' },
    { id: 'compliance-service', kind: 'service', name: 'Compliance', file: 'proton/compliance-service-template.yaml', domain: 'security/compliance' },
    { id: 'controltower-service', kind: 'service', name: 'Control Tower', file: 'proton/controltower-service-template.yaml', domain: 'governance' },
    { id: 'dataquality-service', kind: 'service', name: 'Data Quality', file: 'proton/dataquality-service-template.yaml', domain: 'data/quality' },
    { id: 'eventbridge-service', kind: 'service', name: 'EventBridge', file: 'proton/eventbridge-service-template.yaml', domain: 'orchestration' },
    { id: 'glue-service', kind: 'service', name: 'Glue', file: 'proton/glue-service-template.yaml', domain: 'data/catalog-etl' },
    { id: 'iam-service', kind: 'service', name: 'IAM', file: 'proton/iam-service-template.yaml', domain: 'identity' },
    { id: 'lakeformation-service', kind: 'service', name: 'Lake Formation', file: 'proton/lakeformation-service-template.yaml', domain: 'data/governance' },
    { id: 'lambda-service', kind: 'service', name: 'Lambda', file: 'proton/lambda-service-template.yaml', domain: 'compute/serverless' },
    { id: 'msk-service', kind: 'service', name: 'MSK', file: 'proton/msk-service-template.yaml', domain: 'streaming' },
    { id: 'opensearch-service', kind: 'service', name: 'OpenSearch', file: 'proton/opensearch-service-template.yaml', domain: 'search' },
    { id: 's3-service', kind: 'service', name: 'S3', file: 'proton/s3-service-template.yaml', domain: 'storage' },
    { id: 'sagemaker-service', kind: 'service', name: 'SageMaker', file: 'proton/sagemaker-service-template.yaml', domain: 'ml' },
    { id: 'secrets-manager-service', kind: 'service', name: 'Secrets Manager', file: 'proton/secrets_manager-service-template.yaml', domain: 'security/secrets' },
    { id: 'security-service', kind: 'service', name: 'Security', file: 'proton/security-service-template.yaml', domain: 'security' },
    { id: 'stepfunctions-service', kind: 'service', name: 'Step Functions', file: 'proton/stepfunctions-service-template.yaml', domain: 'orchestration' },
];
