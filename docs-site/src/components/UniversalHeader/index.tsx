import type { JSX } from 'react';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Link from '@docusaurus/Link';
import { useLocation, useHistory } from '@docusaurus/router';
import { useColorMode } from '@docusaurus/theme-common';
import { isLoggedIn, onAuthChange, signOut } from '../../utils/auth-cognito';
import MultiProviderLogin from '../MultiProviderLogin';
import '../../css/header-login.css';
import { preloadPlotly } from '../../utils/plotlyPreload';

interface UniversalHeaderProps {
    height?: string;
}

const MOBILE_BREAKPOINT = '(max-width: 960px)';

const navLinksForState = (authenticated: boolean) => authenticated
    ? [
        { to: '/dashboard', label: 'Dashboard' },
        { to: '/monitoring', label: 'Monitor' }
    ]
    : [
        { to: '/architecture', label: 'Pricing' },
        { to: '/infrastructure', label: 'Infrastructure' },
        { to: '/plugins', label: 'Plugins' },
        { to: '/intro', label: 'Documentation' }
    ];

export default function UniversalHeader({ height = '60px' }: UniversalHeaderProps): JSX.Element {
    const location = useLocation();
    const history = useHistory();
    const { colorMode, setColorMode } = useColorMode();

    const headerRef = useRef<HTMLElement | null>(null);
    const dropdownRef = useRef<HTMLDivElement | null>(null);
    const [hydrated, setHydrated] = useState(false);
    const [loggedIn, setLoggedIn] = useState(false);
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [mobileNavOpen, setMobileNavOpen] = useState(false);
    const [isMobile, setIsMobile] = useState(() => {
        if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false;
        try {
            return window.matchMedia(MOBILE_BREAKPOINT).matches;
        } catch {
            return false;
        }
    });
    const [userFirstName, setUserFirstName] = useState<string | null>(null);

    console.debug('[UniversalHeader] Component rendered');

    useEffect(() => {
        console.debug('[UniversalHeader] useEffect triggered');

        let cancelled = false;

        const sync = async () => {
            try {
                const authenticated = await isLoggedIn();
                console.debug('[UniversalHeader] isLoggedIn:', authenticated);

                if (!cancelled) setLoggedIn(Boolean(authenticated));

                if (authenticated) {
                    console.debug('[UniversalHeader] localStorage keys:', Object.keys(localStorage));

                    const lastAuthUserKey = Object.keys(localStorage).find(key => key.endsWith('LastAuthUser'));
                    console.debug('[UniversalHeader] LastAuthUser key:', lastAuthUserKey);

                    if (lastAuthUserKey) {
                        const userPrefix = lastAuthUserKey.replace('.LastAuthUser', '');
                        const idTokenKey = `${userPrefix}.idToken`;
                        const idToken = localStorage.getItem(idTokenKey);

                        console.debug('[UniversalHeader] Retrieved idToken:', idToken);

                        if (idToken) {
                            try {
                                const payload = JSON.parse(atob(idToken.split('.')[1]));
                                console.debug('[UniversalHeader] Decoded idToken payload:', payload);

                                if (payload && payload.name && !cancelled) {
                                    console.debug('[UniversalHeader] Extracted name:', payload.name);
                                    setUserFirstName(payload.name.split(' ')[0]); // Use the first name only
                                } else {
                                    console.warn('[UniversalHeader] Name field not found in idToken payload');
                                }
                            } catch (error) {
                                console.error('[UniversalHeader] Failed to decode idToken:', error);
                            }
                        } else {
                            console.warn('[UniversalHeader] idToken not found in localStorage');
                        }
                    } else {
                        console.warn('[UniversalHeader] LastAuthUser key not found in localStorage');
                    }
                }
            } catch (error) {
                console.error('[UniversalHeader] Error in sync function:', error);
                if (!cancelled) setLoggedIn(false);
            }
        };

        void sync();
        const unsubscribe = onAuthChange((authenticated) => {
            console.debug('[UniversalHeader] onAuthChange triggered:', authenticated);
            if (!cancelled) setLoggedIn(Boolean(authenticated));
        });

        preloadPlotly();

        return () => {
            cancelled = true;
            unsubscribe();
        };
    }, []);

    useEffect(() => {
        if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return;
        const mq = window.matchMedia(MOBILE_BREAKPOINT);

        const applyMatch = (matches: boolean) => setIsMobile(matches);
        const handler = (event: MediaQueryListEvent) => applyMatch(event.matches);

        applyMatch(mq.matches);

        if (typeof mq.addEventListener === 'function') {
            mq.addEventListener('change', handler);
        } else if (typeof mq.addListener === 'function') {
            mq.addListener(handler);
        }

        return () => {
            if (typeof mq.removeEventListener === 'function') {
                mq.removeEventListener('change', handler);
            } else if (typeof mq.removeListener === 'function') {
                mq.removeListener(handler);
            }
        };
    }, []);

    useEffect(() => {
        setDropdownOpen(false);
        setMobileNavOpen(false);
    }, [location.pathname, location.search]);

    useEffect(() => {
        // Wait for hydration before relying on color mode to avoid mismatches.
        setHydrated(true);
    }, []);

    useEffect(() => {
        if (!dropdownOpen) return;

        const handleClick = (event: MouseEvent) => {
            const target = event.target as Node;
            if (!dropdownRef.current?.contains(target)) setDropdownOpen(false);
        };

        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, [dropdownOpen]);

    useEffect(() => {
        if (!isMobile) setMobileNavOpen(false);
    }, [isMobile]);

    useEffect(() => {
        if (typeof document === 'undefined') return;
        const node = headerRef.current;
        if (!node) return;

        const applyHeight = (value: number) => {
            const rounded = Math.ceil(value);
            document.documentElement.style.setProperty('--ifm-navbar-height', `${rounded}px`);
        };

        applyHeight(node.getBoundingClientRect().height);

        if (typeof ResizeObserver === 'undefined') {
            const handleResize = () => applyHeight(node.getBoundingClientRect().height);
            window.addEventListener('resize', handleResize);
            return () => window.removeEventListener('resize', handleResize);
        }

        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                if (entry.target === node) {
                    applyHeight(entry.contentRect.height);
                }
            }
        });

        observer.observe(node);
        return () => observer.disconnect();
    }, [headerRef, loggedIn, isMobile, mobileNavOpen, dropdownOpen]);

    const isDarkMode = hydrated && colorMode === 'dark';

    const navBaseStyle = useMemo<React.CSSProperties>(() => ({
        textDecoration: 'none',
        color: isDarkMode ? '#e5e7eb' : '#0f172a',
        padding: '0.35rem 0.7rem',
        borderRadius: 10,
        transition: 'background .15s ease, box-shadow .15s ease, transform .12s ease, color .2s ease',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
    }), [isDarkMode]);

    const handleLoginToggle = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        setDropdownOpen((open) => !open);
    }, []);

    const handleLogout = useCallback(async () => {
        await signOut();
        setDropdownOpen(false);
        setTimeout(() => history.push('/'), 0);
    }, [history]);

    const handleColorModeToggle = useCallback(() => {
        setColorMode(colorMode === 'dark' ? 'light' : 'dark');
    }, [colorMode, setColorMode]);

    // Prevent SSR/client hydration mismatch by deferring auth-driven UI until hydrated
    const effectiveAuth = hydrated ? loggedIn : false;
    const navLinks = useMemo(() => navLinksForState(effectiveAuth), [effectiveAuth]);

    const headerRowStyle = isMobile
        ? {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            width: '100%',
            gap: '0.75rem'
        }
        : {
            display: 'grid',
            gridTemplateColumns: 'auto 1fr auto',
            alignItems: 'center',
            width: '100%',
            columnGap: '2rem'
        } as const;

    return (
        <header
            ref={headerRef}
            style={{
                background: isDarkMode
                    ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
                    : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                padding: isMobile ? '0.6rem 1rem' : '0.7rem 3rem',
                borderBottom: isDarkMode
                    ? '1px solid rgba(165, 180, 252, 0.3)'
                    : '1px solid rgba(100, 116, 139, 0.3)',
                position: 'sticky',
                top: 0,
                zIndex: 5000,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'stretch',
                gap: isMobile ? '0.5rem' : 0,
                ...(height ? { minHeight: height } : {}),
                boxSizing: 'border-box',
                maxWidth: '100vw',
                transition: 'background 0.3s ease, border-color 0.3s ease'
            }}
        >
            <div style={headerRowStyle}>
                <Link
                    to="/"
                    style={{
                        textDecoration: 'none',
                        color: isDarkMode ? '#e5e7eb' : '#0f172a',
                        fontSize: isMobile ? '1.1rem' : '1.3rem',
                        fontWeight: 700,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.55rem',
                        transition: 'color 0.3s ease'
                    }}
                >
                    <img
                        src="/img/logo.png"
                        alt="ShieldCraft AI"
                        style={{
                            height: isMobile ? 24 : 28,
                            width: 'auto',
                            display: 'block',
                            filter: isDarkMode
                                ? 'drop-shadow(0 1px 0 rgba(255,255,255,0.06))'
                                : 'drop-shadow(0 1px 0 rgba(0,0,0,0.06))',
                            opacity: 0.96,
                            borderRadius: 6
                        }}
                    />
                    <span>ShieldCraft AI</span>
                </Link>

                {!isMobile && (
                    <nav
                        style={{
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            gap: '2.5rem'
                        }}
                    >
                        {navLinks.map(({ to, label }) => (
                            <Link
                                key={to}
                                to={to}
                                className="sc-nav-pill"
                                style={{ ...navBaseStyle, padding: '0.35rem 0.9rem' }}
                            >
                                {label}
                            </Link>
                        ))}
                    </nav>
                )}

                <div
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'flex-end',
                        gap: isMobile ? '0.6rem' : '1.5rem'
                    }}
                >
                    {isMobile && (
                        <button
                            onClick={() => setMobileNavOpen((open) => !open)}
                            aria-label={mobileNavOpen ? 'Close navigation menu' : 'Open navigation menu'}
                            aria-expanded={mobileNavOpen}
                            style={{
                                border: '1px solid transparent',
                                background: 'transparent',
                                color: isDarkMode ? '#e5e7eb' : '#0f172a',
                                width: 40,
                                height: 40,
                                borderRadius: 10,
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'background .2s ease, border-color .2s ease'
                            }}
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                {mobileNavOpen ? (
                                    <path d="M18 6L6 18M6 6l12 12" />
                                ) : (
                                    <>
                                        <line x1="3" y1="6" x2="21" y2="6" />
                                        <line x1="3" y1="12" x2="21" y2="12" />
                                        <line x1="3" y1="18" x2="21" y2="18" />
                                    </>
                                )}
                            </svg>
                        </button>
                    )}

                    <div style={{ display: 'flex', gap: isMobile ? '0.75rem' : '1.5rem', alignItems: 'center' }}>
                        <div ref={dropdownRef} className="user-dropdown" style={{ position: 'relative' }}>
                            <button
                                onClick={handleLoginToggle}
                                onMouseEnter={preloadPlotly}
                                className="sc-nav-pill"
                                style={{
                                    ...navBaseStyle,
                                    fontSize: '1rem',
                                    fontWeight: 500,
                                    background: 'transparent',
                                    cursor: 'pointer',
                                    minWidth: isMobile ? 'auto' : 120,
                                }}
                                aria-label={effectiveAuth ? 'User menu' : 'Login'}
                            >
                                {effectiveAuth ? (
                                    <>
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                                            <circle cx="12" cy="7" r="4" />
                                        </svg>
                                        {userFirstName && <span style={{ marginLeft: '0.5rem' }}>{userFirstName}</span>}
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: -2 }}>
                                            <polyline points={dropdownOpen ? '18 15 12 9 6 15' : '6 9 12 15 18 9'} />
                                        </svg>
                                    </>
                                ) : (
                                    <>
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                                            <polyline points="10 17 15 12 10 7" />
                                            <line x1="15" y1="12" x2="3" y2="12" />
                                        </svg>
                                        <span>Login</span>
                                    </>
                                )}
                            </button>

                            {dropdownOpen && (
                                <div
                                    style={{
                                        position: 'absolute',
                                        top: '100%',
                                        right: 0,
                                        marginTop: '0.5rem',
                                        background: isDarkMode
                                            ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
                                            : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                                        border: isDarkMode
                                            ? '1px solid rgba(165, 180, 252, 0.3)'
                                            : '1px solid rgba(100, 116, 139, 0.3)',
                                        borderRadius: 8,
                                        boxShadow: isDarkMode
                                            ? '0 8px 32px rgba(0, 0, 0, 0.4)'
                                            : '0 8px 32px rgba(0, 0, 0, 0.15)',
                                        minWidth: 220,
                                        overflow: 'hidden',
                                        zIndex: 1001
                                    }}
                                >
                                    {effectiveAuth ? (
                                        <div>
                                            {[
                                                { to: '/dashboard', label: 'Security Console' },
                                                { to: '/monitoring', label: 'Mission Control' },
                                                { to: '/alerts', label: 'Threat Alerts' },
                                                { to: '/threat-feed', label: 'Intelligence Feed' },
                                                { to: '/system-status', label: 'Platform Health' },
                                                { to: '/recent-activity', label: 'Activity Monitor' }
                                            ].map(({ to, label }) => (
                                                <Link
                                                    key={to}
                                                    to={to}
                                                    style={{
                                                        display: 'block',
                                                        padding: '0.75rem 1rem',
                                                        color: isDarkMode ? '#ffffff' : '#1e293b',
                                                        textDecoration: 'none',
                                                        borderBottom: isDarkMode
                                                            ? '1px solid rgba(165, 180, 252, 0.12)'
                                                            : '1px solid rgba(100, 116, 139, 0.12)'
                                                    }}
                                                    onClick={() => setDropdownOpen(false)}
                                                >
                                                    {label}
                                                </Link>
                                            ))}
                                            <button
                                                onClick={handleLogout}
                                                style={{
                                                    display: 'block',
                                                    width: '100%',
                                                    padding: '0.75rem 1rem',
                                                    color: '#ef4444',
                                                    background: 'transparent',
                                                    border: 'none',
                                                    textAlign: 'left',
                                                    cursor: 'pointer',
                                                    fontSize: '1rem'
                                                }}
                                            >
                                                Logout
                                            </button>
                                        </div>
                                    ) : (
                                        <div style={{ padding: '0.75rem' }}>
                                            <MultiProviderLogin vertical={true} className="provider-dropdown" onLogin={() => setDropdownOpen(false)} />
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        <button
                            onClick={handleColorModeToggle}
                            style={{
                                color: isDarkMode ? '#ffffff' : '#1e293b',
                                background: 'transparent',
                                border: 'none',
                                padding: '0.5rem',
                                borderRadius: 8,
                                cursor: 'pointer',
                                transition: 'all 0.2s',
                                fontSize: '1.1rem',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                            title={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
                        >
                            {isDarkMode ? '☀️' : '🌙'}
                        </button>
                    </div>
                </div>
            </div>

            {isMobile && mobileNavOpen && (
                <nav
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.6rem',
                        alignItems: 'stretch',
                        justifyContent: 'flex-start',
                        width: '100%',
                        paddingTop: '0.25rem'
                    }}
                >
                    {navLinks.map(({ to, label }) => (
                        <Link
                            key={to}
                            to={to}
                            className="sc-nav-pill"
                            style={{
                                ...navBaseStyle,
                                width: '100%',
                                justifyContent: 'space-between'
                            }}
                            onClick={() => setMobileNavOpen(false)}
                        >
                            {label}
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="9 6 15 12 9 18" />
                            </svg>
                        </Link>
                    ))}
                </nav>
            )}
        </header>
    );
}
