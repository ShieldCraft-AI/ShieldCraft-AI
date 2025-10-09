// Amplify configuration for AWS Cognito authentication
// Deployed values from CDK stack

const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1']);
const PROD_REDIRECT_SIGN_IN = [
    'https://shieldcraft-ai.com/dashboard',
    'https://www.shieldcraft-ai.com/dashboard',
];
const PROD_REDIRECT_SIGN_OUT = [
    'https://shieldcraft-ai.com/',
    'https://www.shieldcraft-ai.com/',
];

function unique(values: (string | undefined | null)[]) {
    return Array.from(new Set(values.filter(Boolean) as string[]));
}

function resolveRedirects() {
    if (typeof window === 'undefined') {
        return {
            signIn: ['http://localhost:3000/dashboard', 'http://localhost:3001/dashboard'],
            signOut: ['http://localhost:3000/', 'http://localhost:3001/'],
        };
    }

    const origin = window.location.origin;
    const hostname = window.location.hostname.toLowerCase();
    const isLocal = LOCAL_HOSTS.has(hostname);

    const signInCandidates = isLocal
        ? [
            'http://localhost:3000/dashboard',
            'http://localhost:3001/dashboard',
            `${origin}/dashboard`,
            ...PROD_REDIRECT_SIGN_IN
        ]
        : [`${origin}/dashboard`, ...PROD_REDIRECT_SIGN_IN, 'http://localhost:3000/dashboard', 'http://localhost:3001/dashboard'];

    const signOutCandidates = isLocal
        ? [
            'http://localhost:3000/',
            'http://localhost:3001/',
            `${origin}/`,
            ...PROD_REDIRECT_SIGN_OUT
        ]
        : [`${origin}/`, ...PROD_REDIRECT_SIGN_OUT, 'http://localhost:3000/', 'http://localhost:3001/'];

    return {
        signIn: unique(signInCandidates),
        signOut: unique(signOutCandidates),
    };
}

const redirects = resolveRedirects();

export const amplifyConfig = {
    Auth: {
        Cognito: {
            // AWS Region where Cognito User Pool is deployed
            userPoolId: 'us-east-1_H6KHkYeES',

            // Cognito App Client ID (from CDK output: UserPoolClientId)
            userPoolClientId: '2jio5rlqn6r2qe0otrgip4d5bp',

            // OAuth/Social login configuration
            loginWith: {
                oauth: {
                    // Cognito Hosted UI domain
                    domain: 'shieldcraft-auth.auth.us-east-1.amazoncognito.com',
                    // Scopes to request from identity providers
                    scopes: ['email', 'profile', 'openid'],

                    // Where to redirect after successful login
                    redirectSignIn: redirects.signIn,

                    // Where to redirect after logout
                    redirectSignOut: redirects.signOut,

                    // Use Authorization Code Grant with PKCE (secure for SPAs)
                    responseType: 'code' as const,

                    // Configure social providers
                    providers: [
                        'Google',
                        { custom: 'LoginWithAmazon' }
                    ],
                },
            },
        },
    },
};

// For local development, you can override with a .env.local file:
// REACT_APP_AWS_REGION=us-east-1
// REACT_APP_USER_POOL_ID=us-east-1_ABC123xyz
// REACT_APP_USER_POOL_CLIENT_ID=7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p
// REACT_APP_COGNITO_DOMAIN=shieldcraft-auth.auth.us-east-1.amazoncognito.com
