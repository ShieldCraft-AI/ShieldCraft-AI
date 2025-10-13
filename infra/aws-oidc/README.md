This folder contains helper files and commands to create an AWS IAM role for GitHub Actions OIDC trust and an example least-privilege policy used by the monitoring workflows.

Files:
- trust-policy.json - trust policy for the OIDC role (replace YOUR_AWS_ACCOUNT_ID)
- monitoring-policy.json - inline policy for CloudWatch/SNS actions (adjust resources/actions as needed)

Commands (run in your AWS account, with aws CLI configured):

# 1. (Optional) Create OIDC provider (only if not already created)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# 2. Create role with trust policy
aws iam create-role \
  --role-name github-actions-shieldcraft-oidc-role \
  --assume-role-policy-document file://infra/aws-oidc/trust-policy.json

# 3. Attach inline policy for monitoring
aws iam put-role-policy \
  --role-name github-actions-shieldcraft-oidc-role \
  --policy-name ShieldCraftMonitoringPolicy \
  --policy-document file://infra/aws-oidc/monitoring-policy.json

# 4. Get the role ARN
aws iam get-role --role-name github-actions-shieldcraft-oidc-role --query 'Role.Arn' --output text

# 5. Set repository secret with the role ARN (run locally; replace with real ARN)
# Install gh and authenticate first: gh auth login --web
gh secret set AWS_OIDC_ROLE_ARN -b"arn:aws:iam::123456789012:role/github-actions-shieldcraft-oidc-role" --repo ShieldCraft-AI/ShieldCraft-AI

# 6. Update workflows to use role-to-assume and add permissions:
# - Add at top-level of each workflow:
# permissions:
#   id-token: write
#   contents: read

# - Replace configure-aws-credentials steps with:
# - name: Configure AWS credentials (OIDC)
#   uses: aws-actions/configure-aws-credentials@v4
#   with:
#     role-to-assume: ${{ secrets.AWS_OIDC_ROLE_ARN }}
#     aws-region: us-east-1

# 7. Rerun failing workflows or push an empty commit to trigger runs
# git commit --allow-empty -m "chore(ci): test OIDC role" && git push origin main

Adjust trust policy 'token.actions.githubusercontent.com:sub' condition or the IAM policy as needed for other branches or environments.
