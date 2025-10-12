/**
 * AWS Cognito authentication for ShieldCraft AI
 * Uses Cognito Hosted UI for social login (Google OAuth)
 */

import { fetchAuthSession, signOut as amplifySignOut, signInWithRedirect, getCurrentUser as amplifyGetCurrentUser } from 'aws-amplify/auth';
import 'aws-amplify/auth/enable-oauth-listener';
import { Amplify } from 'aws-amplify';
import { Hub } from 'aws-amplify/utils';
import { amplifyConfig } from '../config/amplify-config';

const isTestEnv = typeof globalThis !== 'undefined' && (globalThis as any)?.process?.env?.NODE_ENV === 'test';
const AUTH_STORAGE_PREFIX = 'CognitoIdentityServiceProvider.';
const AUTH_RECHECK_MAX_ATTEMPTS = 5;
const AUTH_RECHECK_INTERVAL_MS = 3500;
const AUTH_RETRY_DEBOUNCE_MS = 350;
const STORED_OAUTH_SEARCH_KEY = '__sc_oauth_search';
const STORED_OAUTH_HASH_KEY = '__sc_oauth_hash';
const STORED_OAUTH_HREF_KEY = '__sc_oauth_href';

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

function getForcedAuthFlag(): boolean | undefined {
    // Enables automated end-to-end tests to bypass Cognito when __SC_E2E_FORCED_AUTH__ is set.
    try {
        if (typeof window === 'undefined') return undefined;
        const flag = (window as any).__SC_E2E_FORCED_AUTH__;
        if (flag === true) return true;
        if (flag === false) return false;
        return undefined;
    } catch {
        return undefined;
    }
}

let oauthCallbackProcessed = false;

function getStoredOAuthParams() {
    if (typeof window === 'undefined') return null;
    try {
        const search = window.sessionStorage?.getItem(STORED_OAUTH_SEARCH_KEY) || '';
        const hash = window.sessionStorage?.getItem(STORED_OAUTH_HASH_KEY) || '';
        const href = window.sessionStorage?.getItem(STORED_OAUTH_HREF_KEY) || '';
        if (
            (search && search.includes('code=') && search.includes('state=')) ||
            (hash && hash.includes('code=') && hash.includes('state='))
        ) {
            return { search, hash, href };
        }
        return null;
    } catch {
        return null;
    }
}

function clearStoredOAuthParams() {
    if (typeof window === 'undefined') return;
    try {
        window.sessionStorage?.removeItem(STORED_OAUTH_SEARCH_KEY);
        window.sessionStorage?.removeItem(STORED_OAUTH_HASH_KEY);
        window.sessionStorage?.removeItem(STORED_OAUTH_HREF_KEY);
    } catch { /* ignore */ }
}

async function finalizeOAuthRedirect() {
    if (oauthCallbackProcessed) return;
    if (typeof window === 'undefined') return;
    let search = window.location.search || '';
    let hash = window.location.hash || '';
    let usedStoredSearch = false;
    let usedStoredHash = false;
    const storedParams = getStoredOAuthParams();

    if (!search.includes('code=') || !search.includes('state=')) {
        if (storedParams?.search) {
            search = storedParams.search;
            usedStoredSearch = true;
        }
    }
    if (!hash.includes('code=') || !hash.includes('state=')) {
        if (storedParams?.hash) {
            hash = storedParams.hash;
            usedStoredHash = true;
        }
    }

    if (!search.includes('code=') || !search.includes('state=')) {
        if (!hash.includes('code=') || !hash.includes('state=')) return;
    }

    let restoredUrl: string | null = null;
    if (!window.location.search.includes('code=') && storedParams?.search) {
        try {
            const base = storedParams.href && storedParams.href.includes('code=')
                ? storedParams.href
                : `${window.location.origin}${window.location.pathname}${storedParams.search}${storedParams.hash || ''}`;
            window.history.replaceState({ __sc_oauth_restored: true }, document.title, base);
            restoredUrl = base;
            scDebug('OAuth query params restored into URL from capture script.');
        } catch { /* ignore */ }
    }

    const shouldClearStoredParams = !!storedParams;

    if (storedParams && (usedStoredSearch || usedStoredHash)) {
        scDebug('Using stored OAuth params from capture script.', {
            storedSearch: storedParams.search,
            storedHash: storedParams.hash,
            restoredUrl,
        });
    }

    scDebug('Finalizing OAuth redirect via Amplify listener.');
    try {
        const WAIT_SCHEDULE_MS = [0, 150, 350, 700, 1200, 2000, 3000, 4000];
        let tokensDetected = false;
        let session: Awaited<ReturnType<typeof fetchAuthSession>> | null = null;

        for (const delay of WAIT_SCHEDULE_MS) {
            if (delay > 0) await new Promise(resolve => setTimeout(resolve, delay));

            try {
                session = await fetchAuthSession();
            } catch (err) {
                scDebug('fetchAuthSession after redirect failed:', err);
            }

            tokensDetected = !!(session?.tokens?.accessToken || session?.tokens?.idToken || hasTokensInStorage());
            if (tokensDetected) break;

            try {
                session = await fetchAuthSession({ forceRefresh: true });
                tokensDetected = !!(session?.tokens?.accessToken || session?.tokens?.idToken || hasTokensInStorage());
                if (tokensDetected) break;
            } catch (err) {
                scDebug('fetchAuthSession force refresh after redirect failed:', err);
            }
        }

        scDebug('OAuth redirect tokens detected:', tokensDetected);
        if (tokensDetected) {
            oauthCallbackProcessed = true;
            resetAuthCache();

            try {
                const url = new URL(window.location.href);
                url.searchParams.delete('code');
                url.searchParams.delete('state');
                window.history.replaceState({}, document.title, url.toString());
            } catch (err) {
                scDebug('Failed to clean OAuth query params:', err);
            }
        } else {
            try {
                persistDebugSnapshot('oauth-finalize-missing-tokens', {
                    href: window.location.href,
                    attempts: 'listener + forceRefresh',
                    timestamp: new Date().toISOString(),
                });
            } catch { /* ignore */ }
        }
    } catch (error) {
        scDebug('finalizeOAuthRedirect error:', error);
        try { persistDebugSnapshot('oauth-finalize-error', { message: String(error) }); } catch { /* ignore */ }
    } finally {
        if (shouldClearStoredParams) clearStoredOAuthParams();
    }
}

