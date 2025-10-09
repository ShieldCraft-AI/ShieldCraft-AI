# Multi-Provider Authentication Setup Guide

## 🎯 Summary

You now have the infrastructure to support Google, Amazon, Facebook, and GitHub authentication. Here's how to complete the setup:

## 📋 Step-by-Step Setup

### 1. Create OAuth Applications

For each provider, you need to create an OAuth application:

#### Google (Already Done ✅)
- ✅ OAuth Client ID: `280290087757-ukcu2fiiuv9enlh6pa2dhi6beq3l1l6f.apps.googleusercontent.com`
- ✅ Working in production

#### Amazon (Login with Amazon)
1. Go to: https://developer.amazon.com/loginwithamazon/console/site/lwa/overview.html
2. Create new Security Profile: "ShieldCraft AI"
3. Add redirect URI: `https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`
4. Save `Client ID` and `Client Secret`

#### Facebook
1. Go to: https://developers.facebook.com/apps/
2. Create app → "Consumer" type
3. Add "Facebook Login" product
4. Valid OAuth Redirect URIs: `https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`
5. Save `App ID` and `App Secret`

#### GitHub
1. Go to: https://github.com/settings/developers
2. New OAuth App
3. Authorization callback URL: `https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`
4. Save `Client ID` and `Client Secret`

### 2. Configure Cognito (Automated Script)

Once you have all the OAuth credentials, run:

```bash
# Set environment variables
export AMAZON_CLIENT_ID="your_amazon_client_id"
export AMAZON_CLIENT_SECRET="your_amazon_client_secret"
export FACEBOOK_APP_ID="your_facebook_app_id"
export FACEBOOK_APP_SECRET="your_facebook_app_secret"
export GITHUB_CLIENT_ID="your_github_client_id"
export GITHUB_CLIENT_SECRET="your_github_client_secret"

# Run the setup script
./scripts/add-idps.sh
```

### 3. Deploy Frontend Changes

```bash
cd docs-site
npm run build
# Deploy the build/ folder to your hosting
```

### 4. Test Each Provider

Visit: `https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/login?client_id=2jio5rlqn6r2qe0otrgip4d5bp&response_type=code&scope=email+openid+profile&redirect_uri=https://shieldcraft-ai.com/dashboard`

You should see all four provider buttons.

## 🎨 Frontend Features Added

### Multi-Provider Navbar Dropdown
- Click "Login" to see all provider options
- Dropdown shows: Google, Amazon, Facebook, GitHub
- Each with appropriate icons and styling

### Dedicated Sign-In Page
- Visit `/sign-in` for a full login experience
- Educational content about why to create an account
- All providers displayed vertically with explanations

### Modular Components
- `MultiProviderLogin` - Flexible component for any page
- `CompactMultiProviderLogin` - For navbars/headers
- `FullMultiProviderLogin` - For dedicated login pages

## 🔧 Customization Options

### Add More Providers
Edit `getAvailableProviders()` in `auth-cognito.ts`:
```typescript
export function getAvailableProviders() {
    return [
        { id: 'Google', name: 'Google', icon: '🔍' },
        { id: 'Amazon', name: 'Amazon', icon: '📦' },
        { id: 'Facebook', name: 'Facebook', icon: '📘' },
        { id: 'GitHub', name: 'GitHub', icon: '🐙' },
        { id: 'Microsoft', name: 'Microsoft', icon: '🪟' }, // New provider
    ];
}
```

### Customize Styling
Edit the `providerConfig` in `MultiProviderLogin/index.tsx` to change colors, icons, etc.

### Provider-Specific Logic
Add provider-specific handling in the auth callback (different scopes, user data mapping, etc.)

## 🚨 Important Notes

### Facebook Requirements
- Facebook requires app review for `email` permission in production
- You can test with developer accounts before review
- Submit for review once ready for public use

### GitHub Scoping
- GitHub uses `user:email` scope to access email
- Users might have private emails - handle gracefully

### Amazon Scoping
- Amazon uses `profile` scope (not `openid`)
- Limited user data compared to other providers

## 🔍 Testing & Debugging

### Test Each Provider
1. Clear browser cache/cookies
2. Try login with each provider
3. Verify user data is received correctly
4. Check that logout works

### Debug Issues
- Enable debug mode: `window.__SC_AUTH_DEBUG__ = true`
- Check browser console for auth flow logs
- Verify redirect URIs match exactly
- Test in incognito mode to avoid cached auth

## ✅ Next Steps

1. **Set up provider OAuth apps** (get credentials)
2. **Run the setup script** (configure Cognito)
3. **Deploy frontend changes** (build + deploy)
4. **Test thoroughly** (each provider + edge cases)
5. **Consider UX improvements** (remember last provider, social signup vs signin, etc.)

The foundation is ready - you just need the OAuth credentials from each provider!
