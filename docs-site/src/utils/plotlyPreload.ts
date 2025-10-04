let preloadPromise: Promise<any> | null = null;

export function preloadPlotly() {
    if (typeof window === 'undefined') return null;
    if (!preloadPromise) {
        try {
            preloadPromise = import('react-plotly.js');
        } catch {
            // ignore
        }
    }
    return preloadPromise;
}
