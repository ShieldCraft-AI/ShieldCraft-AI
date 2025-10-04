export default function () {
    if (typeof window === 'undefined') return;
    // Diagnostics: detect devicePixelRatio and CSS pixel width for CloudFront variation
    (window as any).__SC_VIEWPORT__ = {
        dpr: window.devicePixelRatio,
        width: window.innerWidth,
        height: window.innerHeight,
        ua: navigator.userAgent,
    };
}
