import React from 'react';
import OriginalDefaultNavbarItem from '@theme-original/NavbarItem/DefaultNavbarItem';
import {
    isLoggedIn,
    onAuthChange,
    loginWithGoogle,
    loginWithAmazon,
    loginWithMicrosoft,
    loginWithGitHub,
    getAvailableProviders,
    signOut
} from '@site/src/utils/auth-cognito';

export default function DefaultNavbarItemWrapper(props: any) {
    const [loggedIn, setLI] = React.useState(false);
    const [showDropdown, setShowDropdown] = React.useState(false);

    React.useEffect(() => {
        (async () => {
            const authenticated = await isLoggedIn();
            setLI(authenticated);
        })();
        const unsubscribe = onAuthChange((isAuth) => setLI(isAuth));
        return () => { unsubscribe(); };
    }, []);

    // Close dropdown when clicking outside
    React.useEffect(() => {
        const handleClickOutside = () => setShowDropdown(false);
        if (showDropdown) {
            document.addEventListener('click', handleClickOutside);
            return () => document.removeEventListener('click', handleClickOutside);
        }
    }, [showDropdown]);

    const isLoginLink = (
        (props?.to && (props.to === '/dashboard' || props.to === '/dashboard')) ||
        (props?.href && (props.href === '/dashboard' || props.href === '/dashboard'))
    );

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
            await handler();
        }
    };

    const handleLogout = async () => {
        await signOut();
        window.location.href = '/';
    };

    if (isLoginLink && !loggedIn) {
        // Show login dropdown with multiple providers
        return (
            <div
                style={{ position: 'relative', display: 'inline-block' }}
                onClick={(e) => e.stopPropagation()}
            >
                <a
                    href="#"
                    className="navbar__item navbar__link"
                    onClick={(e) => {
                        e.preventDefault();
                        setShowDropdown(!showDropdown);
                    }}
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

    if (isLoginLink && loggedIn) {
        // Show logout button
        return (
            <a
                href="#"
                className="navbar__item navbar__link"
                onClick={(e) => {
                    e.preventDefault();
                    handleLogout();
                }}
            >
                Logout
            </a>
        );
    }

    // For non-login links, use original behavior
    return <OriginalDefaultNavbarItem {...props} />;
}
