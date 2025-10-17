// Avoid importing aws-amplify at module load time (prevents SSR/build warnings).
// Lazily require it only in the browser when needed.
// @ts-nocheck

function getAmplifyAny(): any | undefined {
    try {
        if (typeof window === 'undefined') return undefined;
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const mod = require('aws-amplify');
        return mod.Amplify || mod.default || mod;
    } catch (err) {
        return undefined;
    }
}

let cachedAuthModule: any | null | undefined;

function getAuthModule(): any | undefined {
    if (cachedAuthModule !== undefined) {
        return cachedAuthModule === null ? undefined : cachedAuthModule;
    }
    try {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        cachedAuthModule = require('aws-amplify/auth');
        return cachedAuthModule;
    } catch (err) {
        cachedAuthModule = null;
        console.debug('[auth-cognito] aws-amplify/auth unavailable', err);
        return undefined;
    }
}

function getLegacyAuth(): any | undefined {
    return (getAmplifyAny() as any)?.Auth;
}

function getHub(): any | undefined {
    return (getAmplifyAny() as any)?.Hub;
}

function getAmplifyConfig(): any | undefined {
    try {
        const AmplifyAny = getAmplifyAny();
        const cfg = AmplifyAny?.getConfig ? AmplifyAny.getConfig() : AmplifyAny?.resourcesConfig;
        if (cfg && cfg.Auth) return cfg;
    } catch {
        // ignore
    }
    try {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const staticMod = require('../config/amplify-config');
        return staticMod?.amplifyConfig || staticMod?.default || staticMod;
    } catch {
        return undefined;
    }
}

function isUserPoolConfigured(): boolean {
    try {
        const AmplifyAny = getAmplifyAny();
        const cfg = AmplifyAny?.getConfig ? AmplifyAny.getConfig() : AmplifyAny?.resourcesConfig;
        const auth = cfg?.Auth;
        const cognito = auth?.Cognito || auth;
        if (!cognito) return false;
        const hasPool = Boolean(cognito.userPoolId);
        const hasClient = Boolean(cognito.userPoolClientId || cognito.userPoolWebClientId);
        return hasPool && hasClient;
    } catch {
        return false;
    }
}

function resolveRedirect(
    value: string | string[] | undefined,
    origin: string,
    fallbackPath: string
): string {
    console.debug('[auth-cognito] resolveRedirect input', { value, origin, fallbackPath });
    if (typeof value === 'string' && value.trim()) {
        return value.trim();
    }
    if (Array.isArray(value) && value.length > 0) {
        for (const candidate of value) {
            if (!candidate) continue;
            try {
                const candidateUrl = new URL(candidate);
                if (candidateUrl.origin === origin) {
                    console.debug('[auth-cognito] resolveRedirect matched origin', { candidate });
                    return candidate;
                }
            } catch {
                // ignore malformed entries and keep scanning
            }
        }
        const first = value.find((item) => typeof item === 'string' && item.trim());
        if (first) {
            console.debug('[auth-cognito] resolveRedirect using first fallback', { first });
            return first.trim();
        }
    }
    return `${origin}${fallbackPath}`;
}

function readStoredAuthState(): {
    username: string;
    accessToken?: string;
    idToken?: string;
    refreshToken?: string;
    payload?: Record<string, unknown>;
} | null {
    if (typeof window === 'undefined') return null;
    try {
        const lastKey = Object.keys(window.localStorage || {}).find((key) => key.endsWith('LastAuthUser'));
        if (!lastKey) return null;
        const username = window.localStorage.getItem(lastKey) || '';
        if (!username) return null;
        const basePrefix = lastKey.replace(/\.LastAuthUser$/, `.${username}`);
        const accessToken = window.localStorage.getItem(`${basePrefix}.accessToken`) || undefined;
        const idToken = window.localStorage.getItem(`${basePrefix}.idToken`) || undefined;
        const refreshToken = window.localStorage.getItem(`${basePrefix}.refreshToken`) || undefined;
        if (!accessToken && !idToken) return null;
        const payload = idToken ? decodeJwtPayload(idToken) : undefined;
        return { username, accessToken, idToken, refreshToken, payload };
    } catch (err) {
        console.debug('[auth-cognito] readStoredAuthState failed', err);
        return null;
    }
}

function decodeJwtPayload(token: string): Record<string, unknown> | undefined {
    try {
        const segments = token.split('.');
        if (segments.length < 2) return undefined;
        const normalized = segments[1].replace(/-/g, '+').replace(/_/g, '/');
        const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=');
        if (typeof atob === 'function') {
            return JSON.parse(atob(padded));
        }
        if (typeof Buffer !== 'undefined') {
            return JSON.parse(Buffer.from(padded, 'base64').toString('utf8'));
        }
        return undefined;
    } catch {
        return undefined;
    }
}

