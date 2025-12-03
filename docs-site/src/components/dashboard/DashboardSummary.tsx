import React from 'react';

export type SummaryStatus = 'steady' | 'watch' | 'investigate';

interface SummaryItem {
    id: string;
    label: string;
    headline: string;
    status: SummaryStatus;
    lastReviewed: string;
    evidenceSource: string;
    notes: string;
}

const SECTION_STYLE: React.CSSProperties = {
    borderRadius: '14px',
    border: '1px solid rgba(148, 163, 184, 0.35)',
    padding: '1.25rem',
    background: 'linear-gradient(145deg, rgba(10, 15, 28, 0.95), rgba(15, 23, 42, 0.9))',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
};

const GRID_STYLE: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: '1.25rem',
    marginTop: '0.5rem',
};

const CARD_STYLE: React.CSSProperties = {
    borderRadius: '12px',
    border: '1px solid rgba(148, 163, 184, 0.25)',
    padding: '1.25rem',
    backgroundColor: 'rgba(11, 16, 30, 0.9)',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.6rem',
};

const STATUS_THEME: Record<SummaryStatus, { label: string; color: string; background: string }> = {
    steady: {
        label: 'Steady',
        color: '#22c55e',
        background: 'rgba(34, 197, 94, 0.15)',
    },
    watch: {
        label: 'Watch',
        color: '#fbbf24',
        background: 'rgba(251, 191, 36, 0.15)',
    },
    investigate: {
        label: 'Investigate',
        color: '#f97316',
        background: 'rgba(249, 115, 22, 0.15)',
    },
};

const riskBaseline: SummaryItem[] = [
    {
        id: 'identity-access',
        label: 'Identity & Access',
        headline: 'Guard rails steady @ 0.91 posture score',
        status: 'steady',
        lastReviewed: '2025-11-15',
        evidenceSource: 'docs/github/risk_log.md#identity-access-controls',
        notes: 'FedRAMP-derived MFA policy + session isolation referenced in risks_mitigation.md.',
    },
    {
        id: 'supply-chain',
        label: 'Supply Chain',
        headline: 'Pinned SBOM shows two pending acknowledgements',
        status: 'watch',
        lastReviewed: '2025-11-12',
        evidenceSource: 'docs/github/risk_log.md#software-supply-chain',
        notes: 'Waiting on repo-wide npm audit follow-up before promoting score to "steady".',
    },
    {
        id: 'ml-guardrails',
        label: 'ML Guardrails',
        headline: 'Retrieval defenses require additional evals',
        status: 'investigate',
        lastReviewed: '2025-11-10',
        evidenceSource: 'docs/github/risks_mitigation.md#retrieval-guardrails',
        notes: 'Need fresh eval coverage for speculative execution prompts per SC-ML-004.',
    },
];

const retrievalSpotChecks: SummaryItem[] = [
    {
        id: 'rsc-147',
        label: 'RSC-147 (Vector recall)',
        headline: '92% of sampled answers pulled correct context blocks',
        status: 'steady',
        lastReviewed: '2025-11-14',
        evidenceSource: 'docs/github/retrieval_spotcheck.md#vectorscan-synopsis',
        notes: 'Baseline payload aligns with docs/github/artifact_map.md vector coverage.',
    },
    {
        id: 'rsc-148',
        label: 'RSC-148 (Ticket enrichment)',
        headline: 'Edge prompts degrade because stale incidents remain in cache',
        status: 'watch',
        lastReviewed: '2025-11-14',
        evidenceSource: 'docs/github/retrieval_spotcheck.md#ticket-enrichment',
        notes: 'Next action: refresh cache recipe inside scripts/retrieval_spotcheck.py.',
    },
    {
        id: 'rsc-149',
        label: 'RSC-149 (SOC macro answers)',
        headline: 'Requires new hallucination probes before ATU-2',
        status: 'investigate',
        lastReviewed: '2025-11-13',
        evidenceSource: 'docs/github/retrieval_spotcheck.md#soc-responses',
        notes: 'Guardrails hold but evaluation depth is below spec 1.0.0 for macro flows.',
    },
];

