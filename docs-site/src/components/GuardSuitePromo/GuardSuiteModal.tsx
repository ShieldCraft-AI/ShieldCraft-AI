import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import Link from '@docusaurus/Link';
import { isLoggedIn } from '@site/src/utils/auth-cognito';

const STORAGE_KEY = 'sc_guard_modal_last_shown_v1';
const MODAL_DELAY_MS = 7000;
const MODAL_COOLDOWN_MS = 24 * 60 * 60 * 1000; // once per day

interface GuardSuiteModalProps {
    enabled: boolean;
    pathname: string;
}

const marketingPaths = ['/', '/pricing', '/guard-suite', '/infrastructure', '/architecture'];

function isMarketingRoute(pathname: string): boolean {
    if (pathname === '/') return true;
    return marketingPaths.some((prefix) => prefix !== '/' && pathname.startsWith(prefix));
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
                const loggedIn = await isLoggedIn();
                if (loggedIn) return;
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

    return createPortal(
        <div className="guardSuiteModal" role="dialog" aria-modal="true" aria-label="Guard Suite promo">
            <div className="guardSuiteModal__backdrop" onClick={handleClose} />
            <div className="guardSuiteModal__card">
                <span className="guardSuiteModal__pill">New</span>
                <h2>Try VectorScan Free</h2>
                <p>
                    Scan your Terraform plan in one command. No accounts, no uploads. Upgrade to VectorGuard when you&apos;re ready for Zero-Trust
                    enforcement.
                </p>
                <div className="guardSuiteModal__actions">
                    <Link className="button button--primary" to="/products/vectorscan" onClick={handleClose}>
                        Download VectorScan
                    </Link>
                    <Link className="button button--secondary" to="/guard-suite" onClick={handleClose}>
                        Explore Guard Suite
                    </Link>
                </div>
                <button className="guardSuiteModal__close" type="button" aria-label="Close Guard Suite modal" onClick={handleClose}>
                    Close
                </button>
            </div>
        </div>,
        document.body
    );
}
