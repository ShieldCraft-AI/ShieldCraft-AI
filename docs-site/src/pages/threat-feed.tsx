import React, { useEffect, useMemo, useState } from 'react';
import PortalLayout from '../components/PortalLayout';
import FilterToolbar from '../components/FilterToolbar/FilterToolbar';
import styles from './threat-feed.module.css';
import { usePortalMock } from '../context/PortalMockContext';

type Severity = 'low' | 'medium' | 'high' | 'critical';
type FeedItem = {
    id: number;
    source: string;
    title: string;
    description: string;
    publishedOffsetHours: number; // deterministic offset, rendered as "x ago"
    tags: string[];
    severity: Severity;
    risk: number; // 1-100
};

// Small deterministic PRNG to reduce duplicates and allow env-specific variety
function hashSeed(s: string): number {
    let h = 2166136261 >>> 0;
    for (let i = 0; i < s.length; i++) {
        h ^= s.charCodeAt(i);
        h = Math.imul(h, 16777619);
    }
    return h >>> 0;
}
function mulberry32(a: number) {
    return function () {
        let t = (a += 0x6D2B79F5);
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}
function pick<T>(rand: () => number, arr: T[]): T { return arr[Math.floor(rand() * arr.length)]; }
function pickMany<T>(rand: () => number, arr: T[], k: number): T[] {
    const copy = arr.slice();
    const out: T[] = [];
    for (let i = 0; i < Math.min(k, copy.length); i++) {
        const idx = Math.floor(rand() * copy.length);
        out.push(copy.splice(idx, 1)[0]);
    }
    return out;
}
function clamp(n: number, min: number, max: number) { return Math.max(min, Math.min(max, n)); }

const SOURCES = [
    'CrowdStrike', 'Microsoft Threat Intelligence', 'Google Threat Analysis', 'Palo Alto Networks', 'Cisco Talos', 'IBM X-Force', 'CISA', 'Mandiant', 'Cloudflare Radar', 'AWS Security'
];
const ACTORS = ['Scattered Spider', 'ALPHV/BlackCat', 'LockBit 3.0', 'Lazarus Group', 'APT41', 'Volt Typhoon', 'Kimsuky', 'FIN7', 'APT29 (Cozy Bear)'];
const MALWARE = ['Lumma Stealer', 'RedLine Stealer', 'IcedID', 'Gootloader', 'PlugX', 'AsyncRAT', 'Cobalt Strike', 'Metasploit', 'SocGholish'];
const TACTICS = ['AI phishing', 'ransomware-as-a-service', 'API exploitation', 'supply chain compromise', 'zero-day exploitation', 'credential harvesting', 'MFA bypass', 'living-off-the-land'];
const TECHNIQUES = ['T1566', 'T1078', 'T1190', 'T1059.001', 'T1071', 'T1098', 'T1548', 'T1027', 'T1133'];
const CLOUD = ['AWS', 'Microsoft Azure', 'Google Cloud', 'Oracle Cloud', 'Cloudflare'];
const SERVICES = ['IAM', 'EC2', 'Lambda', 'S3', 'RDS', 'EKS', 'CloudTrail', 'GuardDuty', 'Bedrock', 'SageMaker', 'Cognito', 'Secrets Manager'];
const REGIONS = ['us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 'ca-central-1'];

function envBias(env: 'dev' | 'staging' | 'prod') {
    return {
        sourceWeights: (src: string) => {
            if (env === 'prod') return src === 'CISA' ? 4 : src === 'AWS Security' ? 1 : 2;
            if (env === 'staging') return src === 'AWS Security' ? 3 : 2;
            return src === 'AWS Security' ? 4 : 2; // dev
        },
        severityBoost: env === 'prod' ? 1.2 : env === 'staging' ? 1.0 : 0.85,
        riskShift: env === 'prod' ? 10 : env === 'staging' ? 0 : -5,
    };
}

function weightedPick(rand: () => number, items: string[], weight: (x: string) => number): string {
    const weights = items.map(weight);
    const total = weights.reduce((a, b) => a + b, 0);
    let r = rand() * total;
    for (let i = 0; i < items.length; i++) {
        r -= weights[i];
        if (r <= 0) return items[i];
    }
    return items[items.length - 1];
}

function toSeverity(score: number): Severity {
    if (score >= 85) return 'critical';
    if (score >= 65) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

function formatAgo(hours: number): string {
    if (hours < 24) {
        const h = Math.max(1, Math.round(hours));
        return `${h} hour${h === 1 ? '' : 's'} ago`;
    }
    const d = Math.round(hours / 24);
    return `${d} day${d === 1 ? '' : 's'} ago`;
}

function generateFeed(env: 'dev' | 'staging' | 'prod', count = 28): FeedItem[] {
    // Seed with env + week number to rotate slowly without flicker
    const now = new Date();
    const week = Math.floor((Date.UTC(now.getUTCFullYear(), 0, 1) - Date.UTC(now.getUTCFullYear(), 0, 0)) / 86400000 + (now.getTime() / 86400000)) % 52;
    const rng = mulberry32(hashSeed(`${env}:${week}`));
    const bias = envBias(env);

    const items: FeedItem[] = [];
    const titles = new Set<string>();
    let id = 1;
    while (items.length < count && id < count * 3) {
        const src = weightedPick(rng, SOURCES, bias.sourceWeights);
        const actor = pick(rng, ACTORS);
        const family = pick(rng, MALWARE);
        const tactic = pick(rng, TACTICS);
        const technique = pick(rng, TECHNIQUES);
        const cloud = pick(rng, CLOUD);
        const service = pick(rng, SERVICES);
        const region = pick(rng, REGIONS);

        const kind = Math.floor(rng() * 6);
        let title: string;
        if (kind === 0) {
            title = `${actor} targets ${cloud} ${service} using ${family}`;
        } else if (kind === 1) {
            title = `${tactic} campaign observed targeting ${cloud} workloads in ${region}`;
        } else if (kind === 2) {
            const cveY = 2024 + Math.floor(rng() * 2);
            const cveN = 1000 + Math.floor(rng() * 9000);
            title = `CVE-${cveY}-${cveN}: Active exploitation detected in ${service}`;
        } else if (kind === 3) {
            title = `${family} infrastructure shifts detected by ${src}`;
        } else if (kind === 4) {
            title = `${actor} deploys ${tactic} via compromised ${cloud} ${service}`;
        } else {
            title = `Zero-day vulnerability in ${cloud} ${service} exploited by ${actor}`;
        }

        // Env-specific flavor adjustments
        if (env === 'prod' && src === 'CISA' && title.startsWith('CVE-')) {
            title += ' [Critical]';
        } else if (env === 'staging' && src === 'AWS Security') {
            title = title.replace('detected', 'validated in staging');
        } else if (env === 'dev' && src === 'AWS Security') {
            title += ' [Dev Alert]';
        }

        if (titles.has(title)) { id++; continue; }
        titles.add(title);

        const baseRisk = Math.floor(rng() * 100);
        const risk = clamp(baseRisk + bias.riskShift, 1, 99);
        const sev = toSeverity(Math.round(risk * bias.severityBoost));
        const tagSet = new Set<string>([
            tactic.toLowerCase().replace(/[^a-z0-9-]/g, '-'),
            family.toLowerCase().replace(/[^a-z0-9-]/g, '-'),
            cloud.toLowerCase().replace(/\s+/g, '-'),
            service.toLowerCase(),
        ]);
        if (title.startsWith('CVE-')) tagSet.add('cve');
        if (title.includes('zero-day') || title.includes('Zero-day')) tagSet.add('zero-day');
        if (src === 'CISA') tagSet.add('cisa');
        if (env !== 'prod' && src === 'AWS Security') tagSet.add(env);
        const tags = Array.from(tagSet);

        const desc = `${src} identified ${tactic} activity leveraging ${family} malware targeting ${cloud} ${service} infrastructure in ${region}. Attack pattern aligns with MITRE ATT&CK technique ${technique}.`;
        const publishedOffsetHours = Math.floor(rng() * 240) + 1; // within ~10 days

        items.push({
            id: id++,
            source: src,
            title,
            description: desc,
            publishedOffsetHours,
            tags,
            severity: sev,
            risk: risk,
        });
    }
    // Sort by recency by default
    return items.sort((a, b) => a.publishedOffsetHours - b.publishedOffsetHours);
}

function ThreatFeedContent() {
    const { env, searchQuery } = usePortalMock();
    const feed = useMemo(() => generateFeed(env), [env]);

    // Use global search from header
    const effectiveQuery = searchQuery.toLowerCase();
    const [source, setSource] = useState<string>('all');
    const [tag, setTag] = useState<string>('all');
    const [sort, setSort] = useState<'recent' | 'alpha' | 'risk'>('recent');
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(9);

    useEffect(() => { setPage(1); }, [env]);

    const sources = useMemo(() => {
        const uniqueSources = Array.from(new Set(feed.map(f => f.source)));
        // Shorten long source names for filter display
        return uniqueSources.map(s => {
            if (s === 'Microsoft Threat Intelligence') return 'MS Threat Intel';
            if (s === 'Palo Alto Networks') return 'Palo Alto';
            if (s === 'Google Threat Analysis') return 'Google Threat';
            return s;
        });
    }, [feed]);
    const tags = useMemo(() => Array.from(new Set(feed.flatMap(f => f.tags))).sort(), [feed]);

    const filtered = useMemo(() => {
        const ql = effectiveQuery;
        // Map shortened names back to original for filtering
        const sourceMap: Record<string, string> = {
            'MS Threat Intel': 'Microsoft Threat Intelligence',
            'Palo Alto': 'Palo Alto Networks',
            'Google Threat': 'Google Threat Analysis'
        };
        const actualSource = sourceMap[source] || source;
        let rows = feed.filter(item =>
            (source === 'all' || item.source === actualSource) &&
            (tag === 'all' || item.tags.includes(tag)) &&
            (ql === '' || item.title.toLowerCase().includes(ql) || item.description.toLowerCase().includes(ql))
        );
        if (sort === 'alpha') rows = rows.slice().sort((a, b) => a.title.localeCompare(b.title));
        if (sort === 'risk') rows = rows.slice().sort((a, b) => b.risk - a.risk);
        if (sort === 'recent') rows = rows.slice().sort((a, b) => a.publishedOffsetHours - b.publishedOffsetHours);
        return rows;
    }, [feed, effectiveQuery, source, tag, sort]);

    const total = filtered.length;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const currentPage = Math.min(page, totalPages);
    const start = (currentPage - 1) * pageSize;
    const pageRows = filtered.slice(start, start + pageSize);

    return (
        <div className={styles.feedContainer}>
            <FilterToolbar
                groups={[
                    {
                        label: 'Sources',
                        options: [
                            { value: 'all', label: 'All sources' },
                            ...sources.slice(0, 6).map(s => ({ value: s, label: s })),
                        ],
                        activeValue: source,
                        onChange: (value) => { setSource(value); setPage(1); },
                        multiColumn: true,
                    },
                    {
                        label: 'Tags',
                        options: [
                            { value: 'all', label: 'All tags' },
                            ...tags.slice(0, 8).map(t => ({ value: t, label: t })),
                        ],
                        activeValue: tag,
                        onChange: (value) => { setTag(value); setPage(1); },
                        multiColumn: true,
                    },
                    {
                        label: 'Sort',
                        options: [
                            { value: 'recent', label: 'Recent' },
                            { value: 'alpha', label: 'A–Z' },
                            { value: 'risk', label: 'Risk' },
                        ],
                        activeValue: sort,
                        onChange: (value) => setSort(value as 'recent' | 'alpha' | 'risk'),
                    },
                ]}
                summaryStats={
                    <>
                        <span><b>{total}</b> items</span>
                        <span>•</span>
                        <span>Sources: <b>{sources.length}</b></span>
                        <span>•</span>
                        <span>Tags: <b>{tags.length}</b></span>
                    </>
                }
            />

            {pageRows.length === 0 ? (
                <div className={styles.empty}>No results. Try clearing filters or adjusting your search.</div>
            ) : (
                <div className={styles.feedGrid} role="list" aria-label="Threat intelligence articles">
                    {pageRows.map(item => (
                        <article key={item.id} className={styles.feedItem} role="listitem">
                            <div className={styles.feedHeader}>
                                <div className={styles.sourceWrap}>
                                    <span className={styles.avatar} aria-hidden="true">{item.source.split(' ').map(w => w[0]).join('').slice(0, 3)}</span>
                                    <span className={styles.sourceBadge}>{item.source}</span>
                                </div>
                                <div className={styles.metaWrap}>
                                    <span className={`${styles.sevDot} ${styles[item.severity]}`} data-tooltip={`Severity: ${item.severity}`}></span>
                                    <span className={styles.riskBadge} data-tooltip="Risk score">{item.risk}</span>
                                    <span className={styles.published}>{formatAgo(item.publishedOffsetHours)}</span>
                                </div>
                            </div>
                            <h3 className={styles.title}>{item.title}</h3>
                            <p className={styles.description}>{item.description}</p>
                            <div className={styles.tags} aria-label="Tags">
                                {item.tags.map(t => {
                                    const safe = t.replace(/[^a-z0-9]/g, '');
                                    const extra = (styles as Record<string, string>)[`tag_${safe}`] || '';
                                    return <span key={t} className={`${styles.tag} ${extra}`}>{t}</span>;
                                })}
                            </div>
                        </article>
                    ))}
                </div>
            )}

            <div className={styles.pagination} role="navigation" aria-label="Pagination">
                <span>Page {currentPage} of {totalPages}</span>
                {currentPage < totalPages ? (
                    <button className={styles.pageBtn} onClick={() => setPage(p => Math.min(totalPages, p + 1))} aria-label="Load more">Load more</button>
                ) : (
                    <button className={styles.pageBtn} onClick={() => { setPage(1); setPageSize(s => Math.min(24, s + 3)); }} aria-label="Restart">Refresh</button>
                )}
            </div>
        </div>
    );
}

export default function ThreatFeedPage() {
    return (
        <PortalLayout title="Threat Feed" description="Threat Feed in ShieldCraft AI">
            <ThreatFeedContent />
        </PortalLayout>
    );
}