const driftSummaries: SummaryItem[] = [
    {
        id: 'drift-prod-a',
        label: 'Prod · Control Plane',
        headline: 'Latest drift_report only shows log retention delta',
        status: 'steady',
        lastReviewed: '2025-11-16',
        evidenceSource: 'docs/github/drift_reports/README.md#components',
        notes: 'CI job confirmed NO_APPLY=1 with telemetry snapshot attached for auditors.',
    },
    {
        id: 'drift-staging-a',
        label: 'Staging · Data Plane',
        headline: 'Watch S3 bucket policy exception (approved)',
        status: 'watch',
        lastReviewed: '2025-11-16',
        evidenceSource: 'docs/github/drift_reports/README.md#guardrails',
        notes: 'Exception expires 2025-12-01; reminder tracked in docs/github/checklist.md.',
    },
    {
        id: 'drift-dev-a',
        label: 'Dev · Sandbox',
        headline: 'Investigate telemetry gap for vectorguard stack',
        status: 'investigate',
        lastReviewed: '2025-11-15',
        evidenceSource: 'docs/github/drift_reports/README.md#ci-coverage',
        notes: 'Need to re-run `nox -s drift_check -- --stacks vectorguard` to refresh hashes.',
    },
];

const statusPill = (status: SummaryStatus) => {
    const theme = STATUS_THEME[status];
    return (
        <span
            style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '0.15rem 0.6rem',
                borderRadius: '999px',
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

const Section = ({ title, description, items, testId }: { title: string; description: string; items: SummaryItem[]; testId: string }) => (
    <section style={SECTION_STYLE} data-testid={testId}>
        <header style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <p style={{ textTransform: 'uppercase', color: '#94a3b8', fontSize: '0.75rem', letterSpacing: '0.08em' }}>Evidence View</p>
            <h2 style={{ margin: 0, color: '#f8fafc', fontSize: '1.2rem' }}>{title}</h2>
            <p style={{ margin: 0, color: '#cbd5f5' }}>{description}</p>
        </header>
        <div style={GRID_STYLE}>
            {items.map((item) => (
                <article key={item.id} style={CARD_STYLE}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '0.5rem' }}>
                        <div>
                            <p style={{ margin: 0, color: '#f1f5f9', fontSize: '0.95rem', fontWeight: 600 }}>{item.label}</p>
                            <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.8rem' }}>Reviewed {item.lastReviewed}</p>
                        </div>
                        {statusPill(item.status)}
                    </div>
                    <p style={{ margin: 0, color: '#e2e8f0', fontSize: '0.95rem', fontWeight: 500 }}>{item.headline}</p>
                    <p style={{ margin: 0, color: '#cbd5f5', fontSize: '0.85rem' }}>{item.notes}</p>
                    <span style={{ marginTop: 'auto', fontSize: '0.75rem', color: '#a5b4fc' }}>Source: {item.evidenceSource}</span>
                </article>
            ))}
        </div>
    </section>
);

export const DashboardSummary = () => {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <Section
                title="Risk Baseline"
                description="Snapshot derived from docs/github/risk_log.md and related mitigations."
                items={riskBaseline}
                testId="risk-baseline"
            />
            <Section
                title="Retrieval Spot-Checks"
                description="Static pull from docs/github/retrieval_spotcheck.md covering current guardrails."
                items={retrievalSpotChecks}
                testId="retrieval-spotchecks"
            />
            <Section
                title="Signal Drift Summaries"
                description="Latest drift summaries aligned with docs/github/drift_reports/ guidance."
                items={driftSummaries}
                testId="drift-summaries"
            />
        </div>
    );
};

export default DashboardSummary;
