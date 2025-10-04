#!/usr/bin/env python3
"""
Standalone CDK app for authentication stack ONLY.
Completely isolated from main app.py to avoid synthesizing expensive stacks.

Usage: cdk deploy --app "python infra/auth_app.py"
"""

import aws_cdk as cdk
from infra.domains.auth_stack import AuthStack

app = cdk.App()

# Simple, isolated auth stack
# No dependencies, no expensive resources
auth_stack = AuthStack(
    app,
    "ShieldCraftAuthStack",
    domain_name="shieldcraft-ai.com",  # Production custom domain
    env=cdk.Environment(
        region="us-east-1",  # Cognito in us-east-1
        account=None,  # Uses default AWS account
    ),
)

# Tags for cost tracking
cdk.Tags.of(auth_stack).add("Project", "shieldcraft-ai")
cdk.Tags.of(auth_stack).add("Component", "auth")
cdk.Tags.of(auth_stack).add("CostCenter", "portfolio")

app.synth()
