jest.doMock('../../config/amplify-config', () => ({
    amplifyConfig: {
        Auth: {
            Cognito: {
                userPoolClientId: 'TEST_CLIENT_ID',
                loginWith: {
                    oauth: {
                        redirectSignIn: ['https://shieldcraft-ai.com/dashboard', 'http://localhost:3000/dashboard']
                    }
                }
            }
        }
    }
}));

jest.doMock('aws-amplify/auth', () => {
    const fetchAuthSession = jest.fn().mockResolvedValue({ tokens: { accessToken: 'abc', idToken: 'id' } });
    const signInWithRedirect = jest.fn();
    const getCurrentUser = jest.fn();
    const signOut = jest.fn();
    return { fetchAuthSession, signInWithRedirect, getCurrentUser, signOut };
});

describe('notifyAuthChange and onAuthChange', () => {
    beforeEach(() => {
        jest.resetModules();
        jest.clearAllMocks();
        localStorage.clear();
        sessionStorage.clear();
        document.cookie = '';
        const loc = { href: 'https://initial/', origin: 'https://example.test', pathname: '/', search: '', hash: '', assign: jest.fn() };
        Object.defineProperty(window, 'location', { value: loc, writable: true, configurable: true });
    });

    afterEach(() => {
        jest.useRealTimers();
    });

    test('onAuthChange registers and notifyAuthChange invokes callback', async () => {
        const mod = require('../auth-cognito');
        const cb = jest.fn();
        mod.onAuthChange(cb);
        // onAuthChange calls callback immediately and notifyAuthChange will call again
        await mod.notifyAuthChange();
        expect(cb).toHaveBeenCalled();
        // callback receives a boolean auth state on subsequent notify
        expect(typeof cb.mock.calls[0][0]).toBe('boolean');
    });

    test('notifyAuthChange sets sc_logged_in when authenticated and dispatches event', async () => {
        const mod = require('../auth-cognito');
        const listener = jest.fn();
        window.addEventListener('sc-auth-changed', listener as EventListener);
        await mod.notifyAuthChange();
        expect(localStorage.getItem('sc_logged_in')).toBe('1');
        expect(listener).toHaveBeenCalled();
    });

    test('notifyAuthChange rebuilds cached auth state', async () => {
        const amplifyAuth = require('aws-amplify/auth') as {
            fetchAuthSession: jest.Mock;
        };
        amplifyAuth.fetchAuthSession.mockReset();
        amplifyAuth.fetchAuthSession
            .mockResolvedValueOnce({ tokens: {} })
            .mockResolvedValueOnce({ tokens: { accessToken: 'abc' } });

        const mod = require('../auth-cognito');

        expect(await mod.isLoggedIn()).toBe(false);
        expect(amplifyAuth.fetchAuthSession).toHaveBeenCalledTimes(1);

        await mod.notifyAuthChange();

        expect(amplifyAuth.fetchAuthSession).toHaveBeenCalledTimes(2);
        expect(await mod.isLoggedIn()).toBe(true);
        expect(amplifyAuth.fetchAuthSession).toHaveBeenCalledTimes(2);
        expect(localStorage.getItem('sc_logged_in')).toBe('1');
    });

    test('isLoggedIn uses local storage fallback when session is empty', async () => {
        const amplifyAuth = require('aws-amplify/auth') as {
            fetchAuthSession: jest.Mock;
        };
        amplifyAuth.fetchAuthSession.mockReset();
        amplifyAuth.fetchAuthSession.mockResolvedValue({ tokens: {} });

        const prefix = 'CognitoIdentityServiceProvider.TEST_CLIENT_ID';
        localStorage.setItem(`${prefix}.LastAuthUser`, 'user');
        localStorage.setItem(`${prefix}.user.accessToken`, 'token');

        const mod = require('../auth-cognito');

        expect(await mod.isLoggedIn()).toBe(true);
        expect(amplifyAuth.fetchAuthSession).toHaveBeenCalledTimes(1);
    });

    test('signOut clears cached state and local flag', async () => {
        const amplifyAuth = require('aws-amplify/auth') as {
            fetchAuthSession: jest.Mock;
            signOut: jest.Mock;
        };
        amplifyAuth.fetchAuthSession.mockReset();
        amplifyAuth.fetchAuthSession
            .mockResolvedValueOnce({ tokens: { accessToken: 'abc' } })
            .mockResolvedValueOnce({ tokens: { accessToken: 'abc' } })
            .mockResolvedValueOnce({ tokens: {} });

        const mod = require('../auth-cognito');

        expect(await mod.isLoggedIn()).toBe(true);
        expect(amplifyAuth.fetchAuthSession).toHaveBeenCalledTimes(1);

        await mod.notifyAuthChange();
        expect(amplifyAuth.fetchAuthSession).toHaveBeenCalledTimes(2);
        expect(localStorage.getItem('sc_logged_in')).toBe('1');

        await mod.signOut();
        expect(amplifyAuth.signOut).toHaveBeenCalledTimes(1);
        expect(amplifyAuth.fetchAuthSession).toHaveBeenCalledTimes(3);
        expect(localStorage.getItem('sc_logged_in')).toBeNull();

        expect(await mod.isLoggedIn()).toBe(false);
        expect(amplifyAuth.fetchAuthSession).toHaveBeenCalledTimes(3);
    });

    test('refreshAuthState performs manual token exchange fallback', async () => {
        jest.useFakeTimers();
        const amplifyAuth = require('aws-amplify/auth') as {
            fetchAuthSession: jest.Mock;
        };
        amplifyAuth.fetchAuthSession.mockReset();
        amplifyAuth.fetchAuthSession
            .mockResolvedValueOnce({ tokens: {} })
            .mockResolvedValueOnce({ tokens: { accessToken: 'manual-access' } })
            .mockResolvedValueOnce({ tokens: { accessToken: 'manual-access' } });

        const originalFetch = global.fetch;
        const fetchMock = jest.fn()
            .mockResolvedValueOnce({
                ok: false,
                status: 400,
                statusText: 'Bad Request',
                clone: () => ({ text: async () => 'error' })
            })
            .mockResolvedValueOnce({
                ok: true,
                status: 200,
                statusText: 'OK',
                json: async () => ({ access_token: 'manual-access', id_token: 'manual-id', refresh_token: 'manual-refresh', username: 'user123' }),
                clone: () => ({ text: async () => '' })
            });
        global.fetch = fetchMock as any;

        const cfg = require('../../config/amplify-config').amplifyConfig;
        const originalRedirects = [...cfg.Auth.Cognito.loginWith.oauth.redirectSignIn];
        cfg.Auth.Cognito.loginWith.oauth.redirectSignIn = [
            'https://fallback.shieldcraft-ai.com/dashboard',
            'https://shieldcraft-ai.com/dashboard'
        ];

        const loc = {
            href: 'https://shieldcraft-ai.com/dashboard?code=abc&state=xyz',
            origin: 'https://shieldcraft-ai.com',
            pathname: '/dashboard',
            search: '?code=abc&state=xyz',
            hash: '',
        };
        Object.defineProperty(window, 'location', { value: loc, writable: true, configurable: true });
        const historySpy = jest.spyOn(window.history, 'replaceState');

        const mod = require('../auth-cognito');

        const refreshPromise = mod.refreshAuthState();
        await jest.advanceTimersByTimeAsync(2100);
        const result = await refreshPromise;

        expect(result).toBe(true);
        expect(fetchMock).toHaveBeenCalledTimes(2);
        const firstCallBody = (fetchMock.mock.calls[0][1].body as URLSearchParams).toString();
        const secondCallBody = (fetchMock.mock.calls[1][1].body as URLSearchParams).toString();
        expect(firstCallBody).toContain('redirect_uri=https%3A%2F%2Fshieldcraft-ai.com%2Fdashboard');
        expect(secondCallBody).toContain('redirect_uri=https%3A%2F%2Ffallback.shieldcraft-ai.com%2Fdashboard');
        expect(historySpy).toHaveBeenCalled();

        const prefix = 'CognitoIdentityServiceProvider.TEST_CLIENT_ID';
        expect(localStorage.getItem(`${prefix}.LastAuthUser`)).toBe('user123');
        expect(localStorage.getItem(`${prefix}.user123.accessToken`)).toBe('manual-access');
        expect(amplifyAuth.fetchAuthSession).toHaveBeenCalledTimes(3);

        historySpy.mockRestore();
        global.fetch = originalFetch;
        cfg.Auth.Cognito.loginWith.oauth.redirectSignIn = originalRedirects;
        jest.useRealTimers();
    });
});
