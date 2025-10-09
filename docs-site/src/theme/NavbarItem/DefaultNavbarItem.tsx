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

// Wrap the default navbar item to customize the Login/Logout label and behavior.
export default function DefaultNavbarItemWrapper(props: any) {
    const [loggedIn, setLI] = React.useState(false);
    const [showDropdown, setShowDropdown] = React.useState(false);

    React.useEffect(() => {
        (async () => {
            const authenticated = await isLoggedIn();
            setLI(authenticated);
        })();
        const off = onAuthChange((v) => setLI(v));
        return () => { off && off(); };
    }, []);

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
            <div style={{ position: 'relative', display: 'inline-block' }}>
                <button
                    onClick={() => setShowDropdown(!showDropdown)}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: 'inherit',
                        fontSize: 'inherit',
                        cursor: 'pointer',
                        padding: '8px',
                    }}
                >
                    Login ▼
                </button>
                {showDropdown && (
                    <div
                        style={{
                            position: 'absolute',
                            top: '100%',
                            right: 0,
                            backgroundColor: 'white',
                            border: '1px solid #ccc',
                            borderRadius: '4px',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                            minWidth: '160px',
                            zIndex: 1000,
                        }}
                    >
                        {getAvailableProviders().map((provider) => (
                            <button
                                key={provider.id}
                                onClick={() => handleProviderLogin(provider.id)}
                                style={{
                                    width: '100%',
                                    padding: '8px 12px',
                                    border: 'none',
                                    background: 'none',
                                    textAlign: 'left',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                }}
                                onMouseOver={(e) => {
                                    e.currentTarget.style.backgroundColor = '#f5f5f5';
                                }}
                                onMouseOut={(e) => {
                                    e.currentTarget.style.backgroundColor = 'transparent';
                                }}
                            >
                                <span>{provider.icon}</span>
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
            <button
                onClick={handleLogout}
                style={{
                    background: 'none',
                    border: 'none',
                    color: 'inherit',
                    fontSize: 'inherit',
                    cursor: 'pointer',
                    padding: '8px',
                }}
            >
                Logout
            </button>
        );
    }

    // For non-login links, use original behavior
    return <OriginalDefaultNavbarItem {...props} />;
}
