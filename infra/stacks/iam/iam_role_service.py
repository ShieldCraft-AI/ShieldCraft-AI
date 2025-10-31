from aws_cdk import Stack
from constructs import Construct


class IamRoleStack(Stack):
    def __init__(self, scope: Construct, id: str, *args, **kwargs):
        # Accept and ignore all extra args/kwargs for importability
        super().__init__(
            scope,
            id,
            **{k: v for k, v in kwargs.items() if k in ("env", "description")},
        )
        # Placeholder: Add IAM role resources here as needed for test importability
