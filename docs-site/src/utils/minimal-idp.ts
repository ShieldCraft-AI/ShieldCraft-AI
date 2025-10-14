/** Minimal IdP helper for simple OAuth2 code-exchange flows.
 * Exports a tiny, testable surface: init, login, handleRedirectCallback, isLoggedIn, getTokens, signOut, onAuthChange
 */

const STORAGE_KEY = 'sc_auth.tokens';
const PKCE_KEY = 'sc_pkce.verifier';
const LAST_REDIRECT_KEY = 'sc_oauth.lastRedirectUri';
export const AUTH_EVENT = 'sc-auth-changed';
export const AUTH_KEY = 'sc_logged_in';

export interface MinimalIdPConfig {
    domain: string;
    clientId: string;
    redirectUris: string[];
}

type Tokens = { accessToken?: string | null; idToken?: string | null; refreshToken?: string | null; username?: string | null; raw?: any; expiresAt?: number } | null;

let cfg: MinimalIdPConfig | null = null;
const listeners = new Set<(isAuth: boolean) => void>();

export function init(config?: MinimalIdPConfig) {
    if (!config) return;
    cfg = config;
}

export function getConfig() { return cfg; }

// Helper: generate a PKCE code_verifier and code_challenge
function randomString(len = 64) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
    let out = '';
    const rnd = (bytes: number) => {
        try {
            const a = new Uint8Array(bytes);
            (typeof crypto !== 'undefined' && (crypto as any).getRandomValues ? (crypto as any).getRandomValues(a) : require('crypto').randomFillSync(a));
            return a;
        } catch {
            // fallback Math.random
            const a = new Uint8Array(bytes);
            for (let i = 0; i < bytes; i++) a[i] = Math.floor(Math.random() * 256);
            return a;
        }
    };
    const bytes = rnd(len);
    for (let i = 0; i < bytes.length; i++) {
        out += chars[bytes[i] % chars.length];
    }
    return out;
}

