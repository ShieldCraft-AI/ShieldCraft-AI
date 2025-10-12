import React from 'react';

export type Severity = 'High' | 'Medium' | 'Low';

export type Alert = {
    id: number;
    severity: Severity;
    description: string;
    timestamp: string;
    service?: string;
    resource?: string;
    account?: string;
    region?: string;
    resolved?: boolean;
};

type PortalMockState = {
    env: 'dev' | 'staging' | 'prod';
    setEnv: (env: 'dev' | 'staging' | 'prod') => void;

    // Global portal search (header search box)
    searchQuery: string;
    setSearchQuery: (q: string) => void;

    alerts: Alert[];
    setAlerts: React.Dispatch<React.SetStateAction<Alert[]>>;

    // Derived metrics
    counts: { High: number; Medium: number; Low: number; total: number };
    findings24h: number;
    criticalCount: number;
    meanTTR: string;
    coverage: number;

    markResolved: (id: number) => void;
    addMockAlert: (partial?: Partial<Alert>) => void;
};

const PortalMockContext = React.createContext<PortalMockState | undefined>(undefined);

type EnvProfile = {
    label: string;
    account: string;
    regionRotation: string[];
    descriptionTag: string;
    serviceSuffix: string;
    resourceSuffix: string;
    timestampOffsetMinutes: number;
    perItemDriftMinutes: number;
};

const SERVICE_FRIENDLY_NAMES: Record<string, string> = {
    GuardDuty: 'Amazon GuardDuty',
    S3: 'Amazon S3',
    WAF: 'AWS WAF',
    IAM: 'AWS Identity and Access Management',
    SecurityHub: 'AWS Security Hub',
    CloudTrail: 'AWS CloudTrail',
    Inspector: 'Amazon Inspector',
    RDS: 'Amazon RDS',
    KMS: 'AWS Key Management Service',
    EKS: 'Amazon EKS',
    Lambda: 'AWS Lambda',
    APIGateway: 'Amazon API Gateway',
    CloudFront: 'Amazon CloudFront',
    VPC: 'Amazon VPC',
    ECR: 'Amazon ECR',
    SecretsManager: 'AWS Secrets Manager',
    Kinesis: 'Amazon Kinesis',
    DynamoDB: 'Amazon DynamoDB',
    ElastiCache: 'Amazon ElastiCache',
    SNS: 'Amazon SNS',
};

const ENV_PROFILES: Record<'dev' | 'staging' | 'prod', EnvProfile> = {
    dev: {
        label: 'Dev',
        account: '111111111111',
        regionRotation: ['eu-north-1', 'us-west-2', 'ap-southeast-2', 'ca-central-1'],
        descriptionTag: 'DEV',
        serviceSuffix: ' · Dev',
        resourceSuffix: ' [dev]',
        timestampOffsetMinutes: -360,
        perItemDriftMinutes: -4,
    },
    staging: {
        label: 'Staging',
        account: '222222222222',
        regionRotation: ['us-east-2', 'eu-west-2', 'ap-northeast-2', 'me-south-1'],
        descriptionTag: 'STAGING',
        serviceSuffix: ' · Staging',
        resourceSuffix: ' [stg]',
        timestampOffsetMinutes: -120,
        perItemDriftMinutes: -3,
    },
    prod: {
        label: 'Prod',
        account: '333333333333',
        regionRotation: ['us-east-1', 'eu-west-1', 'ap-northeast-1', 'sa-east-1'],
        descriptionTag: 'PROD',
        serviceSuffix: ' · Prod',
        resourceSuffix: ' [prod]',
        timestampOffsetMinutes: 0,
        perItemDriftMinutes: -2,
    },
};

const parseTimestamp = (timestamp: string): Date | null => {
    const iso = timestamp.replace(' ', 'T').replace(' UTC', 'Z');
    const date = new Date(iso);
    return Number.isNaN(date.getTime()) ? null : date;
};

const pad = (value: number) => value.toString().padStart(2, '0');

const formatUtcTimestamp = (date: Date): string => `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())} UTC`;

