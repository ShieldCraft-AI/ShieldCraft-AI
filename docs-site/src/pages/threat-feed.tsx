import React, { useMemo, useState } from 'react';
import PortalLayout from '../components/PortalLayout';
import styles from './threat-feed.module.css';

type FeedItem = { id: number; source: string; title: string; published: string; tags: string[] };

const mockFeed: FeedItem[] = [
    { id: 1, source: 'AlienVault OTX', title: 'New "CryptoChameleon" Phishing Kit Targets Cryptocurrency Users', published: '1 hour ago', tags: ['phishing', 'cryptocurrency'] },
    { id: 2, source: 'CrowdStrike', title: 'Analysis of WIZARD SPIDER\'s latest Conti variant', published: '4 hours ago', tags: ['ransomware', 'threat actor'] },
    { id: 3, source: 'Mandiant', title: 'UNC4841: A New Chinese Cyber Espionage Group', published: '1 day ago', tags: ['espionage', 'apt'] },
    { id: 4, source: 'Internal Research', title: 'Emerging TTPs for cloud environments observed in the wild', published: '2 days ago', tags: ['cloud', 'ttps'] },
    { id: 5, source: 'CISA KEV', title: 'Known Exploited Vulnerability: CVE-2025-1234 in OpenSSH', published: '3 days ago', tags: ['kev', 'cve', 'exploitation'] },
    { id: 6, source: 'Unit42', title: 'Cloud credential harvesting via SSRF in metadata endpoints', published: '5 days ago', tags: ['cloud', 'ssrf', 'defense evasion'] },
    { id: 7, source: 'Talos', title: 'Malvertising campaign targeting AI tooling users', published: '6 days ago', tags: ['malvertising', 'supply chain'] },
    { id: 8, source: 'Recorded Future', title: 'TrickBot infrastructure shifts to new bulletproof hosts', published: '1 week ago', tags: ['trickbot', 'infrastructure'] },
    { id: 9, source: 'Internal Research', title: 'IAM privilege escalation paths detected in staging', published: '1 week ago', tags: ['iam', 'cloud', 'privilege escalation'] },
    { id: 10, source: 'AlienVault OTX', title: 'IOC set for QakBot resurgence', published: '2 weeks ago', tags: ['ioc', 'qakbot'] },
];

function ThreatFeedPage() {
    const [q, setQ] = useState('');
    const [source, setSource] = useState<string>('all');
    const [tag, setTag] = useState<string>('all');
    const [sort, setSort] = useState<'recent' | 'alpha'>('recent');
    const [page, setPage] = useState(1);
    const pageSize = 6;

    const sources = useMemo(() => Array.from(new Set(mockFeed.map(f => f.source))), []);
    const tags = useMemo(() => Array.from(new Set(mockFeed.flatMap(f => f.tags))).sort(), []);

    const filtered = useMemo(() => {
        const ql = q.trim().toLowerCase();
        let rows = mockFeed.filter(item =>
            (source === 'all' || item.source === source) &&
            (tag === 'all' || item.tags.includes(tag)) &&
            (ql === '' || item.title.toLowerCase().includes(ql))
        );
        if (sort === 'alpha') rows = rows.slice().sort((a, b) => a.title.localeCompare(b.title));
        // recent is the default order in mock
        return rows;
    }, [q, source, tag, sort]);

    const total = filtered.length;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const currentPage = Math.min(page, totalPages);
    const start = (currentPage - 1) * pageSize;
    const pageRows = filtered.slice(start, start + pageSize);

    return (
        <PortalLayout title="Threat Feed" description="Threat Feed in ShieldCraft AI">
            <div className={styles.feedContainer}>
                <div className={styles.summaryBar} aria-live="polite">
                    <b>{total}</b> items • Sources: {sources.length} • Tags: {tags.length}
                </div>

                <div className={styles.toolbar} role="region" aria-label="Feed controls">
                    <input
                        className={styles.search}
                        type="search"
                        placeholder="Search titles..."
                        value={q}
                        onChange={e => { setQ(e.target.value); setPage(1); }}
                        aria-label="Search titles"
                    />
                    <select
                        className={styles.select}
                        value={source}
                        onChange={e => { setSource(e.target.value); setPage(1); }}
                        aria-label="Filter by source"
                    >
                        <option value="all">All sources</option>
                        {sources.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                    <select
                        className={styles.select}
                        value={tag}
                        onChange={e => { setTag(e.target.value); setPage(1); }}
                        aria-label="Filter by tag"
                    >
                        <option value="all">All tags</option>
                        {tags.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                    <div role="group" aria-label="Sort">
                        <button
                            className={styles.pill}
                            aria-pressed={sort === 'recent'}
                            onClick={() => setSort('recent')}
                        >Recent</button>
                        <button
                            className={styles.pill}
                            aria-pressed={sort === 'alpha'}
                            onClick={() => setSort('alpha')}
                        >A–Z</button>
                    </div>
                </div>

                {pageRows.length === 0 ? (
                    <div className={styles.empty}>No results. Try clearing filters or adjusting your search.</div>
                ) : (
                    <div className={styles.feedGrid} role="list" aria-label="Threat intelligence articles">
                        {pageRows.map(item => (
                            <article key={item.id} className={styles.feedItem} role="listitem">
                                <div className={styles.feedHeader}>
                                    <span className={styles.sourceBadge}>{item.source}</span>
                                    <span className={styles.published}>{item.published}</span>
                                </div>
                                <h3>{item.title}</h3>
                                <div className={styles.tags} aria-label="Tags">
                                    {item.tags.map(t => <span key={t} className={styles.tag}>{t}</span>)}
                                </div>
                            </article>
                        ))}
                    </div>
                )}

                <div className={styles.pagination} role="navigation" aria-label="Pagination">
                    <button className={styles.pageBtn} onClick={() => setPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} aria-label="Previous page">Prev</button>
                    <span>Page {currentPage} of {totalPages}</span>
                    <button className={styles.pageBtn} onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} aria-label="Next page">Next</button>
                </div>
            </div>
        </PortalLayout>
    );
}

export default ThreatFeedPage;
