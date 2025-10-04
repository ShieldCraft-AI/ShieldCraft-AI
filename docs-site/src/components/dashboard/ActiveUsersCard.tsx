import React from 'react';
import dayjs from 'dayjs';
import CardShell from './CardShell';
import PlotClient from './PlotClient';
import TimeframeControls, { WindowKey } from './TimeframeControls';
import { genInitialSeries, useLiveSeries, formatNumber } from '../../utils/dashboard/live';

function windowStart(key: WindowKey) {
    const now = dayjs();
    switch (key) {
        case '1h': return now.subtract(1, 'hour').valueOf();
        case '24h': return now.subtract(24, 'hour').valueOf();
        case '7d': return now.subtract(7, 'day').valueOf();
        case '30d': return now.subtract(30, 'day').valueOf();
        case '90d':
        default: return now.subtract(90, 'day').valueOf();
    }
}

export default function ActiveUsersCard() {
    const [windowKey, setWindowKey] = React.useState<WindowKey>('24h');
    const live = true;

    // Seed: baseline ~120 users, light drift and jitter
    const initial = React.useMemo(() => genInitialSeries({
        minutes: 30 * 24 * 60, // 30 days for history
        stepSec: 10,           // 10-second points for visible motion
        base: 120,
        jitter: 4.0,
        driftPerMin: 0.01,
        clampMin: 20,
        clampMax: 1200,
    }), []);

    const { series } = useLiveSeries({
        initial,
        tickSec: 1,
        stepSec: 10,
        jitter: 2.0,
        driftPerMin: 0.01,
        clampMin: 20,
        clampMax: 1200,
        live,
        maxPoints: 30 * 24 * 60 * 6, // keep last 30 days of 10s points
    });

    const now = dayjs().valueOf();
    const start = windowStart(windowKey);
    const visible = React.useMemo(() => series.filter(p => p.t >= start && p.t <= now), [series, start, now]);
    const x = visible.map(p => new Date(p.t));
    const y = visible.map(p => p.v);
    const current = y.length ? y[y.length - 1] : 0;

    // KPIs: 24h avg and 24h peak based on visible window (if 24h), otherwise compute over last 24h slice
    const t24h = now - 24 * 60 * 60 * 1000;
    const last24 = React.useMemo(() => series.filter(p => p.t >= t24h && p.t <= now).map(p => p.v), [series, t24h, now]);
    const avg24 = last24.length ? last24.reduce((a, b) => a + b, 0) / last24.length : 0;
    const peak24 = last24.length ? last24.reduce((m, v) => Math.max(m, v), last24[0] ?? 0) : 0;

    const traces: any[] = [
        { type: 'scatter', mode: 'lines', x, y, line: { color: 'rgba(34,211,238,0.28)', width: 8, shape: 'spline', smoothing: 0.6 }, hoverinfo: 'skip', showlegend: false },
        {
            type: 'scatter', mode: 'lines', x, y,
            line: { color: '#22d3ee', width: 2.6, shape: 'spline', smoothing: 0.6 },
            fill: 'tozeroy', fillcolor: 'rgba(34,211,238,0.10)',
            name: 'Active Users',
            hovertemplate: '%{x|%Y-%m-%d %H:%M}<br>%{y:.0f} users<extra></extra>'
        },
    ];

    const layout = React.useMemo(() => ({
        height: 160,
        yaxis: { title: 'users', rangemode: 'tozero' },
        xaxis: { type: 'date' },
        legend: { orientation: 'h', y: -0.2 },
        margin: { t: 12, r: 8, b: 24, l: 44 },
    }), []);

    const kpis = [
        { label: 'Current', value: `${formatNumber(current, 0)}` },
        { label: '24h Avg', value: `${formatNumber(avg24, 0)}` },
    ];

    return (
        <CardShell
            title="Active Users"
            kpis={kpis}
            kpiCols={3}
            controls={<TimeframeControls value={windowKey} onChange={setWindowKey} />}
            ariaLabel="Active users over time"
        >
            <div style={{ height: '100%' }}>
                <PlotClient data={traces} layout={layout} />
            </div>
        </CardShell>
    );
}
