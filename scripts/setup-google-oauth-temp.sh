#!/bin/bash
# Add Google OAuth to Cognito User Pool
# WARNING: Contains secrets - DELETE AFTER USE

echo "🔐 Adding Google OAuth to Cognito"
echo ""

# Hardcoded values
GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID_HERE"
GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET_HERE"

echo "Adding Google identity provider to Cognito..."

aws cognito-idp create-identity-provider \
  --region us-east-1 \
  --user-pool-id us-east-1_H6KHkYeES \
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
    --region us-east-1 \
    --user-pool-id us-east-1_H6KHkYeES \
    --client-id 2jio5rlqn6r2qe0otrgip4d5bp \
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
    echo ""
    echo "⚠️  REMEMBER TO DELETE THIS FILE (contains secrets)"
  else
    echo "❌ Failed to link Google provider"
  fi
else
  echo "❌ Failed to add Google provider"
fi
