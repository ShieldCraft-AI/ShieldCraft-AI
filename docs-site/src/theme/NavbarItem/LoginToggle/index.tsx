import React from 'react';
import { useHistory } from '@docusaurus/router';
import {
    isLoggedIn,
    onAuthChange,
    signOut,
    getAvailableProviders
} from '@site/src/utils/auth-cognito';
import MultiProviderLogin from '@site/src/components/MultiProviderLogin';
import { preloadPlotly } from '@site/src/utils/plotlyPreload';

export default function LoginToggleNavbarItem() {
    const history = useHistory();
    const [loggedIn, setLI] = React.useState(false);
    const [showDropdown, setShowDropdown] = React.useState(false);

    React.useEffect(() => {
        // Subscribe to auth changes - will immediately fire with current state
        const unsubscribe = onAuthChange((isAuth) => {
            setLI(isAuth);
        });

        // Warm the Plotly chunk so Dashboard charts render instantly
        preloadPlotly();

        return () => {
            unsubscribe();
        };
    }, []);

    // Close dropdown when clicking outside
    React.useEffect(() => {
        const handleClickOutside = () => setShowDropdown(false);
        if (showDropdown) {
            document.addEventListener('click', handleClickOutside);
            return () => document.removeEventListener('click', handleClickOutside);
        }
    }, [showDropdown]);

    // Provider login handled by MultiProviderLogin component

    const handleLogout = async (e: React.MouseEvent) => {
        e.preventDefault();
        await signOut();
        setLI(false);
        // Delay navigation a tick so subscribers unmount charts before route change
        setTimeout(() => history.push('/'), 0);
    };

    const onMouseEnter = () => { preloadPlotly(); };

    if (loggedIn) {
        return (
            <a
                href="#"
                className="navbar__item navbar__link"
                onClick={handleLogout}
                aria-label="Logout"
                onMouseEnter={onMouseEnter}
            >
                Logout
            </a>
        );
    }

    // Show multi-provider professional menu for login
    return (
        <div style={{ position: 'relative', display: 'inline-block' }} onClick={(e) => e.stopPropagation()}>
            <a
                href="/dashboard"
                className="navbar__item navbar__link"
                onClick={(e) => {
                    e.preventDefault();
                    setShowDropdown(!showDropdown);
                }}
                aria-label="Login"
                onMouseEnter={onMouseEnter}
            >
                Login ▼
            </a>
            {showDropdown && (
                <div style={{ position: 'absolute', top: '100%', right: 0, zIndex: 1000, marginTop: '8px' }}>
                    <div className="navbar-provider-container" style={{ display: 'block' }}>
                        <MultiProviderLogin showText={true} vertical={true} className="navbar-provider-menu" />
                    </div>
                </div>
            )}
        </div>
    );
}
