/**
 * AWS Cognito authentication for ShieldCraft AI
 * Uses Cognito Hosted UI for social login (Google OAuth)
 */

import { fetchAuthSession, signOut as amplifySignOut, signInWithRedirect, getCurrentUser as amplifyGetCurrentUser } from 'aws-amplify/auth';
import { Hub } from 'aws-amplify/utils';
import { Amplify } from 'aws-amplify';
import { amplifyConfig } from '@site/src/config/amplify-config';

export interface User {
    email: string;
    name?: string;
    sub: string;
    attributes?: Record<string, any>;
}

// Debug helper: enable in the browser console with `window.__SC_AUTH_DEBUG__ = true`
function scDebug(...args: any[]) {
    try {
        if (typeof window !== 'undefined' && (window as any).__SC_AUTH_DEBUG__) {
            // eslint-disable-next-line no-console
            console.debug('[SC-AUTH]', ...args);
        }
    } catch { /* ignore */ }
}

function dumpUrlState() {
    try {
        if (typeof window === 'undefined') return {};
        return {
            href: window.location.href,
            pathname: window.location.pathname,
            search: window.location.search,
            hash: window.location.hash,
            localStorageKeys: Object.keys(window.localStorage || {}).slice(0, 50),
        };
    } catch (err) {
        return { err: String(err) };
    }
}

// Temporary debugging helper: persist a small snapshot to localStorage so
// it can be inspected after reproducing a failing OAuth flow in production.
// Intentionally avoid storing sensitive token material.
function persistDebugSnapshot(key: string, data: Record<string, any>) {
    try {
        if (typeof window === 'undefined') return;
        const LS_KEY = 'sc_debug_oauth';
        const SESS_KEY = 'sc_debug_oauth_sess';
        const COOKIE_KEY = 'sc_debug_oauth_bak';

        // Read current primary snapshot (if any)
        let existing: Record<string, any> = {};
        try {
            const raw = window.localStorage.getItem(LS_KEY) || window.sessionStorage.getItem(SESS_KEY) || '';
            if (raw) existing = JSON.parse(raw);
        } catch { existing = {}; }

        existing[key] = data;

        // Keep the snapshot small - stringify and cap size
        try {
            const serialized = JSON.stringify(existing);
            const capped = serialized.length > 4096 ? serialized.slice(0, 4096) : serialized;

            // Primary store (may be cleared by other runtime code)
            try { window.localStorage.setItem(LS_KEY, capped); } catch { /* ignore */ }

            // Secondary store: sessionStorage (less likely to be mass-cleared)
            try { window.sessionStorage.setItem(SESS_KEY, capped); } catch { /* ignore */ }

            // Tertiary fallback: short-lived cookie (URL-encoded, very small)
            try {
                const cookieVal = encodeURIComponent(capped.slice(0, 2000));
                // keep cookie for 10 minutes
                document.cookie = `${COOKIE_KEY}=${cookieVal}; path=/; max-age=${60 * 10}`;
            } catch { /* ignore */ }

            // In-memory fallback (cleared on navigation but useful intra-page)
            try { (window as any).__sc_debug_oauth_backup = existing; } catch { /* ignore */ }
        } catch { /* ignore serialization issues */ }
    } catch { /* ignore */ }
}

export async function isLoggedIn(): Promise<boolean> {
    if (typeof window === 'undefined') return false;
    return await _isLoggedInDedupe();
}