export async function loginWithProvider(provider: string): Promise<void> {
    const redirectUri = typeof window !== 'undefined' ? window.location.origin : undefined;
    let modularFailure: unknown;
    try {
        await initAuth().catch(() => undefined);
        const authModule = getAuthModule();
        if (authModule && typeof authModule.signInWithRedirect === 'function') {
            if (!isUserPoolConfigured()) {
                console.warn('[auth-cognito] modular Auth missing configuration, using Hosted UI fallback');
            } else {
                const providerInput =
                    provider === 'LoginWithAmazon'
                        ? { provider: { custom: provider } }
                        : { provider };
                try {
                    console.debug('[auth-cognito] using modular signInWithRedirect', { provider });
                    await authModule.signInWithRedirect(providerInput as any);
                    return;
                } catch (err) {
                    modularFailure = err;
                    console.error('[auth-cognito] modular signInWithRedirect failed, falling back', err);
                }
            }
        }

        const legacyAuth = getLegacyAuth();
        if (legacyAuth && typeof legacyAuth.federatedSignIn === 'function') {
            // Try federatedSignIn for social providers (Amplify v5 and below)
            console.debug('[auth-cognito] using Amplify.federatedSignIn', { provider, redirectUri });
            await legacyAuth.federatedSignIn({ customProvider: provider, options: { redirectSignIn: redirectUri } });
            return;
        }
        // Fallback: try Hosted UI URL from config
        if (typeof window !== 'undefined') {
            const cfg = getAmplifyConfig();
            const oauth =
                cfg?.Auth?.oauth ||
                cfg?.Auth?.Cognito?.oauth ||
                cfg?.Auth?.Cognito?.loginWith?.oauth;
            const domain = oauth?.domain;
            const redirectSignIn = redirectUri
                ? resolveRedirect(oauth?.redirectSignIn, redirectUri, '/monitoring')
                : (oauth?.redirectSignIn as string) || '/monitoring';
            const responseType = oauth?.responseType || 'code';
            const clientId =
                cfg?.Auth?.userPoolWebClientId ||
                cfg?.Auth?.userPoolClientId ||
                cfg?.Auth?.Cognito?.userPoolClientId ||
                '';
            if (domain) {
                console.debug('[auth-cognito] redirecting to Hosted UI', { provider, domain, redirectSignIn, clientId });
                const url = `https://${domain}/oauth2/authorize?identity_provider=${encodeURIComponent(provider)}&redirect_uri=${encodeURIComponent(redirectSignIn)}&response_type=${encodeURIComponent(responseType)}&client_id=${encodeURIComponent(clientId)}`;
                window.location.href = url;
                return;
            }
            // Try fetching a runtime config file (served from static/) before final fallback.
            if (typeof fetch === 'function') {
                try {
                    const res = await fetch('/amplify-config.json', { cache: 'no-store' });
                    if (res.ok) {
                        const runtimeCfg = await res.json();
                        const oauth2 =
                            runtimeCfg?.Auth?.oauth ||
                            runtimeCfg?.Auth?.Cognito?.oauth ||
                            runtimeCfg?.Auth?.Cognito?.loginWith?.oauth;
                        const domain2 = oauth2?.domain;
                        const redirect2 = redirectUri ? resolveRedirect(oauth2?.redirectSignIn, redirectUri, '/monitoring') : redirectSignIn;
                        const responseType2 = oauth2?.responseType || responseType;
                        const clientId2 =
                            runtimeCfg?.Auth?.userPoolWebClientId ||
                            runtimeCfg?.Auth?.userPoolClientId ||
                            runtimeCfg?.Auth?.Cognito?.userPoolClientId ||
                            clientId;
                        if (domain2) {
                            console.debug('[auth-cognito] redirecting with runtime config', { provider, domain2, redirect2, clientId2 });
                            const url2 = `https://${domain2}/oauth2/authorize?identity_provider=${encodeURIComponent(provider)}&redirect_uri=${encodeURIComponent(redirect2)}&response_type=${encodeURIComponent(responseType2)}&client_id=${encodeURIComponent(clientId2)}`;
                            window.location.href = url2;
                            return;
                        }
                    } else if (res.status === 404) {
                        console.warn('[auth-cognito] amplify-config.json missing. Run scripts/pull_amplify_config.py before local login.');
                    }
                } catch (e) {
                    console.error('[auth-cognito] runtime fetch failed', e);
                }
            } else {
                console.debug('[auth-cognito] fetch unavailable, skipping runtime config lookup');
            }
            // final fallback: go to generic sign-in doc
            console.warn('[auth-cognito] falling back to /sign-in');
            if (redirectUri) {
                window.location.href = `${redirectUri.replace(/\/$/, '')}/sign-in`;
            } else {
                window.location.href = '/sign-in';
            }
            return;
        }
    } catch (error) {
        console.error('[loginWithProvider] Error during login:', error);
        throw error;
    }
    if (modularFailure) {
        throw modularFailure;
    }
    throw new Error('Unable to initiate login; no Cognito configuration available');
}

