import React from 'react';
import dayjs from 'dayjs';
import CardShell from './CardShell';
import PlotClient from './PlotClient';
import styles from './card.module.css';

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

function seedMatrix(): number[][] {
    // 7 days x 24 hours
    const m: number[][] = Array.from({ length: 7 }, () => Array.from({ length: 24 }, () => 0));
    const now = dayjs();
    // Pre-populate with a gentle baseline and a few peaks
    for (let d = 0; d < 7; d++) {
        for (let h = 0; h < 24; h++) {
            const base = 2 + Math.floor(Math.random() * 3);
            const peak = (h >= 9 && h <= 18) ? Math.floor(Math.random() * 4) : 0; // business hours busier
            m[d][h] = base + peak;
        }
    }
    // Current hour gets a small bump
    const dow = (now.day() + 6) % 7; // make Monday index 0
    const hr = now.hour();
    m[dow][hr] += 3;
    return m;
}

type Sev = 'Critical' | 'High' | 'Medium' | 'Low';

function nextSev(): Sev {
    const r = Math.random();
    if (r < 0.05) return 'Critical';
    if (r < 0.20) return 'High';
    if (r < 0.60) return 'Medium';
    return 'Low';
}

export default function ThreatsCard() {
    const live = true;
    const [matrix, setMatrix] = React.useState<number[][]>(seedMatrix);
    const [sevCounts, setSevCounts] = React.useState<Record<Sev, number>>({ Critical: 5, High: 18, Medium: 64, Low: 120 });
    const [resolvedPct, setResolvedPct] = React.useState(82);

    // Live: increment current hour cell, random severity distribution, slight resolved percent drift
    React.useEffect(() => {
        const id = setInterval(() => {
            setMatrix(prev => {
                const now = dayjs();
                const d = (now.day() + 6) % 7;
                const h = now.hour();
                const m2 = prev.map(row => row.slice());
                m2[d][h] = Math.max(0, m2[d][h] + 1 + Math.floor(Math.random() * 2));
                return m2;
            });
            setSevCounts(prev => {
                const s = nextSev();
                return { ...prev, [s]: prev[s] + 1 };
            });
            setResolvedPct(p => Math.max(60, Math.min(98, p + (Math.random() - 0.5) * 0.3)));
        }, 4000);
        return () => clearInterval(id);
    }, []);

    const total = Object.values(sevCounts).reduce((a, b) => a + b, 0);

    // Heatmap trace (7 rows x 24 columns). Map so y labels align Mon..Sun top-to-bottom
    const heatmap = React.useMemo(() => ({
        type: 'heatmap',
        z: matrix,
        x: Array.from({ length: 24 }, (_, h) => `${h}:00`),
        y: DAYS,
        colorscale: [
            [0, 'rgba(34,211,238,0.05)'],
            [0.25, '#22d3ee'],
            [0.5, '#60a5fa'],
            [0.75, '#a78bfa'],
            [1, '#f472b6'],
        ],
        showscale: false,
        hovertemplate: '%{y} %{x}<br>Events: %{z}<extra></extra>'
    }), [matrix]);

    const donut = React.useMemo(() => ({
        type: 'pie',
        labels: ['Critical', 'High', 'Medium', 'Low'],
        values: [sevCounts.Critical, sevCounts.High, sevCounts.Medium, sevCounts.Low],
        hole: 0.65,
        sort: false,
        marker: { colors: ['#f87171', '#fb923c', '#f59e0b', '#34d399'] },
        textinfo: 'label+percent',
        hovertemplate: '%{label}: %{value}<extra></extra>'
    }), [sevCounts]);

    const kpis = [
        { label: 'Critical / High', value: `${sevCounts.Critical} / ${sevCounts.High}` },
        { label: 'Resolved', value: `${resolvedPct.toFixed(0)}%` },
    ];

    return (
        <CardShell
            title="Threats Detected"
            kpis={kpis}
            kpiCols={3}

            ariaLabel="Threats by day and hour with severity mix"
        >
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 8, height: '100%' }}>
                <div>
                    <PlotClient data={[heatmap]} layout={{ height: 160, margin: { t: 8, r: 8, b: 24, l: 44 }, xaxis: { type: 'category' }, yaxis: { type: 'category' } }} />
                </div>
                <div>
                    <PlotClient data={[donut]} layout={{ height: 160, showlegend: false, margin: { t: 8, r: 8, b: 8, l: 8 } }} />
                </div>
            </div>
        </CardShell>
    );
}
