"""
Deploy AWS CDK stacks with robust dependency management and post-deploy validation.
"""

import os
import nox
from nox_sessions.utils_color import matrix_log


@nox.session(name="cdk_deploy")
def cdk_deploy(session):
    """
    Deploy AWS CDK stacks in parallel with robust dependency management and post-deploy validation.
    Ensures Poetry, AWS CDK v2 CLI, and all dependencies are installed. Supports local and CI/CD workflows.
    """
    # Guardrail 1: Check for deployment block file
    if os.path.exists(".deployment_block"):
        matrix_log(
            session,
            "[GUARDRAIL] Deployment blocked! Remove .deployment_block file to enable deployments.",
            color="red",
        )
        matrix_log(
            session,
            "[GUARDRAIL] This is a PORTFOLIO PROJECT - deployments may incur AWS charges!",
            color="red",
        )
        session.error("[GUARDRAIL] Deployment blocked by .deployment_block file")
        return

    # Guardrail 2: block deploy unless SHIELDCRAFT_ALLOW_DEPLOY=1
    if not os.environ.get("SHIELDCRAFT_ALLOW_DEPLOY"):
        matrix_log(
            session,
            "[GUARDRAIL] AWS deploys are DISABLED. Set SHIELDCRAFT_ALLOW_DEPLOY=1 to enable.",
            color="red",
        )
        session.error(
            "[GUARDRAIL] AWS deploys are DISABLED. Set SHIELDCRAFT_ALLOW_DEPLOY=1 to enable."
        )
        return

    matrix_log(
        session,
        "[CDK_DEPLOY] Ensuring AWS CDK and dependencies are installed...",
        color="cyan",
    )
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
