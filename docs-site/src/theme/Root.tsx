import React from 'react';
import ErrorBoundary from '@site/src/components/ErrorBoundary';
import SiteFooter from '@site/src/components/SiteFooter';
import { isLoggedIn, onAuthChange, notifyAuthChange } from '@site/src/utils/auth-cognito';
import { useLocation } from '@docusaurus/router';

// Log deployment info for debugging cache issues
if (typeof window !== 'undefined') {
    // deployment info fetch removed for production
}

export default function Root({ children }: { children: React.ReactNode }) {
    const location = useLocation();
    const [loggedIn, setLoggedIn] = React.useState<boolean>(false);
    React.useEffect(() => {
        const unsubscribe = onAuthChange((isAuth) => setLoggedIn(isAuth));
        return () => { unsubscribe(); };
    }, []);

    // Handle OAuth callback - Amplify v6 processes automatically, we just notify listeners
    React.useEffect(() => {
        function scDebug(...args: any[]) {
            try {
                if (typeof window !== 'undefined' && (window as any).__SC_AUTH_DEBUG__) {
                    // eslint-disable-next-line no-console
                    console.debug('[SC-ROOT]', ...args);
                }
            } catch { /* ignore */ }
        }

        function dumpUrlState() {
            try {
                if (typeof window === 'undefined') return {};
                return {
                    href: window.location.href,
                    pathname: window.location.pathname,
                    search: window.location.search,
                    hash: window.location.hash,
                };
            } catch (err) { return { err: String(err) }; }
        }

        const handleOAuthCallback = async () => {
            const params = new URLSearchParams(window.location.search);
            const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ''));
            const hasQueryCode = params.has('code') || params.has('state');
            const hasHashTokens = hashParams.has('id_token') || hashParams.has('access_token');
            scDebug('handleOAuthCallback - url state:', dumpUrlState(), 'hasQueryCode:', hasQueryCode, 'hasHashTokens:', hasHashTokens);
            if (!hasQueryCode && !hasHashTokens) {
                // Even without explicit callback markers, we might be landing here right after redirect.
                // Perform a short polling window once on mount to catch freshly established sessions.
                let attempts = 0;
                const maxAttempts = 10; // ~5 seconds
                const interval = setInterval(async () => {
                    attempts++;
                    const authenticated = await isLoggedIn();
                    scDebug('polling attempt', attempts, 'authenticated:', authenticated);
                    if (authenticated) {
                        scDebug('polling detected authenticated - notifying');
                        clearInterval(interval);
                        await notifyAuthChange();
                    } else if (attempts >= maxAttempts) {
                        scDebug('polling finished without auth');
                        clearInterval(interval);
                    }
                }, 500);
                return;
            }
            scDebug('OAuth callback detected, waiting for Amplify to process...');
            let attempts = 0;
            const maxAttempts = 40; // ~20 seconds
            const checkInterval = setInterval(async () => {
                attempts++;
                const authenticated = await isLoggedIn();
                scDebug('Auth check attempt', attempts, 'authenticated:', authenticated);

                if (authenticated) {
                    scDebug('User authenticated - notifying listeners and cleaning URL');
                    clearInterval(checkInterval);
                    await notifyAuthChange();
                    // Clean up URL params/hash without triggering navigation
                    window.history.replaceState({}, document.title, location.pathname);
                } else if (attempts >= maxAttempts) {
                    scDebug('Auth timeout - tokens not received');
                    clearInterval(checkInterval);
                }
            }, 500);
        };
        handleOAuthCallback();
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
