import React from 'react';
import ErrorBoundary from '@site/src/components/ErrorBoundary';
import { Amplify } from 'aws-amplify';
import SiteFooter from '@site/src/components/SiteFooter';
import { isLoggedIn, onAuthChange, notifyAuthChange, initAuth, refreshAuthState } from '@site/src/utils/auth-cognito';
import { useLocation } from '@docusaurus/router';

// Log deployment info for debugging cache issues
if (typeof window !== 'undefined') {
    // deployment info fetch removed for production
}

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
                void notifyAuthChange().catch((err) => {
                    console.debug('[Root] pending auth notify failed', err);
                });
            });
        }
    }, []);
    React.useEffect(() => {
        let cancelled = false;
        // Attempt to load runtime Amplify config (deployed site can drop this file into /)
        (async () => {
            try {
                console.debug('[Root] invoking initAuth for baseline configuration');
                await initAuth();
                if (typeof window === 'undefined' || cancelled) return;
                console.debug('[Root] fetching runtime amplify-config.json');
                const res = await fetch('/amplify-config.json', { cache: 'no-store' });
                if (res.ok) {
                    const cfg = await res.json();
                    console.debug('[Root] fetched amplify config', cfg);
                    if (cfg && typeof (Amplify as any).configure === 'function' && !cancelled) {
                        try {
                            if (typeof window !== 'undefined') {
                                (window as any).__SC_AMPLIFY_CONFIG__ = cfg;
                            }
                            (Amplify as any).configure(cfg);
                            await initAuth({ force: true });
                        } catch (e) { /* ignore */ }
                    }
                } else if (!cancelled) {
                    if (res.status === 404) {
                        console.warn('[Root] amplify-config.json missing. Run scripts/pull_amplify_config.py or ensure CI injects the file before build.');
                    } else {
                        console.warn('[Root] amplify-config fetch failed', res.status, res.statusText);
                    }
                }
            } catch (e) {
                if (!cancelled) {
                    // ignore fetch/config errors - initAuth will still try to work with whatever is available
                    console.error('[Root] amplify-config fetch error', e);
                }
            }
        })();

        const unsubscribe = onAuthChange((isAuth) => {
            console.debug('[Root] onAuthChange', isAuth);
            setLoggedIn(isAuth);
        });
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

        const scDebug = (...args: any[]) => {
            try {
                if (typeof window !== 'undefined' && (window as any).__SC_AUTH_DEBUG__) {
                    // eslint-disable-next-line no-console
                    console.debug('[SC-ROOT]', ...args);
                }
            } catch { /* ignore */ }
        };

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
                scDebug('poll auth attempt', attempt, 'authenticated:', authenticated);
                console.debug('[Root] poll auth attempt', attempt, 'authenticated:', authenticated);
                if (authenticated) {
                    scDebug('authentication detected - notifying listeners');
                    console.debug('[Root] authentication detected, notifying listeners');
                    await notifyAuthChange();
                    if (onSuccess) await onSuccess();
                    return true;
                }
            }
            scDebug('polling finished without authentication');
            return false;
        };

        const dumpUrlState = () => {
            try {
                if (typeof window === 'undefined') return {};
                return {
                    href: window.location.href,
                    pathname: window.location.pathname,
                    search: window.location.search,
                    hash: window.location.hash,
                };
            } catch (err) { return { err: String(err) }; }
        };

        const cleanUrl = () => {
            try { window.history.replaceState({}, document.title, location.pathname); } catch { /* ignore */ }
        };

        const handleOAuthCallback = async () => {
            const params = new URLSearchParams(window.location.search);
            const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ''));
            const hasQueryCode = params.has('code') || params.has('state');
            const hasHashTokens = hashParams.has('id_token') || hashParams.has('access_token');
            scDebug('handleOAuthCallback - url state:', dumpUrlState(), 'hasQueryCode:', hasQueryCode, 'hasHashTokens:', hasHashTokens);
            console.debug('[Root] handleOAuthCallback', { url: dumpUrlState(), hasQueryCode, hasHashTokens });

            if (!hasQueryCode && !hasHashTokens) {
                await pollUntilAuthenticated({ maxAttempts: 10, intervalMs: 500 });
                return;
            }

            scDebug('OAuth callback detected, waiting for Amplify to process...');
            let refreshSucceeded = false;
            try {
                refreshSucceeded = await refreshAuthState();
                scDebug('refreshAuthState completed', { refreshSucceeded });
                console.debug('[Root] refreshAuthState completed', { refreshSucceeded });
            } catch (err) {
                scDebug('refreshAuthState threw', err);
                console.error('[Root] refreshAuthState threw', err);
            }
            if (cancelled) return;
            if (refreshSucceeded) {
                scDebug('refreshAuthState resolved authentication, cleaning URL');
                console.debug('[Root] refreshAuthState succeeded, cleaning URL');
                try {
                    // Force a deterministic sign-in notify so listeners do not need to
                    // re-evaluate isLoggedIn() which may race with the hydrated session.
                    await notifyAuthChange(true);
                } catch (err) {
                    console.error('[Root] forced notifyAuthChange after refresh failed', err);
                }
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
                    scDebug('Auth resolved via polling - cleaning URL');
                    console.debug('[Root] auth resolved via polling, cleaning URL');
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
