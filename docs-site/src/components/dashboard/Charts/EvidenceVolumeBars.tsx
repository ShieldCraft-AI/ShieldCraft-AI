import React from 'react';

const CARD_STYLE: React.CSSProperties = {
    flex: '1 1 280px',
    borderRadius: '14px',
    border: '1px solid rgba(148, 163, 184, 0.35)',
    padding: '1.25rem',
    background: 'linear-gradient(145deg, rgba(10, 15, 28, 0.95), rgba(15, 23, 42, 0.9))',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
};

const monthVolume = [
    { label: 'Aug', value: 18 },
    { label: 'Sep', value: 23 },
    { label: 'Oct', value: 27 },
    { label: 'Nov', value: 31 },
];
const maxVolume = Math.max(...monthVolume.map((m) => m.value));

const EvidenceVolumeBars = () => {
    return (
        <article style={CARD_STYLE} aria-label="Evidence ingestion volume chart">
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Evidence Volume</p>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end' }}>
                {monthVolume.map((month) => (
                    <div key={month.label} style={{ flex: 1, textAlign: 'center' }}>
                        <div
                            style={{
                                margin: '0 auto',
                                width: '60%',
                                height: `${(month.value / maxVolume) * 120}px`,
                                background: 'linear-gradient(180deg, #f472b6 0%, #be123c 100%)',
                                borderRadius: '8px 8px 4px 4px',
                            }}
                        />
                        <p style={{ margin: '0.4rem 0 0', fontSize: '0.8rem', color: '#cbd5f5' }}>{month.label}</p>
                    </div>
                ))}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#a5b4fc', fontSize: '0.85rem' }}>
                <span>Total 3 mo.</span>
                <strong>99 payloads</strong>
            </div>
            <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.8rem' }}>
                Source: docs/github/analyst_evidence_feed.md · static ingest snapshot
            </p>
        </article>
    );
};

export default EvidenceVolumeBars;