export async function isLoggedIn(): Promise<boolean> {
    try {
        let configured = isUserPoolConfigured();
        if (!configured) {
            await initAuth().catch(() => undefined);
            configured = isUserPoolConfigured();
            if (!configured) {
                console.debug('[auth-cognito] isLoggedIn waiting for user pool configuration');
                return false;
            }
        }
        const authModule = getAuthModule();
        if (authModule && typeof authModule.getCurrentUser === 'function') {
            try {
                const user = await authModule.getCurrentUser();
                console.debug('[auth-cognito] isLoggedIn current user (modular)', { user });
                return !!user;
            } catch (err) {
                console.debug('[auth-cognito] isLoggedIn modular getCurrentUser failed', err);
            }
        }

        const legacyAuth = getLegacyAuth();
        if (!legacyAuth || typeof legacyAuth.currentAuthenticatedUser !== 'function') {
            const stored = readStoredAuthState();
            if (stored) {
                console.debug('[auth-cognito] isLoggedIn derived from stored tokens');
                return true;
            }
            console.debug('[auth-cognito] isLoggedIn missing Auth.currentAuthenticatedUser');
            return false;
        }
        const user = await legacyAuth.currentAuthenticatedUser();
        console.debug('[auth-cognito] isLoggedIn current user (legacy)', { user });
        return !!user;
    } catch (error) {
        console.warn('[auth-cognito] isLoggedIn failed', error);
        const stored = readStoredAuthState();
        if (stored) {
            console.debug('[auth-cognito] isLoggedIn recovered via stored tokens after error');
            return true;
        }
        return false;
    }
}

export async function signOutUser(): Promise<void> {
    try {
        const authModule = getAuthModule();
        if (authModule && typeof authModule.signOut === 'function') {
            await authModule.signOut();
            return;
        }
        const legacyAuth = getLegacyAuth();
        if (!legacyAuth || typeof legacyAuth.signOut !== 'function') return;
        await legacyAuth.signOut();
    } catch (error) {
        console.error('[signOutUser] Error during logout:', error);
    }
}

export async function getCurrentUser(): Promise<{ email?: string; name?: string; sub?: string } | null> {
    const stored = readStoredAuthState();
    const mergeWithStored = (base: { email?: string; name?: string; sub?: string | null }): { email?: string; name?: string; sub?: string } => {
        const payload = stored?.payload;
        const email = base.email ?? (typeof payload?.email === 'string' ? payload.email : undefined);
        const name = base.name ?? (typeof payload?.name === 'string' ? payload.name : undefined);
        const sub = base.sub ?? (typeof payload?.sub === 'string' ? payload.sub : stored?.username);
        return { email, name, sub: sub ?? undefined };
    };
    try {
        const authModule = getAuthModule();
        if (authModule && typeof authModule.getCurrentUser === 'function') {
            const user = await authModule.getCurrentUser();
            const attrs = user?.signInDetails?.loginId ? { email: user?.signInDetails?.loginId, ...user?.verifiedContact } : user?.attributes || user;
            const email = attrs?.email;
            const name = attrs?.name || attrs?.preferred_username;
            const sub = attrs?.sub || user?.userId;
            const profile = mergeWithStored({ email, name, sub });
            if (profile.email || profile.name || profile.sub) {
                return profile;
            }
            if (stored?.username) {
                return { email: profile.email, name: profile.name, sub: stored.username };
            }
            return null;
        }
        const legacyAuth = getLegacyAuth();
        if (!legacyAuth || typeof legacyAuth.currentAuthenticatedUser !== 'function') {
            if (stored?.payload || stored?.username) {
                const fallback = mergeWithStored({});
                if (fallback.email || fallback.name || fallback.sub) return fallback;
            }
            return null;
        }
        const user = await legacyAuth.currentAuthenticatedUser();
        const attrs = user?.attributes || user;
        const email = attrs?.email;
        const name = attrs?.name || attrs?.preferred_username;
        const sub = attrs?.sub;
        const profile = mergeWithStored({ email, name, sub });
        if (profile.email || profile.name || profile.sub) {
            return profile;
        }
        return null;
    } catch (err) {
        if (stored?.payload || stored?.username) {
            const fallback = mergeWithStored({});
            if (fallback.email || fallback.name || fallback.sub) {
                return fallback;
            }
        }
        console.debug('[auth-cognito] getCurrentUser falling back failed', err);
        return null;
    }
}

export async function initAuth(options?: { force?: boolean }): Promise<void> {
    try {
        const AmplifyAny = getAmplifyAny();
        if (!AmplifyAny || typeof AmplifyAny.configure !== 'function') {
            console.warn('[initAuth] Amplify not available for configuration');
            return;
        }

        const windowCfg = (typeof window !== 'undefined' && (window as any).__SC_AMPLIFY_CONFIG__) || undefined;
        const existingCfg = AmplifyAny.getConfig ? AmplifyAny.getConfig() : AmplifyAny.resourcesConfig;
        const hasExistingAuth = Boolean(existingCfg?.Auth) && Object.keys(existingCfg.Auth || {}).length > 0;

        if (windowCfg && windowCfg.Auth) {
            console.debug('[auth-cognito] configure from window object');
            AmplifyAny.configure(windowCfg);
            const finalCfg = AmplifyAny.getConfig ? AmplifyAny.getConfig() : AmplifyAny.resourcesConfig;
            console.debug('[initAuth] applied window config', {
                hasAuth: Boolean(finalCfg?.Auth),
                keys: finalCfg ? Object.keys(finalCfg) : []
            });
            return;
        }

        if (hasExistingAuth && !options?.force) {
            // Already configured with Auth, nothing to do.
            return;
        }

        try {
            // eslint-disable-next-line @typescript-eslint/no-var-requires
            const staticMod = require('../config/amplify-config');
            const staticCfg = staticMod?.amplifyConfig || staticMod?.default || staticMod;
            if (staticCfg?.Auth) {
                if (typeof window !== 'undefined') {
                    (window as any).__SC_AMPLIFY_CONFIG__ = staticCfg;
                }
                console.debug('[auth-cognito] configure from static module');
                AmplifyAny.configure(staticCfg);
                const finalCfg = AmplifyAny.getConfig ? AmplifyAny.getConfig() : AmplifyAny.resourcesConfig;
                console.debug('[initAuth] applied static config', {
                    hasAuth: Boolean(finalCfg?.Auth),
                    keys: finalCfg ? Object.keys(finalCfg) : []
                });
                return;
            }
            console.warn('[initAuth] static amplify-config missing Auth block');
        } catch (staticError) {
            console.error('[initAuth] unable to load static amplify-config', staticError);
        }

        if (!hasExistingAuth || options?.force) {
            console.error('[initAuth] Amplify lacks Auth configuration after initialization attempts');
        }
    } catch (error) {
        console.error('[initAuth] Error during initialization:', error);
    }
}

