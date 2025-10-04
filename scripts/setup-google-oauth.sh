#!/bin/bash
# Add Google OAuth to Cognito User Pool

echo "🔐 Adding Google OAuth to Cognito"
echo ""
echo "Enter your Google Client ID (from Google Console):"
read -r GOOGLE_CLIENT_ID

echo ""
echo "Enter your Google Client Secret (from Google Console):"
read -r GOOGLE_CLIENT_SECRET

echo ""
echo "Adding Google identity provider to Cognito..."

aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_p3VQtjFbq \
  --provider-name Google \
  --provider-type Google \
  --provider-details "client_id=$GOOGLE_CLIENT_ID,client_secret=$GOOGLE_CLIENT_SECRET,authorize_scopes=email profile openid" \
  --attribute-mapping email=email,name=name

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Google provider added successfully!"
  echo ""
  echo "Linking Google to your app client..."

  aws cognito-idp update-user-pool-client \
    --user-pool-id us-east-1_p3VQtjFbq \
    --client-id 3u9rbcprme07gut2boqfp1me38 \
    --supported-identity-providers Google COGNITO

  if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Done! Google OAuth is now enabled."
    echo ""
    echo "🎉 You can now test login:"
    echo "   1. Go to http://localhost:3001"
    echo "   2. Click 'Login' button"
    echo "   3. Click 'Google' on Cognito page"
    echo "   4. Sign in with your Google account"
  else
    echo "❌ Failed to link Google provider"
  fi
else
  echo "❌ Failed to add Google provider"
fi
