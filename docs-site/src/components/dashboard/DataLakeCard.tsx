import React from 'react';
import dayjs from 'dayjs';
import PlotClient from './PlotClient';
import CardShell from './CardShell';
import styles from './card.module.css';
import { genDriftSeries, Point } from '../../utils/dashboard/data';

const CAPACITY_TB = 2.0; // 2 TB capacity band

function fmtTB(v: number) {
    return `${v.toFixed(2)} TB`;
}

// Donut focuses on current Used vs Free; we still keep a slow live drift series to
// compute current, utilization, and 24h growth.

export default function DataLakeCard() {
    // Generate a long series (90d, 5-min points)
    const stepMs = 5 * 60_000;
    const totalPoints = Math.floor((90 * 24 * 60) / 5);
    const [series, setSeries] = React.useState<Point[]>(() =>
        genDriftSeries({
            points: totalPoints,
            start: dayjs().subtract(90, 'day').valueOf(),
            stepMs,
            base: 1.2, // TB
            drift: 0.00001, // slow growth per 5 min (~0.17 TB over 90d)
            volatility: 0.002,
            floor: 0.8,
            ceiling: CAPACITY_TB * 1.15,
            seed: 1337,
        })
    );

    const live = true;

    // Live update: append a new point every 10s for demo
    React.useEffect(() => {
        const id = setInterval(() => {
            setSeries(prev => {
                const last = prev[prev.length - 1];
                const nextT = last.t + stepMs;
                let nextV = last.v + 0.00001 + (Math.random() - 0.5) * 0.0015;
                nextV = Math.max(0.8, Math.min(CAPACITY_TB * 1.15, nextV));
                return [...prev.slice(-totalPoints + 1), { t: nextT, v: nextV }];
            });
        }, 3_000);
        return () => clearInterval(id);
    }, [stepMs]);

    // Current and 24h growth
    const now = dayjs().valueOf();
    const current = series.length ? series[series.length - 1].v : CAPACITY_TB * 0.6;
    const t24h = now - 24 * 60 * 60 * 1000;
    const idx24h = series.findIndex(p => p.t >= t24h);
    const base24 = idx24h >= 0 ? series[idx24h].v : current;
    const growthPct = base24 > 0 ? ((current - base24) / base24) * 100 : 0;

    // Donut values
    const used = Math.max(0, Math.min(current, CAPACITY_TB));
    const free = Math.max(0, CAPACITY_TB - used);
    const utilPct = (used / CAPACITY_TB) * 100;

    const traces = React.useMemo(() => ([
        {
            type: 'pie',
            labels: ['Used', 'Free'],
            values: [used, free],
            hole: 0.7,
            sort: false,
            marker: { colors: ['#f59e0b', '#10b981'] },
            textinfo: 'label+percent',
            textposition: 'inside',
            insidetextorientation: 'horizontal',
            direction: 'clockwise',
            hovertemplate: '%{label}: %{value:.2f} TB (%{percent})<extra></extra>',
            name: 'Data Lake',
        },
    ] as any[]), [used, free]);

    const layout = React.useMemo(() => ({
        height: 160, // Reduced to fit within card
        showlegend: false,
        margin: { t: 8, r: 8, b: 8, l: 8 },
        // Fill available plotting area
        grid: { rows: 1, columns: 1 },
        annotations: [
            {
                text: `${utilPct.toFixed(0)}%\n${fmtTB(used)}`,
                x: 0.5, y: 0.5, xref: 'paper', yref: 'paper',
                showarrow: false,
                font: { size: 16, family: 'Inter, system-ui, sans-serif', color: 'var(--portal-text-color, #e5e7eb)' }, // Reduced font size
                align: 'center' as const,
            },
        ],
    }), [utilPct, used]);

    const kpis = [
        { label: 'Used', value: fmtTB(used) },
        { label: 'Utilization', value: `${utilPct.toFixed(1)}%`, delta: growthPct },
    ];

    return (
        <CardShell
            title="Data Lake"
            kpis={kpis}
            kpiCols={3}
            ariaLabel="Data Lake used vs free"
        >
            <div style={{ height: '100%', padding: '0 6px', overflow: 'hidden' }}>
                <PlotClient data={traces as any[]} layout={layout} />
            </div>
        </CardShell>
    );
}