if (typeof window !== 'undefined') {
    void initAuth().catch((error) => {
        console.error('[auth-cognito] auto initAuth failed', error);
    });
}

// onAuthChange returns an unsubscribe function
export function onAuthChange(cb: (isAuth: boolean) => void): () => void {
    try {
        const unsubscribeFns: Array<() => void> = [];

        const Hub = getHub();
        if (Hub && typeof Hub.listen === 'function') {
            const remove = Hub.listen('auth', ({ payload }: any) => {
                try {
                    if (!payload) return;
                    if (payload.event === 'signIn') {
                        cb(true);
                        return;
                    }
                    if (payload.event === 'signOut') {
                        const stored = readStoredAuthState();
                        cb(Boolean(stored));
                    }
                } catch (e) {
                    // swallow
                }
            });
            if (typeof remove === 'function') {
                unsubscribeFns.push(() => {
                    try { remove(); } catch { /* ignore */ }
                });
            }
        }

        if (typeof window !== 'undefined' && typeof window.addEventListener === 'function') {
            // NOTE 2025-10-16: Hard refresh logic was removed to avoid visible UI flicker.
            // If reverting, restore the window.location.replace guard that previously lived here.
            const handler = (event: Event) => {
                try {
                    const detail = (event as CustomEvent<{ authenticated?: boolean }>).detail;
                    if (!detail || typeof detail.authenticated === 'undefined') return;
                    const stored = readStoredAuthState();
                    const finalAuth = Boolean(detail.authenticated) || Boolean(stored);
                    cb(finalAuth);
                } catch {
                    // ignore
                }
            };
            window.addEventListener('sc-auth-change', handler as EventListener, false);
            unsubscribeFns.push(() => {
                try { window.removeEventListener('sc-auth-change', handler as EventListener, false); } catch { /* ignore */ }
            });
        }

        if (unsubscribeFns.length === 0) {
            return () => undefined;
        }
        return () => {
            for (const fn of unsubscribeFns) {
                try { fn(); } catch { /* ignore */ }
            }
        };
    } catch (err) {
        return () => undefined;
    }
}

export async function notifyAuthChange(forced?: boolean | null): Promise<void> {
    try {
        const Hub = getHub();
        let isAuth: boolean;
        if (typeof forced === 'boolean') {
            isAuth = forced;
        } else {
            const authModule = getAuthModule();
            const legacyAuth = getLegacyAuth();
            if (!authModule && !legacyAuth) return;
            isAuth = await isLoggedIn();
        }
        // When sign-in is observed, persist a minimal token snapshot to storage
        // before dispatching events so listeners reading localStorage will see it.
        if (isAuth) {
            try {
                console.debug('[auth-debug] notifyAuthChange will persist token snapshot');
                await persistAuthSnapshotToStorage().catch(() => undefined);
                console.debug('[auth-debug] notifyAuthChange persisted snapshot (check localStorage)');
            } catch { /* ignore */ }
        }

        if (Hub && typeof Hub.dispatch === 'function') {
            // Dispatch an auth event so listeners refresh state
            try {
                Hub.dispatch('auth', { event: isAuth ? 'signIn' : 'signOut' });
            } catch (e) {
                // swallow
            }
        }
        if (typeof window !== 'undefined' && typeof window.dispatchEvent === 'function') {
            try {
                const detail = { authenticated: isAuth };
                console.debug('[auth-debug] dispatching sc-auth-change', { authenticated: isAuth });
                if (typeof CustomEvent === 'function') {
                    window.dispatchEvent(new CustomEvent('sc-auth-change', { detail }));
                    console.debug('[auth-debug] sc-auth-change dispatched');
                } else if (typeof document !== 'undefined' && typeof document.createEvent === 'function') {
                    const evt = document.createEvent('CustomEvent');
                    evt.initCustomEvent('sc-auth-change', false, false, detail);
                    window.dispatchEvent(evt);
                    console.debug('[auth-debug] sc-auth-change dispatched (legacy)');
                }
            } catch (eventError) {
                console.debug('[auth-cognito] notifyAuthChange window event failed', eventError);
            }
        }
    } catch (err) {
        console.error('[notifyAuthChange] error', err);
    }
}

