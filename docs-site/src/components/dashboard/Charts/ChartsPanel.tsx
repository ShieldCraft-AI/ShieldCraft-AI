import React from 'react';
import { EvidenceVolumeBars, ScoreTrendChart } from './index';

const PANEL_STYLE: React.CSSProperties = {
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
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '1.25rem',
    width: '100%',
};

const ChartsPanel = () => {
    return (
        <section style={PANEL_STYLE} aria-labelledby="dashboard-visuals-heading" data-testid="dashboard-charts">
            <header>
                <p style={{ margin: 0, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#94a3b8', fontSize: '0.75rem' }}>Visual Evidence</p>
                <h2 id="dashboard-visuals-heading" style={{ margin: '0.2rem 0 0', color: '#f8fafc' }}>
                    Analyst Dashboard Visuals
                </h2>
                <p style={{ margin: '0.35rem 0 0', color: '#cbd5f5' }}>
                    GuardScore trajectories and ingestion reliability snapshots mirror docs/spec artifacts. Layout snaps to two columns on desktop and
                    stacks on smaller breakpoints without scripts.
                </p>
            </header>
            <div style={GRID_STYLE}>
                <ScoreTrendChart />
                <EvidenceVolumeBars />
            </div>
        </section>
    );
};

export default ChartsPanel;
