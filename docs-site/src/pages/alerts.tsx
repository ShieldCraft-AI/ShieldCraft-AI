import React from 'react';
import PortalLayout from '../components/PortalLayout';
import styles from './alerts.module.css';

type Severity = 'High' | 'Medium' | 'Low';

type Alert = {
    id: number;
    severity: Severity;
    description: string;
    timestamp: string;
    // mock extras for detail view
    service?: string;
    resource?: string;
    account?: string;
    region?: string;
};

const mockAlerts: Alert[] = [
    { id: 1, severity: 'High', description: 'Suspicious login detected from new IP address', timestamp: '2025-08-16 10:00:00 UTC', service: 'IAM', resource: 'user/admin', account: '123456789012', region: 'us-east-1' },
    { id: 2, severity: 'Medium', description: 'Anomalous S3 bucket access pattern observed', timestamp: '2025-08-16 09:30:00 UTC', service: 'S3', resource: 'bucket/prod-logs', account: '123456789012', region: 'us-west-2' },
    { id: 3, severity: 'High', description: 'Potential SQL Injection attempt on "production-db"', timestamp: '2025-08-16 09:15:00 UTC', service: 'RDS', resource: 'instance/prod-db', account: '123456789012', region: 'eu-west-1' },
    { id: 4, severity: 'Low', description: 'Multiple failed login attempts for user "admin"', timestamp: '2025-08-16 08:45:00 UTC', service: 'IAM', resource: 'user/admin', account: '123456789012', region: 'us-east-2' },
    // add a few more to exercise pagination
    { id: 5, severity: 'Low', description: 'Open security group detected on dev instance', timestamp: '2025-08-16 08:30:00 UTC', service: 'EC2', resource: 'sg-1234abcd', account: '123456789012', region: 'ap-south-1' },
    { id: 6, severity: 'Medium', description: 'GuardDuty: UnauthorizedAccess:IAMUser/ConsoleLogin', timestamp: '2025-08-16 08:20:00 UTC', service: 'GuardDuty', resource: 'finding/abcd', account: '123456789012', region: 'us-east-1' },
    { id: 7, severity: 'High', description: 'Inspector: Critical package vulnerability detected', timestamp: '2025-08-16 08:05:00 UTC', service: 'Inspector', resource: 'instance/i-0abcd', account: '123456789012', region: 'us-east-1' },
    { id: 8, severity: 'Low', description: 'CloudTrail: Root API call detected', timestamp: '2025-08-16 08:00:00 UTC', service: 'CloudTrail', resource: 'event/root', account: '123456789012', region: 'us-east-1' },
];

