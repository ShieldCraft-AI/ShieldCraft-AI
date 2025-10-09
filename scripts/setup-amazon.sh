#!/bin/bash
# Quick Amazon OAuth setup for ShieldCraft AI
# Usage: AMAZON_CLIENT_ID=xxx AMAZON_CLIENT_SECRET=yyy ./setup-amazon.sh

set -e

echo "📦 Setting up Amazon (Login with Amazon) for ShieldCraft AI"
echo "==========================================================="
echo ""

# Configuration
USER_POOL_ID="us-east-1_H6KHkYeES"
CLIENT_ID="2jio5rlqn6r2qe0otrgip4d5bp"
REGION="us-east-1"

# Check credentials
if [ -z "$AMAZON_CLIENT_ID" ] || [ -z "$AMAZON_CLIENT_SECRET" ]; then
    echo "❌ Missing Amazon credentials!"
    echo ""
    echo "Usage:"
    echo "  export AMAZON_CLIENT_ID='amzn1.application-oa2-client.YOUR_ID'"
    echo "  export AMAZON_CLIENT_SECRET='YOUR_SECRET'"
    echo "  ./setup-amazon.sh"
    echo ""
    echo "Get credentials from: https://developer.amazon.com/loginwithamazon/console/"
    exit 1
fi

echo "✅ Amazon credentials provided"
echo "   Client ID: ${AMAZON_CLIENT_ID:0:30}..."
echo ""

# Add Amazon IdP
echo "📦 Adding Amazon identity provider to Cognito..."
if aws cognito-idp create-identity-provider \
    --region $REGION \
    --user-pool-id $USER_POOL_ID \
    --provider-name Amazon \
    --provider-type LoginWithAmazon \
    --provider-details "client_id=$AMAZON_CLIENT_ID,client_secret=$AMAZON_CLIENT_SECRET,authorize_scopes=profile" \
    --attribute-mapping email=email,name=name 2>/dev/null; then
    echo "✅ Amazon IdP added successfully!"
else
    echo "⚠️  Amazon IdP might already exist (continuing anyway)"
fi

echo ""
echo "🔗 Updating App Client to support Amazon..."

# Update App Client to support Google + Amazon + COGNITO
if aws cognito-idp update-user-pool-client \
    --region $REGION \
    --user-pool-id $USER_POOL_ID \
    --client-id $CLIENT_ID \
    --supported-identity-providers Google Amazon COGNITO; then
    echo "✅ App Client updated successfully!"
else
    echo "❌ Failed to update App Client"
    exit 1
fi

echo ""
echo "🎉 Amazon OAuth setup complete!"
echo ""
echo "🔍 Test your Amazon login:"
echo "   https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/login?client_id=$CLIENT_ID&response_type=code&scope=email+openid+profile&redirect_uri=https://shieldcraft-ai.com/dashboard"
echo ""
echo "📱 On your site, users will now see:"
echo "   • Login dropdown with Google and Amazon options"
echo "   • Amazon button with 📦 icon"
echo ""
echo "🚀 Next steps:"
echo "   1. Deploy your frontend (npm run build)"
echo "   2. Test Amazon login end-to-end"
echo "   3. Add Microsoft and GitHub when ready"
echo ""
