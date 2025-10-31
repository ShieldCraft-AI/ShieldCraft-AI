"""
Example integration of AuthStack into main CDK app.
Add this section to your app.py after the secrets_stack instantiation.
"""

# After secrets_stack instantiation, add:

# ====================
# Authentication Stack
# ====================
from infra.domains.auth_stack import AuthStack

# Example placeholder values for importability only
auth_domain = "localhost:3000"
auth_stack = AuthStack(
    None,
    "ShieldCraftAuthStack",
    domain_name=auth_domain,
    env=None,
)
# No-op for tags in importability context
