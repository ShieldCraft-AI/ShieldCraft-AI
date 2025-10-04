import React from 'react';
import PortalLayout from '../components/PortalLayout';
import FilterToolbar from '../components/FilterToolbar/FilterToolbar';
import styles from './alerts.module.css';
import { usePortalMock, Severity } from '../context/PortalMockContext';

function AlertsContent() {
    const { alerts, counts, markResolved, searchQuery } = usePortalMock();

    const [filter, setFilter] = React.useState<'All' | Severity>('All');
    // Use global search from header
    const effectiveQuery = searchQuery.toLowerCase();
    const [sortKey, setSortKey] = React.useState<'severity' | 'timestamp' | 'description' | 'service'>('timestamp');
    const [sortDir, setSortDir] = React.useState<'asc' | 'desc'>('desc');
    const [expanded, setExpanded] = React.useState<number | null>(null);
    const [page, setPage] = React.useState(1);
    const pageSize = 20;

    const active = React.useMemo(() => alerts.filter(a => !a.resolved), [alerts]);

    const filtered = React.useMemo(() => {
        const q = effectiveQuery;
        return active.filter(a =>
            (filter === 'All' || a.severity === filter) &&
            (!q || a.description.toLowerCase().includes(q) || a.service?.toLowerCase().includes(q) || a.resource?.toLowerCase().includes(q))
        );
    }, [active, filter, effectiveQuery]);

    const sorted = React.useMemo(() => {
        const arr = [...filtered];
        arr.sort((a, b) => {
            let av: string = '';
            let bv: string = '';
            if (sortKey === 'severity') { av = a.severity; bv = b.severity; }
            if (sortKey === 'timestamp') { av = a.timestamp; bv = b.timestamp; }
            if (sortKey === 'service') { av = a.service || ''; bv = b.service || ''; }
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
        <>
            <FilterToolbar
                groups={[
                    {
                        label: 'Severity',
                        options: [
                            { value: 'All', label: 'All' },
                            { value: 'High', label: 'High', count: counts.High },
                            { value: 'Medium', label: 'Medium', count: counts.Medium },
                            { value: 'Low', label: 'Low', count: counts.Low },
                        ],
                        activeValue: filter,
                        onChange: (value) => { setFilter(value as 'All' | Severity); setPage(1); },
                    },
                ]}
                summaryStats={
                    <>
                        <span><b>{active.length}</b> total</span>
                        <span>•</span>
                        <span>High <b>{counts.High}</b></span>
                        <span>Medium <b>{counts.Medium}</b></span>
                        <span>Low <b>{counts.Low}</b></span>
                    </>
                }
            />

            <section className={styles.alertsContainer}>
                <table className={styles.alertsTable} aria-label="Active alerts table">
                    <colgroup>
                        <col style={{ width: '10%' }} />
                        <col style={{ width: '40%' }} />
                        <col style={{ width: '12%' }} />
                        <col style={{ width: '20%' }} />
                        <col style={{ width: '18%' }} />
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
                            <th scope="col" className={styles.thSortable} onClick={() => onSort('service')}>
                                <span className={styles.thLabel}>Service <span className={styles.sortArrow}>{arrow('service')}</span></span>
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
                                    <td>{alert.service}</td>
                                    <td>{alert.timestamp}</td>
                                    <td className={styles.actionCell}>
                                        <div className={styles.actions}>
                                            <button className="button button--primary button--sm" onClick={(e) => { e.stopPropagation(); }}>Investigate</button>
                                            <button className="button button--secondary button--sm" onClick={(e) => { e.stopPropagation(); markResolved(alert.id); }}>Resolve</button>
                                        </div>
                                    </td>
                                </tr>
                                {expanded === alert.id && (
                                    <tr className={styles.detailsRow}>
                                        <td colSpan={5}>
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
                                <td colSpan={5} style={{ padding: 16, color: '#94a3b8' }}>No alerts match your search/filter.</td>
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
        </>
    );
}

export default function AlertsPage() {
    return (
        <PortalLayout title="Active Alerts" description="Active Alerts in ShieldCraft AI">
            <AlertsContent />
        </PortalLayout>
    );
}
