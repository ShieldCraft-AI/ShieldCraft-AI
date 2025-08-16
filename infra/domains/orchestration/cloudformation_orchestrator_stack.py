"""
ShieldCraft AI CloudFormation Orchestration Service
Scaffolding for managing, monitoring, and automating CloudFormation stacks for all major domains.
"""

from typing import List, Dict, Optional, Any
import threading
import logging
import boto3
import botocore

logging.basicConfig(level=logging.INFO)


class CloudFormationService:
    def __init__(self, region_name: str = "us-east-1", environment: str = "dev"):
        self.client = boto3.client("cloudformation", region_name=region_name)
        self.environment = environment

    def create_stack(
        self,
        stack_name: str,
        template_url: str,
        parameters: Optional[List[Dict]] = None,
        capabilities: Optional[List[str]] = None,
    ) -> Dict:
        """Create a new CloudFormation stack."""
        stack_name_env = f"{stack_name}-{self.environment}"
        params = {
            "StackName": stack_name_env,
            "TemplateURL": template_url,
        }
        if parameters:
            params["Parameters"] = parameters
        if capabilities:
            params["Capabilities"] = capabilities
        logging.info("Creating stack: %s", stack_name_env)
        return self.client.create_stack(**params)

    def update_stack(
        self,
        stack_name: str,
        template_url: str,
        parameters: Optional[List[Dict]] = None,
        capabilities: Optional[List[str]] = None,
    ) -> Dict:
        """Update an existing CloudFormation stack."""
        stack_name_env = f"{stack_name}-{self.environment}"
        params = {
            "StackName": stack_name_env,
            "TemplateURL": template_url,
        }
        if parameters:
            params["Parameters"] = parameters
        if capabilities:
            params["Capabilities"] = capabilities
        logging.info("Updating stack: %s", stack_name_env)
        return self.client.update_stack(**params)

    def delete_stack(self, stack_name: str) -> Dict:
        """Delete a CloudFormation stack."""
        stack_name_env = f"{stack_name}-{self.environment}"
        logging.info("Deleting stack: %s", stack_name_env)
        return self.client.delete_stack(StackName=stack_name_env)

    def get_stack_status(self, stack_name: str) -> Optional[str]:
        """Get the current status of a stack."""
        stack_name_env = f"{stack_name}-{self.environment}"
        try:
            resp = self.client.describe_stacks(StackName=stack_name_env)
            status = resp["Stacks"][0]["StackStatus"]
            logging.info("Stack %s status: %s", stack_name_env, status)
            return status
        except botocore.exceptions.ClientError as e:
            if "does not exist" in str(e):
                return None
            raise

    def list_stacks(self, status_filter: Optional[List[str]] = None) -> List[Dict]:
        """List all CloudFormation stacks, optionally filtered by status."""
        params = {}
        if status_filter:
            params["StackStatusFilter"] = status_filter
        resp = self.client.list_stacks(**params)
        stacks = [
            s
            for s in resp.get("StackSummaries", [])
            if self.environment in s["StackName"]
        ]
        logging.info(
            "Stacks in %s: %s", self.environment, [s["StackName"] for s in stacks]
        )
        return stacks

    def get_stack_events(self, stack_name: str) -> List[Dict]:
        """Get recent events for a stack."""
        stack_name_env = f"{stack_name}-{self.environment}"
        resp = self.client.describe_stack_events(StackName=stack_name_env)
        return resp.get("StackEvents", [])

    def detect_drift(self, stack_name: str) -> Dict:
        """Initiate drift detection for a stack."""
        stack_name_env = f"{stack_name}-{self.environment}"
        logging.info("Detecting drift for stack: %s", stack_name_env)
        return self.client.detect_stack_drift(StackName=stack_name_env)

    def get_stack_outputs(self, stack_name: str) -> Dict:
        """Get outputs from a stack (for cross-stack references)."""
        stack_name_env = f"{stack_name}-{self.environment}"
        resp = self.client.describe_stacks(StackName=stack_name_env)
        return resp["Stacks"][0].get("Outputs", {})

    def deploy_stacks_with_dependencies(self, stack_defs: List[Dict[str, Any]]) -> None:
        """
        Deploy stacks in order, respecting dependencies.
        stack_defs: List of dicts with keys: name, template_url, parameters, capabilities, depends_on (list of stack names)
        """
        deployed = set()
        stack_map = {s["name"]: s for s in stack_defs}

        def deploy_stack(stack):
            # Wait for dependencies
            for dep in stack.get("depends_on", []):
                while self.get_stack_status(dep) not in [
                    "CREATE_COMPLETE",
                    "UPDATE_COMPLETE",
                ]:
                    logging.info("Waiting for dependency %s to complete...", dep)
            self.create_stack(
                stack["name"],
                stack["template_url"],
                stack.get("parameters"),
                stack.get("capabilities"),
            )
            deployed.add(stack["name"])

        for stack in stack_defs:
            if not stack.get("depends_on"):
                threading.Thread(target=deploy_stack, args=(stack,)).start()
        for stack in stack_defs:
            if stack.get("depends_on"):
                deploy_stack(stack)

    # Stub for future Proton integration
    def deploy_proton_template(
        self, template_name: str, parameters: Optional[Dict] = None
    ) -> None:
        """Deploy a Proton template (to be implemented after CloudFormation orchestration is robust)."""
        logging.info(
            "[Proton] Deploying template: %s with parameters: %s",
            template_name,
            parameters,
        )