function AlertsPage() {
    const [filter, setFilter] = React.useState<'All' | Severity>('All');
    const [query, setQuery] = React.useState('');
    const [sortKey, setSortKey] = React.useState<'severity' | 'timestamp' | 'description'>('timestamp');
    const [sortDir, setSortDir] = React.useState<'asc' | 'desc'>('desc');
    const [expanded, setExpanded] = React.useState<number | null>(null);
    const [page, setPage] = React.useState(1);
    const pageSize = 5;

    const counts = React.useMemo(() =>
        mockAlerts.reduce((acc, a) => { acc[a.severity]++; return acc; }, { High: 0, Medium: 0, Low: 0 } as Record<Severity, number>), []);

    const filtered = React.useMemo(() => {
        const q = query.trim().toLowerCase();
        return mockAlerts.filter(a =>
            (filter === 'All' || a.severity === filter) &&
            (!q || a.description.toLowerCase().includes(q) || a.service?.toLowerCase().includes(q) || a.resource?.toLowerCase().includes(q))
        );
    }, [filter, query]);

    const sorted = React.useMemo(() => {
        const arr = [...filtered];
        arr.sort((a, b) => {
            let av: string = '';
            let bv: string = '';
            if (sortKey === 'severity') { av = a.severity; bv = b.severity; }
            if (sortKey === 'timestamp') { av = a.timestamp; bv = b.timestamp; }
            if (sortKey === 'description') { av = a.description; bv = b.description; }
            const cmp = av.localeCompare(bv);
            return sortDir === 'asc' ? cmp : -cmp;
        });
        return arr;
    }, [filtered, sortKey, sortDir]);

    const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
    const paged = React.useMemo(() => sorted.slice((page - 1) * pageSize, page * pageSize), [sorted, page]);

    const onSort = (key: typeof sortKey) => {
        setPage(1);
        if (key === sortKey) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
        else { setSortKey(key); setSortDir('desc'); }
    };

    const arrow = (key: typeof sortKey) => sortKey === key ? (sortDir === 'asc' ? '▲' : '▼') : '↕';

    return (
        <PortalLayout title="Active Alerts" description="Active Alerts in ShieldCraft AI">
            <h1>Active Alerts</h1>
            <div className={styles.summaryBar}>
                <span><b>{mockAlerts.length}</b> total</span>
                <span>•</span>
                <span>High <b>{counts.High}</b></span>
                <span>Medium <b>{counts.Medium}</b></span>
                <span>Low <b>{counts.Low}</b></span>
                <span style={{ marginLeft: 'auto' }}>Last updated: just now</span>
            </div>

            <div className={styles.toolbar}>
                <input
                    className={styles.search}
                    placeholder="Search description, service, resource…"
                    value={query}
                    onChange={e => { setQuery(e.target.value); setPage(1); }}
                    aria-label="Search alerts"
                />
                <div className={styles.filtersRow}>
                    {(['All', 'High', 'Medium', 'Low'] as const).map(f => (
                        <button key={f} className={styles.pill} aria-pressed={filter === f} onClick={() => { setFilter(f); setPage(1); }}>
                            {f}
                        </button>
                    ))}
                </div>
            </div>

            <section className={styles.alertsContainer}>
                <table className={styles.alertsTable} aria-label="Active alerts table">
                    <colgroup>
                        <col style={{ width: 120 }} />
                        <col />
                        <col style={{ width: 240 }} />
                        <col style={{ width: 140 }} />
                    </colgroup>
                    <caption className="sr-only">Active alerts</caption>
                    <thead>
                        <tr>
                            <th scope="col" className={styles.thSortable} onClick={() => onSort('severity')}>
                                <span className={styles.thLabel}>Severity <span className={styles.sortArrow}>{arrow('severity')}</span></span>
                            </th>
                            <th scope="col" className={styles.thSortable} onClick={() => onSort('description')}>
                                <span className={styles.thLabel}>Description <span className={styles.sortArrow}>{arrow('description')}</span></span>
                            </th>
                            <th scope="col" className={styles.thSortable} onClick={() => onSort('timestamp')}>
                                <span className={styles.thLabel}>Timestamp <span className={styles.sortArrow}>{arrow('timestamp')}</span></span>
                            </th>
                            <th scope="col">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {paged.map(alert => (
                            <React.Fragment key={alert.id}>
                                <tr className={`${styles[alert.severity.toLowerCase() as 'high' | 'medium' | 'low']} ${styles.rowHover}`} onClick={() => setExpanded(expanded === alert.id ? null : alert.id)} style={{ cursor: 'pointer' }}>
                                    <td><span className={styles.severity}>{alert.severity}</span></td>
                                    <td>{alert.description}</td>
                                    <td>{alert.timestamp}</td>
                                    <td><button className="button button--primary button--sm" onClick={(e) => { e.stopPropagation(); }}>Investigate</button></td>
                                </tr>
                                {expanded === alert.id && (
                                    <tr className={styles.detailsRow}>
                                        <td colSpan={4}>
                                            <div className={styles.kvGrid}>
                                                <div className={styles.kvItem}><div className={styles.kvLabel}>Service</div><div className={styles.kvValue}>{alert.service}</div></div>
                                                <div className={styles.kvItem}><div className={styles.kvLabel}>Resource</div><div className={styles.kvValue}>{alert.resource}</div></div>
                                                <div className={styles.kvItem}><div className={styles.kvLabel}>Account</div><div className={styles.kvValue}>{alert.account}</div></div>
                                                <div className={styles.kvItem}><div className={styles.kvLabel}>Region</div><div className={styles.kvValue}>{alert.region}</div></div>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </React.Fragment>
                        ))}
                        {paged.length === 0 && (
                            <tr>
                                <td colSpan={4} style={{ padding: 16, color: '#94a3b8' }}>No alerts match your search/filter.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </section>

            <div className={styles.pagination} role="navigation" aria-label="Alerts pagination">
                <button className={styles.pageBtn} disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>Prev</button>
                <span>Page {page} of {totalPages}</span>
                <button className={styles.pageBtn} disabled={page >= totalPages} onClick={() => setPage(p => Math.min(totalPages, p + 1))}>Next</button>
            </div>
        </PortalLayout>
    );
}

export default AlertsPage;
