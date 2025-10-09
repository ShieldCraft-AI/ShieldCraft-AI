import React from 'react';
import detailStyles from '@site/src/pages/plugins/plugin-detail.module.css';

export default function RAGLatencyChart({ sloLimit = 300, data = [] }) {
  const width = 640;
  const height = 320;
  const margin = { top: 28, right: 48, bottom: 56, left: 68 };

  const values = data.flatMap((d) => [d.optimized, d.uncached, sloLimit]);
  const minValue = Math.max(0, Math.min(...values) - 40);
  const maxValue = Math.max(...values) + 40;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const xForIndex = (i) => {
    if (data.length === 1) return margin.left + innerWidth / 2;
    return margin.left + (i / (data.length - 1)) * innerWidth;
  };

  const yForValue = (v) => {
    const ratio = (v - minValue) / (maxValue - minValue);
    return height - margin.bottom - ratio * innerHeight;
  };

  const coordsToPath = (coords) => coords.map((c, i) => `${i === 0 ? 'M' : 'L'}${c.x},${c.y}`).join(' ');

  const optimizedCoords = [];
  const uncachedCoords = [];
  data.forEach((point, idx) => {
    const x = xForIndex(idx);
    optimizedCoords.push({ x, y: yForValue(point.optimized) });
    uncachedCoords.push({ x, y: yForValue(point.uncached) });
  });

  const deltaAreaCoords = [...uncachedCoords, ...optimizedCoords.slice().reverse()];
  const deltaAreaPath = `${coordsToPath(deltaAreaCoords)} Z`;
  const optimizedPath = coordsToPath(optimizedCoords);
  const uncachedPath = coordsToPath(uncachedCoords);

  const axisTicks = data.map((point, index) => ({ x: xForIndex(index), label: point.phase }));

  const tickCount = 5;
  const valueTicks = Array.from({ length: tickCount }, (_, idx) => {
    const value = minValue + ((maxValue - minValue) / (tickCount - 1)) * idx;
    return { value, y: yForValue(value) };
  });

  const sloY = yForValue(sloLimit);

  return (
    <svg className={detailStyles.chartSvg} viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby="rag-latency-chart">
      <title id="rag-latency-chart">RAG latency envelope vs P95 SLO</title>
      <defs>
        <linearGradient id="ragCacheDelta" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="rgba(99, 102, 241, 0.28)" />
          <stop offset="100%" stopColor="rgba(14, 165, 233, 0.08)" />
        </linearGradient>
      </defs>
      <path d={deltaAreaPath} fill="url(#ragCacheDelta)" opacity={0.95} />
      <path d={uncachedPath} fill="none" strokeWidth={2.6} strokeLinecap="round" style={{ stroke: 'orange' }} />
      <path d={optimizedPath} fill="none" strokeWidth={3} strokeLinecap="round" style={{ stroke: '#6366f1' }} />

      {uncachedCoords.map((dot, i) => (
        <circle key={`u-${i}`} cx={dot.x} cy={dot.y} r={5} fill="#fb923c" stroke="#0f172a" strokeWidth={1} />
      ))}
      {optimizedCoords.map((dot, i) => (
        <circle key={`o-${i}`} cx={dot.x} cy={dot.y} r={4.5} fill="#6366f1" stroke="#eef2ff" strokeWidth={1.2} />
      ))}

      <line x1={margin.left} y1={sloY} x2={width - margin.right} y2={sloY} stroke="#ef4444" strokeWidth={2.4} />
      <text x={width - margin.right + 6} y={sloY - 8} style={{ fontSize: 12, fill: '#ef4444' }}>
        {sloLimit}ms P95 SLO
      </text>

      <line x1={margin.left} y1={height - margin.bottom} x2={width - margin.right} y2={height - margin.bottom} stroke="rgba(148, 163, 184, 0.45)" strokeWidth={1} />
      <line x1={margin.left} y1={margin.top} x2={margin.left} y2={height - margin.bottom} stroke="rgba(148, 163, 184, 0.35)" strokeWidth={1} />

      {axisTicks.map((t) => (
        <text key={`tick-${t.label}`} x={t.x} y={height - margin.bottom + 26} className={detailStyles.chartAxisLabel} textAnchor="middle">
          {t.label}
        </text>
      ))}

      {valueTicks.map((tick) => (
        <g key={`vt-${tick.value.toFixed(0)}`}>
          <line x1={margin.left - 6} y1={tick.y} x2={width - margin.right} y2={tick.y} stroke="rgba(148, 163, 184, 0.18)" strokeWidth={0.75} />
          <text x={margin.left - 36} y={tick.y + 4} className={detailStyles.chartAxisLabel} textAnchor="end">
            {tick.value.toFixed(0)}
          </text>
        </g>
      ))}

      <text x={(width + margin.left) / 2} y={height - 8} className={detailStyles.chartAxisTitle}>
        Deployment phase
      </text>
      <text x={margin.left - 48} y={margin.top - 10} className={detailStyles.chartAxisTitle} transform={`rotate(-90 ${margin.left - 48},${margin.top - 10})`}>
        Latency (ms)
      </text>
    </svg>
  );
}
