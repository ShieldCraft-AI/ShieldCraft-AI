/* eslint-env jest */

describe('minimal-idp refresh token flow', () => {
    beforeEach(() => {
        jest.resetModules();
        localStorage.clear();
        sessionStorage.clear();
        document.cookie = '';
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
    });

    test('refreshWithRefreshToken succeeds and persists new tokens', async () => {
        const mod = require('../minimal-idp');
        mod.init({ domain: 'idp.example.com', clientId: 'C123', redirectUris: ['https://app.example.com/dashboard'] });
        // initial tokens with refreshToken
        localStorage.setItem('sc_auth.tokens', JSON.stringify({ refreshToken: 'r1', username: 'u1' }));

        const fetchMock = jest.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({ access_token: 'A2', id_token: 'I2', expires_in: 3600 }) });
        (global as any).fetch = fetchMock;

        const ok = await mod.refreshWithRefreshToken();
        expect(ok).toBe(true);
        const stored = JSON.parse(localStorage.getItem('sc_auth.tokens') || 'null');
        expect(stored.accessToken).toBe('A2');
        expect(stored.idToken).toBe('I2');
        expect(stored.expiresAt).toBeTruthy();
    });

    test('refreshWithRefreshToken fails gracefully when endpoint returns error', async () => {
        const mod = require('../minimal-idp');
        mod.init({ domain: 'idp.example.com', clientId: 'C123', redirectUris: ['https://app.example.com/dashboard'] });
        localStorage.setItem('sc_auth.tokens', JSON.stringify({ refreshToken: 'r1' }));
        const fetchMock = jest.fn().mockResolvedValue({ ok: false, status: 400 });
        (global as any).fetch = fetchMock;
        const ok = await mod.refreshWithRefreshToken();
        expect(ok).toBe(false);
    });
});