function base64UrlEncode(buffer: ArrayBuffer | Buffer) {
    let str: string;
    if ((buffer as any).toString && typeof (buffer as any).toString === 'function' && Buffer.isBuffer(buffer as any)) {
        str = (buffer as any).toString('base64');
    } else {
        const bytes = new Uint8Array(buffer as ArrayBuffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
        str = typeof btoa === 'function' ? btoa(binary) : Buffer.from(binary, 'binary').toString('base64');
    }
    return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function sha256(data: string) {
    // Prefer SubtleCrypto in browser
    try {
        if (typeof window !== 'undefined' && (window as any).crypto && (window as any).crypto.subtle) {
            const enc = new TextEncoder().encode(data);
            const hash = await (window as any).crypto.subtle.digest('SHA-256', enc);
            return base64UrlEncode(hash);
        }
    } catch {
        // fall through to node
    }
    // Node fallback
    try {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const nodeCrypto = require('crypto');
        const buf = nodeCrypto.createHash('sha256').update(data).digest();
        return base64UrlEncode(buf);
    } catch (err) {
        throw err;
    }
}

function sha256Sync(data: string) {
    try {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const nodeCrypto = require('crypto');
        const buf = nodeCrypto.createHash('sha256').update(data).digest();
        return base64UrlEncode(buf);
    } catch (err) {
        throw err;
    }
}

export function login(provider: string): void | Promise<void> {
    if (!cfg) throw new Error('IdP not initialized');
    const { domain, clientId, redirectUris } = cfg;
    const redirectUri = (typeof window !== 'undefined') ? (redirectUris.find(r => r.startsWith(window.location.origin)) || redirectUris[0]) : redirectUris[0];

    // PKCE: generate verifier and challenge. Use synchronous path in Node so tests
    // (and some SSR environments) will set location.href immediately.
    const verifier = randomString(64);
    try {
        if (typeof sessionStorage !== 'undefined') {
            sessionStorage.setItem(PKCE_KEY, verifier);
            sessionStorage.setItem(LAST_REDIRECT_KEY, redirectUri);
        }
    } catch { /* ignore */ }

    const encoded = encodeURIComponent(redirectUri);
    const buildUrl = (challenge: string) => `https://${domain}/oauth2/authorize?identity_provider=${encodeURIComponent(provider)}&client_id=${encodeURIComponent(clientId)}&response_type=code&scope=email+profile+openid&redirect_uri=${encoded}&code_challenge=${encodeURIComponent(challenge)}&code_challenge_method=S256`;

    // Prefer synchronous computation (node crypto) so callers that expect immediate
    // location changes (tests and some sync callers) work. If sync fails, fall
    // back to SubtleCrypto async path.
    try {
        const challenge = sha256Sync(verifier);
        const url = buildUrl(challenge);
        if (typeof window !== 'undefined') window.location.href = url;
        return;
    } catch (err) {
        // If sync not available, try async SubtleCrypto
        if (typeof window !== 'undefined' && (window as any).crypto && (window as any).crypto.subtle) {
            return (async () => {
                const challenge = await sha256(verifier);
                const url = buildUrl(challenge);
                if (typeof window !== 'undefined') window.location.href = url;
            })();
        }
        // last resort: still try synchronous sha256 (may throw)
        const challenge = sha256Sync(verifier);
        const url = buildUrl(challenge);
        if (typeof window !== 'undefined') window.location.href = url;
        return;
    }
}

function emit(isAuth: boolean) {
    for (const cb of Array.from(listeners)) {
        try { cb(isAuth); } catch { /* ignore */ }
    }
    try {
        if (typeof window !== 'undefined') {
            try {
                if ((window as any).__SC_AUTH_DEBUG__) {
                    // eslint-disable-next-line no-console
                    console.debug('[MinimalIdP] emit', { isAuth, storageKey: STORAGE_KEY, authKey: AUTH_KEY, tokens: (() => { try { return localStorage.getItem(STORAGE_KEY); } catch { return null } })() });
                }
            } catch { /* ignore debug failures */ }
            const ev = new CustomEvent(AUTH_EVENT, { detail: { value: isAuth } });
            window.dispatchEvent(ev);
            if (isAuth) localStorage.setItem(AUTH_KEY, '1'); else localStorage.removeItem(AUTH_KEY);
        }
    } catch { /* ignore */ }
}

export async function handleRedirectCallback(url?: string): Promise<{ success: boolean; tokens?: Tokens; error?: string }> {
    if (!cfg) return { success: false, error: 'not-configured' };
    try {
        const href = url || (typeof window !== 'undefined' ? window.location.href : '');
        const u = new URL(href);
        const params = u.searchParams;
        const code = params.get('code') || new URLSearchParams(u.hash.replace(/^#/, '')).get('code');
        if (!code) return { success: false, error: 'no-code' };

        const tokenEndpoint = `https://${cfg.domain}/oauth2/token`;
        let preferredRedirect: string | null = null;
        try {
            if (typeof sessionStorage !== 'undefined') {
                preferredRedirect = sessionStorage.getItem(LAST_REDIRECT_KEY);
            }
        } catch { /* ignore */ }

        // Build candidates: current location origin+pathname first, then configured redirectUris
        const candidates: string[] = [];
        if (preferredRedirect) candidates.push(preferredRedirect);
        try { candidates.push(`${u.origin}${u.pathname}`); } catch { /* ignore */ }
        try { if (cfg.redirectUris && cfg.redirectUris.length) candidates.push(...cfg.redirectUris); } catch { /* ignore */ }

        const seenRedirects = new Set<string>();
        const debugEnabled = (() => {
            try { return typeof window !== 'undefined' && (window as any).__SC_AUTH_DEBUG__; } catch { return false; }
        })();

        let cachedVerifier: string | null = null;
        try { cachedVerifier = (typeof sessionStorage !== 'undefined') ? sessionStorage.getItem(PKCE_KEY) : null; } catch { /* ignore */ }

        for (const redirectUri of candidates) {
            if (!redirectUri) continue;
            if (seenRedirects.has(redirectUri)) continue;
            seenRedirects.add(redirectUri);
            try {
                const body = new URLSearchParams();
                body.set('grant_type', 'authorization_code');
                body.set('code', code);
                body.set('client_id', cfg.clientId);
                body.set('redirect_uri', redirectUri);
                // include PKCE verifier if present
                if (cachedVerifier) body.set('code_verifier', cachedVerifier);

                if (debugEnabled) {
                    try {
                        // eslint-disable-next-line no-console
                        console.debug('[MinimalIdP] token exchange attempt', {
                            redirectUri,
                            hasVerifier: !!cachedVerifier,
                            body: body.toString(),
                        });
                    } catch { /* ignore */ }
                }

                const resp = await fetch(tokenEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
                    body: body.toString(),
                });

                // Capture debug info about the token exchange when requested.
                let json: any = null;
                if (!resp.ok) {
                    let txt: string | null = null;
                    try { txt = await resp.text().catch(() => null); } catch { /* ignore */ }
                    if (typeof window !== 'undefined' && (window as any).__SC_AUTH_DEBUG__) {
                        // eslint-disable-next-line no-console
                        console.debug('[MinimalIdP] token endpoint non-OK response', { url: tokenEndpoint, status: resp.status, text: txt, redirectUri });
                    }
                    try { if (typeof window !== 'undefined') sessionStorage.setItem('__sc_debug_oauth', JSON.stringify({ url: tokenEndpoint, status: resp.status, text: txt, redirectUri })); } catch { }
                    const textLower = (txt || '').toLowerCase();
                    if (resp.status === 400 && (textLower.includes('invalid_grant') || textLower.includes('invalid_client'))) {
                        // Authorization code is spent; no further attempts will succeed.
                        break;
                    }
                    continue;
                }

                json = await resp.json().catch(() => null);
                if (!json) {
                    try {
                        const txt = await resp.text().catch(() => null);
                        if (typeof window !== 'undefined' && (window as any).__SC_AUTH_DEBUG__) {
                            // eslint-disable-next-line no-console
                            console.debug('[MinimalIdP] token endpoint returned non-JSON', { url: tokenEndpoint, status: resp.status, text: txt });
                        }
                        try { if (typeof window !== 'undefined') sessionStorage.setItem('__sc_debug_oauth', JSON.stringify({ url: tokenEndpoint, status: resp.status, text: txt })); } catch { }
                    } catch { }
                    continue;
                }

                // On success, store the raw response for debugging (best-effort, avoid tokens in logs unless debug enabled)
                try {
                    if (typeof window !== 'undefined' && (window as any).__SC_AUTH_DEBUG__) {
                        // eslint-disable-next-line no-console
                        console.debug('[MinimalIdP] token endpoint success', { url: tokenEndpoint, json });
                    }
                    try { if (typeof window !== 'undefined') sessionStorage.setItem('__sc_debug_oauth', JSON.stringify({ url: tokenEndpoint, status: resp.status, json: json })); } catch { }
                } catch { }
                const expiresIn = json.expires_in ? Number(json.expires_in) : undefined;
                const payload: Tokens = {
                    accessToken: json.access_token || null,
                    idToken: json.id_token || null,
                    refreshToken: json.refresh_token || null,
                    username: json.username || json.user || null,
                    raw: json,
                    // expiresAt in ms since epoch
                    ...(expiresIn ? { expiresAt: Date.now() + expiresIn * 1000 } : {}),
                } as any;

                try { localStorage.setItem(STORAGE_KEY, JSON.stringify(payload)); } catch { /* ignore */ }
                emit(true);
                try { if (typeof sessionStorage !== 'undefined') sessionStorage.removeItem(LAST_REDIRECT_KEY); } catch { /* ignore */ }

                // Clean URL if running in browser
                try {
                    if (typeof window !== 'undefined') {
                        const cur = new URL(window.location.href);
                        cur.searchParams.delete('code');
                        cur.searchParams.delete('state');
                        window.history.replaceState({}, document.title, cur.toString());
                    }
                } catch { /* ignore */ }

                return { success: true, tokens: payload };
            } catch (err) {
                continue;
            }
        }

        return { success: false, error: 'no-token' };
    } catch (err: any) {
        return { success: false, error: String(err) };
    }
}

// Refresh tokens using refresh_token grant
export async function refreshWithRefreshToken(): Promise<boolean> {
    if (!cfg) return false;
    try {
        const tokens = getTokens();
        if (!tokens || !tokens.refreshToken) return false;
        const tokenEndpoint = `https://${cfg.domain}/oauth2/token`;
        const body = new URLSearchParams();
        body.set('grant_type', 'refresh_token');
        body.set('refresh_token', tokens.refreshToken || '');
        body.set('client_id', cfg.clientId);

        const resp = await fetch(tokenEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
            body: body.toString(),
        });
        if (!resp.ok) return false;
        const json = await resp.json().catch(() => null);
        if (!json) return false;

        const expiresIn = json.expires_in ? Number(json.expires_in) : undefined;
        const payload: any = {
            accessToken: json.access_token || null,
            idToken: json.id_token || null,
            refreshToken: json.refresh_token || tokens.refreshToken || null,
            username: json.username || tokens.username || null,
            raw: json,
            ...(expiresIn ? { expiresAt: Date.now() + expiresIn * 1000 } : {}),
        };
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(payload)); } catch { /* ignore */ }
        emit(true);
        return true;
    } catch {
        return false;
    }
}