// Force refresh auth state (bypass cache)
export async function refreshAuthState(): Promise<boolean> {
    if (typeof window === 'undefined') return false;
    __sc_lastAuthState = null;
    __sc_lastAuthCheckPromise = null;

    // Check if we're on an OAuth callback URL and handle it
    if (window.location.search.includes('code=') && window.location.search.includes('state=')) {
        scDebug('Detected OAuth callback, processing...');
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            const state = urlParams.get('state');

            scDebug('OAuth callback params:', { code: code ? 'present' : 'missing', state: state ? 'present' : 'missing' });

            if (code) {
                // For direct Cognito OAuth (like Amazon), we need to manually exchange the code
                scDebug('Attempting to exchange OAuth code...');

                // Persist incoming callback info for debugging
                try {
                    persistDebugSnapshot('callbackParams', {
                        href: window.location.href,
                        search: window.location.search,
                        origin: window.location.origin,
                        redirectSignIn0: amplifyConfig.Auth.Cognito.loginWith.oauth.redirectSignIn[0],
                        clientId: amplifyConfig.Auth.Cognito.userPoolClientId,
                        timestamp: new Date().toISOString(),
                    });
                } catch { /* ignore */ }

                // Try to get Amplify to process this callback
                try {
                    // Force Amplify to check for tokens after a delay
                    await new Promise(resolve => setTimeout(resolve, 2000));

                    // Try fetching session with force refresh
                    const session = await fetchAuthSession({ forceRefresh: true });
                    scDebug('Post-callback session:', session);

                    const hasTokens = !!(session?.tokens?.accessToken || session?.tokens?.idToken);
                    scDebug('Tokens after callback processing:', hasTokens);

                    if (hasTokens) {
                        scDebug('OAuth callback successful!');
                        // Clean up the URL
                        const url = new URL(window.location.href);
                        url.searchParams.delete('code');
                        url.searchParams.delete('state');
                        window.history.replaceState({}, document.title, url.toString());

                        // Notify all listeners
                        await notifyAuthChange();
                        return true;
                    } else {
                        scDebug('Amplify did not process OAuth callback, trying manual approach...');

                        // Manual token exchange for direct Cognito OAuth
                        const tokenResponse = await fetch('https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/token', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                            },
                            body: new URLSearchParams({
                                grant_type: 'authorization_code',
                                client_id: amplifyConfig.Auth.Cognito.userPoolClientId,
                                code: code,
                                redirect_uri: window.location.origin + '/dashboard',
                            }),
                        });

                        // Persist token exchange outcome (status only) for debugging
                        try {
                            const debugOutcome: any = { status: tokenResponse.status, statusText: tokenResponse.statusText };
                            // Attempt to capture a short, non-sensitive text body (trimmed)
                            try {
                                const text = await tokenResponse.clone().text();
                                debugOutcome.bodySnippet = text.slice(0, 512);
                            } catch { /* ignore body */ }
                            persistDebugSnapshot('tokenExchange', debugOutcome);
                        } catch { /* ignore */ }

                        if (tokenResponse.ok) {
                            const tokens = await tokenResponse.json();
                            scDebug('Manual token exchange successful:', {
                                hasAccessToken: !!tokens.access_token,
                                hasIdToken: !!tokens.id_token
                            });

                            // Store tokens manually in localStorage for Amplify to find
                            const userPoolId = amplifyConfig.Auth.Cognito.userPoolId;
                            const clientId = amplifyConfig.Auth.Cognito.userPoolClientId;

                            // Create Amplify-compatible token storage
                            const tokenKey = `CognitoIdentityServiceProvider.${clientId}.LastAuthUser`;
                            const userKey = `CognitoIdentityServiceProvider.${clientId}.${tokens.username || 'user'}`;

                            localStorage.setItem(tokenKey, tokens.username || 'user');
                            localStorage.setItem(`${userKey}.accessToken`, tokens.access_token);
                            localStorage.setItem(`${userKey}.idToken`, tokens.id_token);
                            if (tokens.refresh_token) {
                                localStorage.setItem(`${userKey}.refreshToken`, tokens.refresh_token);
                            }

                            // Clean up URL
                            const url = new URL(window.location.href);
                            url.searchParams.delete('code');
                            url.searchParams.delete('state');
                            window.history.replaceState({}, document.title, url.toString());

                            // Force Amplify to reload session
                            await new Promise(resolve => setTimeout(resolve, 500));
                            const newSession = await fetchAuthSession({ forceRefresh: true });
                            scDebug('Session after manual token storage:', newSession);

                            await notifyAuthChange();
                            return !!(newSession?.tokens?.accessToken || newSession?.tokens?.idToken);
                        } else {
                            scDebug('Manual token exchange failed:', tokenResponse.status);
                        }
                    }
                } catch (error) {
                    scDebug('OAuth callback processing error:', error);
                }
            }
        } catch (error) {
            scDebug('OAuth callback error:', error);
        }
    }

    return await _isLoggedInDedupe();
}// Internal cached/deduped implementation
let __sc_lastAuthState: boolean | null = null;
let __sc_lastAuthCheckPromise: Promise<boolean> | null = null;

