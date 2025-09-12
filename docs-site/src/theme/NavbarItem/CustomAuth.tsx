import React from 'react';
import Link from '@docusaurus/Link';

export default function CustomAuth() {
    const [authed, setAuthed] = React.useState(false);
    React.useEffect(() => {
        try { setAuthed(typeof window !== 'undefined' && window.localStorage.getItem('sc-auth') === '1'); } catch { }
    }, []);

    const onLogout = React.useCallback(() => {
        try { window.localStorage.removeItem('sc-auth'); } catch { }
        if (typeof window !== 'undefined') window.location.href = '/login';
    }, []);

    return authed ? (
        <button className="button button--secondary button--sm" onClick={onLogout}>Logout</button>
    ) : (
        <Link className="button button--primary button--sm" to="/login">Login</Link>
    );
}
