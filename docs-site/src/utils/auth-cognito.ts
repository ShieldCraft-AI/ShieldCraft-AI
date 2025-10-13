// Minimal shim delegating to MinimalIdP
import { amplifyConfig } from '../config/amplify-config';
import * as MinimalIdP from './minimal-idp';

export type User = {
    email: string;
    name?: string;
    sub: string;
    attributes?: Record<string, any>;
};

export const AUTH_EVENT = MinimalIdP.AUTH_EVENT;
export const AUTH_KEY = MinimalIdP.AUTH_KEY;

export function initAuth(): void {
    try {
        const oauth = amplifyConfig?.Auth?.Cognito?.loginWith?.oauth;
        const clientId = amplifyConfig?.Auth?.Cognito?.userPoolClientId;
        const redirects = Array.isArray(oauth?.redirectSignIn) ? oauth.redirectSignIn : [];
        if (oauth?.domain && clientId && redirects.length > 0) {
            MinimalIdP.init({ domain: oauth.domain, clientId, redirectUris: redirects });
        }
        // If aws-amplify is present at runtime, configure it with our amplifyConfig
        // This keeps production login flow unchanged while allowing tests to mock modules.
        try {
            // Allow a runtime override to force the lightweight minimal idP
            const useMinimal = (typeof window !== 'undefined' && (window as any).__SC_AUTH_MODE__ === 'minimal');
            if (!useMinimal) {
                // eslint-disable-next-line @typescript-eslint/no-var-requires
                const awsAmplify = require('aws-amplify');
                if (awsAmplify && typeof awsAmplify.Amplify?.configure === 'function') {
                    try { awsAmplify.Amplify.configure(amplifyConfig); } catch { /* ignore */ }
                }
            }
        } catch { /* ignore - aws-amplify not present */ }

        // Attach Amplify Hub listener if available so tests can mock/observe it
        try {
            // eslint-disable-next-line @typescript-eslint/no-var-requires
            const ampUtils = require('aws-amplify/utils');
            const Hub = ampUtils?.Hub;
            if (Hub && typeof Hub.listen === 'function') {
                Hub.listen('auth', async ({ payload }: any) => {
                    try { await notifyAuthChange(); } catch { /* ignore */ }
                });
            }
        } catch {
            // no-op if Amplify utils not present
        }
    } catch { /* ignore */ }

}

export async function isLoggedIn(): Promise<boolean> {
    // Fast path: if we've previously recorded an authenticated state, use it
    try {
        if (typeof window !== 'undefined' && window.localStorage.getItem(AUTH_KEY) === '1') return true;
    } catch { /* ignore */ }

    // If tests or other code mock aws-amplify/auth, prefer their fetchAuthSession
    try {
        // dynamic require to avoid static import-time side-effects
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const amp = require('aws-amplify/auth');
        if (amp && typeof amp.fetchAuthSession === 'function') {
            try {
                const session = await amp.fetchAuthSession();
                const has = !!(session?.tokens?.accessToken || session?.tokens?.idToken);
                if (has) return true;
            } catch { /* swallow and fall back */ }
        }
    } catch { /* not available - fall back to minimal idp */ }

    // As a last-ditch, try Amplify-compatible localStorage keys (LastAuthUser + accessToken)
    try {
        const clientId = amplifyConfig?.Auth?.Cognito?.userPoolClientId;
        if (clientId && typeof window !== 'undefined') {
            const prefix = `CognitoIdentityServiceProvider.${clientId}`;
            const last = window.localStorage.getItem(`${prefix}.LastAuthUser`);
            if (last) {
                const tok = window.localStorage.getItem(`${prefix}.${last}.accessToken`);
                if (tok) return true;
            }
        }
    } catch { /* ignore */ }

    ensureMinimalInit();
    try {
        // If minimal idp supports ensureValidToken, use it to refresh expired tokens
        if (typeof (MinimalIdP as any).ensureValidToken === 'function') {
            const ok = await (MinimalIdP as any).ensureValidToken();
            if (ok) return true;
        }
    } catch { /* ignore */ }
    return MinimalIdP.isLoggedIn();
}

export async function refreshAuthState(): Promise<boolean> {
    try { await finalizeOAuthRedirect(); } catch { /* ignore */ }
    ensureMinimalInit();
    // Use the public notifyAuthChange so that if aws-amplify/auth is mocked
    // the Amplify fetchAuthSession path is exercised (tests rely on this).
    try { await notifyAuthChange(); } catch { /* ignore */ }
    return isLoggedIn();
}