let __sc_lastAuthState: boolean | null = null;
let __sc_lastAuthCheckPromise: Promise<boolean> | null = null;
let authRecheckTimer: number | null = null;
let authPollerHandle: number | null = null;
let authPollerRemaining = 0;

function resetAuthCache() {
    __sc_lastAuthState = null;
    __sc_lastAuthCheckPromise = null;
}

function hasTokensInStorage(): boolean {
    if (typeof window === 'undefined') return false;
    try {
        const clientId = amplifyConfig?.Auth?.Cognito?.userPoolClientId;
        if (!clientId) return false;
        const prefix = `${AUTH_STORAGE_PREFIX}${clientId}`;
        const stores = [window.localStorage, window.sessionStorage];
        for (const store of stores) {
            try {
                const lastAuthUser = store.getItem(`${prefix}.LastAuthUser`);
                if (!lastAuthUser) continue;
                const baseKey = `${prefix}.${lastAuthUser}`;
                const access = store.getItem(`${baseKey}.accessToken`);
                const id = store.getItem(`${baseKey}.idToken`);
                if (access || id) return true;
            } catch { /* ignore per-store issues */ }
        }
        return false;
    } catch (err) {
        scDebug('hasTokensInStorage error:', err);
        return false;
    }
}

function scheduleAuthRefresh(reason: string, immediate = false) {
    if (typeof window === 'undefined') return;
    const run = async () => {
        authRecheckTimer = null;
        try {
            scDebug('scheduleAuthRefresh -> refreshAuthState', reason);
            await refreshAuthState();
        } catch (err) {
            scDebug('scheduleAuthRefresh error:', err);
        }
    };

    if (immediate) {
        void run();
        return;
    }

    if (authRecheckTimer) window.clearTimeout(authRecheckTimer);
    authRecheckTimer = window.setTimeout(run, AUTH_RETRY_DEBOUNCE_MS);
}

function startAuthPoller(reason: string) {
    if (typeof window === 'undefined' || isTestEnv) return;
    if (authPollerHandle) {
        window.clearTimeout(authPollerHandle);
        authPollerHandle = null;
    }
    authPollerRemaining = AUTH_RECHECK_MAX_ATTEMPTS;

    const iterate = async () => {
        authPollerHandle = null;
        try {
            scDebug('auth poll tick', { reason, attemptsLeft: authPollerRemaining });
            const loggedIn = await refreshAuthState();
            authPollerRemaining -= 1;
            if (loggedIn) {
                authPollerRemaining = 0;
                await notifyAuthChange();
                return;
            }
            if (authPollerRemaining <= 0) {
                authPollerRemaining = 0;
                return;
            }
        } catch (err) {
            scDebug('auth poll error:', err);
            authPollerRemaining -= 1;
            if (authPollerRemaining <= 0) return;
        }
        authPollerHandle = window.setTimeout(iterate, AUTH_RECHECK_INTERVAL_MS);
    };

    authPollerHandle = window.setTimeout(iterate, AUTH_RETRY_DEBOUNCE_MS);
}

export async function isLoggedIn(): Promise<boolean> {
    if (typeof window === 'undefined') return false;
    return await _isLoggedInDedupe();
}

// Force refresh auth state (bypass cache)
export async function refreshAuthState(): Promise<boolean> {
    if (typeof window === 'undefined') return false;
    resetAuthCache();
    await finalizeOAuthRedirect();
    return await _isLoggedInDedupe();
}

