"""
ShieldCraftAI ComplianceStack: AWS Config rules and compliance automation.
"""

import os
from typing import Any, Dict, List, Literal, Optional
import yaml
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_config as config
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_lambda as lambda_  # pylint: disable=unused-import
from constructs import Construct  # pylint: disable=unused-import
from pydantic import BaseModel, Field, ValidationError  # pylint: disable=unused-import


class ComplianceRuleConfig(BaseModel):
    name: str
    type: Literal["managed", "custom"] = "managed"
    identifier: Optional[str] = None  # For managed rules
    input_parameters: Optional[Dict[str, Any]] = None
    lambda_function_arn: Optional[str] = None  # For custom rules
    lambda_role_arn: Optional[str] = None  # For custom rules


class ComplianceConfig(BaseModel):
    rules: List[ComplianceRuleConfig] = Field(default_factory=list)


def validate_compliance_config(cfg: dict) -> ComplianceConfig:
    try:
        return ComplianceConfig(**cfg)
    except ValidationError as e:
        raise ValueError(f"Invalid Compliance config: {e}") from e


def load_env_config(env: str) -> dict:
    config_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config"
    )
    config_path = os.path.join(config_dir, f"{env}.yml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Config file for environment '{env}' not found: {config_path}"
        )
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class ComplianceStack(Stack):
    """
    CDK Stack for AWS Config compliance rules, managed/custom rule integration, and cross-stack secret management.
    """

    def _validate_cross_stack_resources(self, envs):
        """
        Validate compliance stack parameters and referenced config files.
        Raises ValueError if any required parameter is missing or misconfigured.
        """
        if not isinstance(envs, list) or not envs:
            raise ValueError("envs must be a non-empty list of environment names.")
        for env in envs:
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config"
            )
            config_path = os.path.join(config_dir, f"{env}.yml")
            if not os.path.exists(config_path):
                raise FileNotFoundError(
                    f"Config file for environment '{env}' not found: {config_path}"
                )

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")

    def __init__(
        self,
        scope,
        construct_id,
        config_dict=None,
        compliance_lambda_role_arn=None,
        envs=None,
        secrets_manager_arn=None,
        *args,
        **kwargs,
    ):
        """
        CDK Stack for AWS Config compliance rules, managed/custom rule integration, and cross-stack secret management.
        """
        super().__init__(scope, construct_id, *args, **kwargs)
        self.secrets_manager_arn = secrets_manager_arn
        self.secrets_manager_secret = None
        self.shared_resources = {}
        if self.secrets_manager_arn:
            self.secrets_manager_secret = (
                secretsmanager.Secret.from_secret_complete_arn(
                    self, "ImportedVaultSecret", self.secrets_manager_arn
                )
            )
            CfnOutput(
                self,
                f"{construct_id}VaultSecretArn",
                value=self.secrets_manager_arn,
                export_name=f"{construct_id}-vault-secret-arn",
            )
            self.shared_resources["vault_secret"] = self.secrets_manager_secret

        # --- Begin required_tag_keys validation ---
        default_tags = ["Project", "Environment", "Owner"]
        tags = None
        if config_dict is None:
            tags = default_tags
        else:
            tags_candidate = config_dict.get("required_tag_keys", default_tags)
            if tags_candidate is None:
                tags = default_tags
            elif not isinstance(tags_candidate, list):
                raise TypeError("required_tag_keys must be a list of strings.")
            elif len(tags_candidate) < 3:
                raise IndexError("required_tag_keys must contain at least 3 items.")
            else:
                tags = tags_candidate
        # Only use first 3 tags
        tags = tags[:3]

        # --- Create the required tags managed rule ---
        rule_name = "RequiredTagsRule"
        input_parameters = {
            "tag1Key": tags[0],
            "tag2Key": tags[1],
            "tag3Key": tags[2],
        }
        managed_rule = config.ManagedRule(
            self,
            rule_name,
            identifier="REQUIRED_TAGS",
            input_parameters=input_parameters,
        )
        self._export_resource(f"{rule_name}ArnOutput", managed_rule.config_rule_arn)