export async function finalizeOAuthRedirect(): Promise<void> {
    if (typeof window === 'undefined') return;
    try {
        ensureMinimalInit();
        const res = await MinimalIdP.handleRedirectCallback(window.location.href).catch(() => null);
        if (res && res.success && res.tokens) {
            // write Amplify-compatible localStorage keys so legacy code/tests can read them
            try {
                const clientId = amplifyConfig?.Auth?.Cognito?.userPoolClientId;
                if (clientId) {
                    const prefix = `CognitoIdentityServiceProvider.${clientId}`;
                    const user = (res.tokens.username as string) || 'user';
                    try { window.localStorage.setItem(`${prefix}.LastAuthUser`, user); } catch { /* ignore */ }
                    try { window.localStorage.setItem(`${prefix}.${user}.accessToken`, res.tokens.accessToken || ''); } catch { /* ignore */ }
                    try { window.localStorage.setItem(`${prefix}.${user}.idToken`, res.tokens.idToken || ''); } catch { /* ignore */ }
                    try { window.localStorage.setItem(`${prefix}.${user}.refreshToken`, res.tokens.refreshToken || ''); } catch { /* ignore */ }
                    try { window.localStorage.setItem(AUTH_KEY, '1'); } catch { /* ignore */ }
                }
            } catch { /* ignore */ }
            // Clear any capture of OAuth params used by older capture scripts/tests
            try {
                if (typeof window !== 'undefined') {
                    sessionStorage.removeItem('__sc_oauth_search');
                    sessionStorage.removeItem('__sc_oauth_hash');
                    sessionStorage.removeItem('__sc_oauth_href');
                }
            } catch { /* ignore */ }
        }
    } catch { /* ignore */ }

    // Notify listeners after processing the redirect and persisting tokens so
    // UI components (which may have mounted shortly after redirect) receive
    // an immediate auth-change event. Best-effort only.
    try { await notifyAuthChange(); } catch { /* ignore */ }
}

export async function getCurrentUser(): Promise<User | null> {
    const tokens = MinimalIdP.getTokens();
    if (!tokens) return null;
    return { email: '', name: undefined, sub: tokens.username || '', attributes: tokens.raw || {} };
}

export async function loginWithHostedUI(): Promise<void> {
    ensureMinimalInit();
    try {
        // prefer Amplify's redirect if available (tests mock this)
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const amp = require('aws-amplify/auth');
        if (amp && typeof amp.signInWithRedirect === 'function') {
            await amp.signInWithRedirect({ provider: 'Google' });
            return;
        }
    } catch { /* ignore */ }
    MinimalIdP.login('Google');
}

export async function loginWithProvider(provider: string): Promise<void> {
    ensureMinimalInit();
    // For explicit provider-based redirects we prefer the direct hosted-ui URL
    // (tests expect window.location.href to be set by loginWithProvider()).
    return MinimalIdP.login(provider);
}

export async function loginWithGoogle(): Promise<void> {
    try {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const amp = require('aws-amplify/auth');
        if (amp && typeof amp.signInWithRedirect === 'function') {
            await amp.signInWithRedirect({ provider: 'Google' });
            return;
        }
    } catch { /* ignore */ }
    ensureMinimalInit();
    return MinimalIdP.login('Google');
}

export const loginWithAmazon = async (): Promise<void> => {
    try {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const amp = require('aws-amplify/auth');
        if (amp && typeof amp.signInWithRedirect === 'function') {
            // Amplify expects a provider object for custom providers
            await amp.signInWithRedirect({ provider: { custom: 'LoginWithAmazon' } });
            return;
        }
    } catch { /* ignore */ }
    ensureMinimalInit();
    return MinimalIdP.login('LoginWithAmazon');
};

function ensureMinimalInit() {
    try {
        const cfg = MinimalIdP.getConfig && MinimalIdP.getConfig();
        if (cfg) return;
        const oauth = amplifyConfig?.Auth?.Cognito?.loginWith?.oauth;
        const clientId = amplifyConfig?.Auth?.Cognito?.userPoolClientId;
        const redirects = Array.isArray(oauth?.redirectSignIn) ? oauth.redirectSignIn : [];
        if (oauth?.domain && clientId && redirects.length > 0) {
            MinimalIdP.init({ domain: oauth.domain, clientId, redirectUris: redirects });
        }
    } catch { /* ignore */ }
}

