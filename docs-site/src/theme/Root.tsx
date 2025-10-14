import React from 'react';
import ErrorBoundary from '@site/src/components/ErrorBoundary';
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
    React.useEffect(() => {
        // Initialize auth subsystem (explicit init avoids import-time side-effects)
        try { initAuth(); } catch { /* ignore init errors during tests */ }

        const unsubscribe = onAuthChange((isAuth) => setLoggedIn(isAuth));
        return () => { unsubscribe(); };
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
                if (authenticated) {
                    scDebug('authentication detected - notifying listeners');
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

            if (!hasQueryCode && !hasHashTokens) {
                await pollUntilAuthenticated({ maxAttempts: 10, intervalMs: 500 });
                return;
            }

            scDebug('OAuth callback detected, waiting for Amplify to process...');
            let refreshSucceeded = false;
            try {
                refreshSucceeded = await refreshAuthState();
                scDebug('refreshAuthState completed', { refreshSucceeded });
            } catch (err) {
                scDebug('refreshAuthState threw', err);
            }
            if (cancelled) return;
            if (refreshSucceeded) {
                scDebug('refreshAuthState resolved authentication, cleaning URL');
                cleanUrl();
                return;
            }

            await pollUntilAuthenticated({
                maxAttempts: 40,
                intervalMs: 500,
                onSuccess: async () => {
                    scDebug('Auth resolved via polling - cleaning URL');
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
