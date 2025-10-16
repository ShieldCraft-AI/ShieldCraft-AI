// Mock amplify-config before importing the module under test
const defaultConfig = {
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
};

const createAuthMock = () => ({
    fetchAuthSession: jest.fn().mockResolvedValue({ tokens: {} }),
    signInWithRedirect: jest.fn().mockResolvedValue(undefined),
    getCurrentUser: jest.fn(),
    signOut: jest.fn()
});

const setWindowLocation = (href: string) => {
    const url = new URL(href);
    (window as any).location = {
        href: url.href,
        origin: url.origin,
        pathname: url.pathname,
        search: url.search,
        hash: url.hash,
        assign: jest.fn(),
        replace: jest.fn(),
        reload: jest.fn()
    } as unknown as Location;
};

describe('auth-cognito', () => {
    let authModule: typeof import('../auth-cognito');
    let awsAuth: ReturnType<typeof createAuthMock>;

    const loadModule = () => {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        authModule = require('../auth-cognito');
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        awsAuth = require('aws-amplify/auth');
    };

    beforeEach(() => {
        jest.resetModules();
        jest.clearAllMocks();
        jest.doMock('../../config/amplify-config', () => defaultConfig);
        jest.doMock('aws-amplify/auth', () => createAuthMock());
        jest.doMock('aws-amplify/utils', () => ({ Hub: { listen: jest.fn() } }));
        jest.doMock('aws-amplify', () => ({
            Amplify: {
                configure: jest.fn(),
                getConfig: jest.fn().mockReturnValue(defaultConfig.amplifyConfig)
            }
        }));

        delete (window as any).location;
        setWindowLocation('http://localhost/');
        window.history.replaceState = jest.fn();
        localStorage.clear();
        sessionStorage.clear();
        (window as any).__SC_AUTH_MODE__ = 'minimal';

        loadModule();
    });

    afterEach(() => {
        delete (window as any).__SC_AUTH_MODE__;
        delete (window as any).__SC_AUTH_RELOADED__;
        try { delete (global as any).fetch; } catch { /* noop */ }
    });

    test('loginWithProvider uses signInWithRedirect when available', async () => {
        await authModule.loginWithProvider('Google');
        expect(awsAuth.signInWithRedirect).toHaveBeenCalledTimes(1);
        expect(awsAuth.signInWithRedirect).toHaveBeenCalledWith({ provider: 'Google' });
    });

    test('loginWithProvider falls back to Hosted UI URL when redirect helper missing', async () => {
        (awsAuth as any).signInWithRedirect = undefined;
        await authModule.loginWithProvider('Google');
        expect(window.location.href).toContain('identity_provider=Google');
        expect(window.location.href).toContain('client_id=TEST_CLIENT_ID');
        expect(window.location.href).toContain('redirect_uri=https%3A%2F%2Fexample.test%2Fcallback');
    });

    test('loginWithProvider falls back to Hosted UI when modular redirect throws', async () => {
        awsAuth.signInWithRedirect.mockRejectedValue(new Error('modular-failure'));
        await authModule.loginWithProvider('Google');
        expect(window.location.href).toContain('identity_provider=Google');
        expect(window.location.href).toContain('redirect_uri=https%3A%2F%2Fexample.test%2Fcallback');
    });

    test('loginWithProvider selects first redirect if origin unmatched', async () => {
        (awsAuth as any).signInWithRedirect = undefined;
        setWindowLocation('https://unknown.example/landing');
        await authModule.loginWithProvider('Google');
        expect(window.location.href).toContain('redirect_uri=https%3A%2F%2Fexample.test%2Fcallback');
    });

    test('onAuthChange listens to custom window event fallback', () => {
        const handler = jest.fn();
        const unsubscribe = authModule.onAuthChange(handler);
        const detailTrue = { authenticated: true };
        const detailFalse = { authenticated: false };
        window.dispatchEvent(new CustomEvent('sc-auth-change', { detail: detailTrue }));
        window.dispatchEvent(new CustomEvent('sc-auth-change', { detail: detailFalse }));
        expect(handler).toHaveBeenCalledWith(true);
        expect(handler).toHaveBeenCalledWith(false);
        unsubscribe();
    });

    test('isLoggedIn returns true when modular getCurrentUser resolves', async () => {
        awsAuth.getCurrentUser.mockResolvedValue({ username: 'tester' });
        const result = await authModule.isLoggedIn();
        expect(result).toBe(true);
        expect(awsAuth.getCurrentUser).toHaveBeenCalledTimes(1);
    });

    test('isLoggedIn returns false when modular getCurrentUser rejects', async () => {
        awsAuth.getCurrentUser.mockRejectedValue(new Error('no user'));
        const result = await authModule.isLoggedIn();
        expect(result).toBe(false);
        expect(awsAuth.getCurrentUser).toHaveBeenCalledTimes(1);
    });

    test('isLoggedIn derives true from stored tokens when auth modules unavailable', async () => {
        jest.doMock('aws-amplify/auth', () => ({
            fetchAuthSession: jest.fn().mockResolvedValue({ tokens: {} }),
            signInWithRedirect: jest.fn().mockResolvedValue(undefined),
            getCurrentUser: jest.fn().mockRejectedValue(new Error('no user')),
            signOut: jest.fn()
        }));
        jest.doMock('aws-amplify', () => ({ Amplify: { configure: jest.fn(), getConfig: jest.fn().mockReturnValue(defaultConfig.amplifyConfig) } }));
        jest.doMock('aws-amplify/utils', () => ({ Hub: { listen: jest.fn() } }));
        localStorage.setItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.LastAuthUser', 'tester');
        localStorage.setItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.tester.accessToken', 'AT');
        localStorage.setItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.tester.idToken', 'eyJhbGciOiAiSFMyNTYifQ.eyJuYW1lIjogIkpvaG4gRG9lIiwgImVtYWlsIjogInRlc3RAZXhhbXBsZS5jb20iLCAic3ViIjogInVzZXItMTIzIn0.signature');
        jest.resetModules();
        const module = require('../auth-cognito');
        const result = await module.isLoggedIn();
        expect(result).toBe(true);
    });

    test('getCurrentUser falls back to stored id token payload', async () => {
        awsAuth.getCurrentUser.mockRejectedValue(new Error('missing user'));
        localStorage.setItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.LastAuthUser', 'tester');
        localStorage.setItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.tester.accessToken', 'AT');
        localStorage.setItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.tester.idToken', 'eyJhbGciOiAiSFMyNTYifQ.eyJuYW1lIjogIkpvaG4gRG9lIiwgImVtYWlsIjogInRlc3RAZXhhbXBsZS5jb20iLCAic3ViIjogInVzZXItMTIzIn0.signature');
        const user = await authModule.getCurrentUser();
        expect(user?.name).toBe('John Doe');
        expect(user?.email).toBe('test@example.com');
        expect(user?.sub).toBe('user-123');
    });

    test('notifyAuthChange dispatches fallback window event when Hub dispatch missing', async () => {
        const listener = jest.fn();
        const fn = (event: Event) => {
            const detail = (event as CustomEvent<{ authenticated: boolean }>).detail;
            listener(detail.authenticated);
        };
        window.addEventListener('sc-auth-change', fn as EventListener);
        awsAuth.getCurrentUser.mockRejectedValue(new Error('no user'));
        localStorage.setItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.LastAuthUser', 'tester');
        localStorage.setItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.tester.accessToken', 'AT');
        localStorage.setItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.tester.idToken', 'eyJhbGciOiAiSFMyNTYifQ.eyJuYW1lIjogIkpvaG4gRG9lIiwgImVtYWlsIjogInRlc3RAZXhhbXBsZS5jb20iLCAic3ViIjogInVzZXItMTIzIn0.signature');
        await authModule.notifyAuthChange();
        expect(listener).toHaveBeenCalledWith(true);
        window.removeEventListener('sc-auth-change', fn as EventListener);
    });

    test('signOutUser invokes modular signOut when available', async () => {
        awsAuth.signOut.mockResolvedValue(undefined);
        await authModule.signOutUser();
        expect(awsAuth.signOut).toHaveBeenCalledTimes(1);
    });

    test('refreshAuthState returns true when fetchAuthSession already has tokens', async () => {
        awsAuth.fetchAuthSession.mockResolvedValue({ tokens: { accessToken: 'AT', idToken: 'IDT' } });
        const result = await authModule.refreshAuthState();
        expect(result).toBe(true);
        expect(awsAuth.fetchAuthSession).toHaveBeenCalledTimes(1);
        expect((global as any).fetch).toBeUndefined();
    });

    test('refreshAuthState performs manual token exchange when Amplify does not process callback', async () => {
        jest.setTimeout(15000);

        awsAuth.fetchAuthSession.mockImplementation(() => {
            const last = localStorage.getItem('CognitoIdentityServiceProvider.TEST_CLIENT_ID.LastAuthUser');
            if (last) {
                return Promise.resolve({ tokens: { accessToken: 'AT' } });
            }
            return Promise.resolve({ tokens: {} });
        });

        setWindowLocation('http://localhost/callback?code=CODE123&state=STATEXYZ');
        sessionStorage.setItem('__sc_oauth_search', '?code=CODE123&state=STATEXYZ');
        sessionStorage.setItem('__sc_oauth_href', 'http://localhost/callback?code=CODE123&state=STATEXYZ');

        (global as any).fetch = jest.fn().mockResolvedValue({
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({ access_token: 'AT', id_token: 'IDT', username: 'tester', refresh_token: 'RT' })
        });

        const result = await authModule.refreshAuthState();
        expect(result).toBe(true);

        const tokenKey = 'CognitoIdentityServiceProvider.TEST_CLIENT_ID.LastAuthUser';
        expect(localStorage.getItem(tokenKey)).toBe('tester');
        const userKeyPrefix = 'CognitoIdentityServiceProvider.TEST_CLIENT_ID.tester';
        expect(localStorage.getItem(`${userKeyPrefix}.accessToken`)).toBe('AT');
        expect(localStorage.getItem(`${userKeyPrefix}.idToken`)).toBe('IDT');
        expect(localStorage.getItem(`${userKeyPrefix}.refreshToken`)).toBe('RT');
        expect(sessionStorage.getItem('__sc_oauth_search')).toBeNull();
        expect(awsAuth.fetchAuthSession).toHaveBeenCalled();
        expect((global as any).fetch).toHaveBeenCalledTimes(1);
    });
});