export function isLoggedIn(): boolean {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return false;
        const obj = JSON.parse(raw);
        return !!(obj?.accessToken || obj?.idToken);
    } catch { return false; }
}

export function getTokens(): Tokens {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null'); } catch { return null; }
}

export async function signOut(): Promise<void> {
    try { localStorage.removeItem(STORAGE_KEY); localStorage.removeItem(AUTH_KEY); } catch { /* ignore */ }
    emit(false);
}

// Ensure there's a valid (non-expired) access token. If expired and refresh_token
// is available, attempt to refresh. Returns true if valid token available.
export async function ensureValidToken(): Promise<boolean> {
    try {
        const t = getTokens();
        if (t && (t.accessToken || t.idToken)) {
            if (t.expiresAt && Date.now() > t.expiresAt - 5000) {
                // token expired (allow 5s clock skew), try refresh
                const ok = await refreshWithRefreshToken();
                return ok;
            }
            return true;
        }
        // no token: try to refresh
        const ok = await refreshWithRefreshToken();
        return ok;
    } catch {
        return false;
    }
}

export function onAuthChange(cb: (isAuth: boolean) => void): () => void {
    listeners.add(cb);
    // call immediately with current state
    try { cb(isLoggedIn()); } catch { /* ignore */ }
    return () => { listeners.delete(cb); };
}

export function notifyAuthChange() { emit(isLoggedIn()); }

export default { init, getConfig, login, handleRedirectCallback, isLoggedIn, getTokens, signOut, onAuthChange, notifyAuthChange };
