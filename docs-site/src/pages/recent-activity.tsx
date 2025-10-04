import React from 'react';
import PortalLayout from '../components/PortalLayout';
import FilterToolbar from '../components/FilterToolbar/FilterToolbar';
import styles from './recent-activity.module.css';
import { usePortalMock } from '../context/PortalMockContext';

type ActivityType = 'alert' | 'system' | 'policy' | 'data' | 'user';

type Activity = {
    id: number;
    user: string;
    action: string;
    type: ActivityType;
    minutesAgo: number; // relative time bucket; we compute a "time ago" string
};
// Deterministic variety generator to avoid duplicates while keeping stability per env/day
function hashSeed(s: string): number {
    let h = 2166136261 >>> 0;
    for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
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
const USERS = ['analyst', 'security.engineer', 'security.lead', 'dataops', 'platform', 'system'];

type Ctx = {
    rng: () => number;
    app: string;
    index: string;
    host: string;
    account: string;
    fleet: string;
};

function genUserAction(ctx: Ctx): string {
    const pick = Math.floor(ctx.rng() * 3);
    if (pick === 0) return `initiated attack simulation against ${ctx.app} (OWASP Top 10)`;
    if (pick === 1) return 'created dashboard “Executive Overview”';
    return 'granted temporary access to audit role (1h)';
}

function genSystemAction(ctx: Ctx): string {
    const pick = Math.floor(ctx.rng() * 6);
    if (pick === 0) return `patched CVE-2025-${1000 + Math.floor(ctx.rng() * 9000)} on ${ctx.host} (requires reboot window)`;
    if (pick === 1) return 'rotated KMS key alias/service-x';
    if (pick === 2) return `ingested threat intel feed from AlienVault OTX (${300 + Math.floor(ctx.rng() * 300)} indicators)`;
    if (pick === 3) return 'applied new WAF rule set (rate limiting enabled)';
    if (pick === 4) return `backfilled logs for account ${ctx.account} (${(1.2 + ctx.rng() * 6.0).toFixed(1)}M records)`;
    return `scheduled inspector scan for ${ctx.fleet} (critical packages)`;
}

function genPolicyAction(ctx: Ctx): string {
    const pick = Math.floor(ctx.rng() * 2);
    if (pick === 0) return 'updated S3 bucket encryption policy (enforce SSE-KMS)';
    return 'approved remediation playbook for open security groups';
}

function genDataAction(ctx: Ctx): string {
    const pick = Math.floor(ctx.rng() * 2);
    if (pick === 0) return `updated vector index ${ctx.index} (segment merge)`;
    return `published new threat bulletin (CVE-2025-${4000 + Math.floor(ctx.rng() * 6000)})`;
}
const FLEETS = { dev: 'dev-fleet', staging: 'staging-fleet', prod: 'prod-fleet' } as const;

function activitiesForEnv(env: 'dev' | 'staging' | 'prod'): Activity[] {
    const now = new Date();
    const day = Math.floor(now.getTime() / 86400000);
    const rng = mulberry32(hashSeed(`${env}:${day}`));

    const account = env === 'dev' ? '111111111111' : env === 'staging' ? '222222222222' : '333333333333';
    const app = env === 'dev' ? 'WebApp-Dev' : env === 'staging' ? 'WebApp-Staging' : 'WebApp-Prod';
    const index = env === 'dev' ? 'threat-intel-dev' : env === 'staging' ? 'threat-intel-staging' : 'threat-intel-prod';
    const host = env === 'dev' ? 'db-server-dev-01' : env === 'staging' ? 'db-server-stg-01' : 'db-server-01';
    const fleet = FLEETS[env];

    const n = 24 + Math.floor(rng() * 10); // 24-33 items
    const items: Activity[] = [];
    let id = 1;
    for (let i = 0; i < n; i++) {
        const r = rng();
        let type: ActivityType;
        if (r < 0.22) type = 'user';
        else if (r < 0.46) type = 'policy';
        else if (r < 0.78) type = 'system';
        else if (r < 0.9) type = 'alert';
        else type = 'data';

        let user = 'system';
        if (type !== 'system' && r < 0.8) {
            user = `${USERS[Math.floor(rng() * (USERS.length - 1))]}@shieldcraft.ai`;
        }

        const ctx: Ctx = { rng, app, index, host, account, fleet };
        let action = '';
        if (type === 'user') action = genUserAction(ctx);
        else if (type === 'policy') action = genPolicyAction(ctx);
        else if (type === 'system') action = genSystemAction(ctx);
        else action = genDataAction(ctx);

        const minutesAgoBase = Math.floor(rng() * (env === 'prod' ? 600 : 900)); // prod tends to be fresher
        const minutesAgoJitter = Math.floor(rng() * 45);
        const minutesAgo = Math.max(1, minutesAgoBase + minutesAgoJitter);

        items.push({ id: id++, user, action, type, minutesAgo });
    }
    // Sort ascending age so groupings feel natural
    items.sort((a, b) => a.minutesAgo - b.minutesAgo);
    return items;
}

function RecentActivityContent() {
    const { env, searchQuery } = usePortalMock();
    const activities = React.useMemo(() => activitiesForEnv(env), [env]);
    // Use global search from header
    const effectiveQuery = searchQuery.toLowerCase();
    const [typeFilter, setTypeFilter] = React.useState<ActivityType | 'all'>('all');
    const [, setTick] = React.useState(0);
    // Refresh every minute so time-ago strings tick forward
    React.useEffect(() => {
        const id = setInterval(() => setTick(t => t + 1), 60000);
        return () => clearInterval(id);
    }, []);

    const filtered = React.useMemo(() => {
        const q = effectiveQuery;
        return activities.filter(a =>
            (typeFilter === 'all' || a.type === typeFilter) &&
            (!q || a.user.toLowerCase().includes(q) || a.action.toLowerCase().includes(q))
        );
    }, [activities, effectiveQuery, typeFilter]);

    // Group into Today vs Earlier (24h threshold)
    const groups = React.useMemo(() => {
        const today = filtered.filter(a => a.minutesAgo < 24 * 60);
        const earlier = filtered.filter(a => a.minutesAgo >= 24 * 60);
        return [
            { label: 'Today', items: today },
            { label: 'Earlier', items: earlier },
        ].filter(g => g.items.length > 0);
    }, [filtered]);

    const todayCount = activities.filter(a => a.minutesAgo < 24 * 60).length;
    const total24h = todayCount; // all current mock items are within a few days; this mirrors "last 24h"

    const types: Array<{ key: ActivityType | 'all'; label: string }> = [
        { key: 'all', label: 'All' },
        { key: 'alert', label: 'Alerts' },
        { key: 'system', label: 'System' },
        { key: 'policy', label: 'Policy' },
        { key: 'data', label: 'Data' },
        { key: 'user', label: 'User' },
    ];

    return (
        <>
            <FilterToolbar
                groups={[
                    {
                        label: 'Activity Type',
                        options: types.map(t => ({ value: t.key, label: t.label })),
                        activeValue: typeFilter,
                        onChange: (value) => setTypeFilter(value as ActivityType | 'all'),
                    },
                ]}
                summaryStats={
                    <>
                        <span><b>{todayCount}</b> today</span>
                        <span>•</span>
                        <span><b>{total24h}</b> in last 24h</span>
                    </>
                }
            />

            <div className={styles.activityFeed} role="list" aria-label="Recent activity feed">
                {groups.map(group => (
                    <React.Fragment key={group.label}>
                        <div className={styles.groupHeader}>{group.label}</div>
                        {group.items.map(item => (
                            <div key={item.id} className={styles.activityItem} role="listitem">
                                <div className={`${styles.activityIcon} ${styles[item.type]}`}></div>
                                <div className={styles.activityContent}>
                                    <div className={styles.activityHeader}>
                                        <span className={styles.user}>{item.user}</span>
                                        <span className={`${styles.badge} ${styles[`badge_${item.type}`]}`}>{item.type}</span>
                                    </div>
                                    <p className={styles.action}>{item.action}</p>
                                </div>
                            </div>
                        ))}
                    </React.Fragment>
                ))}
            </div>
        </>
    );
}

export default function RecentActivityPage() {
    return (
        <PortalLayout title="Recent Activity" description="Recent Activity in ShieldCraft AI">
            <RecentActivityContent />
        </PortalLayout>
    );
}
