import React from 'react';
import Link from '@docusaurus/Link';
import type { Props } from '@theme/NavbarItem/DefaultNavbarItem';

export default function CustomAuthNavbarItem(_props: Props) {
    const [authed, setAuthed] = React.useState<boolean>(() => {
        if (typeof window === 'undefined') return false;
        try { return window.localStorage.getItem('sc-auth') === '1'; } catch { return false; }
    });

    React.useEffect(() => {
        const onStorage = (e: StorageEvent) => {
            if (e.key === 'sc-auth') setAuthed(e.newValue === '1');
        };
        window.addEventListener('storage', onStorage);
        return () => window.removeEventListener('storage', onStorage);
    }, []);

    const onLogout = React.useCallback(() => {
        try { window.localStorage.removeItem('sc-auth'); } catch { }
        if (typeof window !== 'undefined') window.location.href = '/login';
    }, []);

    const onLogin = React.useCallback((e: React.MouseEvent) => {
        e.preventDefault();
        try { window.localStorage.setItem('sc-auth', '1'); } catch { }
        setAuthed(true); // hide immediately
        if (typeof window !== 'undefined') window.location.href = '/portal';
    }, []);

    return authed ? (
        <button className="button button--secondary button--sm" onClick={onLogout} aria-label="Logout">Logout</button>
    ) : (
        <Link className="button button--primary button--sm" to="/login" onClick={onLogin} aria-label="Login">Login</Link>
    );
}
