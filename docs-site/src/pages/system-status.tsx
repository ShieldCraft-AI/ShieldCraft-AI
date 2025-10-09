import React from 'react';
import PortalLayout from '../components/PortalLayout';
import FilterToolbar from '../components/FilterToolbar/FilterToolbar';
import styles from './system-status.module.css';
import { usePortalMock } from '../context/PortalMockContext';

type Status = 'Operational' | 'Degraded' | 'Maintenance' | 'Outage';

type ComponentStatus = {
    component: string;
    status: Status;
    details: string;
};

const componentsCatalog = [
    { component: 'Data Ingestion Pipeline', details: ['Streaming stable; last event 3s ago', 'Ingest buffer at 41%', 'No backpressure observed'] },
    { component: 'AI Core Model Server', details: ['Healthy; 2/2 nodes online', 'Avg latency: 64ms', 'Cold starts: 0 today'] },
    { component: 'Vector Database', details: ['Index health nominal', 'Compaction running on shard 3', 'Read P95 within SLO'] },
    { component: 'Alerting Subsystem', details: ['Email/SMS/Slack active', 'Queue depth: 0', 'Dispatch success 99.98%'] },
    { component: 'Remediation Engine', details: ['Runbooks available', 'No pending approvals', 'Policy sync up-to-date'] },
    { component: 'ETL Orchestrator', details: ['Next job: 10:15 UTC', 'Last DAG success', 'No task retries pending'] },
    { component: 'Threat Intel Collector', details: ['Feeds: 12/12 synced', 'Delta updates enabled', 'Burst schedule OK'] },
    { component: 'API Gateway', details: ['P95: 112ms', 'Error rate < 0.1%', 'All stages green'] },
    { component: 'Authentication Service', details: ['OAuth2 tokens valid', 'MFA enforcement 100%', 'Session store responsive'] },
    { component: 'Load Balancer', details: ['All targets healthy', 'Traffic distribution even', 'SSL certs valid 89d'] },
    { component: 'Cache Layer', details: ['Hit rate: 94.2%', 'Eviction policy optimal', 'Memory usage 67%'] },
    { component: 'Message Queue', details: ['Consumers active: 8/8', 'Lag < 500ms', 'DLQ empty'] },
    { component: 'Backup Service', details: ['Last backup: 02:00 UTC', 'Retention policy met', 'Restore tests passing'] },
    { component: 'CDN Network', details: ['Edge nodes: 24/24 up', 'Cache purge ready', 'Origin latency 45ms'] },
    { component: 'Monitoring Stack', details: ['Metrics flowing', 'Dashboards accessible', 'Alertmanager synced'] },
    { component: 'Compliance Scanner', details: ['Last scan: 3h ago', 'Violations: 0 critical', 'Audit log shipping'] },
];

