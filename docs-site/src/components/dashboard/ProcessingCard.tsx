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

export default function ProcessingCard() {
    const [windowKey, setWindowKey] = React.useState<WindowKey>('24h');
    const live = true;

    // Single high-quality output series for a modern blue "mountain" chart
    const outputInit = React.useMemo(() => genInitialSeries({
        minutes: 30 * 24 * 60,
        stepSec: 5,            // smoother motion
        base: 280,
        jitter: 4.5,
        driftPerMin: 0.02,
        clampMin: 40,
        clampMax: 1200,
    }), []);

    const { series: out } = useLiveSeries({ initial: outputInit, tickSec: 1, stepSec: 5, jitter: 2.2, driftPerMin: 0.02, clampMin: 40, clampMax: 1200, live, maxPoints: 30 * 24 * 60 * 12 });

    const now = dayjs().valueOf();
    const start = windowStart(windowKey);
    const vis = React.useMemo(() => out.filter(p => p.t >= start && p.t <= now), [out, start, now]);
    const x = vis.map(p => new Date(p.t));
    const y = vis.map(p => p.v);
    const current = y.length ? y[y.length - 1] : 0;
    const avg24 = React.useMemo(() => {
        const t24h = now - 24 * 60 * 60 * 1000;
        const last = out.filter(p => p.t >= t24h && p.t <= now).map(p => p.v);
        if (!last.length) return 0;
        return last.reduce((a, b) => a + b, 0) / last.length;
    }, [out, now]);
    const peak24 = React.useMemo(() => {
        const t24h = now - 24 * 60 * 60 * 1000;
        const last = out.filter(p => p.t >= t24h && p.t <= now).map(p => p.v);
        return last.length ? last.reduce((m, v) => Math.max(m, v), last[0] ?? 0) : 0;
    }, [out, now]);
    const startWindow = y.length ? y[0] : 0;
    const deltaPct = startWindow ? ((current - startWindow) / startWindow) * 100 : 0;

    const lastX = x.length ? x[x.length - 1] : undefined;
    const traces: any[] = [
        // Soft glow under the line
        { type: 'scatter', mode: 'lines', x, y, line: { color: 'rgba(56,189,248,0.22)', width: 8, shape: 'spline', smoothing: 0.85 }, hoverinfo: 'skip', showlegend: false, cliponaxis: false },
        // Main blue area
        {
            type: 'scatter', mode: 'lines', x, y,
            line: { color: '#38bdf8', width: 2.6, shape: 'spline', smoothing: 0.85 },
            fill: 'tozeroy', fillcolor: 'rgba(56,189,248,0.12)',
            name: 'Output',
            hovertemplate: '%{x|%Y-%m-%d %H:%M}<br>%{y:.0f}<extra></extra>'
        },
        // Now marker
        ...(lastX !== undefined ? [
            { type: 'scatter', mode: 'markers', x: [lastX], y: [current], marker: { size: 16, color: 'rgba(56,189,248,0.18)', line: { width: 0 } }, hoverinfo: 'skip', showlegend: false },
            { type: 'scatter', mode: 'markers', x: [lastX], y: [current], marker: { size: 7, color: '#38bdf8', line: { width: 2, color: 'rgba(56,189,248,0.48)' } }, name: 'Now', hovertemplate: '%{y:.0f}<extra>Now</extra>' },
        ] : []),
    ];

    const layout = React.useMemo(() => ({
        height: 160,
        xaxis: { type: 'date', showgrid: false, ticks: 'outside', ticklen: 3, tickcolor: 'rgba(255,255,255,0.2)', tickfont: { size: 11, color: 'rgba(229,231,235,0.66)' } },
        yaxis: { showgrid: false, ticks: '', showticklabels: false, rangemode: 'tozero' },
        showlegend: false,
        margin: { t: 8, r: 8, b: 12, l: 8 },
        annotations: (lastX !== undefined) ? [{
            x: lastX, y: current,
            xref: 'x', yref: 'y', showarrow: false,
            text: `${formatNumber(current, 0)}`,
            xanchor: 'left', yanchor: 'bottom',
            bgcolor: 'rgba(2,6,23,0.8)', bordercolor: 'rgba(56,189,248,0.5)', borderwidth: 1,
            font: { size: 11 },
            ay: -16, ax: 8,
        }] : [],
    }), [lastX, current]);

    const kpis = [
        { label: 'Current', value: `${formatNumber(current, 0)}` },
        { label: '24h Avg', value: `${formatNumber(avg24, 0)}` },
        { label: '24h Peak', value: `${formatNumber(peak24, 0)}` },
        { label: 'Change', value: `${formatNumber(deltaPct, 1)}%` },
    ];

    return (
        <CardShell
            title="Processing Output"
            kpis={kpis}
            kpiCols={2}
            kpiNoWrap
            controls={<TimeframeControls value={windowKey} onChange={setWindowKey} />}
            ariaLabel="Blue area output trend"
        >
            <div style={{ height: '100%' }}>
                <PlotClient data={traces} layout={layout} />
            </div>
        </CardShell>
    );
}