async function _isLoggedInOnce(): Promise<boolean> {
    try {
        scDebug('Checking auth session...');
        const session = await fetchAuthSession();

        // Simple, reliable check
        const hasValidTokens = !!(
            session?.tokens?.accessToken ||
            session?.tokens?.idToken
        );

        scDebug('Session check result:', {
            hasValidTokens,
            sessionExists: !!session,
            tokensProperty: !!session?.tokens,
            accessToken: session?.tokens?.accessToken ? 'present' : 'missing',
            idToken: session?.tokens?.idToken ? 'present' : 'missing'
        });

        return hasValidTokens;
    } catch (error) {
        scDebug('Auth check error:', String(error));
        return false;
    }
} async function _isLoggedInDedupe(): Promise<boolean> {
    // If a check is in-flight, await it
    if (__sc_lastAuthCheckPromise) return __sc_lastAuthCheckPromise;

    // If we already have a known last state, return it immediately (fast path)
    if (__sc_lastAuthState !== null) return __sc_lastAuthState;

    // Otherwise perform a single check and cache the result
    __sc_lastAuthCheckPromise = (async () => {
        const res = await _isLoggedInOnce();
        __sc_lastAuthState = res;
        __sc_lastAuthCheckPromise = null;
        return res;
    })();
    return __sc_lastAuthCheckPromise;
}

export async function getCurrentUser(): Promise<User | null> {
    if (typeof window === 'undefined') return null;
    try {
        // Use Amplify's getCurrentUser which properly handles auth state
        const cognitoUser = await amplifyGetCurrentUser();
        const session = await fetchAuthSession();
        const idToken = session.tokens?.idToken?.payload;

        if (!idToken) return null;

        return {
            email: (idToken.email as string) || '',
            name: (idToken.name as string) || (idToken.email as string),
            sub: cognitoUser.userId,
            attributes: idToken as any,
        };
    } catch (error) {
        scDebug('getCurrentUser error:', error);
        return null;
    }
}

