# Amazon Login Setup Guide

## 🚀 Setting up Login with Amazon

Let's get Amazon OAuth working first! Here's the step-by-step process:

## 📋 Step 1: Create Amazon OAuth Application

1. **Go to Amazon Developer Console**:
   https://developer.amazon.com/loginwithamazon/console/site/lwa/overview.html

2. **Create Security Profile**:
   - Click "Create a New Security Profile"
   - **Security Profile Name**: `ShieldCraft AI`
   - **Security Profile Description**: `Authentication for ShieldCraft AI security platform`
   - **Consent Privacy Notice URL**: `https://shieldcraft-ai.com/privacy` (optional)

3. **Configure OAuth Settings**:
   - After creating, click "Show Client ID and Client Secret"
   - **Save these values** (you'll need them in step 2):
     - `Client ID`: (starts with `amzn1.application-oa2-client.`)
     - `Client Secret`: (long random string)

4. **Add Redirect URIs**:
   - Click "Manage" → "Web Settings"
   - **Allowed Return URLs**: Add this exact URL:
     ```
     https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
     ```
   - **Allowed JavaScript Origins** (optional):
     ```
     https://shieldcraft-ai.com
     https://www.shieldcraft-ai.com
     ```

## 🔧 Step 2: Configure Cognito

Once you have the Amazon credentials, run this:

```bash
# Set your Amazon credentials
export AMAZON_CLIENT_ID="amzn1.application-oa2-client.YOUR_ID_HERE"
export AMAZON_CLIENT_SECRET="YOUR_SECRET_HERE"

# Add Amazon to Cognito (just Amazon for now)
aws cognito-idp create-identity-provider \
  --region us-east-1 \
  --user-pool-id us-east-1_H6KHkYeES \
  --provider-name Amazon \
  --provider-type LoginWithAmazon \
  --provider-details "client_id=$AMAZON_CLIENT_ID,client_secret=$AMAZON_CLIENT_SECRET,authorize_scopes=profile" \
  --attribute-mapping email=email,name=name

# Update app client to support Amazon
aws cognito-idp update-user-pool-client \
  --region us-east-1 \
  --user-pool-id us-east-1_H6KHkYeES \
  --client-id 2jio5rlqn6r2qe0otrgip4d5bp \
  --supported-identity-providers Google Amazon COGNITO
```

## ✅ Step 3: Test Amazon Login

1. **Visit Cognito Hosted UI**:
   ```
   https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/login?client_id=2jio5rlqn6r2qe0otrgip4d5bp&response_type=code&scope=email+openid+profile&redirect_uri=https://shieldcraft-ai.com/dashboard
   ```

2. **You should see**:
   - Google button (existing)
   - Amazon button (new!)

3. **Test the flow**:
   - Click "Login with Amazon"
   - Sign in with your Amazon account
   - Should redirect back to your site

## 🎯 Step 4: Deploy Frontend

Your frontend code is already ready! Just deploy the latest build:

```bash
cd docs-site
npm run build
# Deploy the build/ folder
```

After deployment, your users will see:
- **Navbar**: "Login" dropdown with Google, Amazon, Microsoft, GitHub options
- **Sign-in page**: `/sign-in` with all providers displayed

## 🔍 Troubleshooting Amazon

### Common Issues:

**"Invalid redirect URI"**
- Make sure the redirect URI in Amazon console exactly matches:
  `https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`

**"Invalid client"**
- Double-check the Client ID starts with `amzn1.application-oa2-client.`
- Verify you copied the Client Secret correctly

**"Scope error"**
- Amazon uses `profile` scope (not `openid` like others)
- The script above uses the correct scope

**"User data missing"**
- Amazon provides limited user data compared to Google
- You'll get `name` and `email` (if user allows email sharing)

## 📝 Amazon-Specific Notes

- **Email sharing**: Users can opt out of sharing email with your app
- **Name format**: Amazon may provide display name or real name depending on user settings
- **No profile photos**: Amazon doesn't provide profile picture URLs
- **Enterprise friendly**: Many corporate users prefer Amazon login

## 🎉 Next Steps

Once Amazon is working:
1. Test thoroughly with different Amazon accounts
2. Set up Microsoft next (if desired)
3. Add GitHub last (most developer-focused)

Amazon is a great choice for enterprise users who already have Amazon accounts!