const stripEnvDescriptionTag = (description: string): string => description.replace(/^\[(DEV|STAGING|PROD)\]\s*/i, '').trim();

const withEnvDescriptionTag = (description: string, profile: EnvProfile): string => {
    const base = stripEnvDescriptionTag(description);
    return `[${profile.descriptionTag}] ${base}`.trim();
};

const canonicalServiceName = (service: string): string => {
    const friendly = SERVICE_FRIENDLY_NAMES[service];
    if (friendly) return friendly;
    const reverse = Object.values(SERVICE_FRIENDLY_NAMES).find(value => value === service);
    if (reverse) return service;
    return service.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/\s+/g, ' ').trim();
};

const withEnvServiceTag = (service: string | undefined, profile: EnvProfile): string | undefined => {
    if (!service) return service;
    const normalized = service.replace(/\s+·\s+(Dev|Staging|Prod)$/i, '').trim();
    const canonical = canonicalServiceName(normalized);
    return `${canonical}${profile.serviceSuffix}`;
};

const withEnvResourceTag = (resource: string | undefined, profile: EnvProfile): string | undefined => {
    if (!resource) return resource;
    if (resource.endsWith(profile.resourceSuffix)) return resource;
    return `${resource}${profile.resourceSuffix}`;
};

const deriveTimestampForEnv = (timestamp: string, profile: EnvProfile, index: number): string => {
    const parsed = parseTimestamp(timestamp);
    if (!parsed) return timestamp;
    const adjusted = new Date(parsed.getTime());
    adjusted.setUTCMinutes(adjusted.getUTCMinutes() + profile.timestampOffsetMinutes + profile.perItemDriftMinutes * index);
    return formatUtcTimestamp(adjusted);
};

const datasetMatchesEnv = (env: 'dev' | 'staging' | 'prod', dataset: Alert[], requiredCount: number): boolean => {
    if (dataset.length < requiredCount) return false;
    const profile = ENV_PROFILES[env];
    const accountMatches = dataset.every(alert => alert.account === profile.account);
    const suffix = profile.serviceSuffix.trim().toLowerCase();
    const serviceMatches = dataset.some(alert => typeof alert.service === 'string' && alert.service.toLowerCase().includes(suffix));
    return accountMatches && serviceMatches;
};

