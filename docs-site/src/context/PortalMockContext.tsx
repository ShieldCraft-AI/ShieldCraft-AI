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
    const [env, setEnvState] = React.useState<'dev' | 'staging' | 'prod'>(() => {
        if (typeof window === 'undefined') return 'dev';
        try {
            return (window.localStorage.getItem('sc-env') as 'dev' | 'staging' | 'prod') || 'dev';
        } catch {
            return 'dev';
        }
    });

    // Global search persisted per browser
    const [searchQuery, setSearchQueryState] = React.useState<string>(() => {
        if (typeof window === 'undefined') return '';
        try { return window.localStorage.getItem('sc-portal-search') || ''; } catch { return ''; }
    });
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
        const base = initialAlerts;
        const adjustSeverity = (env: 'dev' | 'staging' | 'prod', i: number, s: Severity): Severity => {
            if (env === 'dev') {
                // dev tends to be less severe
                if (s === 'High' && i % 3 === 0) return 'Medium';
                if (s === 'Medium' && i % 4 === 0) return 'Low';
                return s;
            }
            if (env === 'staging') {
                // staging modestly ups lows and occasionally mediums
                if (s === 'Low') return 'Medium';
                if (s === 'Medium' && i % 5 === 0) return 'High';
                return s;
            }
            // prod is strict: Low -> Medium, Medium -> High, High stays High
            if (s === 'Low') return 'Medium';
            if (s === 'Medium') return 'High';
            return 'High';
        };

        const dev = base.map((a, i) => ({ ...a, id: i + 1, severity: adjustSeverity('dev', i, a.severity) }));
        const staging = base.map((a, i) => ({ ...a, id: i + 1, severity: adjustSeverity('staging', i, a.severity) }));
        const prod = base.map((a, i) => ({ ...a, id: i + 1, severity: adjustSeverity('prod', i, a.severity) }));

        return { dev, staging, prod } as Record<'dev' | 'staging' | 'prod', Alert[]>;
    }, []);

    const storageKeyForEnv = (e: 'dev' | 'staging' | 'prod') => `sc-alerts-${e}`;

    const REQUIRED_ALERT_COUNT = initialAlerts.length;

    const [alerts, setAlerts] = React.useState<Alert[]>(() => {
        if (typeof window === 'undefined') return initialAlertsByEnv['dev'];
        try {
            const currentEnv = (window.localStorage.getItem('sc-env') as 'dev' | 'staging' | 'prod') || 'dev';
            const saved = window.localStorage.getItem(storageKeyForEnv(currentEnv));
            // Back-compat: migrate legacy key if present
            if (!saved) {
                const legacy = window.localStorage.getItem('sc-alerts');
                if (legacy) {
                    window.localStorage.setItem(storageKeyForEnv(currentEnv), legacy);
                    window.localStorage.removeItem('sc-alerts');
                    return JSON.parse(legacy) as Alert[];
                }
            }
            if (saved) {
                const parsed = JSON.parse(saved) as Alert[];
                return parsed.length >= REQUIRED_ALERT_COUNT ? parsed : initialAlertsByEnv[currentEnv];
            }
            return initialAlertsByEnv[currentEnv];
        } catch {
            return initialAlertsByEnv['dev'];
        }
    });

    // Switch alerts when environment changes
    React.useEffect(() => {
        if (typeof window === 'undefined') return;
        try {
            const saved = window.localStorage.getItem(storageKeyForEnv(env));
            if (saved) {
                const parsed = JSON.parse(saved) as Alert[];
                setAlerts(parsed.length >= REQUIRED_ALERT_COUNT ? parsed : initialAlertsByEnv[env]);
            } else {
                setAlerts(initialAlertsByEnv[env]);
            }
        } catch {
            setAlerts(initialAlertsByEnv[env]);
        }
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
            const nextId = prev.length ? Math.max(...prev.map(a => a.id)) + 1 : 1;
            const alert: Alert = {
                id: nextId,
                severity: partial?.severity || (['High', 'Medium', 'Low'] as Severity[])[Math.floor(Math.random() * 3)],
                description: partial?.description || 'New mock alert',
                timestamp: new Date().toISOString(),
                service: partial?.service,
                resource: partial?.resource,
                account: partial?.account,
                region: partial?.region || 'us-east-1',
                resolved: false,
            };
            return [alert, ...prev];
        });
    }, []);

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
