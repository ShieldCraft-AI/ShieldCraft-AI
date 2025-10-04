# AWS Cognito Authentication Setup

This guide walks through setting up social identity provider authentication for the ShieldCraft AI static site using AWS Cognito.

## Architecture

```
Static Site (S3 + CloudFront)
    ↓
AWS Amplify Auth SDK (client-side)
    ↓
AWS Cognito User Pool
    ↓
Social IdPs (Google, GitHub, Microsoft)
```

**No backend server required** - Cognito handles OAuth2 flows via client-side redirects.

---

## Step 1: Deploy Cognito Infrastructure

### 1.1 Add Auth Stack to CDK App

```python
# infra/app.py
from domains.auth_stack import AuthStack

auth_stack = AuthStack(
    app,
    "ShieldCraftAuthStack",
    domain_name="yourdomain.com",  # Replace with your CloudFront domain
    env=aws_environment,
)
```

### 1.2 Deploy Stack

```bash
cd infra
cdk deploy ShieldCraftAuthStack
```

### 1.3 Save Outputs

After deployment, note these values (also available in CloudFormation console):
- `UserPoolId`: e.g., `us-east-1_ABC123xyz`
- `UserPoolClientId`: e.g., `7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p`
- `CognitoHostedUIDomain`: e.g., `shieldcraft-auth`

---

## Step 2: Configure Social Identity Providers

### 2.1 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create new OAuth 2.0 Client ID (Web application)
3. Add authorized redirect URIs:
   ```
   https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
   ```
4. Save Client ID and Client Secret

5. Add to Cognito:
   ```bash
   aws cognito-idp create-identity-provider \
     --user-pool-id us-east-1_ABC123xyz \
     --provider-name Google \
     --provider-type Google \
     --provider-details \
       client_id="YOUR_GOOGLE_CLIENT_ID",\
       client_secret="YOUR_GOOGLE_CLIENT_SECRET",\
       authorize_scopes="email profile openid"
   ```

6. Update User Pool Client to use Google:
   ```bash
   aws cognito-idp update-user-pool-client \
     --user-pool-id us-east-1_ABC123xyz \
     --client-id 7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p \
     --supported-identity-providers Google COGNITO
   ```

### 2.2 GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create new OAuth App
3. Set Authorization callback URL:
   ```
   https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
   ```
4. Save Client ID and Client Secret

5. Add to Cognito (GitHub uses generic OIDC provider):
   ```bash
   aws cognito-idp create-identity-provider \
     --user-pool-id us-east-1_ABC123xyz \
     --provider-name GitHub \
     --provider-type OIDC \
     --provider-details \
       client_id="YOUR_GITHUB_CLIENT_ID",\
       client_secret="YOUR_GITHUB_CLIENT_SECRET",\
       attributes_request_method="GET",\
       oidc_issuer="https://github.com",\
       authorize_scopes="read:user user:email"
   ```

### 2.3 Microsoft OAuth Setup