async function persistAuthSnapshotToStorage(): Promise<void> {
    try {
        console.debug('[auth-debug] persistAuthSnapshotToStorage start');
        if (typeof window === 'undefined') return;
        const cfg = getAmplifyConfig();
        const clientId =
            cfg?.Auth?.userPoolWebClientId ||
            cfg?.Auth?.userPoolClientId ||
            cfg?.Auth?.Cognito?.userPoolClientId;
        if (!clientId) return;

        const authModule = getAuthModule();
        const legacyAuth = getLegacyAuth();

        // Try to obtain tokens from modular API
        if (authModule && typeof authModule.fetchAuthSession === 'function') {
            try {
                const session = await authModule.fetchAuthSession();
                const tokens = session?.tokens || {};
                const idToken = tokens?.idToken;
                const accessToken = tokens?.accessToken;
                // Attempt to derive username from idToken or session
                const payload = idToken ? decodeJwtPayload(idToken) : undefined;
                const username = payload?.cognito_username || payload?.username || payload?.sub || (await tryGetUsernameFromAuthModule(authModule));
                if (!username) return;
                const storagePrefix = `CognitoIdentityServiceProvider.${clientId}`;
                const userPrefix = `${storagePrefix}.${username}`;
                try {
                    window.localStorage.setItem(`${storagePrefix}.LastAuthUser`, username);
                    if (accessToken) window.localStorage.setItem(`${userPrefix}.accessToken`, accessToken);
                    if (idToken) window.localStorage.setItem(`${userPrefix}.idToken`, idToken);
                    console.debug('[auth-debug] persistAuthSnapshotToStorage stored keys', {
                        storagePrefix,
                        username,
                        hasAccessToken: Boolean(accessToken),
                        hasIdToken: Boolean(idToken),
                    });
                } catch (e) { /* ignore storage failures */ }
                return;
            } catch (err) {
                // fall through to legacy
            }
        }

        if (legacyAuth && typeof legacyAuth.currentSession === 'function') {
            try {
                const sess = await legacyAuth.currentSession();
                const idToken = sess?.getIdToken?.()?.getJwtToken?.();
                const accessToken = sess?.getAccessToken?.()?.getJwtToken?.();
                const payload = idToken ? decodeJwtPayload(idToken) : undefined;
                const username = payload?.cognito_username || payload?.username || payload?.sub || undefined;
                if (!username) return;
                const storagePrefix = `CognitoIdentityServiceProvider.${clientId}`;
                const userPrefix = `${storagePrefix}.${username}`;
                try {
                    window.localStorage.setItem(`${storagePrefix}.LastAuthUser`, username);
                    if (accessToken) window.localStorage.setItem(`${userPrefix}.accessToken`, accessToken);
                    if (idToken) window.localStorage.setItem(`${userPrefix}.idToken`, idToken);
                    console.debug('[auth-debug] persistAuthSnapshotToStorage stored keys (legacy)', {
                        storagePrefix,
                        username,
                        hasAccessToken: Boolean(accessToken),
                        hasIdToken: Boolean(idToken),
                    });
                } catch (e) { /* ignore storage failures */ }
                return;
            } catch {
                // ignore
            }
        }
    } catch (err) {
        // ignore
    }
}

async function tryGetUsernameFromAuthModule(authModule: any): Promise<string | undefined> {
    try {
        if (!authModule || typeof authModule.getCurrentUser !== 'function') return undefined;
        const user = await authModule.getCurrentUser();
        return user?.username || user?.attributes?.sub || undefined;
    } catch {
        return undefined;
    }
}

