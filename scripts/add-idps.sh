#!/bin/bash
# Add multiple Identity Providers to Cognito User Pool
# Usage: ./add-idps.sh

set -e

echo "🔐 Adding Identity Providers to Cognito User Pool"
echo "================================================"
echo ""

# Configuration
USER_POOL_ID="us-east-1_H6KHkYeES"
CLIENT_ID="2jio5rlqn6r2qe0otrgip4d5bp"
REGION="us-east-1"

# Check if credentials are provided
if [ -z "$AMAZON_CLIENT_ID" ] || [ -z "$AMAZON_CLIENT_SECRET" ]; then
    echo "⚠️  Amazon credentials not provided (AMAZON_CLIENT_ID, AMAZON_CLIENT_SECRET)"
    echo "   Set these environment variables or skip Amazon IdP"
fi

if [ -z "$MICROSOFT_CLIENT_ID" ] || [ -z "$MICROSOFT_CLIENT_SECRET" ]; then
    echo "⚠️  Microsoft credentials not provided (MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET)"
    echo "   Set these environment variables or skip Microsoft IdP"
fi

if [ -z "$GITHUB_CLIENT_ID" ] || [ -z "$GITHUB_CLIENT_SECRET" ]; then
    echo "⚠️  GitHub credentials not provided (GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)"
    echo "   Set these environment variables or skip GitHub IdP"
fi

echo ""
echo "🚀 Adding Identity Providers..."
echo ""

# Track which providers are added successfully
PROVIDERS=("COGNITO" "Google")  # Google should already exist

# Add Amazon IdP
if [ ! -z "$AMAZON_CLIENT_ID" ] && [ ! -z "$AMAZON_CLIENT_SECRET" ]; then
    echo "📦 Adding Amazon (Login with Amazon)..."
    if aws cognito-idp create-identity-provider \
        --region $REGION \
        --user-pool-id $USER_POOL_ID \
        --provider-name Amazon \
        --provider-type LoginWithAmazon \
        --provider-details "client_id=$AMAZON_CLIENT_ID,client_secret=$AMAZON_CLIENT_SECRET,authorize_scopes=profile" \
        --attribute-mapping email=email,name=name 2>/dev/null; then
        echo "✅ Amazon IdP added successfully"
        PROVIDERS+=("Amazon")
    else
        echo "⚠️  Amazon IdP might already exist or failed to add"
        PROVIDERS+=("Amazon")  # Add anyway in case it exists
    fi
    echo ""
fi

# Add Microsoft IdP
if [ ! -z "$MICROSOFT_CLIENT_ID" ] && [ ! -z "$MICROSOFT_CLIENT_SECRET" ]; then
    echo "🪟 Adding Microsoft..."
    if aws cognito-idp create-identity-provider \
        --region $REGION \
        --user-pool-id $USER_POOL_ID \
        --provider-name Microsoft \
        --provider-type SAML \
        --provider-details "MetadataURL=https://login.microsoftonline.com/common/FederationMetadata/2007-06/FederationMetadata.xml" \
        --attribute-mapping email=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress,name=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name 2>/dev/null; then
        echo "✅ Microsoft IdP added successfully"
        PROVIDERS+=("Microsoft")
    else
        echo "⚠️  Microsoft IdP might already exist or failed to add"
        PROVIDERS+=("Microsoft")  # Add anyway in case it exists
    fi
    echo ""
fi

# Add GitHub IdP
if [ ! -z "$GITHUB_CLIENT_ID" ] && [ ! -z "$GITHUB_CLIENT_SECRET" ]; then
    echo "🐙 Adding GitHub..."
    if aws cognito-idp create-identity-provider \
        --region $REGION \
        --user-pool-id $USER_POOL_ID \
        --provider-name GitHub \
        --provider-type OIDC \
        --provider-details "client_id=$GITHUB_CLIENT_ID,client_secret=$GITHUB_CLIENT_SECRET,attributes_request_method=GET,oidc_issuer=https://token.actions.githubusercontent.com,authorize_scopes=user:email" \
        --attribute-mapping email=email,name=name 2>/dev/null; then
        echo "✅ GitHub IdP added successfully"
        PROVIDERS+=("GitHub")
    else
        echo "⚠️  GitHub IdP might already exist or failed to add"
        PROVIDERS+=("GitHub")  # Add anyway in case it exists
    fi
    echo ""
fi

# Update App Client to support all providers
echo "🔗 Updating App Client to support all Identity Providers..."
PROVIDER_LIST=$(IFS=' '; echo "${PROVIDERS[*]}")
echo "   Providers: $PROVIDER_LIST"

if aws cognito-idp update-user-pool-client \
    --region $REGION \
    --user-pool-id $USER_POOL_ID \
    --client-id $CLIENT_ID \
    --supported-identity-providers $PROVIDER_LIST; then
    echo "✅ App Client updated successfully"
else
    echo "❌ Failed to update App Client"
    exit 1
fi

echo ""
echo "🎉 Identity Providers setup complete!"
echo ""
echo "🔍 Test your providers:"
echo "   Hosted UI: https://shieldcraft-auth.auth.us-east-1.amazoncognito.com/login?client_id=$CLIENT_ID&response_type=code&scope=email+openid+profile&redirect_uri=https://shieldcraft-ai.com/dashboard"
echo ""
echo "📝 Next steps:"
echo "   1. Test each provider login"
echo "   2. Update your frontend to show multiple login options"
echo "   3. Consider provider-specific user experience"
echo ""
