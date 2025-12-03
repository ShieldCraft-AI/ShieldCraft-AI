import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import Link from '@docusaurus/Link';

const STORAGE_KEY = 'sc_guard_banner_v1';

interface GuardSuiteBannerProps {
    enabled: boolean;
}

function isLocalhostHost(): boolean {
    if (typeof window === 'undefined') return false;
    const host = window.location.hostname;
    return host === 'localhost' || host === '127.0.0.1' || host === '::1';
}

export default function GuardSuiteBanner({ enabled }: GuardSuiteBannerProps) {
    // Default to visible; respect explicit dismissal stored in localStorage (value 'true').
    const [dismissed, setDismissed] = useState<boolean>(() => {
        if (typeof window === 'undefined') return true;
        return false;
    });
    const [topOffset, setTopOffset] = useState<number | null>(null);
    const [portalRoot, setPortalRoot] = useState<HTMLElement | null>(null);
    const [debugEnabled, setDebugEnabled] = useState<boolean>(false);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        try {
            const params = new URLSearchParams(window.location.search);
            const forceShow = params.get('showBanner') === 'true';
            const debugParam = params.get('debugBanner') === 'true';
            // Only enable verbose/debug visuals when explicitly requested via
            // the `?debugBanner=true` query parameter. Do NOT enable debug
            // visuals automatically on localhost to avoid accidental styling
            // breaks in production-like environments.
            setDebugEnabled(!!debugParam);

            // Prefer sessionStorage for transient dismissals. If an old persistent
            // localStorage dismissal exists, migrate by removing it so returning
            // users will see the banner again (this is intentional to avoid
            // permanent suppression across sessions).
            let dismissedStored = false;
            try {
                const s = window.sessionStorage.getItem(STORAGE_KEY);
                if (s === 'true') dismissedStored = true;
            } catch { }

            if (!dismissedStored) {
                try {
                    const legacy = window.localStorage.getItem(STORAGE_KEY);
                    if (legacy === 'true') {
                        // Migrate: remove legacy persistent dismissal so banner can reappear.
                        try { window.localStorage.removeItem(STORAGE_KEY); } catch { }
                        if (debugParam || isLocalhostHost()) console.debug('[GuardSuiteBanner] migrated legacy dismissal and removed localStorage key');
                        // Do not mark dismissedStored true  -  we want to show the banner again.
                    }
                } catch { }
            }

            if (forceShow) {
                setDismissed(false);
                if (debugParam || isLocalhostHost()) console.debug('[GuardSuiteBanner] forced show via ?showBanner=true');
                return;
            }

            if (dismissedStored) {
                setDismissed(true);
                if (debugParam || isLocalhostHost()) console.debug('[GuardSuiteBanner] dismissed (sessionStorage)');
            } else {
                setDismissed(false);
                if (debugParam || isLocalhostHost()) console.debug('[GuardSuiteBanner] visible (no dismissal found)');
            }
        } catch (err) {
            // ignore storage errors and keep visible
            console.debug('[GuardSuiteBanner] storage read error', err);
        }
    }, []);

    useEffect(() => {
        if (typeof window === 'undefined' || typeof document === 'undefined') return;
        const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
        const debugEnabled = !!(urlParams && urlParams.get('debugBanner') === 'true');
        // Remove any pre-rendered banner instances (e.g., from built HTML) so we don't end up
        // with duplicates (one under the footer and one mounted here).
        try {
            const existing = Array.from(document.querySelectorAll('.guardSuiteBanner'));
            if (debugEnabled) console.debug('[GuardSuiteBanner] found pre-rendered instances:', existing.length);
            for (const el of existing) {
                // remove from DOM
                el.parentNode?.removeChild(el);
            }
        } catch {
            // ignore
        }

        // Ensure a single portal root for the banner
        let root = document.getElementById('sc-guard-banner-root');
        if (!root) {
            root = document.createElement('div');
            root.id = 'sc-guard-banner-root';
            document.body.appendChild(root);
        }
        setPortalRoot(root);

        if (debugEnabled) {
            console.debug('[GuardSuiteBanner] portal root created/attached', root);
        }

        const computeOffset = () => {
            // Try a few sensible selectors first (custom header id, docusaurus navbar, sticky header)
            const selectors = [
                '#sc-universal-header',
                'nav.theme-layout-navbar',
                '.theme-layout-navbar',
                'header[role="banner"]',
                'header',
            ];

            let headerEl: Element | null = null;
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && (el as HTMLElement).getBoundingClientRect().height > 0) {
                    headerEl = el;
                    break;
                }
            }

            // If no header found yet, try to discover a fixed/sticky element pinned to the top
            if (!headerEl) {
                const all = Array.from(document.body.querySelectorAll('*')) as Element[];
                for (const el of all) {
                    try {
                        const style = window.getComputedStyle(el as Element);
                        if ((style.position === 'fixed' || style.position === 'sticky') && style.top && style.top !== 'auto') {
                            const rect = (el as HTMLElement).getBoundingClientRect();
                            if (rect.height > 0 && rect.top <= 1) {
                                headerEl = el;
                                break;
                            }
                        }
                    } catch {
                        // ignore cross-origin or computed style errors
                    }
                }
            }

            if (!headerEl) return;
            const headerHeight = (headerEl as HTMLElement).getBoundingClientRect().height;
            const gap = window.innerWidth < 768 ? 12 : 18; // px spacing between header & banner
            setTopOffset(Math.round(headerHeight + gap));
        };

        computeOffset();

        const handleResize = () => {
            window.requestAnimationFrame(computeOffset);
        };

        window.addEventListener('resize', handleResize);

        let observer: ResizeObserver | null = null;
        if (typeof ResizeObserver !== 'undefined') {
            const headerEl = document.getElementById('sc-universal-header');
            if (headerEl) {
                observer = new ResizeObserver(() => computeOffset());
                observer.observe(headerEl);
            }
        }

        return () => {
            window.removeEventListener('resize', handleResize);
            observer?.disconnect();
            if (debugEnabled) console.debug('[GuardSuiteBanner] cleanup');
        };
    }, []);

    const handleDismiss = (e?: React.MouseEvent) => {
        // Prevent the dismissal click from triggering the banner navigation.
        try {
            e?.preventDefault();
            e?.stopPropagation();
        } catch { }
        setDismissed(true);
        if (typeof window === 'undefined') return;
        try {
            // Use sessionStorage so dismissal lasts only for this browser session.
            window.sessionStorage.setItem(STORAGE_KEY, 'true');
            // Also remove any legacy localStorage key if present.
            try { window.localStorage.removeItem(STORAGE_KEY); } catch { }
        } catch {
            // ignore storage errors
        }
    };

    if (!enabled || dismissed) return null;

    // Only show the banner on the landing page (root path).
    if (typeof window !== 'undefined' && window.location.pathname !== '/') return null;

    const wrapperStyle: React.CSSProperties = {
        position: 'fixed',
        left: 0,
        right: 0,
        top: topOffset ? `${topOffset}px` : 0,
        display: 'flex',
        justifyContent: 'center',
        zIndex: 9999,
        pointerEvents: 'auto',
    };

    // Do not apply debug visual outlines by default. Visual debugging can be
    // enabled explicitly via `?debugBanner=true` which sets `debugEnabled`.
    // Console debug messages are preserved for diagnostics.

    const banner = (
        // Make the entire banner clickable and navigate to /products/vectorscan.
        // Width is controlled via CSS to keep the banner compact and centered.
        <Link className="guardSuiteBanner" to="/products/vectorscan" aria-label="Open VectorScan product page">
            <div className="guardSuiteBanner__content">
                <p>
                    VectorScan  -  free Terraform plan scanner. Scan your <code>tfplan.json</code> in one command.
                </p>
            </div>
            <button className="guardSuiteBanner__close" type="button" aria-label="Dismiss Guard Suite banner" onClick={handleDismiss}>
                ×
            </button>
        </Link>
    );

    if (portalRoot) {
        return createPortal(<div style={wrapperStyle}>{banner}</div>, portalRoot);
    }

    return <div style={wrapperStyle}>{banner}</div>;
}
