import type { JSX } from 'react';
import React, { Component, ErrorInfo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Link from '@docusaurus/Link';
import { useLocation, useHistory } from '@docusaurus/router';
import { useColorMode } from '@docusaurus/theme-common';
import { isLoggedIn, onAuthChange, signOut, getCurrentUser, notifyAuthChange, clearAuthStorage } from '../../utils/auth-cognito';
import MultiProviderLogin from '../MultiProviderLogin';
import '../../css/header-login.css';
import { preloadPlotly } from '../../utils/plotlyPreload';

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

interface UniversalHeaderProps {
    height?: string;
}

// Add an error boundary wrapper to catch hydration errors
class ErrorBoundary extends Component<{ children: React.ReactNode }, { hasError: boolean }> {
    constructor(props: { children: React.ReactNode }) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(): { hasError: boolean } {
        return { hasError: true };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        console.error('[ErrorBoundary] Caught an error:', error, errorInfo);
    }

    render(): React.ReactNode {
        if (this.state.hasError) {
            return <div style={{ color: 'red' }}>Something went wrong.</div>;
        }
        return this.props.children;
    }
}

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
    const [deployInfo, setDeployInfo] = useState({ commit: 'unknown', timestamp: 'unknown' });

    // Helper to derive first name from stored idToken in localStorage.
    const deriveFirstNameFromStorage = async (): Promise<string | null> => {
        if (typeof window === 'undefined') return null;
        try {
            const lastAuthUserKey = Object.keys(localStorage).find((key) => key.endsWith('LastAuthUser'));
            if (!lastAuthUserKey) {
                setUserFirstName(null);
                setLoggedIn(false);
                return null;
            }
            const username = localStorage.getItem(lastAuthUserKey) || '';
            if (!username) {
                setUserFirstName(null);
                setLoggedIn(false);
                return null;
            }
            const userPrefix = lastAuthUserKey.replace(/\.LastAuthUser$/, `.${username}`);
            const idTokenKey = `${userPrefix}.idToken`;
            const idToken = localStorage.getItem(idTokenKey);
            if (!idToken) {
                setUserFirstName(null);
                return null;
            }
            const payload = JSON.parse(atob(idToken.split('.')[1] || ''));
            const first = payload?.name ? String(payload.name).split(' ')[0]?.trim() : (payload?.email ? String(payload.email).split('@')[0]?.trim() : null);
            setUserFirstName(first || null);
            setLoggedIn(true);
            return first || null;
        } catch (error) {
            console.error('[UniversalHeader] deriveFirstNameFromStorage failed', error);
            setUserFirstName(null);
            return null;
        }
    };

    useEffect(() => {
        let cancelled = false;

        const extractFirstName = async (): Promise<string | null> => {
            try {
                const profile = await getCurrentUser();
                if (profile && profile.name) {
                    const first = profile.name.split(' ')[0]?.trim();
                    if (!cancelled) setUserFirstName(first || null);
                    return first || null;
                }
                if (profile && profile.email) {
                    const inferred = profile.email.split('@')[0]?.trim();
                    if (!cancelled) setUserFirstName(inferred || null);
                    return inferred || null;
                }
            } catch (err) {
                console.warn('[UniversalHeader] getCurrentUser failed, falling back to localStorage', err);
            }

            try {
                const lastAuthUserKey = Object.keys(localStorage).find((key) => key.endsWith('LastAuthUser'));
                if (!lastAuthUserKey) {
                    if (!cancelled) setUserFirstName(null);
                    return null;
                }
                const username = localStorage.getItem(lastAuthUserKey) || '';
                if (!username) {
                    if (!cancelled) setUserFirstName(null);
                    return null;
                }
                const userPrefix = lastAuthUserKey.replace(/\.LastAuthUser$/, `.${username}`);
                const idTokenKey = `${userPrefix}.idToken`;
                const idToken = localStorage.getItem(idTokenKey);
                if (!idToken) {
                    if (!cancelled) setUserFirstName(null);
                    return null;
                }
                const payload = JSON.parse(atob(idToken.split('.')[1] || ''));
                const first = payload?.name ? String(payload.name).split(' ')[0]?.trim() : null;
                if (!cancelled) setUserFirstName(first || null);
                return first || null;
            } catch (error) {
                console.error('[UniversalHeader] Failed to derive user name:', error);
                if (!cancelled) setUserFirstName(null);
            }
            return null;
        };

        const sync = async () => {
            try {
                const authenticated = await isLoggedIn();
                if (!cancelled) {
                    setLoggedIn(Boolean(authenticated));
                }
                if (authenticated) {
                    await extractFirstName();
                } else {
                    // Fallback: if stored tokens exist in localStorage, assume
                    // the user is effectively signed in and derive the name
                    // from the stored idToken so client-side navigation doesn't
                    // flip the header to anonymous state.
                    try {
                        const lastAuthUserKey = Object.keys(localStorage).find((key) => key.endsWith('LastAuthUser'));
                        if (lastAuthUserKey) {
                            if (!cancelled) setLoggedIn(true);
                            await extractFirstName();
                        } else if (!cancelled) {
                            setUserFirstName(null);
                        }
                    } catch (err) {
                        if (!cancelled) setUserFirstName(null);
                    }
                }
            } catch {
                if (!cancelled) {
                    setLoggedIn(false);
                    setUserFirstName(null);
                }
            }
        };

        void sync();
        const unsubscribe = onAuthChange((authenticated) => {
            if (cancelled) return;
            const nextAuth = Boolean(authenticated);
            setLoggedIn(nextAuth);
            if (nextAuth) {
                void extractFirstName();
            } else {
                setUserFirstName(null);
            }
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

        // On client-side navigation, synchronously re-check stored auth snapshot
        // to avoid transient flips when in-memory SDK state is lost. Do an
        // immediate best-effort derive from localStorage, proactively set
        // loggedIn if stored tokens exist, and schedule a short fallback
        // re-check in case storage is updated slightly later.
        let t: ReturnType<typeof setTimeout> | null = null;
        try {
            // immediate best-effort sync from localStorage
            void deriveFirstNameFromStorage().catch(() => undefined);

            // Also proactively set loggedIn based on presence of stored tokens
            try {
                const has = Object.keys(localStorage || {}).some((k) =>
                    k.includes('CognitoIdentityServiceProvider') && k.endsWith('LastAuthUser')
                );
                setLoggedIn(Boolean(has));
            } catch { /* ignore */ }

            // fallback deferred re-check in case storage was updated slightly later
            t = setTimeout(() => {
                void deriveFirstNameFromStorage().catch(() => undefined);
            }, 120);
        } catch {
            // ignore
        }

        return () => {
            if (t) clearTimeout(t);
        };
    }, [location.pathname, location.search]);

    useEffect(() => {
        // Wait for hydration before relying on color mode to avoid mismatches.
        setHydrated(true);
    }, []);

    useEffect(() => {
        if (!hydrated || typeof fetch !== 'function') return;
        let cancelled = false;
        (async () => {
            try {
                const res = await fetch('/deploy-info.json', { cache: 'no-store' });
                if (!res.ok) return;
                const data = await res.json();
                if (cancelled) return;
                const commit = typeof data?.commit === 'string' && data.commit.trim() ? data.commit.trim() : 'unknown';
                const timestamp = typeof data?.timestamp === 'string' && data.timestamp.trim() ? data.timestamp.trim() : 'unknown';
                setDeployInfo({ commit, timestamp });
            } catch (err) {
                console.debug('[UniversalHeader] deploy-info fetch skipped', err);
            }
        })();
        return () => {
            cancelled = true;
        };
    }, [hydrated]);

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

    // Listen for storage changes from other tabs/windows and re-sync header state
    useEffect(() => {
        if (typeof window === 'undefined' || typeof window.addEventListener !== 'function') return;
        const handler = (event: StorageEvent) => {
            try {
                if (!event.key) return;
                if (event.key.includes('CognitoIdentityServiceProvider')) {
                    // Re-derive name from storage when Cognito keys change
                    void deriveFirstNameFromStorage().catch(() => undefined);
                    // Update loggedIn based on presence of stored tokens
                    try {
                        const has = Object.keys(localStorage || {}).some((k) => k.includes('CognitoIdentityServiceProvider') && k.endsWith('LastAuthUser'));
                        setLoggedIn(Boolean(has));
                    } catch { /* ignore */ }
                }
            } catch { /* ignore */ }
        };
        window.addEventListener('storage', handler, false);
        return () => {
            try { window.removeEventListener('storage', handler, false); } catch { /* ignore */ }
        };
    }, []);

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
        setDropdownOpen(false);
        try {
            await signOut();
        } catch (err) {
            console.warn('[UniversalHeader] manual logout failed', err);
        }
        try {
            clearAuthStorage();
        } catch (err) {
            console.warn('[UniversalHeader] clearAuthStorage failed', err);
        }
        setLoggedIn(false);
        setUserFirstName(null);
        try {
            await notifyAuthChange(false);
        } catch (err) {
            console.warn('[UniversalHeader] notifyAuthChange after logout failed', err);
        }
        setTimeout(() => history.push('/'), 0);
    }, [history, notifyAuthChange]);

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
        <ErrorBoundary>
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

                    {!isMobile && hydrated && (
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
                            {hydrated && (
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
                            )}

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

                {isMobile && mobileNavOpen && hydrated && (
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
        </ErrorBoundary>
    );
}