export async function refreshAuthState(): Promise<boolean> {
    try {
        if (typeof window === 'undefined') return false;
        const authModule = getAuthModule();
        if (authModule && typeof authModule.fetchAuthSession === 'function') {
            try {
                const modularSession = await authModule.fetchAuthSession();
                if (modularSession?.tokens?.accessToken) return true;
            } catch (sessionError) {
                console.debug('[auth-cognito] fetchAuthSession unavailable', sessionError);
            }
        }

        const legacyAuth = getLegacyAuth();
        if (legacyAuth && typeof legacyAuth.currentSession === 'function') {
            try {
                const activeSession = await legacyAuth.currentSession();
                if (activeSession) return true;
            } catch (sessionError) {
                console.debug('[auth-cognito] currentSession unavailable', sessionError);
            }
        }

        const storedSearch = sessionStorage.getItem('__sc_oauth_search') || window.location.search;
        const storedHref = sessionStorage.getItem('__sc_oauth_href') || window.location.href;
        const workingUrl = new URL(storedHref || window.location.href);
        if (storedSearch) workingUrl.search = storedSearch;

        const params = new URLSearchParams(workingUrl.search);
        const code = params.get('code');
        if (!code) return false;

        const cfg = getAmplifyConfig();
        const oauth =
            cfg?.Auth?.oauth ||
            cfg?.Auth?.Cognito?.oauth ||
            cfg?.Auth?.Cognito?.loginWith?.oauth;
        const domain = oauth?.domain;
        const clientId =
            cfg?.Auth?.userPoolWebClientId ||
            cfg?.Auth?.userPoolClientId ||
            cfg?.Auth?.Cognito?.userPoolClientId;
        // Prefer using the actual captured callback URL (workingUrl) for redirect_uri
        // because it represents the URL Cognito redirected the browser to (and where
        // the authorization code resides). This prevents mismatches when the
        // configured redirectSignIn array contains multiple allowed paths (eg. /dashboard
        // and /monitoring) and the current navigation used a different path.
        let redirectUri: string;
        try {
            redirectUri = `${workingUrl.origin}${workingUrl.pathname}`;
            console.debug('[auth-cognito] refreshAuthState using workingUrl-derived redirectUri', { redirectUri });
        } catch (e) {
            redirectUri = resolveRedirect(oauth?.redirectSignIn, window.location.origin, '/monitoring');
            console.debug('[auth-cognito] refreshAuthState fallback redirectUri', { redirectUri });
        }

        if (!domain || !clientId) {
            console.error('[auth-cognito] refreshAuthState missing domain or clientId');
            return false;
        }
        if (typeof fetch !== 'function') {
            console.error('[auth-cognito] refreshAuthState requires fetch');
            return false;
        }

        const tokenEndpoint = `https://${domain}/oauth2/token`;
        const body = new URLSearchParams({
            grant_type: 'authorization_code',
            client_id: clientId,
            code,
            redirect_uri: redirectUri,
        });
        // If a PKCE verifier was stored during the authorization request, include it
        // so the token exchange succeeds when PKCE is required by the client.
        try {
            const possibleKeys = ['sc_pkce.verifier', 'sc_pkce_verifier', 'code_verifier', 'pkce.verifier', 'pkce_verifier'];
            for (const k of possibleKeys) {
                try {
                    const v = sessionStorage.getItem(k);
                    if (v) {
                        body.set('code_verifier', v);
                        console.debug('[auth-debug] refreshAuthState using code_verifier from sessionStorage', { key: k });
                        break;
                    }
                } catch { /* ignore storage errors */ }
            }
        } catch { /* ignore */ }
        console.debug('[auth-debug] refreshAuthState tokenExchange', { tokenEndpoint, clientId, redirectUri });

        let response = await fetch(tokenEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: body.toString(),
        });

        // If the first token exchange failed, try one immediate retry against
        // the same token endpoint (some transient failures are recoverable).
        if (!response.ok) {
            console.error('[auth-cognito] token exchange failed', response.status, response.statusText);
            try {
                response = await fetch(tokenEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: body.toString(),
                });
            } catch (retryErr) {
                console.debug('[auth-cognito] token exchange retry failed', retryErr);
            }
        }

        // If retry still failed, attempt to fetch runtime config and try an
        // alternate token endpoint constructed from runtime /amplify-config.json.
        if (!response.ok) {
            try {
                if (typeof fetch === 'function') {
                    const runtimeRes = await fetch('/amplify-config.json', { cache: 'no-store' });
                    if (runtimeRes && runtimeRes.ok) {
                        const runtimeCfg = await runtimeRes.json();
                        const oauth2 =
                            runtimeCfg?.Auth?.oauth ||
                            runtimeCfg?.Auth?.Cognito?.oauth ||
                            runtimeCfg?.Auth?.Cognito?.loginWith?.oauth;
                        const domain2 = oauth2?.domain;
                        const clientId2 =
                            runtimeCfg?.Auth?.userPoolWebClientId ||
                            runtimeCfg?.Auth?.userPoolClientId ||
                            runtimeCfg?.Auth?.Cognito?.userPoolClientId ||
                            clientId;
                        const redirect2 = resolveRedirect(oauth2?.redirectSignIn, window.location.origin, '/monitoring');
                        if (domain2 && clientId2) {
                            const tokenEndpoint2 = `https://${domain2}/oauth2/token`;
                            const body2 = new URLSearchParams({
                                grant_type: 'authorization_code',
                                client_id: clientId2,
                                code,
                                redirect_uri: redirect2,
                            });
                            try {
                                response = await fetch(tokenEndpoint2, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                    body: body2.toString(),
                                });
                            } catch (e) {
                                console.debug('[auth-cognito] runtime token exchange retry failed', e);
                            }
                        }
                    }
                }
            } catch (e) {
                console.debug('[auth-cognito] runtime token exchange retry failed', e);
            }
        }

        if (!response.ok) {
            return false;
        }

        const payload = await response.json();
        const username = payload?.username || payload?.id_token || 'anonymous';
        const accessToken = payload?.access_token;
        const idToken = payload?.id_token;
        const refreshToken = payload?.refresh_token;

        console.debug('[auth-debug] refreshAuthState token exchange succeeded', {
            username: username,
            hasAccessToken: Boolean(accessToken),
            hasIdToken: Boolean(idToken),
            hasRefreshToken: Boolean(refreshToken),
        });

        const storagePrefix = `CognitoIdentityServiceProvider.${clientId}`;
        const userPrefix = `${storagePrefix}.${username}`;

        try {
            localStorage.setItem(`${storagePrefix}.LastAuthUser`, username);
            if (accessToken) localStorage.setItem(`${userPrefix}.accessToken`, accessToken);
            if (idToken) localStorage.setItem(`${userPrefix}.idToken`, idToken);
            if (refreshToken) localStorage.setItem(`${userPrefix}.refreshToken`, refreshToken);
        } catch (storageError) {
            console.error('[auth-cognito] failed to persist tokens', storageError);
            return false;
        }

        sessionStorage.removeItem('__sc_oauth_search');
        sessionStorage.removeItem('__sc_oauth_href');
        try {
            sessionStorage.setItem('__sc_auth_pending_emit', '1');
        } catch { /* ignore */ }

        try {
            window.history.replaceState({}, document.title, workingUrl.pathname);
        } catch (historyError) {
            console.debug('[auth-cognito] history cleanup failed', historyError);
        }

        if (authModule && typeof authModule.fetchAuthSession === 'function') {
            try {
                await authModule.fetchAuthSession();
            } catch (fetchError) {
                console.debug('[auth-cognito] fetchAuthSession after hydrate failed', fetchError);
            }
        } else if (legacyAuth && typeof legacyAuth.currentSession === 'function') {
            try {
                await legacyAuth.currentSession();
            } catch (fetchError) {
                console.debug('[auth-cognito] currentSession after hydrate failed', fetchError);
            }
        }

        return true;
    } catch (error) {
        console.error('[auth-cognito] refreshAuthState error', error);
        return false;
    }
}

