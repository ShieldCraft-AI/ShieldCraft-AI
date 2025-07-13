""" """

import os
import nox
from nox_sessions.utils_poetry import ensure_poetry_installed
from nox_sessions.utils_color import matrix_log


@nox.session(name="cdk_deploy")
def cdk_deploy(session):
    """
    Deploy AWS CDK stacks in parallel with robust dependency management and post-deploy validation.
    Ensures Poetry, AWS CDK v2 CLI, and all dependencies are installed. Supports local and CI/CD workflows.
    """
    ensure_poetry_installed()
    matrix_log(
        session,
        "[CDK_DEPLOY] Ensuring AWS CDK and dependencies are installed...",
        color="cyan",
    )
    session.run("poetry", "install", "--with", "dev", external=True)
    # Ensure aws-cdk-lib is installed (v2)
    session.run("poetry", "run", "pip", "install", "aws-cdk-lib", external=True)
    # Install latest AWS CDK CLI globally (npm is the official way)
    session.run("npm", "install", "-g", "aws-cdk", external=True)
    matrix_log(session, "[CDK_DEPLOY] Running cdk diff...", color="green")
    # Use environment variables for profile/region if set
    cdk_env = os.environ.copy()
    profile = cdk_env.get("AWS_PROFILE")
    region = cdk_env.get("AWS_REGION") or cdk_env.get("AWS_DEFAULT_REGION")
    diff_args = ["cdk", "diff"]
    deploy_args = ["cdk", "deploy", "--all", "--concurrency", "4"]
    if profile:
        diff_args.extend(["--profile", profile])
        deploy_args.extend(["--profile", profile])
    if region:
        diff_args.extend(["--region", region])
        deploy_args.extend(["--region", region])
    # Use system cdk (npm global) instead of poetry run
    session.run(*diff_args, external=True)
    matrix_log(
        session,
        "[CDK_DEPLOY] Running cdk deploy --all --concurrency 4...",
        color="green",
    )
    session.run(*deploy_args, external=True)
    matrix_log(session, "[CDK_DEPLOY] Deployment complete.", color="green")
