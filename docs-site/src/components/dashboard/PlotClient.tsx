import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { preloadPlotly } from '@site/src/utils/plotlyPreload';

// Lightweight SSR-safe Plotly wrapper. Lazy-loads react-plotly.js on client only.
export type PlotClientProps = {
    data: any[];
    layout?: any;
    config?: any;
    style?: React.CSSProperties;
    className?: string;
    onInitialized?: (figure: any) => void;
    onUpdate?: (figure: any) => void;
};

// Error boundary to catch rendering/lifecycle errors from the Plotly component.
class PlotErrorBoundary extends React.Component<React.PropsWithChildren<{ fallback?: React.ReactNode }>, { hasError: boolean }> {
    constructor(props: React.PropsWithChildren<{ fallback?: React.ReactNode }>) {
        super(props);
        this.state = { hasError: false };
    }
    static getDerivedStateFromError() {
        return { hasError: true };
    }
    componentDidCatch(err: any) {
        // Swallow known transient Plotly errors during rapid unmount/mount cycles
        const msg = String(err?.message || err || '');
        if (msg.includes("_plots")) {
            // no-op; this happens if Plotly resizes after purge during navigation
            return;
        }
        // Log unexpected errors for diagnostics
        if (typeof console !== 'undefined') console.warn('[PlotClient] Chart error:', err);
    }
    render() {
        if (this.state.hasError) return this.props.fallback ?? <div role="status" aria-live="polite" style={{ height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.7 }}>Chart unavailable</div>;
        return this.props.children as React.ReactElement;
    }
}

export default function PlotClient(props: PlotClientProps) {
    const mountedRef = React.useRef(false);
    React.useEffect(() => { mountedRef.current = true; return () => { mountedRef.current = false; }; }, []);

    // Ensure safe inputs for Plotly
    const safeData = React.useMemo(() => Array.isArray(props.data) ? props.data.filter(Boolean) : [], [props.data]);
    const safeLayout = React.useMemo(() => (props.layout && typeof props.layout === 'object') ? props.layout : {}, [props.layout]);
    const safeConfig = React.useMemo(() => (props.config && typeof props.config === 'object') ? props.config : {}, [props.config]);

    return (
        <BrowserOnly fallback={<div style={{ height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.1)', borderRadius: '8px' }}>Loading chart…</div>}>
            {() => {
                try { preloadPlotly(); } catch { /* no-op */ }
                const Plot = require('react-plotly.js').default as React.ComponentType<any>;
                return (
                    <div
                        className={props.className}
                        style={{
                            width: '100%',
                            height: '160px', // Reduced to fit within 400px cards
                            position: 'relative',
                            overflow: 'hidden', // Critical: prevent charts from breaking out
                            borderRadius: '8px',
                            ...props.style
                        }}
                    >
                        <PlotErrorBoundary>
                            <Plot
                                data={safeData}
                                layout={{
                                    // Force exact container sizing
                                    width: undefined, // Let container control width
                                    height: 160, // Match container height
                                    autosize: false, // Disable autosize to prevent overflow
                                    margin: { t: 20, r: 20, b: 40, l: 50 }, // Reasonable margins
                                    paper_bgcolor: 'transparent',
                                    plot_bgcolor: 'transparent',
                                    font: {
                                        size: 11,
                                        family: 'Inter, ui-sans-serif, system-ui, Segoe UI, Roboto, Helvetica, Arial',
                                        color: 'var(--portal-text-color, #e5e7eb)'
                                    },
                                    colorway: ['#22d3ee', '#a78bfa', '#f472b6', '#34d399', '#f59e0b', '#60a5fa'],
                                    hovermode: 'closest',
                                    hoverlabel: {
                                        bgcolor: 'rgba(17,24,39,0.9)',
                                        bordercolor: 'rgba(255,255,255,0.08)',
                                        font: { color: '#e5e7eb' }
                                    },
                                    xaxis: {
                                        gridcolor: 'rgba(255,255,255,0.06)',
                                        zeroline: false,
                                        linecolor: 'rgba(255,255,255,0.12)',
                                        tickcolor: 'rgba(255,255,255,0.12)',
                                        tickfont: { size: 10 },
                                        showspikes: false, // Disable spikes to reduce clutter
                                    },
                                    yaxis: {
                                        gridcolor: 'rgba(255,255,255,0.06)',
                                        zeroline: false,
                                        linecolor: 'rgba(255,255,255,0.12)',
                                        tickcolor: 'rgba(255,255,255,0.12)',
                                        tickfont: { size: 10 },
                                        showspikes: false, // Disable spikes to reduce clutter
                                    },
                                    showlegend: false, // Disable legend to save space
                                    ...safeLayout,
                                }}
                                useResizeHandler={true} // Enable but controlled by container
                                config={{
                                    displayModeBar: false,
                                    displaylogo: false,
                                    responsive: true, // Let it be responsive within container
                                    ...safeConfig
                                }}
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    maxWidth: '100%', // Prevent overflow
                                    maxHeight: '100%' // Prevent overflow
                                }}
                                onInitialized={(fig: any) => {
                                    if (!mountedRef.current) return;
                                    try { props.onInitialized?.(fig); } catch { /* swallow */ }
                                }}
                                onUpdate={(fig: any) => {
                                    if (!mountedRef.current) return;
                                    try { props.onUpdate?.(fig); } catch { /* swallow */ }
                                }}
                            />
                        </PlotErrorBoundary>
                    </div>
                );
            }}
        </BrowserOnly>
    );
}