export function getAvailableProviders(): Array<{ id: string; name: string }> {
    // Return provider objects synchronously so callers that require immediate
    // availability (header/login UI during render) work reliably.
    try {
        const cfg = getAmplifyConfig();
        const providers =
            cfg?.Auth?.Cognito?.loginWith?.oauth?.providers ||
            cfg?.Auth?.Cognito?.loginWith?.providers ||
            cfg?.Auth?.oauth?.providers;
        if (Array.isArray(providers) && providers.length > 0) {
            return providers.map((p: any) => {
                if (typeof p === 'string') {
                    if (p === 'LoginWithAmazon') return { id: 'LoginWithAmazon', name: 'Amazon' };
                    return { id: p, name: p };
                }
                if (p && typeof p === 'object') {
                    const customId = p.custom || p.id;
                    const customName = p.name || p.label || customId;
                    if (!customId) {
                        return { id: JSON.stringify(p), name: JSON.stringify(p) };
                    }
                    if (customId === 'LoginWithAmazon' || customName === 'LoginWithAmazon') {
                        return { id: 'LoginWithAmazon', name: 'Amazon' };
                    }
                    const displayName = customName === 'LoginWithAmazon' ? 'Amazon' : customName;
                    return { id: String(customId), name: String(displayName || customId) };
                }
                // best-effort fallback
                return { id: String(p), name: String(p) };
            });
        }
    } catch (err) {
        // ignore
    }
    return [
        { id: 'Google', name: 'Google' },
        { id: 'LoginWithAmazon', name: 'Amazon' }
    ];
}

// Backwards-compatible aliases expected by callers
export const signOut = signOutUser;
export const loginWithHostedUI = async (): Promise<void> => {
    // Hosted UI usually handled by Amplify.federatedSignIn or redirect to /sign-in
    try {
        await initAuth().catch(() => undefined);
        const authModule = getAuthModule();
        if (authModule && typeof authModule.signInWithRedirect === 'function') {
            if (!isUserPoolConfigured()) {
                console.warn('[auth-cognito] modular Auth missing configuration, using Hosted UI fallback');
            } else {
                try {
                    console.debug('[auth-cognito] using modular signInWithRedirect for Hosted UI');
                    await authModule.signInWithRedirect({ provider: 'COGNITO' } as any);
                    return;
                } catch (err) {
                    console.error('[auth-cognito] modular Hosted UI redirect failed, falling back', err);
                }
            }
        }
        const legacyAuth = getLegacyAuth();
        if (legacyAuth && typeof legacyAuth.federatedSignIn === 'function') {
            await legacyAuth.federatedSignIn();
            return;
        }
        // Fallback: try to construct Hosted UI from config
        if (typeof window !== 'undefined') {
            const cfg = getAmplifyConfig();
            const oauth =
                cfg?.Auth?.oauth ||
                cfg?.Auth?.Cognito?.oauth ||
                cfg?.Auth?.Cognito?.loginWith?.oauth;
            const domain = oauth?.domain;
            const redirectSignIn = resolveRedirect(oauth?.redirectSignIn, window.location.origin, '/monitoring');
            const responseType = oauth?.responseType || 'code';
            if (domain) {
                const url = `https://${domain}/oauth2/authorize?redirect_uri=${encodeURIComponent(redirectSignIn)}&response_type=${encodeURIComponent(responseType)}&client_id=${encodeURIComponent(
                    cfg?.Auth?.userPoolWebClientId ||
                    cfg?.Auth?.userPoolClientId ||
                    cfg?.Auth?.Cognito?.userPoolClientId ||
                    ''
                )}`;
                window.location.href = url;
                return;
            }
            // Try runtime static config before falling back to generic sign-in page
            if (typeof fetch === 'function') {
                try {
                    const res = await fetch('/amplify-config.json', { cache: 'no-store' });
                    if (res.ok) {
                        const runtimeCfg = await res.json();
                        const oauth2 =
                            runtimeCfg?.Auth?.oauth ||
                            runtimeCfg?.Auth?.Cognito?.oauth ||
                            runtimeCfg?.Auth?.Cognito?.loginWith?.oauth;
                        const domain2 = oauth2?.domain;
                        const redirect2 = resolveRedirect(oauth2?.redirectSignIn, window.location.origin, '/monitoring');
                        const responseType2 = oauth2?.responseType || responseType;
                        const clientId2 =
                            runtimeCfg?.Auth?.userPoolWebClientId ||
                            runtimeCfg?.Auth?.userPoolClientId ||
                            runtimeCfg?.Auth?.Cognito?.userPoolClientId ||
                            '';
                        if (domain2) {
                            const url2 = `https://${domain2}/oauth2/authorize?redirect_uri=${encodeURIComponent(redirect2)}&response_type=${encodeURIComponent(responseType2)}&client_id=${encodeURIComponent(clientId2)}`;
                            window.location.href = url2;
                            return;
                        }
                    } else if (res.status === 404) {
                        console.warn('[loginWithHostedUI] amplify-config.json missing. Run scripts/pull_amplify_config.py before local login.');
                    }
                } catch (e) {
                    // ignore
                }
            } else {
                console.debug('[loginWithHostedUI] fetch unavailable, skipping runtime config lookup');
            }
            // final fallback: go to generic sign-in doc
            window.location.href = `${window.location.origin.replace(/\/$/, '')}/sign-in`;
            return;
        }
    } catch (err) {
        console.error('[loginWithHostedUI] error', err);
        throw err;
    }
};

