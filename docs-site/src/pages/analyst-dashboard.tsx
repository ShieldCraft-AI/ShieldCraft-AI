import React, { useEffect, useState } from 'react';

const styles = {
    shell: { padding: 24, fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif', color: '#e6eef8' },
    header: { marginBottom: 18 },
    card: { background: '#071028', padding: 20, borderRadius: 10, color: '#e6eef8', maxWidth: 980, boxShadow: '0 6px 18px rgba(3,8,23,0.6)' },
    evidence: { flex: 1 },
    rightCol: { width: 300 },
    meta: { marginTop: 12, fontSize: 12, color: '#9fb0d9' },
    scoreBarOuter: { height: 12, background: '#0b2438', borderRadius: 6, overflow: 'hidden', marginTop: 8 },
    scoreBarInner: (pct: number, color: string) => ({ width: `${pct}%`, height: '100%', background: color, transition: 'width 400ms ease' }),
};

const colorForScore = (s: number) => {
    if (s >= 75) return '#ef4444';
    if (s >= 40) return '#f59e0b';
    return '#10b981';
};

const RiskGauge = ({ score }: { score: number }) => {
    // score is 0..100
    const angle = (score / 100) * 180; // semicircle
    const stroke = 10;
    const radius = 48;
    const cx = 60;
    const cy = 60;
    const color = colorForScore(score);

    const startX = cx - radius;
    const startY = cy;
    const endAngle = (180 - angle) * (Math.PI / 180);
    const endX = cx + radius * Math.cos(endAngle);
    const endY = cy - radius * Math.sin(endAngle);

    const d = `M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`;
    const progressPath = `M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${endX} ${endY}`;

    return (
        <svg width={120} height={70} viewBox="0 0 120 70">
            <path d={d} fill="none" stroke="#0f2940" strokeWidth={stroke} strokeLinecap="round" />
            <path d={progressPath} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" />
            <text x="60" y="46" textAnchor="middle" fontSize="14" fill="#e6eef8" fontWeight={700}>{score}%</text>
        </svg>
    );
};

const DemoCard = ({ data }: { data: any }) => {
    // normalize score into 0..100 integer for visualization
    const scorePct = Math.round((data.risk.score ?? 0) * 100);
    const color = colorForScore(scorePct);

    return (
        <div style={styles.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2 style={{ margin: 0 }}>Analyst Demo: {data.findingId}</h2>
                    <div style={{ color: '#9fb0d9', marginTop: 6 }}>Env: {data.meta.env} · Generated: {data.meta.generatedAt}</div>
                </div>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                    <RiskGauge score={scorePct} />
                </div>
            </div>

            <div style={{ display: 'flex', gap: 24, marginTop: 18 }}>
                <div style={styles.evidence}>
                    <h3 style={{ marginTop: 0 }}>Evidence</h3>
                    <ul style={{ paddingLeft: 18 }}>
                        {data.evidence.map((e: any, idx: number) => (
                            <li key={idx} style={{ marginBottom: 10 }}>
                                <div style={{ fontWeight: 700 }}>{e.source}</div>
                                <div style={{ color: '#cfe3ff' }}>{e.snippet}</div>
                                <div style={{ color: '#9fb0d9' }}>Score: {e.score}</div>
                            </li>
                        ))}
                    </ul>
                </div>

                <div style={styles.rightCol}>
                    <h3 style={{ marginTop: 0 }}>Risk</h3>
                    <div style={{ fontSize: 16, fontWeight: 700, color }}>{data.risk.class}</div>
                    <div style={{ marginTop: 8 }}>Score: {(data.risk.score ?? 0)}</div>

                    <div style={styles.scoreBarOuter}>
                        <div style={styles.scoreBarInner(scorePct, color)} />
                    </div>

                    <h4 style={{ marginTop: 18 }}>Remediation</h4>
                    <div style={{ color: '#cfe3ff' }}>Plan: {data.remediation.planId}</div>
                    <ol>
                        {data.remediation.steps.map((s: any, i: number) => (
                            <li key={i} style={{ marginBottom: 6 }}>{s.action} <small style={{ color: '#9fb0d9' }}>({s.owner})</small></li>
                        ))}
                    </ol>
                </div>
            </div>

            <div style={styles.meta}>Version: {data.meta.version}</div>
        </div>
    );
};

export default function AnalystDashboard(): any {
    const [data, setData] = useState<any | null>(null);
    useEffect(() => {
        fetch('/demo/demo_vertical_slice.json')
            .then((r) => r.json())
            .then((j) => setData(j))
            .catch(() => setData(null));
    }, []);

    return (
        <div style={styles.shell}>
            <div style={styles.header}>
                <h1 style={{ marginBottom: 6 }}>Analyst Dashboard Mock</h1>
                <p style={{ marginTop: 0, color: '#9fb0d9' }}>A compact view of the demo vertical slice (finding → evidence → risk → remediation).</p>
            </div>
            {data ? <DemoCard data={data} /> : <div>Loading demo payload…</div>}
        </div>
    );
}
