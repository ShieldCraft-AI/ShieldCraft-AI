#!/bin/bash
# Safe deployment script for auth stack only
# Uses standalone auth_app.py to avoid synthesizing expensive stacks

set -e

echo "🔐 Deploying Authentication Stack (Isolated)"
echo ""
echo "⚠️  This will create:"
echo "   - 1 Cognito User Pool (FREE tier: 50k MAU)"
echo "   - 1 User Pool Client (FREE)"
echo "   - 1 Cognito Domain (FREE)"
echo ""
echo "💰 Estimated cost: \$0/month (under free tier limits)"
echo ""

# Confirm before proceeding
read -p "Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

cd infra

# Check CDK bootstrap
echo ""
echo "Checking CDK bootstrap..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit &>/dev/null; then
    echo "⚠️  CDK not bootstrapped. Run: poetry run cdk bootstrap"
    exit 1
fi

# Show what will be created (dry run)
echo ""
echo "📋 Showing changes (dry run)..."
poetry run cdk diff --app "python auth_app.py" ShieldCraftAuthStack

echo ""
read -p "Deploy these changes? (yes/no): " deploy_confirm
if [ "$deploy_confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Deploy using isolated app
echo ""
echo "Deploying..."
poetry run cdk deploy --app "python auth_app.py" ShieldCraftAuthStack --require-approval never

echo ""
echo "✅ Auth stack deployed!"
echo ""
echo "📋 SAVE THESE VALUES:"
echo "   Check the outputs above for:"
echo "   - UserPoolId"
echo "   - UserPoolClientId"
echo "   - CognitoHostedUIDomain"
echo ""