// Internal cached/deduped implementation

async function _isLoggedInOnce(): Promise<boolean> {
    const forced = getForcedAuthFlag();
    if (typeof forced === 'boolean') return forced;
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

        if (hasValidTokens) return true;

        const storageTokens = hasTokensInStorage();
        scDebug('Local storage fallback tokens present:', storageTokens);
        return storageTokens;
    } catch (error) {
        scDebug('Auth check error:', String(error));
        const storageTokens = hasTokensInStorage();
        scDebug('Fallback after error - storage tokens:', storageTokens);
        return storageTokens;
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
    const oauthConfig = amplifyConfig?.Auth?.Cognito?.loginWith?.oauth;
    const clientId = amplifyConfig?.Auth?.Cognito?.userPoolClientId;
    const domain = oauthConfig?.domain;
    const redirectSignInList = Array.isArray(oauthConfig?.redirectSignIn) ? oauthConfig?.redirectSignIn : [];

    if (!domain || !clientId || redirectSignInList.length === 0) {
        throw new Error('Cognito OAuth configuration is incomplete.');
    }

    let redirectUri = redirectSignInList[0];
    if (typeof window !== 'undefined') {
        const origin = window.location.origin;
        const match = redirectSignInList.find((entry) => entry.startsWith(origin));
        if (match) redirectUri = match;
    }

    const encodedRedirect = encodeURIComponent(redirectUri);
    const url = `https://${domain}/oauth2/authorize?identity_provider=${provider}&client_id=${clientId}&response_type=code&scope=email+profile+openid&redirect_uri=${encodedRedirect}`;
    scDebug('loginWithProvider -> redirecting to', url, 'provider:', provider, 'redirect_uri:', redirectUri, 'url state:', dumpUrlState());
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
            resetAuthCache();
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
    resetAuthCache();
    const authenticated = await isLoggedIn();
    scDebug('notifyAuthChange - authenticated:', authenticated, 'url:', dumpUrlState());

    // Notify all registered callbacks (defensive: isolate listener errors)
    authChangeListeners.forEach(callback => {
        try {
            callback(authenticated);
        } catch (err) {
            scDebug('authChange listener threw an error:', err);
            // swallow to avoid bubbling into UI consumers
        }
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
        try {
            const authenticated = await isLoggedIn();
            try {
                callback(authenticated);
            } catch (err) {
                scDebug('onAuthChange initial callback threw an error:', err);
            }
        } catch (err) {
            scDebug('onAuthChange initial isLoggedIn check failed:', err);
        }
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

        if (Hub && typeof Hub.listen === 'function') {
            try {
                Hub.listen('auth', async ({ payload }: any) => {
                    const event = payload?.event as string | undefined;
                    scDebug('Amplify auth event:', event);
                    if (!event) return;
                    resetAuthCache();
                    // On any auth state change, notify listeners
                    await notifyAuthChange();
                    startAuthPoller(`hub-event:${event}`);
                });
            } catch (err) {
                scDebug('Hub.listen failed to attach:', err);
            }
        } else {
            scDebug('Amplify Hub not available; auth events will rely on polling/explicit notifyAuthChange');
            startAuthPoller('hub-missing');
        }

        // Check for OAuth callback on page load
        const handleOAuthCallback = async () => {
            const hasOAuthParams = window.location.search.includes('code=') && window.location.search.includes('state=');
            if (hasOAuthParams) {
                scDebug('OAuth callback detected on page load');
                await finalizeOAuthRedirect();
            }

            await notifyAuthChange();
            startAuthPoller(hasOAuthParams ? 'oauth-callback' : 'initial-load');
        };

        // Handle OAuth callback or regular auth check
        setTimeout(handleOAuthCallback, 100);

        const focusListener = () => scheduleAuthRefresh('window-focus');
        const visibilityListener = () => {
            try {
                if (typeof document !== 'undefined' && !document.hidden) scheduleAuthRefresh('visibility');
            } catch { /* ignore */ }
        };
        const storageListener = (event: StorageEvent) => {
            const key = event?.key || '';
            if (!key) return;
            if (key.startsWith(AUTH_STORAGE_PREFIX) || key === AUTH_KEY) {
                scDebug('Storage event triggered auth refresh', key);
                scheduleAuthRefresh('storage');
            }
        };
        const pageShowListener = () => scheduleAuthRefresh('pageshow', true);

        try { window.addEventListener('focus', focusListener); } catch { /* ignore */ }
        try { window.addEventListener('pageshow', pageShowListener); } catch { /* ignore */ }
        try { window.addEventListener('storage', storageListener); } catch { /* ignore */ }
        try { if (typeof document !== 'undefined') document.addEventListener('visibilitychange', visibilityListener); } catch { /* ignore */ }
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
