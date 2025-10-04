import React from 'react';
import ErrorBoundary from '@site/src/components/ErrorBoundary';
import SiteFooter from '@site/src/components/SiteFooter';
import { isLoggedIn, onAuthChange, notifyAuthChange } from '@site/src/utils/auth-cognito';
import { useLocation } from '@docusaurus/router';
import { Amplify } from 'aws-amplify';
import { amplifyConfig } from '@site/src/config/amplify-config';

// Initialize Amplify once
if (typeof window !== 'undefined') {
    Amplify.configure(amplifyConfig);
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
        const handleOAuthCallback = async () => {
            const params = new URLSearchParams(window.location.search);
            if (params.has('code') || params.has('state')) {
                console.log('OAuth callback detected, waiting for Amplify to process...');
                // Amplify v6 automatically handles the OAuth callback
                // Poll for auth state to detect when tokens are ready
                let attempts = 0;
                const checkInterval = setInterval(async () => {
                    attempts++;
                    const authenticated = await isLoggedIn();
                    console.log(`Auth check attempt ${attempts}: ${authenticated}`);

                    if (authenticated) {
                        console.log('✅ User authenticated! Notifying listeners...');
                        clearInterval(checkInterval);
                        await notifyAuthChange();
                        // Clean up URL params
                        window.history.replaceState({}, document.title, location.pathname);
                    } else if (attempts > 20) {
                        // Stop after 10 seconds
                        console.error('❌ Auth timeout - tokens not received');
                        clearInterval(checkInterval);
                    }
                }, 500);
            }
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
    const isArchitecture = path === '/architecture' || path.startsWith('/architecture/');
    // Static pages = any non-portal, non-architecture routes (landing, docs, pricing, etc.)
    const isStaticPage = !isPortalRoute && !isArchitecture;
    // Footer should display on static pages regardless of auth state per clarified requirement.
    const showFooter = isStaticPage;
    return (
        <ErrorBoundary>
            <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
                <div style={{ flex: '1 0 auto' }}>{children}</div>
                {showFooter && <SiteFooter />}
            </div>
        </ErrorBoundary>
    );
}
