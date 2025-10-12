describe('Amplify Hub auth bridge', () => {
    beforeEach(() => {
        jest.resetModules();
        jest.useFakeTimers();
        localStorage.clear();
        sessionStorage.clear();
        document.cookie = '';

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
        jest.useRealTimers();
    });

    test('Hub auth event triggers notifyAuthChange', async () => {
        jest.doMock('../../config/amplify-config', () => ({
            amplifyConfig: {
                Auth: {
                    Cognito: {
                        userPoolClientId: 'TEST_CLIENT_ID',
                        userPoolId: 'us-east-1_TEST',
                        loginWith: {
                            oauth: {
                                redirectSignIn: ['https://shieldcraft-ai.com/dashboard'],
                            },
                        },
                    },
                },
            },
        }));

        const fetchAuthSession = jest.fn().mockResolvedValue({ tokens: { accessToken: 'ACCESS', idToken: 'ID' } });
        jest.doMock('aws-amplify/auth', () => ({
            fetchAuthSession,
            signInWithRedirect: jest.fn(),
            getCurrentUser: jest.fn(),
            signOut: jest.fn(),
        }));

        const hubCallbacks: Array<(payload: any) => Promise<void>> = [];
        jest.doMock('aws-amplify', () => ({
            Amplify: { configure: jest.fn() },
            Hub: {
                listen: (_channel: string, cb: (input: any) => Promise<void>) => {
                    hubCallbacks.push(cb);
                    return cb;
                },
            },
        }));

        await jest.isolateModulesAsync(async () => {
            await import('../auth-cognito');
            expect(hubCallbacks).toHaveLength(1);

            const cb = hubCallbacks[0];
            await cb({ payload: { event: 'signedIn' } });

            expect(fetchAuthSession).toHaveBeenCalled();
            expect(localStorage.getItem('sc_logged_in')).toBe('1');
        });
    });
});
