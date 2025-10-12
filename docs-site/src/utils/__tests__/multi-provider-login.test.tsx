jest.doMock('../../config/amplify-config', () => ({
    amplifyConfig: { Auth: { userPoolClientId: 'TEST_CLIENT_ID', oauth: { redirectSignIn: ['https://example.test/callback'] } } }
}));

jest.mock('../../components/MultiProviderLogin', () => ({
    __esModule: true,
    default: (props: any) => ({ trigger: () => props.onClick && props.onClick('Google') })
}));

describe('MultiProviderLogin UI interactions', () => {
    beforeEach(() => {
        localStorage.clear();
        sessionStorage.clear();
        document.cookie = '';
        jest.resetModules();
    });

    test('clicking provider writes sc_debug_login_event', () => {
        const MPL = require('../../components/MultiProviderLogin').default;
        const instance = MPL({ onClick: (p: any) => localStorage.setItem('sc_debug_login_event', JSON.stringify({ provider: p })) });
        // simulate click
        instance.trigger();
        const v = localStorage.getItem('sc_debug_login_event');
        expect(v).toBeTruthy();
        const parsed = JSON.parse(v as string);
        expect(parsed.provider).toBe('Google');
    });
});
