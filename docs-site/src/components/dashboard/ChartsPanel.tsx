import React from 'react';
import { EvidenceVolumeBars, ScoreTrendChart } from './Charts';

const PANEL_STYLE: React.CSSProperties = {
    marginTop: '2rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
};

const GRID_STYLE: React.CSSProperties = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '1rem',
};

const ChartsPanel = () => {
    return (
        <section style={PANEL_STYLE} aria-labelledby="dashboard-visuals-heading" data-testid="dashboard-charts">
            <header>
                <h2 id="dashboard-visuals-heading" style={{ margin: 0 }}>Analyst Dashboard Visuals</h2>
                <p style={{ marginTop: '0.5rem', color: '#94a3b8', maxWidth: '720px' }}>
                    Snapshot helps you explain guardscore trajectories and ingestion reliability during stakeholder briefings.
                    All values are static for the prototype and sourced from docs/spec and evidence feed fixtures.
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
