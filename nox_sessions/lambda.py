"""
lambda.py - Nox sessions for managing AWS Lambda functions.
"""

import os
import nox

LAMBDA_DIR = "lambda"


@nox.session()
def lint(session):
    """Lint all Lambda code."""
    session.run("poetry", "run", "flake8", LAMBDA_DIR)


@nox.session()
def test(session):
    """Run unit tests for all Lambda functions."""
    session.run("poetry", "run", "pytest", LAMBDA_DIR)


@nox.session()
def package(session):
    """Package Lambda functions for deployment."""
    for fn in os.listdir(LAMBDA_DIR):
        fn_path = os.path.join(LAMBDA_DIR, fn)
        if os.path.isdir(fn_path):
            session.run("poetry", "build", external=True)


@nox.session()
def deploy(session):
    """Deploy Lambdas using AWS CLI v2.27.50 via CDK."""
    import os
    from nox_sessions.utils_color import matrix_log

    # Guardrail 1: Check for deployment block file
    if os.path.exists(".deployment_block"):
        matrix_log(
            session,
            "[GUARDRAIL] Lambda deployment blocked! Remove .deployment_block file to enable deployments.",
            color="red",
        )
        matrix_log(
            session,
            "[GUARDRAIL] This is a PORTFOLIO PROJECT - deployments may incur AWS charges!",
            color="red",
        )
        session.error("[GUARDRAIL] Lambda deployment blocked by .deployment_block file")
        return

    # Guardrail 2: block deploy unless SHIELDCRAFT_ALLOW_DEPLOY=1
    if not os.environ.get("SHIELDCRAFT_ALLOW_DEPLOY"):
        matrix_log(
            session,
            "[GUARDRAIL] Lambda deploys are DISABLED. Set SHIELDCRAFT_ALLOW_DEPLOY=1 to enable.",
            color="red",
        )
        session.error(
            "[GUARDRAIL] Lambda deploys are DISABLED. Set SHIELDCRAFT_ALLOW_DEPLOY=1 to enable."
        )
        return

    session.run(
        "aws",
        "cloudformation",
        "deploy",
        "--template-file",
        "cdk.out/LambdaStack.template.json",
        "--stack-name",
        "ShieldCraftLambda",
        external=True,
    )
