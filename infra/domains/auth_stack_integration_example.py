"""
Example integration of AuthStack into main CDK app.
Add this section to your app.py after the secrets_stack instantiation.
"""

# After secrets_stack instantiation, add:

# ====================
# Authentication Stack
# ====================
from infra.domains.auth_stack import AuthStack

# Get your CloudFront distribution domain from config or environment
# For testing, you can use localhost
auth_domain = config.get("app", {}).get("auth_domain", "localhost:3000")

auth_stack = AuthStack(
    app,
    "ShieldCraftAuthStack",
    domain_name=auth_domain,
    env=cdk_env,
)

# Apply standard tags
apply_standard_tags(
    auth_stack,
    project=standard_tags["Project"],
    environment=standard_tags["Environment"],
    owner=standard_tags["Owner"],
    cost_center=standard_tags["CostCenter"],
    team=standard_tags["Team"],
    compliance=standard_tags["Compliance"],
)

# No dependencies needed - auth stack is independent
