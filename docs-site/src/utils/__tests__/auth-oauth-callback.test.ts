const TOKEN_ENDPOINT = 'https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/token';

function buildResponse(overrides: Partial<Response> & { json?: () => Promise<any>; text?: () => Promise<string> }): any {
    const base: Partial<Response> = {
        ok: true,
        status: 200,
        statusText: 'OK',
    };
    const response = { ...base, ...overrides } as Response;
    if (!response.clone) {
        response.clone = () => ({ text: overrides.text || (async () => '') } as any);
    }
    if (!response.text) {
        response.text = async () => '';
    }
    if (!response.json) {
        response.json = async () => ({}) as any;
    }
    return response;
}

describe('OAuth callback handling', () => {
    let originalFetch: typeof global.fetch | undefined;

    beforeEach(() => {
        jest.resetModules();
        // Use real timers to avoid flakiness with nested async + fake timers
        jest.useRealTimers();
        originalFetch = global.fetch;
        (global.fetch as any) = jest.fn();
        localStorage.clear();
        sessionStorage.clear();
        document.cookie = '';
        window.history.replaceState = jest.fn();
        (window as any).__SC_AUTH_MODE__ = 'minimal';

        const locationMock: Location = {
            href: 'https://shieldcraft-ai.com/',
            origin: 'https://shieldcraft-ai.com',
            pathname: '/',
            search: '',
            hash: '',
            assign: jest.fn(),
            reload: jest.fn(),
            replace: jest.fn(),
            ancestorOrigins: ({} as any),
            host: 'shieldcraft-ai.com',
            hostname: 'shieldcraft-ai.com',
            port: '',
            protocol: 'https:',
        };
        Object.defineProperty(window, 'location', { value: locationMock, writable: true });
    });

    afterEach(() => {
        // ensure timers restored
        jest.useRealTimers();
        if (originalFetch) {
            global.fetch = originalFetch;
        }
        delete (window as any).__SC_AUTH_MODE__;
    });

    test('performs manual token exchange when session lacks tokens', async () => {
        jest.doMock('../../config/amplify-config', () => ({
            amplifyConfig: {
                Auth: {
                    Cognito: {
                        userPoolClientId: 'TEST_CLIENT_ID',
                        userPoolId: 'us-east-1_TEST',
                        loginWith: {
                            oauth: {
                                domain: 'shieldcraft-auth.auth.us-east-1.amazoncognito.com',
                                redirectSignIn: [
                                    'https://shieldcraft-ai.com/dashboard',
                                    'http://localhost:3000/auth/callback',
                                ],
                            },
                        },
                    },
                },
            },
        }));

        const fetchAuthSession = jest
            .fn()
            .mockResolvedValueOnce({ tokens: {} })
            .mockResolvedValueOnce({ tokens: { accessToken: 'ACCESS', idToken: 'ID' } });

        jest.doMock('aws-amplify/auth', () => ({
            fetchAuthSession,
            signInWithRedirect: jest.fn(),
            getCurrentUser: jest.fn(),
            signOut: jest.fn(),
        }));

        const hubListen = jest.fn();
        jest.doMock('aws-amplify', () => ({
            Amplify: { configure: jest.fn() },
            Hub: { listen: hubListen },
        }));

        await jest.isolateModulesAsync(async () => {
            const mod = await import('../auth-cognito');
            const fetchMock = global.fetch as jest.Mock;
            fetchMock
                .mockResolvedValueOnce(
                    buildResponse({ ok: false, status: 400, statusText: 'Bad Request', text: async () => 'error' })
                )
                .mockResolvedValueOnce(
                    buildResponse({
                        json: async () => ({
                            access_token: 'access-token',
                            id_token: 'id-token',
                            refresh_token: 'refresh-token',
                            username: 'mock-user',
                        }),
                        text: async () => '{}',
                    })
                );

            const loc = window.location as Location;
            loc.href = 'https://shieldcraft-ai.com/auth/callback?code=abc123&state=xyz';
            loc.pathname = '/auth/callback';
            loc.search = '?code=abc123&state=xyz';

            const refreshPromise = mod.refreshAuthState();
            // Wait a short amount to let the code perform its async token exchange attempts
            await new Promise(res => setTimeout(res, 2600));
            const result = await refreshPromise;

            expect(result).toBe(true);
            expect(fetchMock).toHaveBeenCalledTimes(2);
            expect(fetchMock).toHaveBeenNthCalledWith(1, TOKEN_ENDPOINT, expect.any(Object));
            expect(fetchMock).toHaveBeenNthCalledWith(2, TOKEN_ENDPOINT, expect.any(Object));
            expect(fetchAuthSession).toHaveBeenCalledTimes(2);

            const firstCall = fetchMock.mock.calls[0][1] as any;
            const firstBody = firstCall?.body instanceof URLSearchParams ? firstCall.body.toString() : String(firstCall?.body);
            expect(firstBody).toContain('redirect_uri=https%3A%2F%2Fshieldcraft-ai.com%2Fauth%2Fcallback');

            const secondCall = fetchMock.mock.calls[1][1] as any;
            const secondBody = secondCall?.body instanceof URLSearchParams ? secondCall.body.toString() : String(secondCall?.body);
            expect(secondBody).toContain('redirect_uri=https%3A%2F%2Fshieldcraft-ai.com%2Fdashboard');

            const prefix = 'CognitoIdentityServiceProvider.TEST_CLIENT_ID';
            expect(localStorage.getItem(`${prefix}.LastAuthUser`)).toBe('mock-user');
            expect(localStorage.getItem(`${prefix}.mock-user.accessToken`)).toBe('access-token');
            expect(localStorage.getItem(`${prefix}.mock-user.idToken`)).toBe('id-token');
            expect(localStorage.getItem('sc_logged_in')).toBe('1');

            expect(window.history.replaceState).toHaveBeenCalledWith({}, document.title, 'https://shieldcraft-ai.com/auth/callback');
        });
    });
});
