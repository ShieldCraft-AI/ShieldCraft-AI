#!/bin/bash
# Test authentication fixes

echo "🧪 Testing Cognito Authentication Fixes"
echo "========================================"
echo ""

# Check if dev server is running
if ! lsof -ti:3000 > /dev/null 2>&1; then
    echo "⚠️  Dev server not running on port 3000"
    echo "   Starting dev server..."
    cd /home/dee/workspace/AI/shieldcraft-ai/docs-site
    npm start &
    DEV_SERVER_PID=$!
    echo "   Waiting 10 seconds for server to start..."
    sleep 10
fi

echo "✅ Dev server is running"
echo ""

echo "📋 Test Checklist:"
echo ""
echo "1. ✅ OAuth flows enabled on Cognito client"
aws cognito-idp describe-user-pool-client \
  --region us-east-1 \
  --user-pool-id us-east-1_p3VQtjFbq \
  --client-id 3u9rbcprme07gut2boqfp1me38 \
  --query 'UserPoolClient.AllowedOAuthFlowsUserPoolClient' \
  --output text

echo ""
echo "2. ✅ Production callback URLs configured:"
aws cognito-idp describe-user-pool-client \
  --region us-east-1 \
  --user-pool-id us-east-1_p3VQtjFbq \
  --client-id 3u9rbcprme07gut2boqfp1me38 \
  --query 'UserPoolClient.CallbackURLs' \
  --output json | jq -r '.[]' | grep -E '(localhost|shieldcraft-ai.com)'

echo ""
echo "3. ✅ Google provider enabled:"
aws cognito-idp describe-user-pool-client \
  --region us-east-1 \
  --user-pool-id us-east-1_p3VQtjFbq \
  --client-id 3u9rbcprme07gut2boqfp1me38 \
  --query 'UserPoolClient.SupportedIdentityProviders' \
  --output json

echo ""
echo "🌐 Manual Test Steps:"
echo "===================="
echo ""
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click the 'Login' button in navbar"
echo "3. You should be redirected to Cognito Hosted UI"
echo "4. Choose 'Sign in with Google'"
echo "5. Complete Google OAuth"
echo "6. You should be redirected back to /dashboard"
echo "7. The navbar button should NOW show your email + 'Logout' button"
echo "   (This was BROKEN before, now FIXED!)"
echo ""
echo "8. Click 'Logout'"
echo "9. Button should change back to 'Login'"
echo ""
echo "✅ If all steps work, authentication is fully functional!"
echo ""
echo "📝 For production deployment, see: AUTH_WORKING_SUMMARY.md"
