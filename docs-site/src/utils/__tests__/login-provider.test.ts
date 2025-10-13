
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
                            'https://prod.shieldcraft-ai.com/dashboard',
                            'http://localhost:3000/auth/callback',
                        ],
                    },
                },
            },
        },
    },
}));

jest.doMock('aws-amplify/auth', () => ({
    fetchAuthSession: jest.fn().mockResolvedValue({ tokens: {} }),
    signInWithRedirect: jest.fn().mockResolvedValue(undefined),
    getCurrentUser: jest.fn(),
    signOut: jest.fn(),
}));

describe('loginWithProvider URL builder', () => {
    beforeEach(() => {
        jest.resetModules();
        // make window.location writable
        const loc = { href: 'https://initial/', origin: 'https://example.test', pathname: '/', search: '', assign: jest.fn() };
        Object.defineProperty(window, 'location', { value: loc, writable: true });
    });

    test('sets window.location.href with google provider', () => {
        const mod = require('../auth-cognito');
        mod.loginWithProvider('Google');
        expect(window.location.href).toContain('identity_provider=Google');
        expect(window.location.href).toContain('response_type=code');
        expect(window.location.href).toContain('redirect_uri=https%3A%2F%2Fprod.shieldcraft-ai.com%2Fdashboard');
    });

    test('sets window.location.href with Amazon provider', () => {
        const mod = require('../auth-cognito');
        mod.loginWithProvider('LoginWithAmazon');
        expect(window.location.href).toContain('identity_provider=LoginWithAmazon');
        expect(window.location.href).toContain('redirect_uri=https%3A%2F%2Fprod.shieldcraft-ai.com%2Fdashboard');
    });

    test('loginWithGoogle delegates to Amplify redirect', async () => {
        const amplifyAuth = require('aws-amplify/auth');
        const mod = require('../auth-cognito');
        await mod.loginWithGoogle();
        expect(amplifyAuth.signInWithRedirect).toHaveBeenCalledWith({ provider: 'Google' });
    });

    test('loginWithAmazon uses custom provider', async () => {
        const amplifyAuth = require('aws-amplify/auth');
        const mod = require('../auth-cognito');
        await mod.loginWithAmazon();
        expect(amplifyAuth.signInWithRedirect).toHaveBeenCalledWith({ provider: { custom: 'LoginWithAmazon' } });
    });
});
