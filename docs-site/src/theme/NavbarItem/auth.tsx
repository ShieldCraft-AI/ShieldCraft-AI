import React from 'react';
import type { Props } from '@theme/NavbarItem/DefaultNavbarItem';
import { loginWithHostedUI, signOut, isLoggedIn, getCurrentUser } from '@site/src/utils/auth-cognito';
import logger from '@site/src/utils/logger';

export default function AuthNavbarItem(_props: Props) {
    const [user, setUser] = React.useState<any>(null);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        checkAuth();

        // Listen for auth state changes via custom event
        const handleAuthChange = (_event: any) => {
            checkAuth();
        };
        window.addEventListener('sc-auth-changed', handleAuthChange);

        return () => {
            window.removeEventListener('sc-auth-changed', handleAuthChange);
        };
    }, []);

    async function checkAuth() {
        try {
            const authenticated = await isLoggedIn();
            if (authenticated) {
                const currentUser = await getCurrentUser();
                setUser(currentUser);
            } else {
                setUser(null);
            }
        } catch (error) {
            logger.error('Auth check failed:', error);
            setUser(null);
        } finally {
            setLoading(false);
        }
    }

    const handleLogin = async () => {
        try {
            await loginWithHostedUI();
        } catch (error) {
            logger.error('Login failed:', error);
        }
    };

    const handleLogout = async () => {
        try {
            await signOut();
            setUser(null);
            window.location.href = '/';
        } catch (error) {
            logger.error('Logout failed:', error);
        }
    };

    if (loading) return null;

    return user ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--ifm-navbar-link-color)' }}>
                {user.email}
            </span>
            <button className="button button--secondary button--sm" onClick={handleLogout}>
                Logout
            </button>
        </div>
    ) : (
        <button className="button button--primary button--sm" onClick={handleLogin}>
            Login
        </button>
    );
}
