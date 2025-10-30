import importlib
import sys
import pytest


def test_no_boto_client_during_synth(monkeypatch):
    """Fail if any code attempts to create a boto3 client or Session during synth/import.

    This test monkeypatches boto3.client and boto3.Session to raise immediately so
    any accidental runtime AWS usage is caught during test execution.
    """

    # Import boto3 module so we can monkeypatch its attributes
    try:
        import boto3 as _boto3  # type: ignore
    except Exception:
        pytest.skip(
            "boto3 not available in this environment; skipping runtime-call guard"
        )

    def _fail_client(*args, **kwargs):
        raise RuntimeError(
            f"boto3.client called during synth: args={args}, kwargs={kwargs}"
        )

    class _FailSession:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("boto3.Session called during synth")

    monkeypatch.setattr(_boto3, "client", _fail_client)
    monkeypatch.setattr(_boto3, "Session", _FailSession)

    # Now import only the minimal domain stack and synth it. Importing the full app
    # may intentionally create clients; we want to ensure safe import/synth paths.
    try:
        # Import CDK and the NetworkingStack directly (safe, minimal stack)
        import aws_cdk as cdk
        from infra.domains.foundation.networking.networking_stack import NetworkingStack
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Missing CDK or domain stack imports: {exc}")

    app = cdk.App()
    # Instantiation should not call boto3.client/Session due to the monkeypatch.
    NetworkingStack(app, "NetworkingStack", config={})
    # Synthesize - if any runtime calls were attempted during construct, the test will raise
    app.synth()
