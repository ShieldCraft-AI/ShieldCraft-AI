import React from 'react';
import Link from '@docusaurus/Link';
import { useLocation, useHistory } from '@docusaurus/router';
import { useColorMode } from '@docusaurus/theme-common';
import { isLoggedIn, onAuthChange, loginWithHostedUI, signOut } from '@site/src/utils/auth-cognito';
import { preloadPlotly } from '@site/src/utils/plotlyPreload';

interface UniversalHeaderProps {
    height?: string;
}

export default function UniversalHeader({ height = '60px' }: UniversalHeaderProps): React.JSX.Element {
    const location = useLocation();
    const history = useHistory();
    const [loggedIn, setLI] = React.useState(false);
    const [dropdownOpen, setDropdownOpen] = React.useState(false);

    // Use Docusaurus's built-in color mode hook - uniform across all routes
    const { colorMode, setColorMode } = useColorMode();

    React.useEffect(() => {
        const unsubscribe = onAuthChange((isAuth) => setLI(isAuth));
        preloadPlotly();
        return () => { unsubscribe(); };
    }, []);

    // Close dropdown when clicking outside
    React.useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as Element;
            if (!target.closest('.user-dropdown')) {
                setDropdownOpen(false);
            }
        };

        if (dropdownOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [dropdownOpen]);

    const handleLoginClick = async (e: React.MouseEvent) => {
        if (loggedIn) {
            setDropdownOpen(!dropdownOpen);
            return;
        }
        e.preventDefault();
        await loginWithHostedUI();
    };

    const handleLogout = async () => {
        await signOut();
        setDropdownOpen(false);
        setTimeout(() => history.push('/'), 0);
    };

    const handleColorModeToggle = () => {
        const newMode = colorMode === 'dark' ? 'light' : 'dark';
        setColorMode(newMode);
    };

    const navBaseStyle: React.CSSProperties = {
        textDecoration: 'none',
        color: colorMode === 'dark' ? '#e5e7eb' : '#0f172a',
        padding: '0.35rem 0.7rem',
        borderRadius: 10,
        transition: 'background .15s ease, box-shadow .15s ease, transform .12s ease, color .2s ease',
        border: '1px solid transparent',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
    };

    return (
        <header style={{
            background: colorMode === 'dark'
                ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
                : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
            padding: '0.7rem 3rem',
            borderBottom: colorMode === 'dark'
                ? '1px solid rgba(165, 180, 252, 0.3)'
                : '1px solid rgba(100, 116, 139, 0.3)',
            position: 'sticky',
            top: 0,
            zIndex: 5000,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            height: height,
            boxSizing: 'border-box',
            maxWidth: '100vw',
            transition: 'background 0.3s ease, border-color 0.3s ease'
        }}>
            {/* Left Section - Brand */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', flex: '0 0 auto' }}>
                <Link to="/" style={{
                    textDecoration: 'none',
                    color: colorMode === 'dark' ? '#e5e7eb' : '#0f172a',
                    fontSize: '1.3rem',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.55rem',
                    transition: 'color 0.3s ease'
                }}>
                    <img
                        src={"/img/logo.png"}
                        alt="ShieldCraft AI"
                        style={{
                            height: 28,
                            width: 'auto',
                            display: 'block',
                            filter: colorMode === 'dark'
                                ? 'drop-shadow(0 1px 0 rgba(255,255,255,0.06))'
                                : 'drop-shadow(0 1px 0 rgba(0,0,0,0.06))',
                            opacity: 0.96,
                            borderRadius: 6
                        }}
                    />
                    <span>ShieldCraft AI</span>
                </Link>
            </div>

            {/* Center Section - Navigation */}
            <nav style={{
                display: 'flex',
                gap: '3rem',
                alignItems: 'center',
                flex: '1 1 auto',
                justifyContent: 'center',
                maxWidth: '600px'
            }}>
                <Link
                    to="/architecture"
                    className="sc-nav-pill"
                    style={navBaseStyle}
                >
                    Pricing
                </Link>

                <Link
                    to="/intro"
                    className="sc-nav-pill"
                    style={navBaseStyle}
                >
                    Documentation
                </Link>
            </nav>

            {/* Right Section - Controls */}
            <div style={{
                display: 'flex',
                gap: '1.5rem',
                alignItems: 'center',
                flex: '0 0 auto'
            }}>
                {/* User Menu */}
                <div className="user-dropdown" style={{ position: 'relative' }}>
                    <button
                        onClick={handleLoginClick}
                        onMouseEnter={() => preloadPlotly()}
                        className="sc-nav-pill"
                        style={{
                            ...navBaseStyle,
                            fontSize: '1rem',
                            fontWeight: 500,
                            background: 'transparent',
                            cursor: 'pointer',
                            minWidth: 'auto',
                            padding: '0.35rem 0.7rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.4rem'
                        }}
                        aria-label={loggedIn ? 'User menu' : 'Login'}
                    >
                        {loggedIn ? (
                            <>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                    <circle cx="12" cy="7" r="4"></circle>
                                </svg>
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: '-2px' }}>
                                    <polyline points={dropdownOpen ? '18 15 12 9 6 15' : '6 9 12 15 18 9'}></polyline>
                                </svg>
                            </>
                        ) : (
                            <>
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                                    <polyline points="10 17 15 12 10 7"></polyline>
                                    <line x1="15" y1="12" x2="3" y2="12"></line>
                                </svg>
                                <span>Login</span>
                            </>
                        )}
                    </button>

                    {/* Dropdown Menu */}
                    {loggedIn && dropdownOpen && (
                        <div style={{
                            position: 'absolute',
                            top: '100%',
                            right: '0',
                            marginTop: '0.5rem',
                            background: colorMode === 'dark'
                                ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
                                : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                            border: colorMode === 'dark'
                                ? '1px solid rgba(165, 180, 252, 0.3)'
                                : '1px solid rgba(100, 116, 139, 0.3)',
                            borderRadius: '8px',
                            boxShadow: colorMode === 'dark'
                                ? '0 8px 32px rgba(0, 0, 0, 0.4)'
                                : '0 8px 32px rgba(0, 0, 0, 0.15)',
                            minWidth: '200px',
                            overflow: 'hidden',
                            zIndex: 1001
                        }}>
                            <Link
                                to="/dashboard"
                                style={{
                                    display: 'block',
                                    padding: '0.75rem 1rem',
                                    color: colorMode === 'dark' ? '#ffffff' : '#1e293b',
                                    textDecoration: 'none',
                                    borderBottom: colorMode === 'dark'
                                        ? '1px solid rgba(165, 180, 252, 0.1)'
                                        : '1px solid rgba(100, 116, 139, 0.1)',
                                    transition: 'background 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = colorMode === 'dark'
                                    ? 'rgba(165, 180, 252, 0.1)'
                                    : 'rgba(100, 116, 139, 0.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                onClick={() => setDropdownOpen(false)}
                            >
                                Security Console
                            </Link>
                            <Link
                                to="/monitoring"
                                style={{
                                    display: 'block',
                                    padding: '0.75rem 1rem',
                                    color: colorMode === 'dark' ? '#ffffff' : '#1e293b',
                                    textDecoration: 'none',
                                    borderBottom: colorMode === 'dark'
                                        ? '1px solid rgba(165, 180, 252, 0.1)'
                                        : '1px solid rgba(100, 116, 139, 0.1)',
                                    transition: 'background 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = colorMode === 'dark'
                                    ? 'rgba(165, 180, 252, 0.1)'
                                    : 'rgba(100, 116, 139, 0.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                onClick={() => setDropdownOpen(false)}
                            >
                                Mission Control
                            </Link>
                            <Link
                                to="/alerts"
                                style={{
                                    display: 'block',
                                    padding: '0.75rem 1rem',
                                    color: colorMode === 'dark' ? '#ffffff' : '#1e293b',
                                    textDecoration: 'none',
                                    borderBottom: colorMode === 'dark'
                                        ? '1px solid rgba(165, 180, 252, 0.1)'
                                        : '1px solid rgba(100, 116, 139, 0.1)',
                                    transition: 'background 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = colorMode === 'dark'
                                    ? 'rgba(165, 180, 252, 0.1)'
                                    : 'rgba(100, 116, 139, 0.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                onClick={() => setDropdownOpen(false)}
                            >
                                Threat Alerts
                            </Link>
                            <Link
                                to="/threat-feed"
                                style={{
                                    display: 'block',
                                    padding: '0.75rem 1rem',
                                    color: colorMode === 'dark' ? '#ffffff' : '#1e293b',
                                    textDecoration: 'none',
                                    borderBottom: colorMode === 'dark'
                                        ? '1px solid rgba(165, 180, 252, 0.1)'
                                        : '1px solid rgba(100, 116, 139, 0.1)',
                                    transition: 'background 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = colorMode === 'dark'
                                    ? 'rgba(165, 180, 252, 0.1)'
                                    : 'rgba(100, 116, 139, 0.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                onClick={() => setDropdownOpen(false)}
                            >
                                Intelligence Feed
                            </Link>
                            <Link
                                to="/system-status"
                                style={{
                                    display: 'block',
                                    padding: '0.75rem 1rem',
                                    color: colorMode === 'dark' ? '#ffffff' : '#1e293b',
                                    textDecoration: 'none',
                                    borderBottom: colorMode === 'dark'
                                        ? '1px solid rgba(165, 180, 252, 0.1)'
                                        : '1px solid rgba(100, 116, 139, 0.1)',
                                    transition: 'background 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = colorMode === 'dark'
                                    ? 'rgba(165, 180, 252, 0.1)'
                                    : 'rgba(100, 116, 139, 0.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                onClick={() => setDropdownOpen(false)}
                            >
                                Platform Health
                            </Link>
                            <Link
                                to="/recent-activity"
                                style={{
                                    display: 'block',
                                    padding: '0.75rem 1rem',
                                    color: colorMode === 'dark' ? '#ffffff' : '#1e293b',
                                    textDecoration: 'none',
                                    borderBottom: colorMode === 'dark'
                                        ? '1px solid rgba(165, 180, 252, 0.1)'
                                        : '1px solid rgba(100, 116, 139, 0.1)',
                                    transition: 'background 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = colorMode === 'dark'
                                    ? 'rgba(165, 180, 252, 0.1)'
                                    : 'rgba(100, 116, 139, 0.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                onClick={() => setDropdownOpen(false)}
                            >
                                Activity Monitor
                            </Link>
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
                                    transition: 'background 0.2s',
                                    fontSize: '1rem'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            >
                                Logout
                            </button>
                        </div>
                    )}
                </div>

                {/* Color Mode Toggle - Moved to end */}
                <button
                    onClick={handleColorModeToggle}
                    style={{
                        color: colorMode === 'dark' ? '#ffffff' : '#1e293b',
                        background: 'transparent',
                        border: 'none',
                        padding: '0.5rem',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        fontSize: '1.1rem',
                        width: '40px',
                        height: '40px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                    title={`Switch to ${colorMode === 'dark' ? 'light' : 'dark'} mode`}
                >
                    {colorMode === 'dark' ? '☀️' : '🌙'}
                </button>
            </div>
        </header>
    );
}
