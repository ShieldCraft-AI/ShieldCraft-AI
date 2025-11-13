import React from 'react';
import ErrorBoundary from '@site/src/components/ErrorBoundary';
import { Amplify } from 'aws-amplify';
import SiteFooter from '@site/src/components/SiteFooter';
import { isLoggedIn, onAuthChange, notifyAuthChange, initAuth, refreshAuthState } from '@site/src/utils/auth-cognito';
import { useLocation } from '@docusaurus/router';

export default function Root({ children }: { children: React.ReactNode }) {
    const location = useLocation();
    const [loggedIn, setLoggedIn] = React.useState<boolean>(false);
    // NOTE 2025-10-16: Prior version forced window.location.replace() after refreshAuthState success.
    // To revert that behaviour, reintroduce the reload guard in handleOAuthCallback and onAuthChange.
    React.useEffect(() => {
        if (typeof window === 'undefined') return;
        const pending = sessionStorage.getItem('__sc_auth_pending_emit');
        if (pending === '1') {
            sessionStorage.removeItem('__sc_auth_pending_emit');
            window.requestAnimationFrame(() => {
                void notifyAuthChange().catch(() => undefined);
            });
        }
    }, []);
    React.useEffect(() => {
        let cancelled = false;
        // Attempt to load runtime Amplify config (deployed site can drop this file into /)
        (async () => {
            try {
                await initAuth();
                if (typeof window === 'undefined' || cancelled) return;
                const res = await fetch('/amplify-config.json', { cache: 'no-store' });
                if (!res.ok) return;
                const cfg = await res.json();
                if (cfg && typeof (Amplify as any).configure === 'function' && !cancelled) {
                    try {
                        if (typeof window !== 'undefined') {
                            (window as any).__SC_AMPLIFY_CONFIG__ = cfg;
                        }
                        (Amplify as any).configure(cfg);
                        await initAuth({ force: true });
                    } catch { /* ignore */ }
                }
            } catch {
                /* ignore fetch/config errors - initAuth will still attempt default flow */
            }
        })();

        const unsubscribe = onAuthChange((isAuth) => {
            setLoggedIn(isAuth);
        });

        // HMR: when auth-cognito changes during development, re-import and re-init
        try {
            if (typeof module !== 'undefined' && (module as any).hot) {
                (module as any).hot.accept('@site/src/utils/auth-cognito', async () => {
                    try {
                        const auth = await import('@site/src/utils/auth-cognito');
                        if (auth && typeof auth.initAuth === 'function') {
                            await auth.initAuth({ force: true }).catch(() => undefined);
                        }
                        if (auth && typeof auth.notifyAuthChange === 'function') {
                            await auth.notifyAuthChange(true).catch(() => undefined);
                        }
                    } catch (e) {
                        /* ignore HMR reload failures */
                    }
                });
            }
        } catch { /* ignore HMR errors */ }
        return () => {
            cancelled = true;
            unsubscribe();
        };
    }, []);

    // Handle OAuth callback - Amplify v6 processes automatically, we just notify listeners
    React.useEffect(() => {
        let cancelled = false;
        let timer: ReturnType<typeof setTimeout> | undefined;
        let settleWait: (() => void) | undefined;

        const clearTimer = () => {
            if (timer !== undefined) {
                clearTimeout(timer);
                timer = undefined;
            }
            if (settleWait) {
                const settle = settleWait;
                settleWait = undefined;
                settle();
            }
        };

        const wait = (ms: number) => new Promise<void>((resolve) => {
            clearTimer();
            settleWait = resolve;
            timer = setTimeout(() => {
                settleWait = undefined;
                timer = undefined;
                resolve();
            }, ms);
        });

        const pollUntilAuthenticated = async ({ maxAttempts, intervalMs, onSuccess }: { maxAttempts: number; intervalMs: number; onSuccess?: () => Promise<void> | void; }) => {
            for (let attempt = 1; attempt <= maxAttempts && !cancelled; attempt += 1) {
                await wait(intervalMs);
                if (cancelled) return false;
                const authenticated = await isLoggedIn();
                if (authenticated) {
                    await notifyAuthChange();
                    if (onSuccess) await onSuccess();
                    return true;
                }
            }
            return false;
        };

        const cleanUrl = () => {
            try { window.history.replaceState({}, document.title, location.pathname); } catch { /* ignore */ }
        };

        const handleOAuthCallback = async () => {
            const params = new URLSearchParams(window.location.search);
            const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ''));
            const hasQueryCode = params.has('code') || params.has('state');
            const hasHashTokens = hashParams.has('id_token') || hashParams.has('access_token');

            if (!hasQueryCode && !hasHashTokens) {
                await pollUntilAuthenticated({ maxAttempts: 10, intervalMs: 500 });
                return;
            }

            let refreshSucceeded = false;
            try {
                refreshSucceeded = await refreshAuthState();
            } catch (err) {
                /* ignore refresh failures, poll authentication below */
            }
            if (cancelled) return;
            if (refreshSucceeded) {
                try {
                    // Force a deterministic sign-in notify so listeners do not need to
                    // re-evaluate isLoggedIn() which may race with the hydrated session.
                    await notifyAuthChange(true);
                } catch { /* ignore */ }
                cleanUrl();
                try {
                    sessionStorage.removeItem('__sc_auth_pending_emit');
                } catch { /* ignore */ }
                return;
            }

            await pollUntilAuthenticated({
                maxAttempts: 40,
                intervalMs: 500,
                onSuccess: async () => {
                    cleanUrl();
                },
            });
        };

        handleOAuthCallback();

        return () => {
            cancelled = true;
            clearTimer();
        };
    }, [location.pathname, location.search]);
    // For safety: also hide footer on authenticated app-like routes even if auth missed
    const path = location.pathname;
    const isPortalRoute = (
        path.startsWith('/alerts') ||
        path.startsWith('/dashboard') ||
        path.startsWith('/recent-activity') ||
        path.startsWith('/threat-feed') ||
        path.startsWith('/system-status') ||
        path.startsWith('/monitoring') ||
        path.startsWith('/portal')
    );
    const showFooter = !isPortalRoute;
    return (
        <ErrorBoundary>
            <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
                <div style={{ flex: '1 0 auto' }}>{children}</div>
                {showFooter && <SiteFooter />}
            </div>
        </ErrorBoundary>
    );
}
