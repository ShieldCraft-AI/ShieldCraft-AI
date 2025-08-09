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