// Provider-specific helpers used across the codebase
export const loginWithGoogle = async (): Promise<void> => loginWithProvider('Google');
export const loginWithAmazon = async (): Promise<void> => loginWithProvider('LoginWithAmazon');
// Facebook removed per request

export async function debugAuthSnapshot(): Promise<Record<string, unknown>> {
    const snapshot: Record<string, unknown> = {
        timestamp: new Date().toISOString(),
    };
    try {
        const authModule = getAuthModule();
        const legacyAuth = getLegacyAuth();
        const cfg = getAmplifyConfig();
        snapshot.amplifyConfigured = Boolean(cfg);
        snapshot.authConfig = cfg?.Auth ? { hasAuth: true } : { hasAuth: false };

        if (typeof window !== 'undefined') {
            const storageKeys = Object.keys(window.localStorage || {}).filter((key) => key.includes('CognitoIdentityServiceProvider'));
            snapshot.localStorageKeys = storageKeys;
            snapshot.cookies = typeof document !== 'undefined' ? document.cookie : '';
        }

        if (authModule && typeof authModule.getCurrentUser === 'function') {
            try {
                const user = await authModule.getCurrentUser();
                snapshot.currentUser = {
                    username: user?.username,
                    attributes: user?.attributes ?? user?.verifiedContact,
                };
            } catch (err) {
                snapshot.currentUserError = String(err);
            }
        } else if (legacyAuth && typeof legacyAuth.currentAuthenticatedUser === 'function') {
            try {
                const user = await legacyAuth.currentAuthenticatedUser();
                snapshot.currentUser = {
                    username: user?.username,
                    attributes: user?.attributes,
                };
            } catch (err) {
                snapshot.currentUserError = String(err);
            }
        } else {
            const stored = readStoredAuthState();
            if (stored) {
                snapshot.currentUser = {
                    username: stored.username,
                    attributes: stored.payload,
                };
            }
        }

        if (authModule && typeof authModule.fetchAuthSession === 'function') {
            try {
                const session = await authModule.fetchAuthSession();
                snapshot.session = {
                    idToken: session?.tokens?.idToken,
                    accessToken: session?.tokens?.accessToken,
                    clockDrift: session?.clockDrift,
                };
            } catch (err) {
                snapshot.sessionError = String(err);
            }
        } else if (legacyAuth && typeof legacyAuth.currentSession === 'function') {
            try {
                const session = await legacyAuth.currentSession();
                snapshot.session = {
                    idToken: session?.getIdToken?.()?.decodePayload?.(),
                    accessToken: session?.getAccessToken?.()?.getExpiration?.(),
                    clockDrift: session?.clockDrift,
                };
            } catch (err) {
                snapshot.sessionError = String(err);
            }
        } else {
            const stored = readStoredAuthState();
            if (stored) {
                snapshot.session = {
                    idToken: stored.idToken,
                    accessToken: stored.accessToken,
                };
            }
        }
    } catch (error) {
        snapshot.unhandledError = String(error);
    }
    console.groupCollapsed('[auth-cognito] debug snapshot');
    console.log(snapshot);
    console.groupEnd();
    return snapshot;
}

export function clearAuthStorage(): { removedKeys: string[]; clearedCookies: string[] } {
    const removedKeys: string[] = [];
    const clearedCookies: string[] = [];
    try {
        if (typeof window !== 'undefined') {
            const allKeys = Object.keys(window.localStorage || {});
            for (const key of allKeys) {
                if (key.includes('CognitoIdentityServiceProvider')) {
                    window.localStorage.removeItem(key);
                    removedKeys.push(key);
                }
            }
            const hostedUICookieNames = ['amplify-signin-with-hostedUI'];
            for (const cookieName of hostedUICookieNames) {
                document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/;`;
                clearedCookies.push(cookieName);
            }
        }
        if (typeof sessionStorage !== 'undefined') {
            sessionStorage.clear();
        }
    } catch (error) {
        console.error('[auth-cognito] clearAuthStorage error', error);
    }
    console.debug('[auth-cognito] cleared auth storage', { removedKeys, clearedCookies });
    return { removedKeys, clearedCookies };
}
