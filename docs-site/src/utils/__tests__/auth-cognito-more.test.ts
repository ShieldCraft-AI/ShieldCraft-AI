// Mock amplify-config before importing the module under test so client id is set
jest.doMock('../../config/amplify-config', () => ({
    amplifyConfig: {
        Auth: {
            Cognito: {
                userPoolClientId: 'TEST_CLIENT_ID',
                userPoolId: 'us-east-1_TESTPOOL',
                loginWith: { oauth: { redirectSignIn: ['https://example.test/callback'] } }
            }
        }
    }
}));

// Ensure mocks for aws-amplify are set up before requiring the module
jest.doMock('aws-amplify/auth', () => ({ fetchAuthSession: jest.fn(), signInWithRedirect: jest.fn(), getCurrentUser: jest.fn(), signOut: jest.fn() }));
jest.doMock('aws-amplify/utils', () => ({ Hub: { listen: jest.fn() } }));
jest.doMock('aws-amplify', () => ({ Amplify: { configure: jest.fn() } }));

(function () {
    const authModule = require('../auth-cognito');

    describe('auth-cognito fallback behaviors', () => {
        const ORIGINAL_LOCATION = window.location

        beforeEach(() => {
            // Ensure a writable location object in jsdom by redefining href
            const loc = new URL('https://example.com/oauth2/idpresponse?code=TEST_CODE&state=STATE')
            Object.defineProperty(window, 'location', {
                configurable: true,
                enumerable: true,
                writable: true,
                value: loc,
            })
        })

        afterEach(() => {
            // Restore original location
            Object.defineProperty(window, 'location', {
                configurable: true,
                enumerable: true,
                writable: true,
                value: ORIGINAL_LOCATION,
            })
            jest.resetAllMocks()
            localStorage.clear()
            sessionStorage.clear()
        })

        test('refreshAuthState falls back to manual token exchange and retries with configured redirectSignIn', async () => {
            jest.setTimeout(15000);
            jest.resetModules();

            // Mock amplify-config for this test so the module import picks up CLIENT_ID
            jest.doMock('../../config/amplify-config', () => ({
                amplifyConfig: {
                    Auth: {
                        Cognito: {
                            userPoolClientId: 'CLIENT_ID',
                            userPoolId: 'us-east-1_TESTPOOL',
                            loginWith: { oauth: { redirectSignIn: ['https://redirect.example.com/callback'] } }
                        }
                    }
                }
            }));

            // Re-require the module so it picks up the mocked amplify-config at module-init
            const reAuthModule = require('../auth-cognito');

            // Mock Amplify behavior: make aws-amplify/auth.fetchAuthSession return tokens only after localStorage has LastAuthUser
            const awsAuth = require('aws-amplify/auth');
            const fetchAuthSessionSpy = jest.spyOn(awsAuth, 'fetchAuthSession').mockImplementation(() => {
                const last = localStorage.getItem('CognitoIdentityServiceProvider.CLIENT_ID.LastAuthUser');
                if (last) {
                    return Promise.resolve({ tokens: { accessToken: 'AT', idToken: 'ID' } });
                }
                return Promise.resolve({ tokens: {} });
            });

            // First fetch to token endpoint returns 400 -> triggers retry
            let fetchCallCount: number = 0;
            // Provide a global fetch implementation (jsdom may not provide fetch)
            ; (global as any).fetch = jest.fn().mockImplementation(() => {
                fetchCallCount += 1;
                if (fetchCallCount === 1) {
                    return Promise.resolve({ ok: false, status: 400, text: async () => 'bad' });
                }
                // Second call succeeds with token response (include username so storage keys are set)
                return Promise.resolve({ ok: true, status: 200, json: async () => ({ access_token: 'AT', id_token: 'ID', refresh_token: 'RT', expires_in: 3600, username: 'retryuser' }) });
            }) as unknown as typeof global.fetch;

            // Spy on setItem to validate storage writes (more reliable across environments)
            const setSpy = jest.spyOn(Storage.prototype, 'setItem');
            try {
                const result = await (reAuthModule as any).refreshAuthState();
                expect(result).toBeTruthy();

                // Ensure fetch was called at least twice (retry path)
                expect(fetchCallCount).toBeGreaterThanOrEqual(2);

                const calls = setSpy.mock.calls as Array<[string, string]>;
                const lastAuthCall = calls.find(c => c[0].endsWith('.LastAuthUser'));
                expect(lastAuthCall).toBeDefined();
                expect(lastAuthCall![1]).toBe('retryuser');
                const tokenCall = calls.find(c => c[0].includes('.accessToken') || c[0].includes('.idToken') || c[0].includes('.refreshToken'));
                expect(tokenCall).toBeDefined();
            } finally {
                fetchAuthSessionSpy.mockRestore();
                setSpy.mockRestore();
                jest.useRealTimers();
            }
        })
    })
})();
