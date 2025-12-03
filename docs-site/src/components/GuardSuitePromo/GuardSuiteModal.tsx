import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import Link from '@docusaurus/Link';
import { isLoggedIn } from '@site/src/utils/auth-cognito';

const STORAGE_KEY = 'sc_guard_modal_last_shown_v1';
// Keep default short for user-perceived responsiveness; changeable if desired.
const MODAL_DELAY_MS = 5000;
const MODAL_COOLDOWN_MS = 24 * 60 * 60 * 1000; // once per day

interface GuardSuiteModalProps {
    enabled: boolean;
    pathname: string;
}

const marketingPaths = ['/', '/pricing', '/guard-suite', '/infrastructure', '/architecture'];

function isMarketingRoute(pathname: string): boolean {
    // Only show modal on the landing page ('/').
    return pathname === '/';
}

function isLocalhostHost(): boolean {
    if (typeof window === 'undefined') return false;
    const host = window.location.hostname;
    return host === 'localhost' || host === '127.0.0.1' || host === '::1';
}

export default function GuardSuiteModal({ enabled, pathname }: GuardSuiteModalProps) {
    const [visible, setVisible] = useState(false);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        return () => setMounted(false);
    }, []);

    useEffect(() => {
        if (!enabled) {
            setVisible(false);
            return;
        }
        if (!isMarketingRoute(pathname)) {
            setVisible(false);
            return;
        }

        let timer: number | null = null;
        let cancelled = false;

        const scheduleModal = async () => {
            const bypassCooldown = isLocalhostHost();
            try {
                // Skip logged-in check on localhost/dev so modal is visible for testing.
                if (!bypassCooldown) {
                    const loggedIn = await isLoggedIn();
                    if (loggedIn) return;
                }
            } catch {
                // fail open (assume logged out)
            }

            if (typeof window === 'undefined') return;
            if (!bypassCooldown) {
                try {
                    const lastShown = window.localStorage.getItem(STORAGE_KEY);
                    if (lastShown) {
                        const elapsed = Date.now() - Number(lastShown);
                        if (!Number.isNaN(elapsed) && elapsed < MODAL_COOLDOWN_MS) {
                            return;
                        }
                    }
                } catch {
                    // ignore
                }
            }

            timer = window.setTimeout(() => {
                if (!cancelled) setVisible(true);
            }, MODAL_DELAY_MS);
        };

        void scheduleModal();

        return () => {
            cancelled = true;
            if (timer) window.clearTimeout(timer);
        };
    }, [enabled, pathname]);

    const handleClose = () => {
        setVisible(false);
        if (typeof window === 'undefined') return;
        if (isLocalhostHost()) return;
        try {
            window.localStorage.setItem(STORAGE_KEY, String(Date.now()));
        } catch {
            // ignore
        }
    };

    if (!mounted || !visible) return null;

    // Inline styles used as a robust fallback so the modal behaves correctly
    // even if site CSS is missing or overridden.
    const overlayStyle: React.CSSProperties = {
        position: 'fixed',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 12000,
        pointerEvents: 'auto',
    };

    const backdropStyle: React.CSSProperties = {
        position: 'fixed',
        inset: 0,
        // Allow CSS to tune backdrop darkness per theme via variable
        background: 'var(--guard-modal-backdrop, rgba(0,0,0,0.72))',
        backdropFilter: 'saturate(90%) blur(2px)',
        WebkitBackdropFilter: 'saturate(90%) blur(2px)',
    };

    const cardStyle: React.CSSProperties = {
        position: 'relative',
        maxWidth: 760,
        width: 'min(92%, 760px)',
        // Use a CSS variable with an opaque fallback so the modal card is
        // never transparent (prevents background copy bleeding through).
        // Use an opaque fallback (alpha = 1) to guarantee no bleed-through.
        background: 'var(--guard-modal-bg, rgba(255,255,255,1))',
        color: 'var(--guard-modal-fg, var(--ifm-font-color-base, #0f172a))',
        borderRadius: 12,
        boxShadow: '0 12px 40px rgba(2,6,23,0.25)',
        padding: '1.25rem 1.5rem',
        opacity: 1,
        mixBlendMode: 'normal',
        zIndex: 12001,
    };

    const pillStyle: React.CSSProperties = {
        display: 'inline-block',
        background: 'var(--ifm-color-primary, #0366d6)',
        color: '#fff',
        padding: '0.18rem 0.5rem',
        borderRadius: 8,
        fontSize: '0.85rem',
        fontWeight: 700,
        marginBottom: 8,
    };

    const actionsStyle: React.CSSProperties = {
        display: 'flex',
        gap: 12,
        marginTop: 12,
        flexWrap: 'wrap',
        justifyContent: 'flex-end',
    };

    return createPortal(
        <div style={overlayStyle} role="presentation">
            <div style={backdropStyle} onClick={handleClose} aria-hidden="true" />
            <div role="dialog" aria-modal="true" aria-label="Guard Suite promo" style={cardStyle}>
                <h2>Try VectorScan Free</h2>
                <p>
                    Scan your Terraform plan in one command. No accounts, no uploads. Upgrade to VectorGuard when you&apos;re ready for Zero-Trust
                    enforcement.
                </p>
                <div style={actionsStyle} className="guardSuiteModal__actions">
                    <Link className="button button--primary" to="/products/vectorscan" onClick={handleClose}>
                        Try VectorScan
                    </Link>
                    <Link className="button button--secondary" to="/guard-suite" onClick={handleClose}>
                        Explore Guard Suite
                    </Link>
                </div>
            </div>
        </div>,
        document.body
    );
}
