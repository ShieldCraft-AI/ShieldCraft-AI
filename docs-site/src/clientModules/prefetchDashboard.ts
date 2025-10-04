export default function () {
    if (typeof window === 'undefined') return;
    // Skip prefetch on the landing page to avoid showing the top progress bar
    if (location.pathname === '/') return;
    // Prefetch the chart lib shortly after load for non-landing routes
    setTimeout(() => {
        try {
            import('react-plotly.js');
        } catch { /* no-op */ }
    }, 300);
}
