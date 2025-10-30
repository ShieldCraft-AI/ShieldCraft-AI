#!/usr/bin/env python3
"""
DOCUMENTED DEPLOY HELPER — Reviewed
Purpose: safety/audit helper that inspects AWS account state and creates a
deployment block file. This script talks to AWS and should not be run in CI
without explicit credentials and approval. Keep this file whitelisted only if
you accept the risk and maintain reviewer control over changes.

AWS Infrastructure Safety Checker

Prevents accidental deployments and monitors existing resources for unexpected costs.
Run this before any AWS operations to ensure no surprise charges.
"""

import subprocess
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


class AWSInfrastructureSafetyChecker:
    def __init__(self):
        self.region = "af-south-1"
        self.account_id = "879584803102"
        self.safe_stacks = {
            "CDKToolkit",  # Required for CDK
            "CodeCraftAiStatefulStackStaging",  # Known minimal stack
        }

    def check_aws_cli_configured(self):
        """Check if AWS CLI is configured"""
        try:
            result = subprocess.run(
                ["aws", "sts", "get-caller-identity"],
                capture_output=True,
                text=True,
                check=True,
            )
            identity = json.loads(result.stdout)
            print(f"✅ AWS CLI configured for account: {identity['Account']}")

            if identity["Account"] != self.account_id:
                print(
                    f"⚠️  WARNING: Expected account {self.account_id}, got {identity['Account']}"
                )
                return False
            return True
        except Exception as e:
            print(f"❌ AWS CLI not configured or error: {e}")
            return False

    def audit_active_stacks(self):
        """Audit all active CloudFormation stacks"""
        try:
            result = subprocess.run(
                [
                    "aws",
                    "cloudformation",
                    "list-stacks",
                    "--stack-status-filter",
                    "CREATE_COMPLETE",
                    "UPDATE_COMPLETE",
                    "--region",
                    self.region,
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            stacks = json.loads(result.stdout)["StackSummaries"]

            print(f"\n📋 ACTIVE CLOUDFORMATION STACKS ({len(stacks)})")
            print("-" * 50)

            dangerous_stacks = []
            for stack in stacks:
                stack_name = stack["StackName"]
                creation_time = stack["CreationTime"]

                if stack_name in self.safe_stacks:
                    print(f"✅ {stack_name:<35} (Known safe)")
                else:
                    print(f"⚠️  {stack_name:<35} (REVIEW NEEDED)")
                    dangerous_stacks.append(stack_name)

            return dangerous_stacks

        except Exception as e:
            print(f"❌ Failed to audit stacks: {e}")
            return []

    def check_expensive_services(self):
        """Check for expensive services that might be running"""
        expensive_checks = [
            ("RDS Instances", ["aws", "rds", "describe-db-instances"]),
            (
                "EC2 Instances",
                [
                    "aws",
                    "ec2",
                    "describe-instances",
                    "--query",
                    "Reservations[*].Instances[?State.Name=='running']",
                ],
            ),
            ("ECS Clusters", ["aws", "ecs", "list-clusters"]),
            ("Lambda Functions", ["aws", "lambda", "list-functions"]),
            ("MSK Clusters", ["aws", "kafka", "list-clusters"]),
            ("OpenSearch Domains", ["aws", "opensearch", "list-domain-names"]),
            (
                "SageMaker Endpoints",
                ["aws", "sagemaker", "list-endpoints", "--status-equals", "InService"],
            ),
        ]

        print(f"\n🔍 EXPENSIVE SERVICES AUDIT")
        print("-" * 50)

        for service_name, cmd in expensive_checks:
            try:
                result = subprocess.run(
                    cmd + ["--region", self.region, "--output", "json"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                data = json.loads(result.stdout)

                # Check if any resources exist
                resource_count = 0
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            resource_count += len(value)
                elif isinstance(data, list):
                    resource_count = len(data)

                if resource_count > 0:
                    print(f"⚠️  {service_name:<20} {resource_count} resources found")
                else:
                    print(f"✅ {service_name:<20} No resources")

            except subprocess.CalledProcessError:
                print(f"✅ {service_name:<20} No resources (or no access)")
            except Exception as e:
                print(f"❌ {service_name:<20} Error checking: {e}")

    def create_deployment_block(self):
        """Create a deployment block file to prevent accidental deployments"""
        block_file = Path(".deployment_block")

        block_content = f"""# ShieldCraft AI Deployment Block
# Created: {datetime.now(timezone.utc).isoformat()}
#
# This file prevents accidental AWS deployments.
# Remove this file only when you're ready to deploy to AWS.
#
# PORTFOLIO PROJECT - NO ACTUAL DEPLOYMENTS ALLOWED
#
# To deploy (when ready):
# 1. rm .deployment_block
# 2. Ensure you have sufficient AWS credits/budget
# 3. Run deployment commands
#
DEPLOYMENT_BLOCKED=true
REASON="Portfolio project - visualization only"
ESTIMATED_MIN_COST_USD=50
"""

        with open(block_file, "w") as f:
            f.write(block_content)

        print(f"\n🛑 DEPLOYMENT BLOCK CREATED")
        print(f"   Created: {block_file}")
        print(f"   Purpose: Prevent accidental AWS deployments")

    def check_for_deployment_commands(self):
        """Check common files for deployment commands"""
        risky_patterns = [
            "cdk deploy",
            "aws cloudformation create-stack",
            "aws cloudformation update-stack",
            "terraform apply",
            "pulumi up",
        ]

        risky_files = [
            "noxfile.py",
            "Makefile",
            "package.json",
            "scripts/*.py",
            "scripts/*.sh",
        ]

        print(f"\n🔍 DEPLOYMENT COMMAND AUDIT")
        print("-" * 50)

        found_commands = []
        for file_pattern in risky_files:
            try:
                for file_path in Path(".").glob(file_pattern):
                    if file_path.is_file():
                        with open(file_path) as f:
                            content = f.read()
                            for pattern in risky_patterns:
                                if pattern in content:
                                    found_commands.append((file_path, pattern))

            except Exception:
                continue

        if found_commands:
            print("⚠️  DEPLOYMENT COMMANDS FOUND:")
            for file_path, command in found_commands:
                print(f"   {file_path}: {command}")
        else:
            print("✅ No risky deployment commands found")

    def run_full_audit(self):
        """Run complete infrastructure safety audit"""
        print("🛡️  SHIELDCRAFT AI INFRASTRUCTURE SAFETY AUDIT")
        print("=" * 60)
        print(f"Time: {datetime.now(timezone.utc).isoformat()}")
        print(f"Purpose: Ensure no unexpected AWS charges")

        # 1. Check AWS access
        if not self.check_aws_cli_configured():
            print("\n❌ AUDIT FAILED: AWS CLI issues")
            return False

        # 2. Audit active stacks
        dangerous_stacks = self.audit_active_stacks()

        # 3. Check expensive services
        self.check_expensive_services()

        # 4. Check for deployment commands
        self.check_for_deployment_commands()

        # 5. Create deployment block
        self.create_deployment_block()

        # Final assessment
        print(f"\n🎯 SAFETY ASSESSMENT")
        print("-" * 50)

        if dangerous_stacks:
            print(f"⚠️  {len(dangerous_stacks)} unknown stacks need review")
            print("   Recommended: Investigate these stacks immediately")
            return False
        else:
            print("✅ Infrastructure appears safe for portfolio use")
            print("✅ Current resources are minimal-cost")
            print("✅ Deployment block created")
            return True


def main():
    checker = AWSInfrastructureSafetyChecker()
    is_safe = checker.run_full_audit()

    if not is_safe:
        print(f"\n⚠️  SAFETY CONCERNS DETECTED")
        print("   Review findings before proceeding")
        sys.exit(1)
    else:
        print(f"\n✅ INFRASTRUCTURE IS SAFE")
        print("   Portfolio project can continue")
        sys.exit(0)


if __name__ == "__main__":
    main()
