import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import EvidenceFeed from '@site/src/components/Dashboard/EvidenceFeed';

const shellStyle: React.CSSProperties = {
    maxWidth: '960px',
    margin: '0 auto',
    padding: '2rem 1.5rem 4rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '2rem',
};

const infoCardStyle: React.CSSProperties = {
    borderRadius: '12px',
    border: '1px solid rgba(148, 163, 184, 0.4)',
    padding: '1.25rem',
    background: 'rgba(11, 22, 39, 0.9)',
    color: '#e2e8f0',
};

const linkRowStyle: React.CSSProperties = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.75rem',
    marginTop: '1rem',
};

const linkStyle: React.CSSProperties = {
    textDecoration: 'none',
    padding: '0.55rem 0.9rem',
    borderRadius: '10px',
    fontWeight: 600,
};

const EvidenceFeedPage = () => (
    <Layout title="Analyst Evidence Feed" description="Static placeholder feed powering SC-APP-UI-002." >
        <main style={shellStyle}>
            <section style={infoCardStyle}>
                <h1 style={{ marginTop: 0, marginBottom: '0.75rem', fontSize: '1.5rem', color: '#f8fafc' }}>Analyst Evidence Feed · Placeholder</h1>
                <p style={{ margin: 0, color: '#cbd5f5' }}>
                    This route delivers the SC-APP-UI-002 Atomic Task: exposing a deterministic evidence feed placeholder that mirrors
                    the JSON envelope future ingestion jobs will publish. The payloads reference existing docs artifacts only and run entirely client-side.
                </p>
                <div style={linkRowStyle}>
                    <Link style={{ ...linkStyle, border: '1px solid rgba(148, 163, 184, 0.5)', color: '#cbd5f5' }} to="/dashboard">
                        ← Back to Summary
                    </Link>
                    <Link style={{ ...linkStyle, background: 'rgba(59, 130, 246, 0.15)', color: '#93c5fd', border: '1px solid rgba(59, 130, 246, 0.35)' }} to="/github/analyst-evidence-feed">
                        Evidence Spec
                    </Link>
                </div>
            </section>
            <EvidenceFeed />
        </main>
    </Layout>
);

export default EvidenceFeedPage;
