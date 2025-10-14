// Mock amplify-config before importing the module under test
jest.doMock('../../config/amplify-config', () => ({
    amplifyConfig: {
        Auth: {
            Cognito: {
                userPoolClientId: 'TEST_CLIENT_ID',
                userPoolId: 'us-east-1_TESTPOOL',
                loginWith: {
                    oauth: {
                        domain: 'shieldcraft-auth.auth.us-east-1.amazoncognito.com',
                        redirectSignIn: ['https://example.test/callback', 'https://alt.example/callback']
                    }
                }
            }
        }
    }
}));

// Mock aws-amplify modules
jest.doMock('aws-amplify/auth', () => ({
    fetchAuthSession: jest.fn(),
    signInWithRedirect: jest.fn(),
    getCurrentUser: jest.fn(),
    signOut: jest.fn()
}));

jest.doMock('aws-amplify/utils', () => ({
    Hub: { listen: jest.fn() }
}));

jest.doMock('aws-amplify', () => ({
    Amplify: { configure: jest.fn() }
}));

(function () {
    // Now import the module under test
    const authModule = require('../auth-cognito');
    const awsAuth = require('aws-amplify/auth');

    describe('auth-cognito', () => {
        beforeEach(() => {
            jest.resetAllMocks();
            // ensure clean storage
            try { localStorage.clear(); sessionStorage.clear(); } catch (e) { /* ignore */ }
            // reset location
            // @ts-ignore
            delete window.location;
            // @ts-ignore
            window.location = new URL('http://localhost/');
            window.history.replaceState = jest.fn();
            (window as any).__SC_AUTH_MODE__ = 'minimal';
        });
        afterEach(() => {
            delete (window as any).__SC_AUTH_MODE__;
        });
        test('loginWithProvider constructs correct Hosted UI URL and sets location.href', async () => {
            jest.resetModules();
            const authModule = require('../auth-cognito');
            // Ensure amplify-config mock is used
            const redirect = encodeURIComponent('https://example.test/callback');
            await authModule.loginWithProvider('Google');
            // location.href should be set
            expect(window.location.href).toContain('identity_provider=Google');
            expect(window.location.href).toContain('client_id=TEST_CLIENT_ID');
            expect(window.location.href).toContain(`redirect_uri=${redirect}`);
        });

        test('loginWithProvider selects first redirect if origin unmatched', async () => {
            // @ts-ignore
            window.location = new URL('https://unknown.example/landing');
            window.history.replaceState = jest.fn();
            jest.resetModules();
            const authModule = require('../auth-cognito');
            await authModule.loginWithProvider('Google');
            const expectedRedirect = encodeURIComponent('https://example.test/callback');
            expect(window.location.href).toContain(`redirect_uri=${expectedRedirect}`);
        });

        test('refreshAuthState performs manual token exchange when Amplify does not process callback', async () => {
            jest.setTimeout(15000);

            // Prepare window as OAuth callback
            // @ts-ignore
            window.location = new URL('http://localhost/callback?code=CODE123&state=STATEXYZ');
            sessionStorage.setItem('__sc_oauth_search', '?code=CODE123&state=STATEXYZ');
            sessionStorage.setItem('__sc_oauth_href', 'http://localhost/callback?code=CODE123&state=STATEXYZ');

            jest.resetModules();
            const authModule = require('../auth-cognito');
            const awsAuth = require('aws-amplify/auth');

            // Mock fetchAuthSession to return no tokens initially, but return tokens after manual storage
            const fetchAuthSessionMock = awsAuth.fetchAuthSession;
            fetchAuthSessionMock.mockImplementation(() => {
                const last = localStorage.getItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.LastAuthUser');
                if (last) {
                    return Promise.resolve({ tokens: { accessToken: 'AT' } });
                }
                return Promise.resolve({ tokens: {} });
            });

            // Mock fetch to simulate token endpoint returning tokens
            (global as any).fetch = jest.fn().mockImplementation((input: any, init: any) => {
                return Promise.resolve({
                    ok: true,
                    status: 200,
                    statusText: 'OK',
                    json: async () => ({ access_token: 'AT', id_token: 'IDT', username: 'tester', refresh_token: 'RT' }),
                    clone() { return this; },
                    text: async () => '{"access_token":"AT"}'
                } as any);
            });

            // Call refreshAuthState (it contains timers/delays) and await the real timers
            const result = await authModule.refreshAuthState();
            expect(result).toBe(true);

            // Check that localStorage was written with Amplify-compatible keys
            const tokenKey = `CognitoIdentityServiceProvider.TEST_CLIENT_ID.LastAuthUser`;
            expect(localStorage.getItem(tokenKey)).toBe('tester');
            const userKeyPrefix = `CognitoIdentityServiceProvider.TEST_CLIENT_ID.tester`;
            expect(localStorage.getItem(`${userKeyPrefix}.accessToken`)).toBe('AT');
            expect(localStorage.getItem(`${userKeyPrefix}.idToken`)).toBe('IDT');
            expect(localStorage.getItem(`${userKeyPrefix}.refreshToken`)).toBe('RT');

            expect(sessionStorage.getItem('__sc_oauth_search')).toBeNull();

            try { (global as any).fetch = undefined; } catch { /* ignore */ }
        }, 15000);
    });
})();