export function getAvailableProviders(): Array<{ id: string; name: string; icon?: string }> {
    return [
        { id: 'Google', name: 'Google', icon: '🔍' },
        { id: 'LoginWithAmazon', name: 'Amazon', icon: '📦' },
    ];
}

export async function signOut(): Promise<void> {
    try {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const amp = require('aws-amplify/auth');
        if (amp && typeof amp.signOut === 'function') {
            await amp.signOut();
        }
    } catch { /* ignore */ }
    await MinimalIdP.signOut();
}


type AuthChangeCallback = (isAuthenticated: boolean) => void;
const authChangeListeners = new Set<AuthChangeCallback>();

export async function notifyAuthChange(): Promise<void> {
    // Ensure tokens are valid before notifying listeners. If a refresh is
    // possible this will attempt it so consumers receive up-to-date tokens.
    try {
        if (typeof (MinimalIdP as any).ensureValidToken === 'function') {
            // best-effort: don't let failures block notification
            try { await (MinimalIdP as any).ensureValidToken(); } catch { /* ignore */ }
        }
    } catch { /* ignore */ }
    // Prefer Amplify's fetchAuthSession if available (tests often mock it).
    let state: boolean = false;
    try {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const amp = require('aws-amplify/auth');
        if (amp && typeof amp.fetchAuthSession === 'function') {
            try {
                // First normal fetch
                const session = await amp.fetchAuthSession();
                state = !!(session?.tokens?.accessToken || session?.tokens?.idToken);
            } catch {
                // ignore and try forceRefresh below
            }

            if (!state) {
                try {
                    // Second attempt: forceRefresh
                    const session2 = await amp.fetchAuthSession({ forceRefresh: true });
                    state = !!(session2?.tokens?.accessToken || session2?.tokens?.idToken);
                } catch { /* ignore */ }
            }

            try {
                if ((typeof window !== 'undefined') && (window as any).__SC_AUTH_DEBUG__) {
                    // eslint-disable-next-line no-console
                    console.debug('[auth-cognito] notifyAuthChange -> amplify path', { state });
                }
                if (state) window.localStorage.setItem(AUTH_KEY, '1'); else window.localStorage.removeItem(AUTH_KEY);
            } catch { /* ignore */ }
            try {
                if ((typeof window !== 'undefined') && (window as any).__SC_AUTH_DEBUG__) {
                    // eslint-disable-next-line no-console
                    console.debug('[auth-cognito] dispatching event', { event: AUTH_EVENT, detail: { value: state } });
                }
                const ev = new CustomEvent(AUTH_EVENT, { detail: { value: state } }); window.dispatchEvent(ev);
            } catch { /* ignore */ }
        } else {
            MinimalIdP.notifyAuthChange();
            state = MinimalIdP.isLoggedIn();
        }
    } catch {
        // require failed: fall back
        MinimalIdP.notifyAuthChange();
        state = MinimalIdP.isLoggedIn();
    }

    authChangeListeners.forEach(cb => { try { cb(state); } catch { /* ignore */ } });
}

export function onAuthChange(callback: AuthChangeCallback): () => void {
    authChangeListeners.add(callback);
    try { callback(MinimalIdP.isLoggedIn()); } catch { /* ignore */ }
    return () => { authChangeListeners.delete(callback); };
}

export { init as initMinimalIdP } from './minimal-idp';

// Also export initAuth as the canonical initializer name
export { initAuth as init };


// NOTE: initialization is now explicit via initAuth() and must be called by the
// application bootstrap (e.g. src/theme/Root.tsx). This avoids import-time
// side-effects during tests. Tests should call initAuth() when they need the
// Hub listeners or timers attached.

// Expose a small helper to clear debug snapshots from the console
try {
    if (typeof window !== 'undefined') {
        (window as any).scClearAuthDebug = () => {
            try {
                try { localStorage.removeItem('sc_debug_oauth'); } catch { }
                try { sessionStorage.removeItem('sc_debug_oauth_sess'); } catch { }
                try { (window as any).__sc_debug_oauth_backup = undefined; } catch { }
                try { document.cookie = 'sc_debug_oauth_bak=; path=/; max-age=0'; } catch { }
                return true;
            } catch { return false; }
        };
    }
} catch { /* ignore */ }
