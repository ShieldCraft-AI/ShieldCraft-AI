import React from 'react';
import { useLocation } from '@docusaurus/router';
import OriginalLayout from '@theme-original/Layout';
import AppSidebar from '@site/src/components/AppSidebar/AppSidebar';
import './layout.css';
import { isLoggedIn, onAuthChange } from '@site/src/utils/auth-cognito';
import UniversalHeader from '@site/src/components/UniversalHeader';

export default function Layout(props: React.ComponentProps<typeof OriginalLayout>) {
    const [loggedIn, setLoggedIn] = React.useState<boolean>(false);
    const location = useLocation();
    React.useEffect(() => {
        (async () => {
            const authenticated = await isLoggedIn();
            setLoggedIn(authenticated);
        })();
        const unsubscribe = onAuthChange((isAuth) => {
            setLoggedIn(isAuth);
        });
        return () => { unsubscribe(); };
    }, []);
    const isPortalRoute = React.useMemo(() => {
        const p = location.pathname;
        return (
            p.startsWith('/alerts') ||
            p.startsWith('/system-status') ||
            p.startsWith('/recent-activity') ||
            p.startsWith('/threat-feed') ||
            p.startsWith('/dashboard') ||
            p.startsWith('/monitoring') ||
            p.startsWith('/portal')
        );
    }, [location.pathname]);

    const isLandingPage = React.useMemo(() => {
        return location.pathname === '/';
    }, [location.pathname]);

    const isPricingPage = React.useMemo(() => {
        const p = location.pathname;
        return p === '/pricing' || p.startsWith('/pricing/');
    }, [location.pathname]);

    const isDocsRoute = React.useMemo(() => {
        // Anything that is not a portal route, not the landing page, and not the pricing experience is treated as documentation.
        // This removes the need for brittle prefix whitelists and prevents layout jumping when new docs are added.
        if (isPortalRoute) return false;
        if (isLandingPage) return false;
        if (isPricingPage) return false;
        return true;
    }, [isPortalRoute, isLandingPage, isPricingPage]);

    const showAppSidebar = !isPortalRoute && !isLandingPage && !isPricingPage && !isDocsRoute;
    const contentStyle = showAppSidebar ? { marginLeft: 'max(15vw, 220px)' } : undefined;

    return (
        <OriginalLayout {...props}>
            <UniversalHeader />
            <div className={`sc-layout ${isDocsRoute ? 'docs-route' : ''} ${isPricingPage ? 'pricing-route' : ''}`}>
                {showAppSidebar && <AppSidebar />}
                <div className="sc-content" style={contentStyle} key={location.pathname}>{props.children}</div>
            </div>
        </OriginalLayout >
    );
}
