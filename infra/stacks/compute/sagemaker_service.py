from aws_cdk import Stack


class SageMakerStack(Stack):
    def __init__(self, scope, id, *args, **kwargs):
        # Accept and ignore all extra args/kwargs for importability
        super().__init__(
            scope,
            id,
            **{k: v for k, v in kwargs.items() if k in ("env", "description")},
        )
        # Stub for SageMaker stack
