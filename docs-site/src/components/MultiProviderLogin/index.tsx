// @ts-nocheck
/** @jsxImportSource react */
import * as React from 'react';
import {
    loginWithGoogle,
    loginWithAmazon,
    loginWithProvider,
    getAvailableProviders
} from '../../utils/auth-cognito';
import '../../css/header-login.css';

interface MultiProviderLoginProps {
    onLogin?: (provider: string) => void;
    showText?: boolean;
    vertical?: boolean;
    className?: string;
}

const providerConfig: Record<string, { color: string; logo: string; handler: () => Promise<void>; subtitle?: string }> = {
    Google: {
        color: '#4285F4',
        logo: '/img/idp/google.svg',
        handler: loginWithGoogle,
    },
    LoginWithAmazon: {
        color: '#FF9900',
        logo: '/img/idp/amazon.svg',
        handler: loginWithAmazon,
    },
    Amazon: {
        color: '#FF9900',
        logo: '/img/idp/amazon.svg',
        handler: loginWithAmazon,
    },
    Microsoft: {
        color: '#00A4EF',
        logo: '/img/idp/microsoft.svg',
        handler: async () => { await loginWithProvider('Microsoft'); },
    },
    GitHub: {
        color: '#181717',
        logo: '/img/idp/github.svg',
        handler: async () => { await loginWithProvider('GitHub'); },
    },
};

export default function MultiProviderLogin({
    onLogin,
    showText = true,
    vertical = false,
    className = ''
}: MultiProviderLoginProps) {
    const availableProviders = React.useMemo(() => {
        const list = getAvailableProviders();
        if (!Array.isArray(list)) {
            console.warn('[MultiProviderLogin] No providers available – verify Cognito configuration.');
            return [];
        }
        return list.filter((provider) => provider && provider.id && provider.name);
    }, []);

    const hasProviders = availableProviders.length > 0;

    const handleProviderLogin = async (providerId: string) => {
        // Lightweight runtime logging for live-site debugging.
        try {
            const debugObj = { time: new Date().toISOString(), provider: providerId, href: window.location.href };
            // keep only the last event
            try { localStorage.setItem('sc_debug_login_event', JSON.stringify(debugObj)); } catch (e) { /* ignore */ }
            console.debug('sc_debug_login_event', debugObj);
        } catch (e) { /* non-blocking */ }
        try {
            const config = providerConfig[providerId];
            if (config) {
                await config.handler();
                onLogin?.(providerId);
            } else {
                // unknown provider: attempt generic handler
                console.warn('Unknown provider:', providerId);
            }
        } catch (error) {
            console.error(`Login with ${providerId} failed:`, error);
        }
    };

    const containerStyle: React.CSSProperties = {
        display: 'flex',
        flexDirection: vertical ? 'column' : 'row',
        alignItems: 'stretch',
        gap: '12px',
        flexWrap: 'nowrap',
    };

    if (!hasProviders) {
        return (
            <div className={`${className} provider-menu`} style={{ ...containerStyle, justifyContent: 'center' }}>
                <div style={{ fontSize: '0.9rem', color: 'var(--ifm-color-content-secondary)' }}>
                    Sign-in options are loading. Refresh the page if this persists.
                </div>
            </div>
        );
    }

    return (
        <div className={`${className} provider-menu`} style={containerStyle}>
            {availableProviders.map((provider) => {
                const cfg = providerConfig[provider.id] || providerConfig[provider.id as any] || null;
                const logo = cfg?.logo || '/img/idp/default.svg';
                const color = cfg?.color || '#111827';
                const subtitle = cfg?.subtitle || `Sign in with ${provider.name}`;

                return (
                    <div
                        key={provider.id}
                        className="provider-row"
                        role="button"
                        tabIndex={0}
                        onClick={() => handleProviderLogin(provider.id)}
                        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleProviderLogin(provider.id); } }}
                        title={`Sign in with ${provider.name} — authenticate using your ${provider.name} account (opens ${provider.name} sign-in via AWS Cognito).`}
                        aria-label={`Sign in with ${provider.name}`}
                        data-tooltip={`Authenticate using your ${provider.name} account. You will be redirected to ${provider.name} to sign in; credentials are handled by the provider and federated via AWS Cognito.`}
                    >
                        <div className="provider-icon" aria-hidden style={{ background: 'var(--ifm-color-content-inverse)' }}>
                            <img src={logo} alt="" width={32} height={32} style={{ display: 'block', maxWidth: '100%', maxHeight: '100%' }} />
                        </div>

                        <div className="provider-content">
                            <div className="provider-title">{provider.name}</div>
                            {showText && <div className="provider-sub">{subtitle}</div>}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

// Compact version for navbar/header
export function CompactMultiProviderLogin() {
    return (
        <MultiProviderLogin
            showText={false}
            className="compact-provider-login"
        />
    );
}

// Full version for login pages
export function FullMultiProviderLogin() {
    return (
        <div style={{ textAlign: 'center', padding: '20px' }}>
            <h3 style={{ marginBottom: '20px' }}>Choose your sign-in method</h3>
            <MultiProviderLogin
                vertical={true}
                showText={true}
                className="full-provider-login"
            />
        </div>
    );
}
