import { loginWithProvider, refreshAuthState } from '../docs-site/src/utils/auth-cognito';

// Simple tests to validate Hosted UI URL construction and manual token exchange flow.

describe('auth-cognito', () => {
    beforeEach(() => {
        // Clear storage
        try { localStorage.clear(); } catch { }
        try { sessionStorage.clear(); } catch { }
        // reset window.location
        try { delete (window as any).location; } catch { }
        (window as any).location = {
            href: 'https://example.com/',
            origin: 'https://example.com',
            pathname: '/',
            search: '',
            hostname: 'example.com',
            replace: (s: string) => { (window as any).location.href = s; }
        } as any;
    });

    test('loginWithProvider builds correct Hosted UI URL for current origin', async () => {
        jest.resetModules();
        // Mock amplify-config before importing auth-cognito so the module uses our fake config
        jest.doMock('../docs-site/src/config/amplify-config', () => ({
            amplifyConfig: {
                Auth: {
                    Cognito: {
                        userPoolClientId: 'FAKECLIENTID',
                        loginWith: {
                            oauth: {
                                domain: 'shieldcraft-auth.auth.us-east-1.amazoncognito.com',
                                redirectSignIn: [
                                    'https://example.com/dashboard',
                                    'https://shieldcraft-ai.com/dashboard'
                                ]
                            }
                        }
                    }
                }
            }
        }));

        const authPath = require('../docs-site/src/utils/auth-cognito');
        // Call loginWithProvider which should set window.location.href
        await authPath.loginWithProvider('Google');

        // Validate that window.location.href was set to a Cognito Hosted UI URL with matching redirect
        const href = (window as any).location.href;
        expect(href).toMatch(/https:\/\/shieldcraft-auth.auth.us-east-1.amazoncognito.com\/oauth2\/authorize\?/);
        expect(href).toContain('identity_provider=Google');
        expect(href).toContain('client_id=FAKECLIENTID');
        expect(href).toContain(`redirect_uri=${encodeURIComponent('https://example.com/dashboard')}`);
    });

    test('loginWithProvider falls back to first redirect when origin not listed', async () => {
        jest.resetModules();
        // Alter window origin to something not present in redirect list
        (window as any).location.origin = 'https://unknown.example';
        (window as any).location.href = 'https://unknown.example/';

        jest.doMock('../docs-site/src/config/amplify-config', () => ({
            amplifyConfig: {
                Auth: {
                    Cognito: {
                        userPoolClientId: 'CLIENT2',
                        loginWith: {
                            oauth: {
                                domain: 'shieldcraft-auth.auth.us-east-1.amazoncognito.com',
                                redirectSignIn: [
                                    'https://primary.example/callback',
                                    'https://secondary.example/callback'
                                ]
                            }
                        }
                    }
                }
            }
        }));

        const authPath = require('../docs-site/src/utils/auth-cognito');
        await authPath.loginWithProvider('Amazon');

        const href = (window as any).location.href;
        expect(href).toContain('identity_provider=Amazon');
        expect(href).toContain('client_id=CLIENT2');
        expect(href).toContain(`redirect_uri=${encodeURIComponent('https://primary.example/callback')}`);
    });

    test('refreshAuthState attempts manual token exchange and stores tokens', async () => {
        jest.resetModules();
        // Mock amplify-config so auth-cognito picks it up on import
        jest.doMock('../docs-site/src/config/amplify-config', () => ({
            amplifyConfig: {
                Auth: {
                    Cognito: {
                        userPoolClientId: 'FAKECLIENTID',
                        loginWith: {
                            oauth: {
                                domain: 'shieldcraft-auth.auth.us-east-1.amazoncognito.com',
                                redirectSignIn: ['https://example.com/dashboard']
                            }
                        }
                    }
                }
            }
        }));
        const authPath = require('../docs-site/src/utils/auth-cognito');

        // Mock window location to mimic callback with code/state
        (window as any).location = {
            href: 'https://example.com/callback?code=AUTHCODE123&state=STATE123',
            origin: 'https://example.com',
            pathname: '/callback',
            search: '?code=AUTHCODE123&state=STATE123',
            hostname: 'example.com',
            replace: (s: string) => { (window as any).location.href = s; }
        } as any;

        // Seed stored OAuth params to mimic capture script
        sessionStorage.setItem('__sc_oauth_search', '?code=AUTHCODE123&state=STATE123');
        sessionStorage.setItem('__sc_oauth_href', 'https://example.com/callback?code=AUTHCODE123&state=STATE123');

        // Mock fetch for token exchange
        const tokenResponse = {
            access_token: 'AT123',
            id_token: 'ID123',
            refresh_token: 'RT123',
            username: 'user123'
        };

        (global as any).fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => tokenResponse, status: 200, statusText: 'OK', clone: () => ({ text: async () => JSON.stringify(tokenResponse) }) });

        // Call refreshAuthState which should process callback and store tokens
        const res = await authPath.refreshAuthState();

        // After processing, localStorage should contain the hand-rolled Cognito keys
        const clientId = 'FAKECLIENTID';
        const lastUserKey = `CognitoIdentityServiceProvider.${clientId}.LastAuthUser`;
        expect(localStorage.getItem(lastUserKey)).toBeDefined();

        const storedUserKey = `CognitoIdentityServiceProvider.${clientId}.user123`;
        expect(localStorage.getItem(`${storedUserKey}.accessToken`)).toBe('AT123');
        expect(localStorage.getItem(`${storedUserKey}.idToken`)).toBe('ID123');

        // Stored OAuth params should be cleared even if already read
        expect(sessionStorage.getItem('__sc_oauth_search')).toBeNull();

        // Note: the boolean return value depends on Amplify's fetchAuthSession; the important side-effect
        // is that tokens were stored so Amplify can pick them up. We assert storage above.
    }, 15000);
});
