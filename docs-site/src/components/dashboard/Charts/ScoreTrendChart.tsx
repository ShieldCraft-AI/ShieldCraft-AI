import React from 'react';

const CARD_STYLE: React.CSSProperties = {
    flex: '1 1 280px',
    minWidth: 0,
    borderRadius: '14px',
    border: '1px solid rgba(148, 163, 184, 0.35)',
    padding: '1.25rem',
    background: 'linear-gradient(145deg, rgba(10, 15, 28, 0.95), rgba(15, 23, 42, 0.9))',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
};

const SPARKLINE_HEIGHT = 80;
const SPARKLINE_WIDTH = 320;
const trendValues = [68, 71, 70, 74, 77, 79, 82, 84];
const maxValue = 100;
const pointGap = SPARKLINE_WIDTH / (trendValues.length - 1);
const sparklinePath = trendValues
    .map((value, index) => {
        const x = index * pointGap;
        const y = SPARKLINE_HEIGHT - (value / maxValue) * SPARKLINE_HEIGHT;
        return `${index === 0 ? 'M' : 'L'}${x},${y}`;
    })
    .join(' ');

const badgeColors = ['#4ade80', '#a5b4fc', '#fbbf24', '#fb7185'];

const ScoreTrendChart = () => {
    return (
        <article style={CARD_STYLE} aria-label="GuardScore trend chart">
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8', letterSpacing: '0.08em', textTransform: 'uppercase' }}>GuardScore Trend</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '0.5rem' }}>
                <h3 style={{ margin: 0, color: '#f8fafc', fontSize: '1.5rem' }}>84</h3>
                <span style={{ color: '#4ade80', fontSize: '0.9rem', fontWeight: 600 }}>+3 week over week</span>
            </div>
            <svg
                width="100%"
                height={SPARKLINE_HEIGHT}
                viewBox={`0 0 ${SPARKLINE_WIDTH} ${SPARKLINE_HEIGHT}`}
                role="img"
                aria-label="Sparkline showing GuardScore increases"
            >
                <path d={sparklinePath} fill="none" stroke="url(#trendGradient)" strokeWidth={3} strokeLinecap="round" />
                <defs>
                    <linearGradient id="trendGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#38bdf8" />
                        <stop offset="100%" stopColor="#60a5fa" />
                    </linearGradient>
                </defs>
            </svg>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                {['Identity', 'Drift', 'Retrieval', 'AI'].map((label, idx) => (
                    <span
                        key={label}
                        style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.35rem',
                            fontSize: '0.75rem',
                            color: '#cbd5f5',
                        }}
                    >
                        <span style={{ width: 10, height: 10, borderRadius: '50%', background: badgeColors[idx] }} />
                        {label}
                    </span>
                ))}
            </div>
        </article>
    );
};

export default ScoreTrendChart;
