import React from 'react';
import { useHistory } from '@docusaurus/router';
import {
    isLoggedIn,
    onAuthChange,
    signOut,
    loginWithGoogle,
    loginWithAmazon,
    loginWithMicrosoft,
    loginWithGitHub,
    getAvailableProviders
} from '@site/src/utils/auth-cognito';
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

    const providerHandlers = {
        Google: loginWithGoogle,
        LoginWithAmazon: loginWithAmazon,
        Microsoft: loginWithMicrosoft,
        GitHub: loginWithGitHub,
    };

    const handleProviderLogin = async (providerId: string) => {
        const handler = providerHandlers[providerId];
        if (handler) {
            setShowDropdown(false);
            preloadPlotly();
            await handler();
        }
    };

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

    // Show multi-provider dropdown for login
    return (
        <div
            style={{ position: 'relative', display: 'inline-block' }}
            onClick={(e) => e.stopPropagation()}
        >
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
                <div
                    style={{
                        position: 'absolute',
                        top: '100%',
                        right: 0,
                        backgroundColor: 'var(--ifm-color-content-inverse)',
                        border: '1px solid var(--ifm-color-emphasis-300)',
                        borderRadius: '6px',
                        boxShadow: 'var(--ifm-global-shadow-md)',
                        minWidth: '180px',
                        zIndex: 1000,
                        marginTop: '4px',
                    }}
                >
                    {getAvailableProviders().map((provider) => (
                        <button
                            key={provider.id}
                            onClick={() => handleProviderLogin(provider.id)}
                            style={{
                                width: '100%',
                                padding: '12px 16px',
                                border: 'none',
                                background: 'none',
                                textAlign: 'left',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '10px',
                                color: 'var(--ifm-color-content)',
                                fontSize: '14px',
                                transition: 'background-color 0.2s ease',
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = 'var(--ifm-color-emphasis-100)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = 'transparent';
                            }}
                        >
                            <span style={{ fontSize: '16px' }}>{provider.icon}</span>
                            <span>Continue with {provider.name}</span>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
