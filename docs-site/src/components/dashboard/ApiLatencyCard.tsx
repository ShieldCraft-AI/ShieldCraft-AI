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

export default function ApiLatencyCard() {
    const [windowKey, setWindowKey] = React.useState<WindowKey>('24h');
    const live = true;

    // Seed with realistic baseline ~50ms with tiny drift and jitter
    const initial = React.useMemo(() => genInitialSeries({
        minutes: 24 * 60,
        stepSec: 10,
        base: 50,
        jitter: 1.0,
        driftPerMin: 0.01,
        clampMin: 20,
        clampMax: 120,
    }), []);

    const { series } = useLiveSeries({
        initial,
        tickSec: 1,
        stepSec: 10,
        jitter: 0.6,
        driftPerMin: 0.01,
        clampMin: 20,
        clampMax: 120,
        live,
        maxPoints: 9000, // ~24h @ 10s steps
    });

    const now = dayjs().valueOf();
    const start = windowStart(windowKey);
    const visible = React.useMemo(() => series.filter(p => p.t >= start && p.t <= now), [series, start, now]);
    const x = visible.map(p => new Date(p.t));
    const y = visible.map(p => p.v);

    // Percentiles over visible window
    const current = y.length ? y[y.length - 1] : 0;
    const lastX = x.length ? x[x.length - 1] : undefined;

    // Rolling quantile ribbon for a modern, high-signal view
    function rollingQuantile(arr: number[], window: number, q: number) {
        const out: number[] = new Array(arr.length).fill(0);
        for (let i = 0; i < arr.length; i++) {
            const s = Math.max(0, i - window + 1);
            const slice = arr.slice(s, i + 1).slice();
            slice.sort((a, b) => a - b);
            const idx = (slice.length - 1) * q;
            const lo = Math.floor(idx);
            const hi = Math.ceil(idx);
            const val = lo === hi ? slice[lo] : slice[lo] + (slice[hi] - slice[lo]) * (idx - lo);
            out[i] = val;
        }
        return out;
    }
    const WINDOW = 30; // ~5 minutes at 10s cadence
    const p10Arr = React.useMemo(() => rollingQuantile(y, WINDOW, 0.10), [y]);
    const p50Arr = React.useMemo(() => rollingQuantile(y, WINDOW, 0.50), [y]);
    const p90Arr = React.useMemo(() => rollingQuantile(y, WINDOW, 0.90), [y]);

    // Create ribbons for p50/p95/p99 bands: We'll plot the series, plus horizontal threshold lines.
    const traces: any[] = [
        // Ribbon: lower (invisible line)
        { type: 'scatter', mode: 'lines', x, y: p10Arr, line: { width: 0 }, hoverinfo: 'skip', showlegend: false },
        // Ribbon: upper filled to previous (creates band p10→p90)
        { type: 'scatter', mode: 'lines', x, y: p90Arr, line: { width: 0 }, fill: 'tonexty', fillcolor: 'rgba(34,211,238,0.09)', hoverinfo: 'skip', name: 'p10–p90' },
        // Glow under the median
        { type: 'scatter', mode: 'lines', x, y: p50Arr, line: { color: 'rgba(34,211,238,0.22)', width: 8, shape: 'spline', smoothing: 0.6 }, hoverinfo: 'skip', showlegend: false },
        // Median line
        {
            type: 'scatter', mode: 'lines', x, y: p50Arr,
            line: { color: '#22d3ee', width: 2.8, shape: 'spline', smoothing: 0.6 },
            name: 'Median',
            hovertemplate: '%{x|%Y-%m-%d %H:%M}<br>%{y:.1f} ms<extra></extra>'
        },
        // Now marker (halo + dot)
        ...(lastX !== undefined ? [
            { type: 'scatter', mode: 'markers', x: [lastX], y: [current], marker: { size: 18, color: 'rgba(34,211,238,0.18)', line: { width: 0 } }, hoverinfo: 'skip', showlegend: false },
            { type: 'scatter', mode: 'markers', x: [lastX], y: [current], marker: { size: 8, color: '#22d3ee', line: { width: 2, color: 'rgba(34,211,238,0.5)' } }, name: 'Now', hovertemplate: '%{y:.1f} ms<extra>Now</extra>' },
        ] : []),
    ];

    const layout = React.useMemo(() => ({
        height: 160,
        yaxis: { title: 'ms', rangemode: 'tozero', gridcolor: 'rgba(255,255,255,0.04)', tickformat: '.0f' },
        xaxis: { type: 'date' },
        showlegend: false,
        margin: { t: 14, r: 10, b: 26, l: 48 },
        // Current value tag
        annotations: (lastX !== undefined) ? [{
            x: lastX, y: current,
            xref: 'x', yref: 'y', showarrow: false,
            text: `${formatNumber(current, 1)} ms`,
            xanchor: 'left', yanchor: 'bottom',
            bgcolor: 'rgba(2,6,23,0.8)', bordercolor: 'rgba(34,211,238,0.5)', borderwidth: 1,
            font: { size: 11 },
            ay: -20, ax: 10,
        }] : [],
    }), [lastX, current]);

    // KPIs updated to emphasize current and stability band
    const kpis = [
        { label: 'Current', value: `${formatNumber(current, 1)} ms` },
        { label: 'Median band', value: 'p10–p90' },
    ];

    return (
        <CardShell
            title="API Latency"
            kpis={kpis}
            controls={<TimeframeControls value={windowKey} onChange={setWindowKey} />}
            ariaLabel="API latency over time"
        >
            <div style={{ height: '100%' }}>
                <PlotClient data={traces} layout={layout} />
            </div>
        </CardShell>
    );
}
