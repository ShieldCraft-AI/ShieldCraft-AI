/**
 * AWS Cognito authentication for ShieldCraft AI
 * Uses Cognito Hosted UI for social login (Google OAuth)
 */

import { fetchAuthSession, signOut as amplifySignOut, signInWithRedirect, getCurrentUser as amplifyGetCurrentUser } from 'aws-amplify/auth';

export interface User {
    email: string;
    name?: string;
    sub: string;
    attributes?: Record<string, any>;
}

export async function isLoggedIn(): Promise<boolean> {
    if (typeof window === 'undefined') return false;
    try {
        const session = await fetchAuthSession();
        console.log('isLoggedIn - session:', {
            hasTokens: !!session.tokens,
            hasAccessToken: !!session.tokens?.accessToken,
            hasIdToken: !!session.tokens?.idToken,
            tokens: session.tokens
        });
        return !!session.tokens;
    } catch (error) {
        console.error('isLoggedIn - error:', error);
        return false;
    }
}

export async function getCurrentUser(): Promise<User | null> {
    if (typeof window === 'undefined') return null;
    try {
        // Use Amplify's getCurrentUser which properly handles auth state
        const cognitoUser = await amplifyGetCurrentUser();
        const session = await fetchAuthSession();
        const idToken = session.tokens?.idToken?.payload;

        if (!idToken) return null;

        return {
            email: (idToken.email as string) || '',
            name: (idToken.name as string) || (idToken.email as string),
            sub: cognitoUser.userId,
            attributes: idToken as any,
        };
    } catch (error) {
        console.log('getCurrentUser error:', error);
        return null;
    }
}

export async function loginWithHostedUI(): Promise<void> {
    try {
        // Use Amplify's built-in OAuth flow which handles callback automatically
        await signInWithRedirect({ provider: 'Google' });
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
}

export async function loginWithProvider(provider: string): Promise<void> {
    const cognitoDomain = 'shieldcraft-auth.auth.us-east-1.amazoncognito.com';
    const clientId = '3u9rbcprme07gut2boqfp1me38';
    const redirectUri = encodeURIComponent(window.location.origin + '/dashboard');

    window.location.href = `https://${cognitoDomain}/oauth2/authorize?identity_provider=${provider}&client_id=${clientId}&response_type=code&scope=email+profile+openid&redirect_uri=${redirectUri}`;
}

export async function signOut(): Promise<void> {
    try {
        await amplifySignOut();
    } catch (error) {
        console.error('Sign out failed:', error);
    }
}

type AuthChangeCallback = (isAuthenticated: boolean) => void;
const authChangeListeners = new Set<AuthChangeCallback>();

// Call all registered listeners
export async function notifyAuthChange(): Promise<void> {
    const authenticated = await isLoggedIn();

    // Notify all registered callbacks
    authChangeListeners.forEach(callback => {
        callback(authenticated);
    });
}

export function onAuthChange(callback: AuthChangeCallback): () => void {
    authChangeListeners.add(callback);

    // Immediately check current auth state
    (async () => {
        const authenticated = await isLoggedIn();
        callback(authenticated);
    })();

    return () => {
        authChangeListeners.delete(callback);
    };
}

export const AUTH_EVENT = 'sc-auth-changed';
export const AUTH_KEY = 'sc_logged_in';
