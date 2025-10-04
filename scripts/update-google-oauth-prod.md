# Update Google OAuth for Production

Your Cognito is now configured for production, but you need to update Google OAuth Client settings:

## 🔧 Steps:

1. **Go to Google Cloud Console**: https://console.cloud.google.com/apis/credentials

2. **Find your OAuth Client**: `280290087757-ukcu2fiiuv9enlh6pa2dhi6beq3l1l6f.apps.googleusercontent.com`

3. **Add Authorized Redirect URIs**:
   - Currently you probably only have localhost
   - Add these:
     ```
     https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
     https://shieldcraft-ai.com/dashboard
     https://shieldcraft-ai.com/auth/callback
     ```

4. **Add Authorized JavaScript Origins** (if field exists):
   ```
   https://shieldcraft-ai.com
   https://d1039p1dgncyvs.cloudfront.net
   ```

5. **Save** the changes

## ⚠️ Important:
- Don't remove localhost URLs (needed for development)
- The `/oauth2/idpresponse` URL is where Google redirects back to Cognito
- The `/dashboard` and `/auth/callback` URLs are where Cognito redirects to your site

## ✅ After updating:
Your production site at `https://shieldcraft-ai.com` will work with Google OAuth login!
