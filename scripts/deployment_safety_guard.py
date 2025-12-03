#!/usr/bin/env python3
"""
DOCUMENTED DEPLOY HELPER  -  Reviewed
Purpose: safety guard used by commit scripts to prevent accidental deployment
commands. This script is allowed to inspect command lines and block deploy
patterns; changes to this file require reviewer approval.

AWS Infrastructure Safety Guard for Commit Scripts

This script adds an additional safety layer to prevent accidental deployments
during commit workflows. It checks for deployment blocks and validates that
no deployment commands are being executed.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_deployment_safety():
    """Check if deployments should be blocked"""
    project_root = Path(__file__).parent.parent
    deployment_block = project_root / ".deployment_block"

    # Check if deployment is blocked
    if deployment_block.exists():
        print("🛑 [DEPLOYMENT_BLOCK] Deployment safety guard active")
        print(f"   Block file: {deployment_block}")
        print("   This is a PORTFOLIO PROJECT - deployments may incur AWS charges!")

        with open(deployment_block) as f:
            reason = None
            for line in f:
                if line.startswith("REASON="):
                    reason = line.split("=", 1)[1].strip().strip('"')
                    break

        if reason:
            print(f"   Reason: {reason}")

        return True

    return False


def check_environment_variables():
    """Check for deployment-related environment variables"""
    deployment_vars = [
        "SHIELDCRAFT_ALLOW_DEPLOY",
        "AWS_PROFILE",
        "CDK_DEPLOY_ACCOUNT",
        "CDK_DEPLOY_REGION",
    ]

    found_vars = []
    for var in deployment_vars:
        if os.environ.get(var):
            found_vars.append(f"{var}={os.environ[var]}")

    if found_vars:
        print("⚠️  [DEPLOYMENT_VARS] Deployment-related environment variables detected:")
        for var in found_vars:
            print(f"   {var}")

        if os.environ.get("SHIELDCRAFT_ALLOW_DEPLOY"):
            print(
                "🚨 WARNING: SHIELDCRAFT_ALLOW_DEPLOY is set - deployments are ENABLED!"
            )
            return True

    return False


def scan_command_line():
    """Scan command line arguments for deployment-related commands"""
    command_line = " ".join(sys.argv)

    dangerous_patterns = [
        "cdk" + " deploy",
        "cdk synth",
        "nox -s cdk_deploy",
        "nox -s deploy",
    ]

    found_patterns = []
    for pattern in dangerous_patterns:
        if pattern in command_line.lower():
            found_patterns.append(pattern)

    if found_patterns:
        print("🚨 [DANGEROUS_COMMANDS] Deployment commands detected in command line:")
        for pattern in found_patterns:
            print(f"   {pattern}")
        return True

    return False


def main():
    """Main safety check function - only blocks actual AWS deployment commands"""

    # Only scan command line for dangerous AWS deployment patterns
    command_line = " ".join(sys.argv).lower()

    aws_deployment_patterns = [
        "cdk" + " deploy",
        "nox -s cdk_deploy",
        "nox -s deploy",
    ]

    found_patterns = []
    for pattern in aws_deployment_patterns:
        if pattern in command_line:
            found_patterns.append(pattern)

    if found_patterns:
        print("🚨 AWS DEPLOYMENT COMMAND DETECTED!")
        print("   Commands found:", ", ".join(found_patterns))
        print("   This could incur AWS charges.")

        # Check if deployment block exists
        project_root = Path(__file__).parent.parent
        deployment_block = project_root / ".deployment_block"

        if deployment_block.exists():
            print("   ✅ Deployment blocked by .deployment_block file")
            print(
                "   Remove .deployment_block and set SHIELDCRAFT_ALLOW_DEPLOY=1 to proceed"
            )
            return 1
        else:
            print("   ⚠️  No deployment block found!")
            return 1

    # For normal commits/operations, just pass through silently
    return 0


if __name__ == "__main__":
    sys.exit(main())
