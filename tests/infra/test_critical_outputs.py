from aws_cdk import App, CfnOutput
import pytest

from infra.domains.foundation.identity_security.secrets_manager_stack import (
    SecretsManagerStack,
)
from infra.domains.data_platform.storage.s3_stack import S3Stack


@pytest.mark.unit
def test_secrets_manager_exports_present():
    app = App()
    stack = SecretsManagerStack(app, "TestSecretsManagerStack", config={})
    outputs = [c for c in stack.node.children if isinstance(c, CfnOutput)]
    names = [o.node.id for o in outputs]
    assert any("Secret" in n or "Arn" in n for n in names)


@pytest.mark.unit
def test_s3_exports_present():
    app = App()
    stack = S3Stack(app, "TestS3Stack", config={})
    outputs = [c for c in stack.node.children if isinstance(c, CfnOutput)]
    names = [o.node.id for o in outputs]
    assert any("Bucket" in n or "Arn" in n or "Name" in n for n in names)