const initialAlerts: Alert[] = [
    {
        id: 1,
        severity: 'High',
        description: 'GuardDuty: EC2 instance communicating with known C2 domain',
        timestamp: '2025-09-27 10:18:04 UTC',
        service: 'GuardDuty',
        resource: 'instance/i-0f2c9e21',
        account: '123456789012',
        region: 'us-east-1',
    },
    {
        id: 2,
        severity: 'Medium',
        description: 'S3: Public READ detected on bucket logs-archive',
        timestamp: '2025-09-27 09:56:10 UTC',
        service: 'S3',
        resource: 'bucket/logs-archive',
        account: '123456789012',
        region: 'us-west-2',
    },
    {
        id: 3,
        severity: 'High',
        description: 'WAF: SQLi pattern blocked on /api/v1/search',
        timestamp: '2025-09-27 09:44:51 UTC',
        service: 'WAF',
        resource: 'webacl/prod-edge',
        account: '123456789012',
        region: 'us-east-1',
    },
    {
        id: 4,
        severity: 'Low',
        description: 'IAM: Access key unused for 90 days (user: dataops)',
        timestamp: '2025-09-27 09:28:22 UTC',
        service: 'IAM',
        resource: 'user/dataops',
        account: '123456789012',
        region: 'us-east-2',
    },
    {
        id: 5,
        severity: 'Low',
        description: 'Security Hub: SSM agent not installed on 2 instances',
        timestamp: '2025-09-27 09:20:05 UTC',
        service: 'SecurityHub',
        resource: 'fleet/ssm-missing',
        account: '123456789012',
        region: 'eu-west-1',
    },
    {
        id: 6,
        severity: 'Medium',
        description: 'CloudTrail: Root API call detected (GetAccountSummary)',
        timestamp: '2025-09-27 09:12:33 UTC',
        service: 'CloudTrail',
        resource: 'event/root-activity',
        account: '123456789012',
        region: 'ap-south-1',
    },
    {
        id: 7,
        severity: 'High',
        description: 'Inspector: Critical CVE on AMI base (openssl)',
        timestamp: '2025-09-27 08:59:18 UTC',
        service: 'Inspector',
        resource: 'ami/ami-08ddc',
        account: '123456789012',
        region: 'us-east-1',
    },
    {
        id: 8,
        severity: 'Low',
        description: 'RDS: Publicly accessible flag enabled on dev snapshot',
        timestamp: '2025-09-27 08:47:51 UTC',
        service: 'RDS',
        resource: 'snapshot/dev-db-snap',
        account: '123456789012',
        region: 'eu-central-1',
    },
    {
        id: 9,
        severity: 'Medium',
        description: 'KMS: Key scheduled for deletion still referenced by service account',
        timestamp: '2025-09-27 08:39:10 UTC',
        service: 'KMS',
        resource: 'alias/service-x',
        account: '123456789012',
        region: 'us-east-1',
    },
    {
        id: 10,
        severity: 'Low',
        description: 'EKS: Node joined cluster with outdated AMI baseline',
        timestamp: '2025-09-27 08:31:42 UTC',
        service: 'EKS',
        resource: 'cluster/prod-apps',
        account: '123456789012',
        region: 'us-west-2',
    },
    {
        id: 11,
        severity: 'Medium',
        description: 'Lambda: Over-permissive IAM policy attached to function',
        timestamp: '2025-09-27 08:24:07 UTC',
        service: 'Lambda',
        resource: 'function/report-ingestor',
        account: '123456789012',
        region: 'eu-west-1',
    },
    {
        id: 12,
        severity: 'Medium',
        description: 'API Gateway: Spike in 5xx responses from edge API',
        timestamp: '2025-09-27 08:17:55 UTC',
        service: 'APIGateway',
        resource: 'api/edge-v1',
        account: '123456789012',
        region: 'us-east-2',
    },
    {
        id: 13,
        severity: 'Low',
        description: 'CloudFront: Origin shield disabled for high-traffic distribution',
        timestamp: '2025-09-27 08:10:29 UTC',
        service: 'CloudFront',
        resource: 'dist/E3ABCDEF',
        account: '123456789012',
        region: 'us-east-1',
    },
    {
        id: 14,
        severity: 'Medium',
        description: 'VPC Flow Logs: Unusual port scan pattern from 198.51.100.24',
        timestamp: '2025-09-27 08:04:43 UTC',
        service: 'VPC',
        resource: 'vpc/vpc-0abc12',
        account: '123456789012',
        region: 'ap-southeast-1',
    },
    {
        id: 15,
        severity: 'High',
        description: 'ECR: Image scan detected HIGH severity CVE (openssl)',
        timestamp: '2025-09-27 07:57:16 UTC',
        service: 'ECR',
        resource: 'repo/app-backend:latest',
        account: '123456789012',
        region: 'eu-west-1',
    },
    {
        id: 16,
        severity: 'Medium',
        description: 'Secrets Manager: Secret rotated outside policy window',
        timestamp: '2025-09-27 07:51:02 UTC',
        service: 'SecretsManager',
        resource: 'secret/db-password',
        account: '123456789012',
        region: 'us-east-1',
    },
    {
        id: 17,
        severity: 'High',
        description: 'Kinesis: Stream exposed via overly permissive resource policy',
        timestamp: '2025-09-27 07:44:28 UTC',
        service: 'Kinesis',
        resource: 'stream/events',
        account: '123456789012',
        region: 'us-west-2',
    },
    {
        id: 18,
        severity: 'Low',
        description: 'DynamoDB: Point-in-time recovery disabled for critical table',
        timestamp: '2025-09-27 07:36:15 UTC',
        service: 'DynamoDB',
        resource: 'table/orders',
        account: '123456789012',
        region: 'eu-central-1',
    },
    {
        id: 19,
        severity: 'Medium',
        description: 'ElastiCache: Redis cluster not enforcing TLS',
        timestamp: '2025-09-27 07:29:49 UTC',
        service: 'ElastiCache',
        resource: 'redis/primary',
        account: '123456789012',
        region: 'ap-south-1',
    },
    {
        id: 20,
        severity: 'Medium',
        description: 'SNS: Public subscription created on internal topic',
        timestamp: '2025-09-27 07:21:33 UTC',
        service: 'SNS',
        resource: 'topic/internal-events',
        account: '123456789012',
        region: 'us-east-1',
    },
];

