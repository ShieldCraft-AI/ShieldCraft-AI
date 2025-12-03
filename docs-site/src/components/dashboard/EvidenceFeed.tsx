import React from 'react';

type EvidencePriority = 'info' | 'watch' | 'investigate';

type EvidenceItem = {
    id: string;
    title: string;
    artifactType: 'drift_summary' | 'retrieval_case' | 'risk_register';
    priority: EvidencePriority;
    ingestedAt: string;
    evidenceSource: string;
    summary: string;
    payload: Record<string, unknown>;
};

const FEED_STYLES: React.CSSProperties = {
    border: '1px solid #1f2933',
    borderRadius: '14px',
    padding: '1.5rem',
    background: 'rgba(15, 24, 42, 0.92)',
    boxShadow: '0 16px 55px rgba(2, 6, 23, 0.45)',
};

const LIST_STYLES: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.15rem',
    marginTop: '1rem',
};

const CARD_STYLES: React.CSSProperties = {
    border: '1px solid rgba(148, 163, 184, 0.35)',
    borderRadius: '12px',
    padding: '1rem',
    background: 'rgba(12, 18, 34, 0.85)',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.65rem',
};

const JSON_STYLES: React.CSSProperties = {
    margin: 0,
    padding: '0.85rem',
    background: '#030712',
    borderRadius: '10px',
    border: '1px solid rgba(148, 163, 184, 0.25)',
    color: '#cbd5f5',
    fontSize: '0.85rem',
    overflowX: 'auto',
};

const PRIORITY_THEME: Record<EvidencePriority, { label: string; color: string; background: string }> = {
    info: {
        label: 'Info',
        color: '#60a5fa',
        background: 'rgba(96, 165, 250, 0.18)',
    },
    watch: {
        label: 'Watch',
        color: '#fbbf24',
        background: 'rgba(251, 191, 36, 0.18)',
    },
    investigate: {
        label: 'Investigate',
        color: '#f87171',
        background: 'rgba(248, 113, 113, 0.18)',
    },
};

const evidenceItems: EvidenceItem[] = [
    {
        id: 'EV-001',
        title: 'Vectorguard drift snapshot (prod)',
        artifactType: 'drift_summary',
        priority: 'watch',
        ingestedAt: '2025-11-18T07:10:00Z',
        evidenceSource: 'docs/github/drift_reports/README.md#summary',
        summary: 'Prod control plane drift report captured a CloudTrail retention override awaiting acknowledgement.',
        payload: {
            stack: 'vectorguard-control-plane',
            comparison_status: 'acknowledged',
            diff_sha: '6c7fd1c8',
            pending_actions: ['confirm-log-retention'],
        },
    },
    {
        id: 'EV-002',
        title: 'Retrieval case QA artifact',
        artifactType: 'retrieval_case',
        priority: 'info',
        ingestedAt: '2025-11-18T07:25:00Z',
        evidenceSource: 'docs/github/retrieval_spotcheck.md#ticket-enrichment',
        summary: 'Ticket enrichment prompts returned steady 0.82 confidence yet surfaced stale incident cache markers.',
        payload: {
            case_id: 'RSC-148',
            evaluation: {
                relevance_score: 0.82,
                hallucination_score: 0.08,
            },
            remediation_hint: 'scripts/retrieval_spotcheck.py --refresh-cache',
        },
    },
    {
        id: 'EV-003',
        title: 'Risk register delta',
        artifactType: 'risk_register',
        priority: 'investigate',
        ingestedAt: '2025-11-18T07:40:00Z',
        evidenceSource: 'docs/github/risk_log.md#retrieval-guardrails',
        summary: 'ML guardrails flagged for follow-up because speculative execution prompts lack coverage for SC-APP-UI-003.',
        payload: {
            risk_id: 'RR-019',
            posture_score: 0.74,
            follow_up_owner: 'AppSec Guild',
            target_date: '2025-12-05',
        },
    },
];

const PriorityBadge = ({ priority }: { priority: EvidencePriority }) => {
    const theme = PRIORITY_THEME[priority];
    return (
        <span
            style={{
                alignSelf: 'flex-start',
                borderRadius: '999px',
                padding: '0.15rem 0.65rem',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: theme.color,
                background: theme.background,
            }}
        >
            {theme.label}
        </span>
    );
};

const EvidenceFeed = () => (
    <section style={FEED_STYLES} data-testid="evidence-feed">
        <header style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <p style={{ textTransform: 'uppercase', color: '#94a3b8', fontSize: '0.75rem', letterSpacing: '0.08em' }}>Evidence Feed</p>
            <h2 style={{ margin: 0, color: '#f8fafc', fontSize: '1.35rem' }}>Live Evidence Placeholder</h2>
            <p style={{ margin: 0, color: '#cbd5f5' }}>
                Static JSON payload curated for SC-APP-UI-002. Items mirror the future ingestion envelope so analysts can
                validate formatting before wiring the real data plane.
            </p>
        </header>
        <div style={LIST_STYLES}>
            {evidenceItems.map((item) => (
                <article key={item.id} style={CARD_STYLES} aria-label={`${item.title} evidence`}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '0.75rem' }}>
                        <div>
                            <p style={{ margin: 0, color: '#f8fafc', fontSize: '1rem', fontWeight: 600 }}>{item.title}</p>
                            <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.8rem' }}>
                                {item.artifactType} · captured {item.ingestedAt}
                            </p>
                        </div>
                        <PriorityBadge priority={item.priority} />
                    </div>
                    <p style={{ margin: 0, color: '#e2e8f0' }}>{item.summary}</p>
                    <p style={{ margin: 0, fontSize: '0.78rem', color: '#a5b4fc' }}>Source: {item.evidenceSource}</p>
                    <pre style={JSON_STYLES}>{JSON.stringify(item.payload, null, 2)}</pre>
                </article>
            ))}
        </div>
    </section>
);

export default EvidenceFeed;
