const path = require('path');

// Ensure we mock amplify-config before importing the module
const configPath = path.resolve(__dirname, '../../config/amplify-config');
jest.doMock(configPath, () => ({
    amplifyConfig: { Auth: { Cognito: { userPoolClientId: 'HAPPY_CLIENT_ID', loginWith: { oauth: { redirectSignIn: ['https://happy.test/callback'] } } } } }
}));

jest.doMock('aws-amplify/auth', () => ({
    fetchAuthSession: jest.fn().mockResolvedValue({ tokens: { accessToken: 'AT' } }),
    signInWithRedirect: jest.fn(),
    getCurrentUser: jest.fn(),
    signOut: jest.fn()
}));

jest.doMock('aws-amplify/utils', () => ({ Hub: { listen: jest.fn() } }));
jest.doMock('aws-amplify', () => ({ Amplify: { configure: jest.fn() } }));

(function () {
    const authModule = require('../auth-cognito');

    describe('auth-cognito happy path', () => {
        beforeEach(() => {
            jest.resetAllMocks();
            try { localStorage.clear(); sessionStorage.clear(); } catch (e) { }
            // set a safe writable location
            const loc = new URL('https://happy.test/callback?code=CODEHAPPY&state=S');
            Object.defineProperty(window, 'location', { configurable: true, writable: true, value: loc });
        });

        test('isLoggedIn returns true when Amplify has a session', async () => {
            jest.resetModules();
            const authModule = require('../auth-cognito');
            // aws-amplify/auth.fetchAuthSession is mocked above to resolve with tokens
            const res = await authModule.isLoggedIn();
            expect(res).toBe(true);
        });
    });
})();
