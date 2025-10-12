jest.doMock('../../config/amplify-config', () => ({
    amplifyConfig: { Auth: { Cognito: { userPoolClientId: 'TEST_CLIENT_ID', loginWith: { oauth: { redirectSignIn: ['https://example.test/callback'] } } } } }
}));

jest.doMock('aws-amplify/auth', () => ({ fetchAuthSession: jest.fn(), signInWithRedirect: jest.fn(), getCurrentUser: jest.fn(), signOut: jest.fn() }));
jest.doMock('aws-amplify/utils', () => ({ Hub: { listen: jest.fn() } }));
jest.doMock('aws-amplify', () => ({ Amplify: { configure: jest.fn() } }));

describe('scClearAuthDebug global helper', () => {
    beforeEach(() => {
        jest.resetModules();
        try { localStorage.clear(); sessionStorage.clear(); document.cookie = ''; } catch { }
    });

    test('scClearAuthDebug exists and clears debug keys', () => {
        require('../auth-cognito');
        // ensure a debug key exists
        try { localStorage.setItem('sc_debug_oauth', JSON.stringify({ a: 1 })); } catch { }
        const fn = (global as any).scClearAuthDebug || (window as any).scClearAuthDebug;
        expect(typeof fn).toBe('function');
        const res = fn();
        expect(res).toBe(true);
        expect(localStorage.getItem('sc_debug_oauth')).toBeNull();
    });
});