function deriveEnvStatuses(env: 'dev' | 'staging' | 'prod'): ComponentStatus[] {
    // Use a deterministic seeded RNG based on env so switching environments
    // produces different, but repeatable, fake data. This simulates live
    // differences between dev/staging/prod while remaining testable.

    // simple string -> 32-bit seed hash (cyrb32)
    const seedFromString = (s: string) => {
        let h = 2166136261 >>> 0;
        for (let i = 0; i < s.length; i++) {
            h ^= s.charCodeAt(i);
            h = Math.imul(h, 16777619) >>> 0;
        }
        return h >>> 0;
    };

    // mulberry32 PRNG
    const mulberry32 = (a: number) => {
        return () => {
            a |= 0;
            a = (a + 0x6D2B79F5) | 0;
            let t = Math.imul(a ^ (a >>> 15), 1 | a);
            t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    };

    const seed = seedFromString(env);
    const rnd = mulberry32(seed);

    // environment-tuned thresholds (lower is better for prod)
    const thresholds: Record<typeof env, { outage: number; maintenance: number; degraded: number }> = {
        dev: { outage: 0.06, maintenance: 0.20, degraded: 0.45 },
        staging: { outage: 0.03, maintenance: 0.12, degraded: 0.30 },
        prod: { outage: 0.01, maintenance: 0.07, degraded: 0.18 },
    };

    const t = thresholds[env];

    return componentsCatalog.map((c, i) => {
        // derive a per-item pseudo-random value
        const r1 = rnd();
        const r2 = rnd();

        // determine status from r1
        let status: Status = 'Operational';
        if (r1 < t.outage) status = 'Outage';
        else if (r1 < t.maintenance) status = 'Maintenance';
        else if (r1 < t.degraded) status = 'Degraded';

        // pick or slightly vary a details line
        const baseDetails = c.details[i % c.details.length];
        // add a small numeric tweak to make each env distinct (latency, buffer, nodes)
        const tweakNum = Math.round((r2 * (env === 'prod' ? 200 : env === 'staging' ? 400 : 800)));

        // heuristics to append sensible-looking metrics to existing details
        let details = baseDetails;
        if (/latency|p95|p99|avg/i.test(baseDetails)) {
            details = baseDetails.replace(/\d+ms/, `${Math.max(10, tweakNum)}ms`);
        } else if (/buffer|depth|lag|queue/i.test(baseDetails)) {
            details = baseDetails.replace(/\d+%|< \d+ms|< \d+/, `${Math.max(0, tweakNum % 100)}%`);
        } else if (/nodes|targets|consumers|feeds/i.test(baseDetails)) {
            details = `${baseDetails} (${Math.max(1, 1 + (t.degraded > 0.3 ? Math.floor(r2 * 3) : Math.floor(r2 * 1)))} nodes)`;
        } else if (/Last backup|Next job|Last scan/i.test(baseDetails)) {
            details = `${baseDetails} (sim ${env.toUpperCase()})`;
        } else {
            // fallback: append a small env-specific hint
            details = `${baseDetails} • ${env.toUpperCase()} view (${tweakNum})`;
        }

        return {
            component: c.component,
            status,
            details,
        };
    });
}

function SystemStatusContent() {
    const { env, searchQuery } = usePortalMock();
    const items = React.useMemo(() => deriveEnvStatuses(env), [env]);
    const [statusFilter, setStatusFilter] = React.useState<Status | 'all'>('all');
    // Use global search from header
    const effectiveQuery = searchQuery.toLowerCase();

    // Calculate counts from ALL items (not filtered), so they remain constant
    const counts = React.useMemo(() => items.reduce(
        (acc, it) => {
            acc[it.status]++;
            return acc;
        },
        { Operational: 0, Degraded: 0, Maintenance: 0, Outage: 0 } as Record<Status, number>
    ), [items]);

    // Overall status based on all items, not filtered subset
    const overall = counts.Outage > 0
        ? 'Partial Outage'
        : counts.Degraded > 0
            ? 'Degraded Performance'
            : counts.Maintenance > 0
                ? 'Maintenance Ongoing'
                : 'All Systems Operational';

    const filtered = React.useMemo(() => {
        const q = effectiveQuery;
        let results = items;
        if (statusFilter !== 'all') {
            results = results.filter(it => it.status === statusFilter);
        }
        if (q) {
            results = results.filter(it => it.component.toLowerCase().includes(q) || it.details.toLowerCase().includes(q));
        }
        return results;
    }, [items, effectiveQuery, statusFilter]);

    const [lastUpdated, setLastUpdated] = React.useState<string>(() => new Date().toLocaleTimeString('en-GB', { hour12: false }) + ' UTC');
    React.useEffect(() => {
        const id = setInterval(() => setLastUpdated(new Date().toLocaleTimeString('en-GB', { hour12: false }) + ' UTC'), 30000);
        return () => clearInterval(id);
    }, []);

    return (
        <>
            <FilterToolbar
                groups={[
                    {
                        label: 'Status',
                        options: [
                            { value: 'all', label: 'All', count: items.length },
                            { value: 'Operational', label: 'Operational', count: counts.Operational },
                            { value: 'Degraded', label: 'Degraded', count: counts.Degraded },
                            { value: 'Maintenance', label: 'Maintenance', count: counts.Maintenance },
                            { value: 'Outage', label: 'Outage', count: counts.Outage },
                        ],
                        activeValue: statusFilter,
                        onChange: (value) => setStatusFilter(value as Status | 'all'),
                    },
                ]}
                summaryStats={
                    <>
                        <span className={styles.overall}>
                            <span className={`${styles.dot} ${overall === 'All Systems Operational' ? styles.ok : counts.Outage > 0 ? styles.outage : counts.Degraded > 0 ? styles.degraded : styles.maintenance}`}></span>
                            {overall}
                        </span>
                        <span>•</span>
                        <span>Last updated: {lastUpdated}</span>
                    </>
                }
            />

            <div className={styles.statusGrid}>
                {filtered.map((item) => (
                    <div
                        key={item.component}
                        className={`${styles.statusCard} ${styles[item.status.toLowerCase() as 'operational' | 'degraded' | 'maintenance' | 'outage']}`}
                        aria-label={`${item.component} status ${item.status}`}
                        onClick={() => {
                            // Show detailed modal or expand card (not logging in production)
                            // In a real app, this would open a detailed view
                        }}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                // activate keyboard action
                            }
                        }}
                        tabIndex={0}
                        role="button"
                    >
                        <div className={styles.cardHeader}>
                            <h3>{item.component}</h3>
                            <span className={styles.statusBadge}>{item.status}</span>
                        </div>
                        <p className={styles.statusDetails}>{item.details}</p>
                    </div>
                ))}
            </div>

            {filtered.length === 0 && (
                <div style={{ marginTop: 12, color: '#94a3b8' }}>No components match your search.</div>
            )}

            <div className={styles.legend} aria-hidden>
                <span className={styles.legendItem}><span className={`${styles.dot} ${styles.ok}`}></span> Operational</span>
                <span className={styles.legendItem}><span className={`${styles.dot} ${styles.degraded}`}></span> Degraded</span>
                <span className={styles.legendItem}><span className={`${styles.dot} ${styles.maintenance}`}></span> Maintenance</span>
                <span className={styles.legendItem}><span className={`${styles.dot} ${styles.outage}`}></span> Outage</span>
            </div>
        </>
    );
}

export default function SystemStatusPage() {
    return (
        <PortalLayout title="System Status" description="System Status in ShieldCraft AI">
            <SystemStatusContent />
        </PortalLayout>
    );
}
