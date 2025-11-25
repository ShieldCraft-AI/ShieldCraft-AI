import React, { useEffect, useState } from 'react';
import Link from '@docusaurus/Link';

const STORAGE_KEY = 'sc_guard_banner_v1';

interface GuardSuiteBannerProps {
    enabled: boolean;
}

export default function GuardSuiteBanner({ enabled }: GuardSuiteBannerProps) {
    const [dismissed, setDismissed] = useState(true);
    const [topOffset, setTopOffset] = useState<number | null>(null);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        try {
            const stored = window.localStorage.getItem(STORAGE_KEY);
            if (stored !== 'true') {
                setDismissed(false);
            }
        } catch {
            setDismissed(false);
        }
    }, []);

    useEffect(() => {
        if (typeof window === 'undefined' || typeof document === 'undefined') return;

        const computeOffset = () => {
            const headerEl = document.getElementById('sc-universal-header');
            if (!headerEl) return;
            const headerHeight = headerEl.getBoundingClientRect().height;
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
        };
    }, []);

    const handleDismiss = () => {
        setDismissed(true);
        if (typeof window === 'undefined') return;
        try {
            window.localStorage.setItem(STORAGE_KEY, 'true');
        } catch {
            // ignore storage errors
        }
    };

    if (!enabled || dismissed) return null;

    return (
        <div className="guardSuiteBanner" style={topOffset ? { top: `${topOffset}px` } : undefined}>
            <div className="guardSuiteBanner__content">
                <span className="guardSuiteBanner__pill">New</span>
                <p>
                    VectorScan  -  free Terraform plan scanner. Scan your <code>tfplan.json</code> in one command.
                </p>
                <div className="guardSuiteBanner__actions">
                    <Link className="button button--primary button--sm" to="/products/vectorscan">
                        Try VectorScan
                    </Link>
                    <Link className="button button--secondary button--sm" to="/guard-suite">
                        Guard Suite
                    </Link>
                </div>
            </div>
            <button className="guardSuiteBanner__close" type="button" aria-label="Dismiss Guard Suite banner" onClick={handleDismiss}>
                ×
            </button>
        </div>
    );
}
