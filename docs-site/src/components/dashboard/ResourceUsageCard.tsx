import React from 'react';
import CardShell from './CardShell';
import PlotClient from './PlotClient';
import styles from './card.module.css';

function clamp(v: number, min = 0, max = 100) { return Math.min(max, Math.max(min, v)); }

export default function ResourceUsageCard() {
    const live = true;
    const [cpu, setCpu] = React.useState(65);
    const [mem, setMem] = React.useState(70);

    React.useEffect(() => {
        const id = setInterval(() => {
            setCpu(p => clamp(p + (Math.random() - 0.5) * 3));
            setMem(p => clamp(p + (Math.random() - 0.5) * 3));
        }, 2500);
        return () => clearInterval(id);
    }, []);

    const gauge = (value: number, label: string, colors: [string, string]) => ({
        type: 'pie',
        values: [value, 100 - value],
        labels: [label, ''],
        hole: 0.7,
        textinfo: 'none',
        marker: { colors: [colors[0], 'rgba(255,255,255,0.06)'] },
        sort: false,
        direction: 'clockwise' as const,
        hovertemplate: `${label}: %{value:.0f}%<extra></extra>`,
        name: label,
        showlegend: false,
    });

    const cpuColor = cpu > 85 ? '#f87171' : cpu > 70 ? '#fb923c' : '#34d399';
    const memColor = mem > 85 ? '#f87171' : mem > 70 ? '#fb923c' : '#60a5fa';

    const kpis = [
        { label: 'CPU', value: `${cpu.toFixed(0)}%` },
        { label: 'Memory', value: `${mem.toFixed(0)}%` },
    ];

    return (
        <CardShell
            title="Resource Usage"
            kpis={kpis}
            kpiCols={2}
            ariaLabel="CPU and Memory utilization"
        >
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, height: '100%' }}>
                <PlotClient data={[gauge(cpu, 'CPU', [cpuColor, 'rgba(255,255,255,0.06)'])]} layout={{ height: 160, showlegend: false, margin: { t: 8, r: 8, b: 8, l: 8 }, annotations: [{ text: `${cpu.toFixed(0)}%`, x: 0.5, y: 0.5, xref: 'paper', yref: 'paper', showarrow: false, font: { size: 16 } }] }} />
                <PlotClient data={[gauge(mem, 'Memory', [memColor, 'rgba(255,255,255,0.06)'])]} layout={{ height: 160, showlegend: false, margin: { t: 8, r: 8, b: 8, l: 8 }, annotations: [{ text: `${mem.toFixed(0)}%`, x: 0.5, y: 0.5, xref: 'paper', yref: 'paper', showarrow: false, font: { size: 16 } }] }} />
            </div>
        </CardShell>
    );
}
