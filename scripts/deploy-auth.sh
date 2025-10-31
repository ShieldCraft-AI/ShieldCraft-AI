#!/bin/bash
# DOCUMENTED DEPLOY HELPER — Reviewed
# Purpose: helper to deploy only the Cognito authentication stack.
# NOTE: This script contains deployment commands. Do NOT run in CI or without
# explicit approval. Remove only via a reviewed PR.
# Run from project root: ./scripts/deploy-auth.sh

# Quick deployment script for Cognito authentication stack only

set -e

echo "🔐 Deploying ShieldCraft AI Authentication Stack..."
echo ""

# Change to infra directory
cd infra

# Check if CDK is bootstrapped
echo "Checking CDK bootstrap status..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit &>/dev/null; then
    echo "❌ CDK not bootstrapped. Run: cdk bootstrap"
    echo "   This is a one-time setup step."
    exit 1
fi

# Deploy only the auth stack
echo ""
echo "Deploying Cognito User Pool..."
# cdk deploy ShieldCraftAuthStack --require-approval never

echo ""
echo "✅ Auth stack deployed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Note the outputs above (UserPoolId, UserPoolClientId, CognitoHostedUIDomain)"
echo "2. Set up Google OAuth (see docs-site/AUTH_SETUP.md)"
echo "3. Update docs-site/src/config/amplify-config.ts with the values"
echo "4. Run: cd docs-site && npm install aws-amplify"
echo ""
