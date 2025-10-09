# Add Additional Identity Providers to Cognito

This guide shows how to add Amazon, Facebook, and GitHub OAuth to your existing Cognito setup.

## 🔧 Overview

Your current setup has:
- ✅ Google OAuth (working)
- 🔄 Need to add: Amazon, Facebook, GitHub

## 📋 Prerequisites

Each IdP requires you to create an OAuth application first:

### 1. Amazon (Login with Amazon)
1. Go to [Amazon Developer Console](https://developer.amazon.com/loginwithamazon/console/site/lwa/overview.html)
2. Create a new Security Profile
3. Add these redirect URIs:
   ```
   https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
   ```
4. Note down: `Client ID` and `Client Secret`

### 2. Facebook
1. Go to [Facebook Developers](https://developers.facebook.com/apps/)
2. Create a new app → "Consumer" type
3. Add "Facebook Login" product
4. In Facebook Login settings, add Valid OAuth Redirect URIs:
   ```
   https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
   ```
5. Note down: `App ID` and `App Secret`

### 3. GitHub
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create a new OAuth App
3. Set Authorization callback URL:
   ```
   https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
   ```
4. Note down: `Client ID` and `Client Secret`

## 🚀 Cognito Configuration Commands

Once you have the credentials, run these AWS CLI commands:

### Add Amazon IdP
```bash
aws cognito-idp create-identity-provider \
  --region us-east-1 \
  --user-pool-id us-east-1_H6KHkYeES \
  --provider-name Amazon \
  --provider-type LoginWithAmazon \
  --provider-details "client_id=YOUR_AMAZON_CLIENT_ID,client_secret=YOUR_AMAZON_CLIENT_SECRET,authorize_scopes=profile" \
  --attribute-mapping email=email,name=name
```

### Add Facebook IdP
```bash
aws cognito-idp create-identity-provider \
  --region us-east-1 \
  --user-pool-id us-east-1_H6KHkYeES \
  --provider-name Facebook \
  --provider-type Facebook \
  --provider-details "client_id=YOUR_FACEBOOK_APP_ID,client_secret=YOUR_FACEBOOK_APP_SECRET,authorize_scopes=email,public_profile" \
  --attribute-mapping email=email,name=name
```

### Add GitHub IdP
```bash
aws cognito-idp create-identity-provider \
  --region us-east-1 \
  --user-pool-id us-east-1_H6KHkYeES \
  --provider-name GitHub \
  --provider-type OIDC \
  --provider-details "client_id=YOUR_GITHUB_CLIENT_ID,client_secret=YOUR_GITHUB_CLIENT_SECRET,attributes_request_method=GET,oidc_issuer=https://token.actions.githubusercontent.com,authorize_scopes=user:email" \
  --attribute-mapping email=email,name=name
```

### Update App Client to Support All IdPs
```bash
aws cognito-idp update-user-pool-client \
  --region us-east-1 \
  --user-pool-id us-east-1_H6KHkYeES \
  --client-id 2jio5rlqn6r2qe0otrgip4d5bp \
  --supported-identity-providers Google Amazon Facebook GitHub COGNITO
```

## ✅ Verification

Test each IdP:
1. Go to your Cognito Hosted UI: `https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/login?client_id=2jio5rlqn6r2qe0otrgip4d5bp&response_type=code&scope=email+openid+profile&redirect_uri=https://shieldcraft-ai.com/dashboard`
2. You should see buttons for Google, Amazon, Facebook, and GitHub
3. Test login with each provider

## 🔍 Troubleshooting

- **Amazon**: Make sure to request `profile` scope (not `openid`)
- **Facebook**: Requires app review for `email` permission in production
- **GitHub**: Uses OIDC flow, not direct OAuth (hence the different setup)
- **All**: Redirect URI must exactly match what you configure in each provider

## 📝 Next Steps

After adding IdPs, update your frontend code to support multiple providers (see next guide).