export async function loginWithHostedUI(): Promise<void> {
    try {
        // Use Amplify's built-in OAuth flow which handles callback automatically
        await signInWithRedirect({ provider: 'Google' });
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
}

export async function loginWithProvider(provider: string): Promise<void> {
    const cognitoDomain = 'shieldcraft-auth.auth.us-east-1.amazoncognito.com';
    // Use the same client ID as amplifyConfig to avoid mismatches
    const clientId = amplifyConfig.Auth.Cognito.userPoolClientId;
    // Use the first configured redirect URI (matches Amplify's behavior)
    const redirectUri = encodeURIComponent(amplifyConfig.Auth.Cognito.loginWith.oauth.redirectSignIn[0]);

    const url = `https://${cognitoDomain}/oauth2/authorize?identity_provider=${provider}&client_id=${clientId}&response_type=code&scope=email+profile+openid&redirect_uri=${redirectUri}`;
    scDebug('loginWithProvider -> redirecting to', url, 'provider:', provider, 'redirect_uri:', redirectUri, 'url state:', dumpUrlState());
    // Navigate the browser to the Hosted UI
    window.location.href = url;
}

// Convenience functions for specific providers using Amplify's OAuth
export async function loginWithGoogle(): Promise<void> {
    try {
        await signInWithRedirect({ provider: 'Google' });
    } catch (error) {
        console.error('Google login failed:', error);
        throw error;
    }
}

export const loginWithAmazon = async (): Promise<void> => {
    try {
        // Use the custom provider configuration as defined in amplify-config
        await signInWithRedirect({ provider: { custom: 'LoginWithAmazon' } });

    } catch (error) {
        scDebug('Amazon OAuth error:', error);
        throw error;
    }
};


// Get available identity providers with professional branding
export function getAvailableProviders(): Array<{ id: string, name: string, icon?: string }> {
    return [
        { id: 'Google', name: 'Google', icon: '🔍' },
        { id: 'LoginWithAmazon', name: 'Amazon', icon: '📦' },
        // Microsoft and GitHub login options removed from public UI
    ];
}

export async function signOut(): Promise<void> {
    try {
        await amplifySignOut();
        // Proactively notify subscribers so UI updates immediately after logout
        try {
            await notifyAuthChange();
        } catch {
            // noop
        }
    } catch (error) {
        console.error('Sign out failed:', error);
    }
}

type AuthChangeCallback = (isAuthenticated: boolean) => void;
const authChangeListeners = new Set<AuthChangeCallback>();

// Call all registered listeners
export async function notifyAuthChange(): Promise<void> {
    const authenticated = await isLoggedIn();
    scDebug('notifyAuthChange - authenticated:', authenticated, 'url:', dumpUrlState());

    // Notify all registered callbacks
    authChangeListeners.forEach(callback => {
        callback(authenticated);
    });

    // Also broadcast a window-level event for any decoupled listeners
    try {
        if (typeof window !== 'undefined') {
            const ev = new CustomEvent('sc-auth-changed', { detail: { value: authenticated } });
            window.dispatchEvent(ev);
            // Sync a simple localStorage flag for ultra-light consumers
            try {
                if (authenticated) window.localStorage.setItem('sc_logged_in', '1');
                else window.localStorage.removeItem('sc_logged_in');
            } catch { /* ignore storage errors */ }
        }
    } catch { /* ignore dispatch errors */ }
}

export function onAuthChange(callback: AuthChangeCallback): () => void {
    authChangeListeners.add(callback);

    // Immediately check current auth state
    (async () => {
        const authenticated = await isLoggedIn();
        callback(authenticated);
    })();

    return () => {
        authChangeListeners.delete(callback);
    };
}

export const AUTH_EVENT = 'sc-auth-changed';
export const AUTH_KEY = 'sc_logged_in';

// Bridge Amplify Auth events to our notifier
if (typeof window !== 'undefined') {
    try {
        // Ensure Amplify is configured as early as possible for any consumers of this module
        // Configure Amplify with type assertion to handle complex OAuth provider configuration
        Amplify.configure(amplifyConfig as any);

        Hub.listen('auth', async ({ payload }) => {
            const event = payload?.event as string | undefined;
            scDebug('Amplify auth event:', event);
            if (!event) return;
            // On any auth state change, notify listeners
            await notifyAuthChange();
        });

        // Check for OAuth callback on page load
        const handleOAuthCallback = async () => {
            if (window.location.search.includes('code=') && window.location.search.includes('state=')) {
                scDebug('OAuth callback detected on page load');
                await new Promise(resolve => setTimeout(resolve, 2000)); // Give Amplify more time
                await notifyAuthChange();
            } else {
                // Regular page load - check auth state
                await notifyAuthChange();
            }
        };

        // Handle OAuth callback or regular auth check
        setTimeout(handleOAuthCallback, 100);
    } catch (err) {
        console.error('[auth-cognito] Initialization error:', err);
    }
}

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
