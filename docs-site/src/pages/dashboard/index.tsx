import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import DashboardSummary from '@site/src/components/Dashboard/DashboardSummary';
import { ChartsPanel } from '@site/src/components/Dashboard/Charts';

const meta = {
    specVersion: '1.0.0',
    atuId: 'ATU-1',
    lastSynced: '2025-11-18T00:00:00Z',
};

const shellStyle: React.CSSProperties = {
    maxWidth: '1100px',
    margin: '0 auto',
    padding: '2.5rem 1.5rem 4rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1.75rem',
};

const responsiveClusterStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
    gap: '1.5rem',
    alignItems: 'start',
};

const infoCardStyle: React.CSSProperties = {
    borderRadius: '14px',
    border: '1px solid rgba(148, 163, 184, 0.35)',
    padding: '1.25rem',
    background: 'linear-gradient(145deg, rgba(10, 15, 28, 0.95), rgba(15, 23, 42, 0.9))',
    color: '#e2e8f0',
};

const ctaStyle: React.CSSProperties = {
    marginTop: '1.25rem',
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.75rem',
};

const metadataRowStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '1rem',
    marginTop: '1rem',
};

const MetadataRow = ({ label, value }: { label: string; value: string }) => (
    <div>
        <p style={{ margin: 0, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#94a3b8' }}>{label}</p>
        <p style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>{value}</p>
    </div>
);

const DashboardPage = () => (
    <Layout title="Analyst Dashboard" description="Deterministic summary of risk, retrieval, and drift artifacts.">
        <main style={shellStyle} data-testid="dashboard-responsive-wrapper">
            <section style={infoCardStyle}>
                <h1 style={{ marginTop: 0, marginBottom: '0.75rem', fontSize: '1.5rem', color: '#f8fafc' }}>Analyst Dashboard · Summary Only</h1>
                <p style={{ margin: 0, color: '#cbd5f5' }}>
                    This view satisfies checklist item SC-APP-UI-001 by projecting the existing risk baseline, retrieval spot-checks,
                    and drift summaries into a single static dashboard. Everything below is sourced from docs artifacts and does not
                    perform API calls or background timers.
                </p>
                <div aria-label="Dashboard metadata" style={{ display: 'block' }}>
                    <div style={metadataRowStyle}>
                        <MetadataRow label="ATU" value={meta.atuId} />
                        <MetadataRow label="Spec Version" value={meta.specVersion} />
                        <MetadataRow label="Last Synced" value={meta.lastSynced} />
                    </div>
                </div>
                <div style={ctaStyle}>
                    <Link
                        to="/dashboard/evidence"
                        style={{
                            textDecoration: 'none',
                            padding: '0.55rem 0.9rem',
                            borderRadius: '10px',
                            fontWeight: 600,
                            border: '1px solid rgba(59, 130, 246, 0.35)',
                            color: '#93c5fd',
                            background: 'rgba(59, 130, 246, 0.12)',
                        }}
                    >
                        View Evidence Feed Preview →
                    </Link>
                </div>
            </section>
            <div style={responsiveClusterStyle}>
                <DashboardSummary />
                <ChartsPanel />
            </div>
        </main>
    </Layout>
);

export default DashboardPage;
