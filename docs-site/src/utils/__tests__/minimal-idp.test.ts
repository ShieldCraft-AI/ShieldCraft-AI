/* eslint-env jest */

import * as path from 'path';

// We'll import the module under test inside isolateModules to control globals

describe('minimal-idp module', () => {
    beforeEach(() => {
        jest.resetModules();
        localStorage.clear();
        sessionStorage.clear();
        document.cookie = '';
        // Provide a default window.location usable by the module
        const locationMock: any = {
            href: 'https://app.example.com/dashboard',
            origin: 'https://app.example.com',
            pathname: '/dashboard',
            search: '',
            hash: '',
            assign: jest.fn(),
            reload: jest.fn(),
            replace: jest.fn(),
        };
        Object.defineProperty(window, 'location', { value: locationMock, writable: true, configurable: true });
        // ensure history.replaceState exists (used in cleanup)
        if (!window.history.replaceState) window.history.replaceState = jest.fn() as any;
    });

    test('init + getConfig returns config', () => {
        const mod = require('../minimal-idp');
        expect(mod.getConfig()).toBeNull();
        mod.init({ domain: 'example.com', clientId: 'cid', redirectUris: ['https://app.example.com/dashboard'] });
        const cfg = mod.getConfig();
        expect(cfg).toBeTruthy();
        expect(cfg.domain).toBe('example.com');
    });

    test('login builds hosted-ui URL and sets location.href', () => {
        const mod = require('../minimal-idp');
        mod.init({ domain: 'idp.example.com', clientId: 'C123', redirectUris: ['https://app.example.com/dashboard'] });
        // capture original href
        const before = (window.location as any).href;
        // Call login
        mod.login('Google');
        // Expect location.href was set to a hosted UI url
        const after = (window.location as any).href;
        expect(typeof after).toBe('string');
        expect(after).not.toBe(before);
        expect(after).toMatch(/https:\/\/idp.example.com\/oauth2\/authorize/);
        expect(after).toContain('identity_provider=Google');
        expect(after).toContain('client_id=C123');
    });

    test('handleRedirectCallback attempts token exchange against current origin then configured redirectUris', async () => {
        const mod = require('../minimal-idp');
        mod.init({ domain: 'idp.example.com', clientId: 'C123', redirectUris: ['https://fallback.example.com/cb', 'https://app.example.com/dashboard'] });

        const fetchMock = jest.fn()
            .mockResolvedValueOnce({ ok: false, status: 400, statusText: 'Bad' })
            .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ access_token: 'a', id_token: 'i', refresh_token: 'r', username: 'u' }) });
        (global as any).fetch = fetchMock;

        // Set location to a callback URL so first candidate is origin+pathname
        const loc = window.location as any;
        loc.href = 'https://app.example.com/auth/cb?code=xyz';
        loc.pathname = '/auth/cb';
        loc.search = '?code=xyz';

        const res = await mod.handleRedirectCallback();
        expect(res.success).toBe(true);
        expect(res.tokens).toBeTruthy();
        expect(fetchMock).toHaveBeenCalledTimes(2);

        // tokens persisted
        const stored = JSON.parse(localStorage.getItem('sc_auth.tokens') || 'null');
        expect(stored.accessToken).toBe('a');
        expect(localStorage.getItem('sc_logged_in')).toBe('1');
    });

    test('isLoggedIn/getTokens reflect persisted state and signOut clears it', async () => {
        const mod = require('../minimal-idp');
        mod.init({ domain: 'idp.example.com', clientId: 'C123', redirectUris: ['https://app.example.com/dashboard'] });
        // Manually persist
        localStorage.setItem('sc_auth.tokens', JSON.stringify({ accessToken: 'A', idToken: 'I', username: 'u' }));
        expect(mod.isLoggedIn()).toBe(true);
        const tokens = mod.getTokens();
        expect(tokens?.accessToken).toBe('A');
        await mod.signOut();
        expect(mod.isLoggedIn()).toBe(false);
        expect(localStorage.getItem('sc_auth.tokens')).toBeNull();
    });

    test('onAuthChange notifies listeners immediately and on changes', async () => {
        const mod = require('../minimal-idp');
        mod.init({ domain: 'idp.example.com', clientId: 'C123', redirectUris: ['https://app.example.com/dashboard'] });
        const cb = jest.fn();
        const off = mod.onAuthChange(cb);
        // initial call executed synchronously
        expect(cb).toHaveBeenCalled();
        cb.mockClear();
        // simulate login
        localStorage.setItem('sc_auth.tokens', JSON.stringify({ accessToken: 'ax' }));
        mod.notifyAuthChange();
        expect(cb).toHaveBeenCalledWith(true);
        cb.mockClear();
        // simulate logout
        localStorage.removeItem('sc_auth.tokens');
        mod.notifyAuthChange();
        expect(cb).toHaveBeenCalledWith(false);
        off();
    });

    test('handleRedirectCallback returns error when no code present', async () => {
        const mod = require('../minimal-idp');
        mod.init({ domain: 'idp.example.com', clientId: 'C123', redirectUris: ['https://app.example.com/dashboard'] });
        const loc = window.location as any;
        loc.href = 'https://app.example.com/';
        loc.pathname = '/';
        loc.search = '';
        const res = await mod.handleRedirectCallback();
        expect(res.success).toBe(false);
        expect(res.error).toBe('no-code');
    });
});
