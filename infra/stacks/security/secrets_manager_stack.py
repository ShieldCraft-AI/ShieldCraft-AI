"""
ShieldCraftAI SecretsManagerStack: Centralized secrets management using AWS Secrets Manager.
Creates and exports secrets for cross-stack consumption.
"""

from typing import Dict, Optional  # pylint: disable=unused-import
from constructs import Construct  # pylint: disable=unused-import
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_secretsmanager as secretsmanager


class SecretsManagerStack(Stack):
    def __init__(self, scope, construct_id, *args, **kwargs):
        secrets_config = kwargs.pop("secrets_config", None)
        shared_tags = kwargs.pop("shared_tags", None)
        environment = kwargs.pop("environment", None)
        if secrets_config is None:
            secrets_config = {}
        super().__init__(scope, construct_id, *args, **kwargs)
        tags_to_apply = {"Project": "ShieldCraftAI"}
        if environment:
            # Use region if available, else fallback to string
            region = getattr(environment, "region", None)
            env_tag = region if region else str(environment)
            tags_to_apply["Environment"] = env_tag
        if shared_tags:
            tags_to_apply.update(shared_tags)
        for k, v in tags_to_apply.items():
            self.tags.set_tag(str(k), str(v))

        self.secrets = {}
        for secret_name, secret_props in secrets_config.items():
            # Config validation
            if not isinstance(secret_props, dict):
                raise ValueError(f"Secret config for {secret_name} must be a dict.")
            name = secret_props.get("name", secret_name)
            if not name:
                raise ValueError(f"Secret {secret_name} must have a name.")
            description = secret_props.get("description", f"Secret for {secret_name}")
            # Prefix secret name with environment/project for uniqueness
            full_name = f"{environment or 'dev'}-{name}"
            # Resource policy support (optional)
            resource_policy = secret_props.get("resource_policy")
            secret = secretsmanager.Secret(
                self,
                secret_name,
                secret_name=full_name,
                description=description,
                generate_secret_string=(
                    secretsmanager.SecretStringGenerator(
                        secret_string_template=secret_props.get("template", "{}"),
                        generate_string_key=secret_props.get(
                            "generate_key", "password"
                        ),
                        exclude_characters=secret_props.get("exclude_characters", ""),
                    )
                    if secret_props.get("generate", False)
                    else None
                ),
            )
            # Tags are applied at the stack level and propagate to child resources
            # Attach resource policy if provided
            if resource_policy:
                secret.add_to_resource_policy(resource_policy)
            self.secrets[secret_name] = secret
            CfnOutput(
                self,
                f"{secret_name}Arn",
                value=secret.secret_arn,
                export_name=f"{self.stack_name}-{secret_name}-arn",
            )
