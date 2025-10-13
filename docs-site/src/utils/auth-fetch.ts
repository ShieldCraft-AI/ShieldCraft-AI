/** Small fetch wrapper that ensures a valid access token is present (calls
 * MinimalIdP.ensureValidToken()) and attaches the Authorization header when
 * available. This keeps API clients consistent and avoids token-expiry races.
 */
import * as MinimalIdP from './minimal-idp';

export async function authFetch(input: RequestInfo, init?: RequestInit): Promise<Response> {
    try {
        if (typeof (MinimalIdP as any).ensureValidToken === 'function') {
            try { await (MinimalIdP as any).ensureValidToken(); } catch { /* ignore */ }
        }
    } catch { /* ignore */ }

    const tokens = MinimalIdP.getTokens();
    const headers = new Headers(init?.headers as any || undefined);
    if (tokens && tokens.accessToken) {
        headers.set('Authorization', `Bearer ${tokens.accessToken}`);
    }

    const merged: RequestInit = { ...(init || {}), headers };
    return fetch(input, merged);
}

export default authFetch;
