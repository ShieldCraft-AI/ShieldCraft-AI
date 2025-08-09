"""
ShieldCraft AI Control Tower Orchestration Service
Automates landing zone setup, guardrail management, and organizational unit
operations using AWS CLI v2.27.50 and boto3.
"""

import subprocess
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("shieldcraft.controltower")
logger.setLevel(logging.INFO)


class ControlTowerService:
    def __init__(self, region_name="us-east-1"):
        self.region = region_name
        self.session = boto3.Session(region_name=region_name)
        self.ct_client = self.session.client("controltower")
        self.org_client = self.session.client("organizations")

    def create_landing_zone(self, landing_zone_name, ou_name):
        """
        Create a Control Tower landing zone and organizational unit using AWS CLI v2.27.50.
        Validates input and handles unhappy paths robustly.
        """
        if not landing_zone_name or not ou_name:
            logger.error("Landing zone name and OU name must be provided.")
            raise ValueError("Landing zone name and OU name are required.")
        try:
            cmd = [
                "aws",
                "controltower",
                "create-landing-zone",
                "--landing-zone-name",
                landing_zone_name,
                "--region",
                self.region,
            ]
            logger.info("Creating landing zone: %s", landing_zone_name)
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Landing zone creation output: %s", result.stdout)
            response = self.org_client.create_organizational_unit(
                ParentId=self.get_root_id(), Name=ou_name
            )
            logger.info(
                "Created OU: %s (ID: %s)", ou_name, response["OrganizationalUnit"]["Id"]
            )
            return response["OrganizationalUnit"]["Id"]
        except subprocess.CalledProcessError as e:
            logger.error("AWS CLI error: %s", e)
            raise RuntimeError(f"Landing zone creation failed: {e}")
        except ClientError as e:
            logger.error("Boto3 error: %s", e)
            raise RuntimeError(f"Organizational unit creation failed: {e}")

    def get_root_id(self):
        """Get the root ID for the AWS Organization."""
        roots = self.org_client.list_roots()
        return roots["Roots"][0]["Id"]

    def enable_guardrail(self, guardrail_name, landing_zone_id):
        """
        Enable a Control Tower guardrail using AWS CLI v2.27.50.
        Validates input and handles unhappy paths robustly.
        """
        if not guardrail_name or not landing_zone_id:
            logger.error("Guardrail name and landing zone ID must be provided.")
            raise ValueError("Guardrail name and landing zone ID are required.")
        try:
            cmd = [
                "aws",
                "controltower",
                "enable-guardrail",
                "--guardrail-name",
                guardrail_name,
                "--landing-zone-id",
                landing_zone_id,
                "--region",
                self.region,
            ]
            logger.info(
                "Enabling guardrail: %s on landing zone %s",
                guardrail_name,
                landing_zone_id,
            )
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Guardrail enable output: %s", result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error("AWS CLI error: %s", e)
            raise RuntimeError(f"Guardrail enable failed: {e}")

    def list_landing_zones(self):
        """List existing Control Tower landing zones using AWS CLI v2.27.50."""
        try:
            cmd = ["aws", "controltower", "list-landing-zones", "--region", self.region]
            logger.info("Listing landing zones...")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Landing zones output: %s", result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error("AWS CLI error: %s", e)
            raise RuntimeError(f"Listing landing zones failed: {e}")

    def list_guardrails(self, landing_zone_id):
        """List guardrails for a landing zone using AWS CLI v2.27.50."""
        if not landing_zone_id:
            logger.error("Landing zone ID must be provided.")
            raise ValueError("Landing zone ID is required.")
        try:
            cmd = [
                "aws",
                "controltower",
                "list-guardrails",
                "--landing-zone-id",
                landing_zone_id,
                "--region",
                self.region,
            ]
            logger.info("Listing guardrails for landing zone %s", landing_zone_id)
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Guardrails output: %s", result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error("AWS CLI error: %s", e)
            raise RuntimeError(f"Listing guardrails failed: {e}")