export function PortalMockProvider({ children }: { children: React.ReactNode }) {
    const [env, setEnvState] = React.useState<'dev' | 'staging' | 'prod'>('dev');

    React.useEffect(() => {
        if (typeof window === 'undefined') return;
        try {
            const stored = window.localStorage.getItem('sc-env') as 'dev' | 'staging' | 'prod' | null;
            if (stored && stored !== env) {
                setEnvState(stored);
            }
        } catch {
            /* ignore */
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Global search persisted per browser
    const [searchQuery, setSearchQueryState] = React.useState<string>('');

    React.useEffect(() => {
        if (typeof window === 'undefined') return;
        try {
            const storedSearch = window.localStorage.getItem('sc-portal-search');
            if (storedSearch !== null) {
                setSearchQueryState(storedSearch);
            }
        } catch {
            /* ignore */
        }
    }, []);
    const setSearchQuery = React.useCallback((q: string) => {
        try { window.localStorage.setItem('sc-portal-search', q); } catch { }
        setSearchQueryState(q);
    }, []);

    const setEnv = React.useCallback((e: 'dev' | 'staging' | 'prod') => {
        try { window.localStorage.setItem('sc-env', e); } catch { }
        setEnvState(e);
    }, []);

    // Build environment-specific default alert sets so switching env changes data deterministically.
    const initialAlertsByEnv = React.useMemo(() => {
        const adjustSeverity = (env: 'dev' | 'staging' | 'prod', index: number, severity: Severity): Severity => {
            if (env === 'dev') {
                if (severity === 'High' && index % 3 === 0) return 'Medium';
                if (severity === 'Medium' && index % 4 === 0) return 'Low';
                return severity;
            }
            if (env === 'staging') {
                if (severity === 'Low') return 'Medium';
                if (severity === 'Medium' && index % 5 === 0) return 'High';
                return severity;
            }
            if (severity === 'Low') return 'Medium';
            if (severity === 'Medium') return 'High';
            return 'High';
        };

        const transform = (env: 'dev' | 'staging' | 'prod') => {
            const profile = ENV_PROFILES[env];
            return initialAlerts.map((alert, index) => ({
                ...alert,
                id: index + 1,
                severity: adjustSeverity(env, index, alert.severity),
                description: withEnvDescriptionTag(alert.description, profile),
                timestamp: deriveTimestampForEnv(alert.timestamp, profile, index),
                service: withEnvServiceTag(alert.service, profile),
                resource: withEnvResourceTag(alert.resource, profile),
                account: profile.account,
                region: profile.regionRotation[index % profile.regionRotation.length],
                resolved: alert.resolved ?? false,
            }));
        };

        return {
            dev: transform('dev'),
            staging: transform('staging'),
            prod: transform('prod'),
        } as Record<'dev' | 'staging' | 'prod', Alert[]>;
    }, []);

    const storageKeyForEnv = (e: 'dev' | 'staging' | 'prod') => `sc-alerts-${e}`;

    const REQUIRED_ALERT_COUNT = initialAlerts.length;

    const resolveAlertsForEnv = (targetEnv: 'dev' | 'staging' | 'prod'): Alert[] => {
        if (typeof window === 'undefined') return initialAlertsByEnv[targetEnv];
        try {
            const saved = window.localStorage.getItem(storageKeyForEnv(targetEnv));
            if (!saved) {
                const legacy = window.localStorage.getItem('sc-alerts');
                if (legacy) {
                    window.localStorage.setItem(storageKeyForEnv(targetEnv), legacy);
                    window.localStorage.removeItem('sc-alerts');
                    const legacyParsed = JSON.parse(legacy) as Alert[];
                    return datasetMatchesEnv(targetEnv, legacyParsed, REQUIRED_ALERT_COUNT) ? legacyParsed : initialAlertsByEnv[targetEnv];
                }
                return initialAlertsByEnv[targetEnv];
            }
            const parsed = JSON.parse(saved) as Alert[];
            return datasetMatchesEnv(targetEnv, parsed, REQUIRED_ALERT_COUNT) ? parsed : initialAlertsByEnv[targetEnv];
        } catch {
            return initialAlertsByEnv[targetEnv];
        }
    };

    const [alerts, setAlerts] = React.useState<Alert[]>(initialAlertsByEnv['dev']);

    // Switch alerts when environment changes
    React.useEffect(() => {
        setAlerts(resolveAlertsForEnv(env));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [env]);

    React.useEffect(() => {
        try { window.localStorage.setItem(storageKeyForEnv(env), JSON.stringify(alerts)); } catch { }
    }, [alerts, env]);

    const counts = React.useMemo(() => {
        const active = alerts.filter(a => !a.resolved);
        return {
            High: active.filter(a => a.severity === 'High').length,
            Medium: active.filter(a => a.severity === 'Medium').length,
            Low: active.filter(a => a.severity === 'Low').length,
            total: active.length,
        };
    }, [alerts]);

    // Display-only: drift coverage mildly
    const [coverage, setCoverage] = React.useState<number>(92);
    React.useEffect(() => {
        const id = setInterval(() => {
            setCoverage(prev => Math.max(88, Math.min(96, prev + (Math.random() - 0.5) * 0.2)));
        }, 4000);
        return () => clearInterval(id);
    }, []);

    const findings24h = counts.total + 120; // pretend more historical
    const criticalCount = counts.High;
    const meanTTR = '14m';

    const markResolved = React.useCallback((id: number) => {
        setAlerts(prev => prev.map(a => (a.id === id ? { ...a, resolved: true } : a)));
    }, []);

    const addMockAlert = React.useCallback((partial?: Partial<Alert>) => {
        setAlerts(prev => {
            const profile = ENV_PROFILES[env];
            const nextId = prev.length ? Math.max(...prev.map(a => a.id)) + 1 : 1;
            const severityChoices: Severity[] = ['High', 'Medium', 'Low'];
            const severity = partial?.severity || severityChoices[Math.floor(Math.random() * severityChoices.length)];
            const description = partial?.description ? withEnvDescriptionTag(partial.description, profile) : `[${profile.descriptionTag}] Synthetic ${profile.label} alert #${nextId}`;
            const timestamp = formatUtcTimestamp(new Date());
            const service = withEnvServiceTag(partial?.service || 'Custom Insight', profile);
            const resource = withEnvResourceTag(partial?.resource || `resource/${profile.label.toLowerCase()}-${nextId}`, profile);
            const regionPool = profile.regionRotation;
            const region = partial?.region || regionPool[nextId % regionPool.length];

            const alert: Alert = {
                id: nextId,
                severity,
                description,
                timestamp,
                service,
                resource,
                account: partial?.account || profile.account,
                region,
                resolved: false,
            };
            return [alert, ...prev];
        });
    }, [env]);

    const value: PortalMockState = {
        env, setEnv,
        searchQuery, setSearchQuery,
        alerts, setAlerts,
        counts,
        findings24h,
        criticalCount,
        meanTTR,
        coverage,
        markResolved,
        addMockAlert,
    };

    return <PortalMockContext.Provider value={value}>{children}</PortalMockContext.Provider>;
}

export function usePortalMock() {
    const ctx = React.useContext(PortalMockContext);
    if (!ctx) throw new Error('usePortalMock must be used within PortalMockProvider');
    return ctx;
}
