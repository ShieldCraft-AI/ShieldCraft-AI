import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { loadPlotly } from '@site/src/utils/plotlyPreload';
import logger from '@site/src/utils/logger';

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
        logger.warn('[PlotClient] Chart error:', err);
    }
    render() {
        if (this.state.hasError) return this.props.fallback ?? <div role="status" aria-live="polite" style={{ height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.7 }}>Chart unavailable</div>;
        return this.props.children as React.ReactElement;
    }
}

export default function PlotClient(props: PlotClientProps) {
    const containerRef = React.useRef<HTMLDivElement | null>(null);
    const mountedRef = React.useRef(false);
    const [shouldLoad, setShouldLoad] = React.useState(false);
    const [Plot, setPlot] = React.useState<React.ComponentType<any> | null>(null);

    React.useEffect(() => {
        mountedRef.current = true;
        return () => { mountedRef.current = false; };
    }, []);

    React.useEffect(() => {
        if (typeof window === 'undefined' || shouldLoad) return;
        const node = containerRef.current;
        if (!node) {
            setShouldLoad(true);
            return;
        }
        if (!('IntersectionObserver' in window)) {
            setShouldLoad(true);
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting || entry.intersectionRatio > 0) {
                    setShouldLoad(true);
                    observer.disconnect();
                }
            });
        }, { rootMargin: '160px' });

        observer.observe(node);
        return () => observer.disconnect();
    }, [shouldLoad]);

    React.useEffect(() => {
        if (!shouldLoad || Plot || typeof window === 'undefined') return;
        let cancelled = false;
        const promise = loadPlotly();
        if (!promise) {
            setShouldLoad(true);
            return;
        }
        promise
            .then((mod) => {
                if (cancelled || !mountedRef.current) return;
                setPlot(() => mod.default);
            })
            .catch((err) => {
                if (!cancelled) logger.warn('[PlotClient] Failed to load Plotly chunk:', err);
            });
        return () => {
            cancelled = true;
        };
    }, [Plot, shouldLoad]);

    const safeData = React.useMemo(() => Array.isArray(props.data) ? props.data.filter(Boolean) : [], [props.data]);
    const safeLayout = React.useMemo(() => (props.layout && typeof props.layout === 'object') ? props.layout : {}, [props.layout]);
    const safeConfig = React.useMemo(() => (props.config && typeof props.config === 'object') ? props.config : {}, [props.config]);

    const containerStyle = React.useMemo<React.CSSProperties>(() => ({
        width: '100%',
        height: '160px',
        position: 'relative',
        overflow: 'hidden',
        borderRadius: '8px',
        ...(props.style ?? {})
    }), [props.style]);

    const placeholder = (
        <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.1)', borderRadius: '8px' }}>
            Loading chart…
        </div>
    );

    return (
        <div ref={containerRef} className={props.className} style={containerStyle}>
            <BrowserOnly fallback={placeholder}>
                {() => {
                    if (!shouldLoad || !Plot) {
                        return placeholder;
                    }
                    return (
                        <PlotErrorBoundary>
                            <Plot
                                data={safeData}
                                layout={{
                                    width: undefined,
                                    height: 160,
                                    autosize: false,
                                    margin: { t: 20, r: 20, b: 40, l: 50 },
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
                                        showspikes: false,
                                    },
                                    yaxis: {
                                        gridcolor: 'rgba(255,255,255,0.06)',
                                        zeroline: false,
                                        linecolor: 'rgba(255,255,255,0.12)',
                                        tickcolor: 'rgba(255,255,255,0.12)',
                                        tickfont: { size: 10 },
                                        showspikes: false,
                                    },
                                    showlegend: false,
                                    ...safeLayout,
                                }}
                                useResizeHandler={true}
                                config={{
                                    displayModeBar: false,
                                    displaylogo: false,
                                    responsive: true,
                                    ...safeConfig
                                }}
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    maxWidth: '100%',
                                    maxHeight: '100%'
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
                    );
                }}
            </BrowserOnly>
        </div>
    );
}