1. Go to [Azure Portal](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Register new application
3. Add redirect URI:
   ```
   https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
   ```
4. Create client secret
5. Save Application (client) ID and secret

6. Add to Cognito (Microsoft uses SAML):
   ```bash
   aws cognito-idp create-identity-provider \
     --user-pool-id us-east-1_ABC123xyz \
     --provider-name Microsoft \
     --provider-type OIDC \
     --provider-details \
       client_id="YOUR_MICROSOFT_CLIENT_ID",\
       client_secret="YOUR_MICROSOFT_CLIENT_SECRET",\
       attributes_request_method="GET",\
       oidc_issuer="https://login.microsoftonline.com/common/v2.0",\
       authorize_scopes="openid email profile"
   ```

---

## Step 3: Frontend Integration

### 3.1 Install Dependencies

```bash
cd docs-site
npm install aws-amplify @aws-amplify/ui-react
```

### 3.2 Create Amplify Configuration

```typescript
// src/config/amplify-config.ts
export const amplifyConfig = {
  Auth: {
    region: 'us-east-1',
    userPoolId: 'us-east-1_ABC123xyz',  // From CDK output
    userPoolWebClientId: '7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p',  // From CDK output
    oauth: {
      domain: 'shieldcraft-auth.auth.us-east-1.amazoncognito.com',
      scope: ['email', 'profile', 'openid'],
      redirectSignIn: 'https://yourdomain.com/dashboard',
      redirectSignOut: 'https://yourdomain.com/',
      responseType: 'code',  // Authorization Code with PKCE (secure for SPAs)
    },
  },
};
```

### 3.3 Replace Mock Auth with Amplify

```typescript
// src/utils/auth.ts - REPLACE ENTIRE FILE
import { Auth } from 'aws-amplify';

export interface User {
  email: string;
  name?: string;
  sub: string;  // Cognito user ID
}

export async function isLoggedIn(): Promise<boolean> {
  try {
    await Auth.currentAuthenticatedUser();
    return true;
  } catch {
    return false;
  }
}

export async function getCurrentUser(): Promise<User | null> {
  try {
    const cognitoUser = await Auth.currentAuthenticatedUser();
    return {
      email: cognitoUser.attributes.email,
      name: cognitoUser.attributes.name || cognitoUser.attributes.email,
      sub: cognitoUser.attributes.sub,
    };
  } catch {
    return null;
  }
}

export async function loginWithProvider(provider: 'Google' | 'GitHub' | 'Microsoft') {
  await Auth.federatedSignIn({ provider });
}

export async function loginWithEmail(email: string, password: string) {
  await Auth.signIn(email, password);
}

export async function signOut() {
  await Auth.signOut();
}

// Event emitter for auth state changes
const authChangeListeners = new Set<(isAuthed: boolean) => void>();

export function onAuthChange(callback: (isAuthed: boolean) => void) {
  authChangeListeners.add(callback);
  return () => authChangeListeners.delete(callback);
}

// Listen to Amplify Hub events
import { Hub } from 'aws-amplify';
Hub.listen('auth', ({ payload: { event } }) => {
  const isAuthed = ['signIn', 'cognitoHostedUI'].includes(event);
  authChangeListeners.forEach(cb => cb(isAuthed));
});
```

### 3.4 Initialize Amplify in Root

```typescript
// src/theme/Root.tsx (or create if doesn't exist)
import React from 'react';
import { Amplify } from 'aws-amplify';
import { amplifyConfig } from '../config/amplify-config';

Amplify.configure(amplifyConfig);

export default function Root({ children }) {
  return <>{children}</>;
}
```

### 3.5 Update Navbar Component

```typescript
// src/theme/NavbarItem/auth.tsx
import React from 'react';
import { Auth } from 'aws-amplify';
import type { Props } from '@theme/NavbarItem/DefaultNavbarItem';

export default function AuthNavbarItem(_props: Props) {
  const [user, setUser] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const currentUser = await Auth.currentAuthenticatedUser();
      setUser(currentUser);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  const handleLogin = () => {
    // Option 1: Use Cognito Hosted UI (easiest)
    Auth.federatedSignIn();

    // Option 2: Specific provider
    // Auth.federatedSignIn({ provider: 'Google' });
  };

  const handleLogout = async () => {
    await Auth.signOut();
    setUser(null);
    window.location.href = '/';
  };

  if (loading) return null;

  return user ? (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <span style={{ fontSize: '0.875rem' }}>{user.attributes?.email}</span>
      <button className="button button--secondary button--sm" onClick={handleLogout}>
        Logout
      </button>
    </div>
  ) : (
    <button className="button button--primary button--sm" onClick={handleLogin}>
      Login
    </button>
  );
}
```

---

## Step 4: Test Authentication

### 4.1 Local Development

```bash
npm start
```

Visit `http://localhost:3000` and click Login - you'll be redirected to Cognito Hosted UI.

### 4.2 Deploy to S3

```bash
npm run build
aws s3 sync build/ s3://your-bucket-name/
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

---

## Step 5: Customize Hosted UI (Optional)

### 5.1 Update Cognito Hosted UI Branding

```bash
aws cognito-idp set-ui-customization \
  --user-pool-id us-east-1_ABC123xyz \
  --css ".logo { background: url('https://yourdomain.com/logo.png'); }" \
  --image-file fileb://logo.png
```

### 5.2 Build Custom Login Page

Instead of Cognito Hosted UI, use Amplify UI components:

```typescript
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

export default function LoginPage() {
  return (
    <Authenticator
      socialProviders={['google', 'facebook']}
      hideSignUp={false}
    >
      {({ signOut, user }) => (
        <div>Welcome {user?.username}!</div>
      )}
    </Authenticator>
  );
}
```

---

## Troubleshooting

### Issue: "Invalid redirect_uri"
- Verify callback URLs in Cognito User Pool Client match exactly
- Ensure protocol (http vs https) matches
- Check CloudFront domain vs S3 bucket domain

### Issue: "User pool client does not have secret"
- Cognito App Client must NOT have a secret for SPAs
- Recreate client without "Generate client secret" option

### Issue: Social login button doesn't appear
- Verify identity provider is linked to User Pool Client
- Check `supported-identity-providers` includes provider name
- Clear browser cache and retry

### Issue: CORS errors
- Cognito doesn't require CORS for static sites
- If seeing errors, check CloudFront is serving with proper headers

---

## Security Best Practices

1. **Use HTTPS everywhere** - Required for OAuth2
2. **Enable MFA** - Add to Cognito User Pool settings
3. **Rotate secrets** - Store IdP secrets in AWS Secrets Manager
4. **Monitor auth logs** - Enable CloudWatch Logs for Cognito
5. **Set token expiration** - Use short-lived access tokens (1 hour)
6. **Use PKCE** - Already enabled in Authorization Code grant

---

## Cost Estimate

- **Cognito User Pool**: Free for first 50,000 MAUs
- **After 50k MAUs**: $0.0055 per MAU
- **Social IdP auth**: No additional cost
- **Estimated cost for demo**: $0/month

---

## Next Steps

1. Deploy CDK stack
2. Configure one social IdP (recommend starting with Google)
3. Test login flow locally
4. Deploy to S3/CloudFront
5. Add additional IdPs as needed
6. Customize branding/UI
