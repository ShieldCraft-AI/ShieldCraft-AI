// Amplify configuration for AWS Cognito authentication
// Deployed values from CDK stack

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
                    domain: 'shieldcraft-auth.auth.us-east-1.amazoncognito.com',                    // Scopes to request from identity providers
                    scopes: ['email', 'profile', 'openid'],

                    // Where to redirect after successful login
                    redirectSignIn: typeof window !== 'undefined'
                        ? [`${window.location.origin}/dashboard`]
                        : ['http://localhost:3000/dashboard'],

                    // Where to redirect after logout
                    redirectSignOut: typeof window !== 'undefined'
                        ? [window.location.origin]
                        : ['http://localhost:3000/'],

                    // Use Authorization Code Grant with PKCE (secure for SPAs)
                    responseType: 'code' as const,
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
