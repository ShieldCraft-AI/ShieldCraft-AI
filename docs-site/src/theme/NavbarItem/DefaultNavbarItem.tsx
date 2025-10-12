import React from 'react';
import OriginalDefaultNavbarItem from '@theme-original/NavbarItem/DefaultNavbarItem';
import {
    isLoggedIn,
    onAuthChange,
    signOut
} from '@site/src/utils/auth-cognito';
import MultiProviderLogin from '@site/src/components/MultiProviderLogin';

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

    const extractPathname = (val: any): string => {
        if (!val) return '';
        try {
            const u = new URL(String(val), window.location.origin);
            return u.pathname || '';
        } catch {
            return String(val || '');
        }
    };

    const pathname = extractPathname(props?.to || props?.href);
    const isLoginLink = pathname === '/dashboard' || pathname === '/dashboard/' || pathname.startsWith('/dashboard');

    // Provider login is handled by the centralized MultiProviderLogin component.

    const handleLogout = async () => {
        await signOut();
        window.location.href = '/';
    };

    if (isLoginLink && !loggedIn) {
        // Show a professional menu using the centralized component
        return (
            <div style={{ position: 'relative', display: 'inline-block' }} onClick={(e) => e.stopPropagation()}>
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
                    <div style={{ position: 'absolute', top: '100%', right: 0, zIndex: 1000, marginTop: '8px' }}>
                        <div className="navbar-provider-container" style={{ display: 'block' }}>
                            <MultiProviderLogin showText={true} vertical={true} className="navbar-provider-menu" />
                        </div>
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
