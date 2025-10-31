from aws_cdk import Stack
from constructs import Construct


class AirbyteStack(Stack):
    def __init__(self, scope: Construct, id: str, *args, **kwargs):
        # Accept and ignore all extra args/kwargs for importability
        super().__init__(
            scope,
            id,
            **{k: v for k, v in kwargs.items() if k in ("env", "description")},
        )
        # Placeholder: Add Airbyte resources here as needed for test importability
