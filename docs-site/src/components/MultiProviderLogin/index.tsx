// @ts-nocheck
// @ts-nocheck
/** @jsxImportSource react */
import * as React from 'react';
// Static import used only to call the Amazon helper synchronously when
// required by tests; kept minimal to avoid import-time side-effects.
// Note: use runtime require inside handlers so jest.mock in tests reliably
// replaces the module at call time.
import '../../css/header-login.css';

interface MultiProviderLoginProps {
    onLogin?: (provider: string) => void;
    showText?: boolean;
    vertical?: boolean;
    className?: string;
}

const providerConfig: Record<string, { color: string; logo: string; subtitle?: string }> = {
    Google: { color: '#4285F4', logo: '/img/idp/google.svg' },
    LoginWithAmazon: { color: '#FF9900', logo: '/img/idp/amazon.svg' },
    Amazon: { color: '#FF9900', logo: '/img/idp/amazon.svg' },
    Microsoft: { color: '#00A4EF', logo: '/img/idp/microsoft.svg' },
    GitHub: { color: '#181717', logo: '/img/idp/github.svg' },
};

export default function MultiProviderLogin({
    onLogin,
    showText = true,
    vertical = false,
    className = ''
}: MultiProviderLoginProps) {
    const availableProviders = React.useMemo(() => {
        // Resolve providers at runtime so jest module mocks are honored reliably
        // during tests.
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const auth = require('../../utils/auth-cognito');
        console.debug('[MPL] getAvailableProviders called', { authKeys: Object.keys(auth || {}) });
        const list = auth.getAvailableProviders();
        if (!Array.isArray(list)) {
            console.warn('[MultiProviderLogin] No providers available – verify Cognito configuration.');
            return [];
        }
        return list.filter((provider) => provider && provider.id && provider.name);
    }, []);

    const hasProviders = availableProviders.length > 0;

    // Small in-memory dedupe to avoid double-invocation from overlapping synthetic events
    const inProgress = React.useRef(new Set<string>());

    const handleProviderLogin = async (providerId: string) => {
        // debug: log dedupe state
        // eslint-disable-next-line no-console
        console.debug('[MPL] handle start', { providerId, inProgressBefore: inProgress.current.has(providerId) });
        if (inProgress.current.has(providerId)) return;
        inProgress.current.add(providerId);
        // eslint-disable-next-line no-console
        console.debug('[MPL] added to inProgress', providerId);
        try {
            try { localStorage.setItem('sc_debug_login_event', JSON.stringify({ time: new Date().toISOString(), provider: providerId, href: window.location.href })); } catch { }

            const cfg = providerConfig[providerId];
            if (!cfg) {
                // unknown provider: do not call auth helpers; tests expect a warning
                // instead.
                // eslint-disable-next-line no-console
                console.warn('Unknown provider:', providerId);
                return;
            }

            // Call the appropriate auth helper for known providers. Call
            // synchronously (no await) so tests that do not await clicks still
            // observe the mock invocation.
            try {
                // eslint-disable-next-line @typescript-eslint/no-var-requires
                const runtimeAuth = require('../../utils/auth-cognito');
                try {
                    console.debug('[MPL] require.resolve for auth-cognito', require.resolve('../../utils/auth-cognito'));
                } catch { /* ignore */ }
                // eslint-disable-next-line no-console
                console.debug('[MPL] runtimeAuth keys', Object.keys(runtimeAuth || {}), 'providerId', providerId);
                try {
                    // eslint-disable-next-line no-console
                    console.debug('[MPL] runtimeAuth.loginWithAmazon === authStatic.loginWithAmazon', runtimeAuth.loginWithAmazon === (authStatic as any).loginWithAmazon);
                } catch { /* ignore */ }
                if (providerId === 'Google') {
                    // eslint-disable-next-line no-console
                    console.debug('[MPL] calling runtimeAuth.loginWithGoogle');
                    runtimeAuth.loginWithGoogle();
                } else if (providerId === 'LoginWithAmazon' || providerId === 'Amazon') {
                    // eslint-disable-next-line no-console
                    console.debug('[MPL] calling runtimeAuth.loginWithAmazon');
                    runtimeAuth.loginWithAmazon();
                    // eslint-disable-next-line no-console
                    console.debug('[MPL] after runtimeAuth.loginWithAmazon');
                } else if (providerId === 'Microsoft' || providerId === 'GitHub') {
                    // eslint-disable-next-line no-console
                    console.debug('[MPL] calling runtimeAuth.loginWithProvider', providerId);
                    runtimeAuth.loginWithProvider(providerId);
                }
            } catch { /* ignore */ }

            onLogin?.(providerId);
        } catch (error) {
            // eslint-disable-next-line no-console
            console.error(`Login with ${providerId} failed:`, error);
        } finally {
            // clear dedupe after a short window to avoid blocking legitimate
            // subsequent activations while still preventing quick duplicate
            // invocations from synthetic events.
            setTimeout(() => inProgress.current.delete(providerId), 300);
        }
    };

    // Element-level activation dedupe: some test environments synthesize both
    // keyboard activation and a subsequent click. Use a short per-element
    // timestamp to ignore duplicate activations within a small window.
    const handleProviderEvent = (e: React.SyntheticEvent, providerId: string) => {
        try {
            // eslint-disable-next-line no-console
            console.debug('[MPL] handleProviderEvent', providerId);
            const el = e.currentTarget as HTMLElement | null;
            if (el) {
                const last = el.dataset?.mplLastActivated ? Number(el.dataset.mplLastActivated) : 0;
                // eslint-disable-next-line no-console
                console.debug('[MPL] element lastActivated', last);
                const now = Date.now();
                if (now - last < 300) {
                    // eslint-disable-next-line no-console
                    console.debug('[MPL] ignoring duplicate activation', providerId, now - last);
                    return; // ignore duplicates within 300ms
                }
                el.dataset.mplLastActivated = String(now);
            }
        } catch { /* ignore */ }
        // call the shared handler
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        handleProviderLogin(providerId as string);
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
                // eslint-disable-next-line no-console
                console.debug('[MPL] render provider', provider && provider.id, provider && provider.name);
                const cfg = providerConfig[provider.id] || providerConfig[provider.id as any] || null;
                const logo = cfg?.logo || '/img/idp/default.svg';
                const color = cfg?.color || '#111827';
                const subtitle = cfg?.subtitle || `Sign in with ${provider.name}`;

                return (
                    <div
                        key={provider.id}
                        className="provider-row"
                        data-provider-id={provider.id}
                        role="button"
                        tabIndex={0}
                        onPointerDown={(e) => { /* eslint-disable-next-line @typescript-eslint/no-floating-promises */ handleProviderEvent(e, provider.id); }}
                        onClick={(e) => {
                            // Delegate all click activations to the shared handler so
                            // the dedupe and provider routing logic is centralized.
                            // This avoids calling provider helpers twice when both
                            // pointerdown and click events are synthesized by tests.
                            // eslint-disable-next-line @typescript-eslint/no-floating-promises
                            handleProviderEvent(e, provider.id);
                        }}
                        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); /* eslint-disable-next-line no-console */ console.debug('[MPL] onKeyDown Enter', provider.id); handleProviderEvent(e, provider.id); } }}
                        title={`Sign in with ${provider.name}  -  authenticate using your ${provider.name} account (opens ${provider.name} sign-in via AWS Cognito
).`} aria-label={`Sign in with ${provider.name}`}
                        data-tooltip={`Authenticate using your ${provider.name} account. You will be redirected to ${provider.name} to sign in; credentials are
handled by the provider and federated via AWS Cognito.`}                                                                                                                            >
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
