"""
LakeFormation Stack for ShieldCraft AI
"""

import logging
import re
from typing import Optional
from aws_cdk import RemovalPolicy, Stack, CfnOutput, Fn, Token
from aws_cdk import aws_lakeformation as lakeformation
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import aws_events as events
from aws_cdk import Tags

from constructs import Construct
from pydantic import BaseModel, Field, ValidationError


# --- Pydantic Models for LakeFormation Config ---
class LakeFormationResourceModel(BaseModel):
    databaseName: str = Field(..., min_length=1)
    tableName: str | None = None
    arn: str | None = None


class LakeFormationPermissionModel(BaseModel):
    template: str | None = None
    principal: str
    resource_type: str
    resource: dict
    actions: list[str] | None = None


class LakeFormationConfigModel(BaseModel):
    admin_role: str
    data_lake_location: str
    permissions: list[LakeFormationPermissionModel]


class LakeFormationStack(Stack):
    # Permission templates for common roles (can be extended via config)
    default_permission_templates = {
        "etl": {
            "table": ["SELECT", "DESCRIBE"],
            "bucket": ["DATA_LOCATION_ACCESS"],
        },
        "read_only": {
            "table": ["SELECT"],
            "bucket": ["DATA_LOCATION_ACCESS"],
        },
        "admin": {
            "database": ["ALL"],
            "table": ["ALL"],
            "bucket": ["ALL"],
        },
    }
    valid_actions = {"ALL", "SELECT", "DESCRIBE", "ALTER", "DATA_LOCATION_ACCESS"}

    def _validate_lakeformation_permissions(
        self,
        permissions,
        s3_bucket_ids,
        glue_crawler_resources,
        glue_db_name,
        exported_opensearch_domains,
        exported_sagemaker_endpoints,
        permission_templates,
    ):
        exported_sagemaker_models = set()
        for perm_cfg in permissions:
            template = perm_cfg.get("template")
            principal = perm_cfg.get("principal")
            resource_type = perm_cfg.get("resource_type")
            resource = perm_cfg.get("resource")
            actions = perm_cfg.get("actions")

            # Template logic
            if template:
                if template not in permission_templates:
                    raise ValueError(f"Unknown permission template: {template}")
                if resource_type not in permission_templates[template]:
                    raise ValueError(
                        f"Template '{template}' does not support resource type '{resource_type}'"
                    )
                actions = permission_templates[template][resource_type]

            if not principal or not resource or not actions:
                raise ValueError(
                    f"Permission config must include principal, resource, and actions. {perm_cfg}"
                )

            # --- Resource mapping for Glue/S3 ---
            if resource_type == "table":
                bucket_id = (
                    resource.get("bucketId")
                    or resource.get("bucket_id")
                    or resource.get("bucket")
                )
                if bucket_id:
                    if bucket_id not in s3_bucket_ids:
                        raise ValueError(
                            f"LakeFormation permission references unknown bucketId: {bucket_id}"
                        )
                    if bucket_id in glue_crawler_resources:
                        resource["tableArn"] = glue_crawler_resources[bucket_id][
                            "table_arn"
                        ]
                        resource["tableName"] = glue_crawler_resources[bucket_id][
                            "table_name"
                        ]
                        resource["databaseName"] = glue_db_name
                    else:
                        resource["databaseName"] = glue_db_name
                else:
                    resource["databaseName"] = glue_db_name
            if resource_type == "bucket":
                bucket_id = (
                    resource.get("bucketId")
                    or resource.get("bucket_id")
                    or resource.get("bucket")
                )
                if bucket_id:
                    if bucket_id not in s3_bucket_ids:
                        raise ValueError(
                            f"LakeFormation permission references unknown bucketId: {bucket_id}"
                        )
                    if bucket_id in glue_crawler_resources:
                        resource["arn"] = glue_crawler_resources[bucket_id][
                            "bucket_arn"
                        ]
            if resource_type == "opensearch_domain":
                domain_name = (
                    resource.get("domainName")
                    or resource.get("domain_name")
                    or resource.get("name")
                )
                if not domain_name:
                    raise ValueError(
                        f"LakeFormation permission OpenSearch must include domainName. {resource}"
                    )
                if domain_name not in exported_opensearch_domains:
                    raise ValueError(
                        f"LakeFormation permission unknown OpenSearch domain: {domain_name}"
                    )
            if resource_type == "sagemaker_model":
                model_name = (
                    resource.get("modelName")
                    or resource.get("model_name")
                    or resource.get("name")
                )
                if not model_name:
                    raise ValueError(
                        f"LF permission SageMaker must include modelName{resource}"
                    )
                if model_name not in exported_sagemaker_models:
                    raise ValueError(
                        f"LF permission references unknown SageMaker model: {model_name}"
                    )
            if resource_type == "sagemaker_endpoint":
                endpoint_name = (
                    resource.get("endpointName")
                    or resource.get("endpoint_name")
                    or resource.get("name")
                )
                if not endpoint_name:
                    raise ValueError(
                        f"LF permission SageMaker must include endpointName. {resource}"
                    )
                if endpoint_name not in exported_sagemaker_endpoints:
                    raise ValueError(
                        f"LF permission unknown SageMaker endpoint: {endpoint_name}"
                    )

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: dict,
        s3_buckets: Optional[dict] = None,
        shared_tags: Optional[dict] = None,
        lakeformation_admin_role_arn: Optional[str] = None,
        secrets_manager_arn: Optional[str] = None,
        **kwargs,
    ):
        stack_kwargs = {
            k: kwargs[k] for k in ("env", "tags", "description") if k in kwargs
        }
        super().__init__(scope, construct_id, **stack_kwargs)
        self._validate_cross_stack_resources(config)
        self.logger = logging.getLogger(f"LakeFormationStack-{construct_id}")
        # Vault integration: import the main secrets manager secret if provided
        self.secrets_manager_arn = secrets_manager_arn
        self.secrets_manager_secret = None
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
        lf_cfg = config.get("lakeformation", {})
        # Support custom permission templates via config
        permission_templates = lf_cfg.get(
            "permission_templates", self.default_permission_templates
        )
        env = config.get("app", {}).get("env", "dev")
        # Validate LakeFormation config using Pydantic
        try:
            LakeFormationConfigModel(**lf_cfg)
        except ValidationError as e:
            self.logger.error(f"LakeFormation config validation error: {e}")
            CfnOutput(
                self,
                f"{construct_id}ConfigError",
                value=str(e),
                export_name=f"{construct_id}-lakeformation-config-error",
            )
            raise ValueError(f"Invalid LakeFormation config: {e}") from e

        # --- Import GlueStack Outputs for LakeFormation Permissions ---
        # Fn already imported at top

        glue_db_name = Fn.import_value("GlueStack-glue-db-name")
        Fn.import_value("GlueStack-glue-db-arn")
        # For each crawler-enabled bucket, import table and bucket ARNs
        glue_crawler_resources = {}
        s3_cfg = config.get("s3", {})
        buckets_cfg = s3_cfg.get("buckets", [])
        for bucket_cfg in buckets_cfg:
            if not bucket_cfg.get("enable_glue_crawler", False):
                continue
            bucket_id = bucket_cfg.get("id") or bucket_cfg.get("name")
            name = f"{bucket_id}Crawler"
            table_name = Fn.import_value(f"GlueStack-glue-crawler-{name}-table-name")
            table_arn = Fn.import_value(f"GlueStack-glue-crawler-{name}-table-arn")
            bucket_arn = Fn.import_value(f"GlueStack-glue-crawler-{name}-bucket-arn")
            glue_crawler_resources[bucket_id] = {
                "table_name": table_name,
                "table_arn": table_arn,
                "bucket_arn": bucket_arn,
            }

        # --- Import OpenSearchStack Outputs for LakeFormation Permissions ---
        opensearch_cfg = config.get("opensearch", {})
        opensearch_domain_cfg = opensearch_cfg.get("domain", {})
        opensearch_domain_name = opensearch_domain_cfg.get("name")
        opensearch_domain_arn = None
        exported_opensearch_domains = set()
        if opensearch_domain_name:
            opensearch_domain_arn = Fn.import_value(
                f"OpenSearchStack-opensearch-domain-arn"
            )
            exported_opensearch_domains.add(opensearch_domain_name)

        # --- Import SageMakerStack Outputs for LakeFormation Permissions ---
        sagemaker_cfg = config.get("sagemaker", {})
        sagemaker_model_name = sagemaker_cfg.get("model_name")
        sagemaker_endpoint_name = sagemaker_cfg.get("endpoint_name")
        sagemaker_model_arn = None
        exported_sagemaker_models = set()
        exported_sagemaker_endpoints = set()
        if sagemaker_model_name:
            sagemaker_model_arn = Fn.import_value("shieldcraft-model-model-arn")
            exported_sagemaker_models.add(sagemaker_model_name)
        if sagemaker_endpoint_name:
            Fn.import_value("shieldcraft-model-endpoint-arn")
            exported_sagemaker_endpoints.add(sagemaker_endpoint_name)

        # Tagging for traceability and custom tags
        tags_to_apply = {"Project": "ShieldCraftAI", "Environment": env}
        tags_to_apply.update(lf_cfg.get("tags", {}))
        if shared_tags:
            tags_to_apply.update(shared_tags)
        for k, v in tags_to_apply.items():
            self.tags.set_tag(k, v)

        # --- Lake Formation S3 Resources ---
        buckets = lf_cfg.get("buckets", [])
        self.shared_resources = {}
        self.resources = []
        if s3_buckets:
            bucket_items = s3_buckets.items() if isinstance(s3_buckets, dict) else []
            if not bucket_items:
                self.logger.error(
                    "s3_buckets must be a non-empty dict of bucket constructs."
                )
                CfnOutput(
                    self,
                    f"{construct_id}S3BucketsError",
                    value="s3_buckets must be a non-empty dict of bucket constructs.",
                    export_name=f"{construct_id}-lakeformation-s3-buckets-error",
                )
                raise ValueError(
                    "s3_buckets must be a non-empty dict of bucket constructs."
                )
            for bucket_id, bucket in bucket_items:
                name = getattr(bucket, "bucket_name", None)
                arn = getattr(bucket, "bucket_arn", None)
                if not name or not arn:
                    self.logger.error(
                        f"S3 bucket construct must have bucket_name and bucket_arn. Got: {bucket}"
                    )
                    CfnOutput(
                        self,
                        f"{construct_id}BucketError{bucket_id}",
                        value=f"S3 bucket construct must have bucket_name and bucket_arn. Got: {bucket}",
                        export_name=f"{construct_id}-lakeformation-bucket-error-{bucket_id}",
                    )
                    raise ValueError(
                        f"S3 bucket construct must have bucket_name and bucket_arn. Got: {bucket}"
                    )
                import re

                if not Token.is_unresolved(name):
                    if not isinstance(name, str) or not re.match(
                        r"^[a-z0-9.-]{3,63}$", name
                    ):
                        self.logger.error(
                            f"Invalid S3 bucket name for LakeFormation: {name}"
                        )
                        CfnOutput(
                            self,
                            f"{construct_id}BucketNameError{bucket_id}",
                            value=f"Invalid S3 bucket name for LakeFormation: {name}",
                            export_name=f"{construct_id}-lakeformation-bucket-name-error-{bucket_id}",
                        )
                        raise ValueError(
                            f"Invalid S3 bucket name for LakeFormation: {name}"
                        )
                resource = lakeformation.CfnResource(
                    self,
                    f"{construct_id}LakeFormationResource{bucket_id}",
                    resource_arn=arn,
                    use_service_linked_role=True,
                )
                # Propagate tags to resource (CDK v2)
                # Tags are imported at top level

                for k, v in tags_to_apply.items():
                    Tags.of(resource).add(k, v)
                # Set removal policy based on environment (default: DESTROY for dev, RETAIN for others)
                removal_policy = (
                    RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
                )
                if hasattr(resource, "apply_removal_policy"):
                    resource.apply_removal_policy(removal_policy)
                self._export_resource(f"LakeFormationResource{bucket_id}Arn", arn)
                self._export_resource(
                    f"LakeFormationResource{bucket_id}RemovalPolicy",
                    str(removal_policy),
                )
                self.resources.append(resource)
                self.shared_resources[bucket_id] = resource
        else:
            if not isinstance(buckets, list) or not buckets:
                self.logger.error("LakeFormation buckets must be a non-empty list.")
                CfnOutput(
                    self,
                    f"{construct_id}BucketsError",
                    value="LakeFormation buckets must be a non-empty list.",
                    export_name=f"{construct_id}-lakeformation-buckets-error",
                )
                raise ValueError("LakeFormation buckets must be a non-empty list.")
            bucket_names = set()
            for bucket_cfg in buckets:
                name = bucket_cfg.get("name")
                arn = bucket_cfg.get("arn")
                removal_policy = bucket_cfg.get("removal_policy", None)
                if isinstance(removal_policy, str):
                    removal_policy = getattr(
                        RemovalPolicy, removal_policy.upper(), None
                    )
                if removal_policy is None:
                    removal_policy = (
                        RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
                    )
                if not name or not arn:
                    self.logger.error(
                        f"LakeFormation bucket config must include name and arn. Got: {bucket_cfg}"
                    )
                    CfnOutput(
                        self,
                        f"{construct_id}BucketConfigError{name}",
                        value=f"LakeFormation bucket config must include name and arn. Got: {bucket_cfg}",
                        export_name=f"{construct_id}-lakeformation-bucket-config-error-{name}",
                    )
                    raise ValueError(
                        f"LakeFormation bucket config must include name and arn. Got: {bucket_cfg}"
                    )
                if name in bucket_names:
                    self.logger.error(f"Duplicate LakeFormation bucket name: {name}")
                    CfnOutput(
                        self,
                        f"{construct_id}BucketDuplicateError{name}",
                        value=f"Duplicate LakeFormation bucket name: {name}",
                        export_name=f"{construct_id}-lakeformation-bucket-duplicate-error-{name}",
                    )
                    raise ValueError(f"Duplicate LakeFormation bucket name: {name}")
                bucket_names.add(name)
                import re

                if not Token.is_unresolved(name):
                    if not isinstance(name, str) or not re.match(
                        r"^[a-z0-9.-]{3,63}$", name
                    ):
                        self.logger.error(
                            f"Invalid S3 bucket name for LakeFormation: {name}"
                        )
                        CfnOutput(
                            self,
                            f"{construct_id}BucketNameError{name}",
                            value=f"Invalid S3 bucket name for LakeFormation: {name}",
                            export_name=f"{construct_id}-lakeformation-bucket-name-error-{name}",
                        )
                        raise ValueError(
                            f"Invalid S3 bucket name for LakeFormation: {name}"
                        )
                resource = lakeformation.CfnResource(
                    self,
                    f"{construct_id}LakeFormationResource{name}",
                    resource_arn=arn,
                    use_service_linked_role=True,
                )
                if hasattr(resource, "apply_removal_policy"):
                    resource.apply_removal_policy(removal_policy)
                # Propagate tags to resource (CDK v2)
                # Tags are imported at top level

                for k, v in tags_to_apply.items():
                    Tags.of(resource).add(k, v)
                self._export_resource(f"LakeFormationResource{name}Arn", arn)
                self._export_resource(
                    f"LakeFormationResource{name}RemovalPolicy", str(removal_policy)
                )
                self.resources.append(resource)
                self.shared_resources[name] = resource
        self.event_rule = None
        try:
            # events already imported at top

            self.event_rule = events.Rule(
                self,
                f"{construct_id}LakeFormationFailureRule",
                event_pattern=events.EventPattern(
                    source=["aws.lakeformation"],
                    detail_type=["AWS API Call via CloudTrail"],
                    detail={"errorCode": [{"exists": True}]},
                ),
                description="Alert on Lake Formation API errors via CloudTrail",
                enabled=True,
            )
            # Export event rule ARN for auditability
            CfnOutput(
                self,
                f"{construct_id}EventRuleArn",
                value=self.event_rule.rule_arn,
                export_name=f"{construct_id}-lakeformation-event-rule-arn",
            )
        except ImportError:
            self.logger.error("aws_events import failed; event rule not created.")
            CfnOutput(
                self,
                f"{construct_id}EventRuleError",
                value="aws_events import failed; event rule not created.",
                export_name=f"{construct_id}-lakeformation-event-rule-error",
            )

        # --- Lake Formation Permissions ---
        permissions = lf_cfg.get("permissions", [])
        if not isinstance(permissions, list):
            self.logger.error("LakeFormation permissions must be a list.")
            CfnOutput(
                self,
                f"{construct_id}PermissionsError",
                value="LakeFormation permissions must be a list.",
                export_name=f"{construct_id}-lakeformation-permissions-error",
            )
            raise ValueError("LakeFormation permissions must be a list.")
        perm_keys = set()
        self.permissions = []
        self.shared_permissions = {}

        def sanitize_export_name(s):
            import re

            return re.sub(r"[^A-Za-z0-9:-]", "-", s)

        # ARNs from IAM stack
        iam_role_arns = {
            "LAKEFORMATION_ADMIN_ROLE_ARN": lakeformation_admin_role_arn,
            "GLUE_EXECUTION_ROLE_ARN": config.get("iam", {}).get("glue_role_arn"),
            "SAGEMAKER_EXECUTION_ROLE_ARN": config.get("iam", {}).get(
                "sagemaker_role_arn"
            ),
            "AIRBYTE_EXECUTION_ROLE_ARN": config.get("iam", {}).get("airbyte_role_arn"),
            "LAMBDA_EXECUTION_ROLE_ARN": config.get("iam", {}).get("lambda_role_arn"),
            "OPENSEARCH_EXECUTION_ROLE_ARN": config.get("iam", {}).get(
                "opensearch_role_arn"
            ),
            "MSK_CLIENT_ROLE_ARN": config.get("iam", {}).get("msk_client_role_arn"),
            "MSK_PRODUCER_ROLE_ARN": config.get("iam", {}).get("msk_producer_role_arn"),
            "MSK_CONSUMER_ROLE_ARN": config.get("iam", {}).get("msk_consumer_role_arn"),
            "VPC_FLOW_LOGS_ROLE_ARN": config.get("iam", {}).get(
                "vpc_flow_logs_role_arn"
            ),
            "DATA_QUALITY_ROLE_ARN": config.get("iam", {}).get("data_quality_role_arn"),
            "COMPLIANCE_ROLE_ARN": config.get("iam", {}).get("compliance_role_arn"),
        }

        arn_regex = r"^arn:aws:[a-z0-9-]+:[a-z0-9-]*:[0-9]*:[^\s]+$"
        for logical_name, arn in iam_role_arns.items():
            if arn is not None and not re.match(arn_regex, arn):
                raise ValueError(f"Invalid ARN for {logical_name}: {arn}")

        # Permission templates for common roles
        permission_templates = {
            "etl": {
                "table": ["SELECT", "DESCRIBE"],
                "bucket": ["DATA_LOCATION_ACCESS"],
            },
            "read_only": {
                "table": ["SELECT"],
                "bucket": ["DATA_LOCATION_ACCESS"],
            },
            "admin": {
                "database": ["ALL"],
                "table": ["ALL"],
                "bucket": ["ALL"],
            },
        }

        valid_actions = {"ALL", "SELECT", "DESCRIBE", "ALTER", "DATA_LOCATION_ACCESS"}

        s3_bucket_ids = set([b.get("id") or b.get("name") for b in buckets_cfg])
        for perm_cfg in permissions:
            try:
                template = perm_cfg.get("template")
                principal = perm_cfg.get("principal")
                resource_type = perm_cfg.get("resource_type")
                resource = perm_cfg.get("resource")
                actions = perm_cfg.get("actions")

                # Template logic
                if template:
                    if template not in permission_templates:
                        self.logger.error(f"Unknown permission template: {template}")
                        CfnOutput(
                            self,
                            f"{construct_id}PermTemplateError{template}",
                            value=f"Unknown permission template: {template}",
                            export_name=f"{construct_id}-lakeformation-perm-template-error-{template}",
                        )
                        raise ValueError(f"Unknown permission template: {template}")
                    if resource_type not in permission_templates[template]:
                        self.logger.error(
                            f"Template '{template}' does not support resource type '{resource_type}'"
                        )
                        CfnOutput(
                            self,
                            f"{construct_id}PermTemplateTypeError{template}{resource_type}",
                            value=f"Template '{template}' does not support resource type '{resource_type}'",
                            export_name=f"{construct_id}-lakeformation-perm-template-type-error-{template}-{resource_type}",
                        )
                        raise ValueError(
                            f"Template '{template}' does not support resource type '{resource_type}'"
                        )
                    actions = permission_templates[template][resource_type]

                if not principal or not resource or not actions:
                    self.logger.error(
                        f"Permission config must include principal, resource, and actions: {perm_cfg}"
                    )
                    CfnOutput(
                        self,
                        f"{construct_id}PermConfigError{hash(str(perm_cfg))}",
                        value=f"Permission config must include principal, resource, and actions: {perm_cfg}",
                        export_name=f"{construct_id}-lakeformation-perm-config-error-{hash(str(perm_cfg))}",
                    )
                    raise ValueError(
                        f"Permission config must include principal, resource, and actions: {perm_cfg}"
                    )

                resolved_principal = iam_role_arns.get(principal, principal)
                if not resolved_principal:
                    self.logger.error(f"Principal not found or invalid: {principal}")
                    CfnOutput(
                        self,
                        f"{construct_id}PermPrincipalError{principal}",
                        value=f"Principal not found or invalid: {principal}",
                        export_name=f"{construct_id}-lakeformation-perm-principal-error-{principal}",
                    )
                    raise ValueError(f"Principal not found or invalid: {principal}")

                for action in actions:
                    if action not in valid_actions:
                        self.logger.error(f"Invalid Lake Formation action: {action}")
                        CfnOutput(
                            self,
                            f"{construct_id}PermActionError{action}",
                            value=f"Invalid Lake Formation action: {action}",
                            export_name=f"{construct_id}-lakeformation-perm-action-error-{action}",
                        )
                        raise ValueError(f"Invalid Lake Formation action: {action}")

                # --- Resource mapping for Glue/S3 ---
                # If resource_type is 'table', use imported Glue table ARN
                if resource_type == "table":
                    bucket_id = (
                        resource.get("bucketId")
                        or resource.get("bucket_id")
                        or resource.get("bucket")
                    )
                    if bucket_id:
                        if bucket_id not in s3_bucket_ids:
                            self.logger.error(
                                f"LakeFormation permission references unknown bucketId: {bucket_id}"
                            )
                            CfnOutput(
                                self,
                                f"{construct_id}PermBucketIdError{bucket_id}",
                                value=f"LakeFormation permission references unknown bucketId: {bucket_id}",
                                export_name=f"{construct_id}-lakeformation-perm-bucketid-error-{bucket_id}",
                            )
                            raise ValueError(
                                f"LakeFormation permission references unknown bucketId: {bucket_id}"
                            )
                        if bucket_id in glue_crawler_resources:
                            resource["tableArn"] = glue_crawler_resources[bucket_id][
                                "table_arn"
                            ]
                            resource["tableName"] = glue_crawler_resources[bucket_id][
                                "table_name"
                            ]
                            resource["databaseName"] = glue_db_name
                        else:
                            resource["databaseName"] = glue_db_name
                    else:
                        resource["databaseName"] = glue_db_name
                # If resource_type is 'bucket', use imported S3 bucket ARN
                if resource_type == "bucket":
                    bucket_id = (
                        resource.get("bucketId")
                        or resource.get("bucket_id")
                        or resource.get("bucket")
                    )
                    if bucket_id:
                        if bucket_id not in s3_bucket_ids:
                            self.logger.error(
                                f"LakeFormation permission references unknown bucketId: {bucket_id}"
                            )
                            CfnOutput(
                                self,
                                f"{construct_id}PermBucketIdError{bucket_id}",
                                value=f"LakeFormation permission references unknown bucketId: {bucket_id}",
                                export_name=f"{construct_id}-lakeformation-perm-bucketid-error-{bucket_id}",
                            )
                            raise ValueError(
                                f"LakeFormation permission references unknown bucketId: {bucket_id}"
                            )
                        if bucket_id in glue_crawler_resources:
                            resource["arn"] = glue_crawler_resources[bucket_id][
                                "bucket_arn"
                            ]

                # --- Resource mapping and validation for OpenSearch ---
                if resource_type == "opensearch_domain":
                    domain_name = (
                        resource.get("domainName")
                        or resource.get("domain_name")
                        or resource.get("name")
                    )
                    if not domain_name:
                        self.logger.error(
                            f"LF permission for OpenSearch must include domainName. Got: {resource}"
                        )
                        CfnOutput(
                            self,
                            f"{construct_id}PermOpenSearchError{hash(str(resource))}",
                            value=f"LF permission for OpenSearch must include domainName. Got: {resource}",
                            export_name=f"{construct_id}-lakeformation-perm-opensearch-error-{hash(str(resource))}",
                        )
                        raise ValueError(
                            f"LF permission for OpenSearch must include domainName. Got: {resource}"
                        )
                    if domain_name not in exported_opensearch_domains:
                        self.logger.error(
                            f"LF permission references unknown OpenSearch domain: {domain_name}"
                        )
                        CfnOutput(
                            self,
                            f"{construct_id}PermOpenSearchDomainError{domain_name}",
                            value=f"LF permission references unknown OpenSearch domain: {domain_name}",
                            export_name=f"{construct_id}-lakeformation-perm-opensearch-domain-error-{domain_name}",
                        )
                        raise ValueError(
                            f"LF permission references unknown OpenSearch domain: {domain_name}"
                        )
                    resource["arn"] = opensearch_domain_arn

                # --- Resource mapping and validation for SageMaker ---
                if resource_type == "sagemaker_model":
                    model_name = (
                        resource.get("modelName")
                        or resource.get("model_name")
                        or resource.get("name")
                    )
                    if not model_name:
                        self.logger.error(
                            f"LF permission for SageMaker must include modelName. Got: {resource}"
                        )
                        CfnOutput(
                            self,
                            f"{construct_id}PermSageMakerModelError{hash(str(resource))}",
                            value=f"LF permission for SageMaker must include modelName. Got: {resource}",
                            export_name=f"{construct_id}-lakeformation-perm-sagemaker-model-error-{hash(str(resource))}",
                        )
                        raise ValueError(
                            f"LF permission for SageMaker must include modelName. Got: {resource}"
                        )
                    if model_name not in exported_sagemaker_models:
                        self.logger.error(
                            f"LF permission references unknown SageMaker model: {model_name}"
                        )
                        CfnOutput(
                            self,
                            f"{construct_id}PermSageMakerModelDomainError{model_name}",
                            value=f"LF permission references unknown SageMaker model: {model_name}",
                            export_name=f"{construct_id}-lakeformation-perm-sagemaker-model-domain-error-{model_name}",
                        )
                        raise ValueError(
                            f"LF permission references unknown SageMaker model: {model_name}"
                        )
                    resource["arn"] = sagemaker_model_arn

                if resource_type == "sagemaker_endpoint":
                    endpoint_name = (
                        resource.get("endpointName")
                        or resource.get("endpoint_name")
                        or resource.get("name")
                    )
                    if not endpoint_name:
                        self.logger.error(
                            f"LF permission for SageMaker must include endpointName. Got: {resource}"
                        )
                        CfnOutput(
                            self,
                            f"{construct_id}PermSageMakerEndpointError{hash(str(resource))}",
                            value=f"LF permission for SageMaker must include endpointName. Got: {resource}",
                            export_name=f"{construct_id}-lakeformation-perm-sagemaker-endpoint-error-{hash(str(resource))}",
                        )
                        raise ValueError(
                            f"LF permission for SageMaker must include endpointName. Got: {resource}"
                        )
                    if endpoint_name not in exported_sagemaker_endpoints:
                        self.logger.error(
                            f"LF permission references unknown SageMaker endpoint: {endpoint_name}"
                        )
                        CfnOutput(
                            self,
                            f"{construct_id}PermSageMakerEndpointDomainError{endpoint_name}",
                            value=f"LF permission references unknown SageMaker endpoint: {endpoint_name}",
                            export_name=f"{construct_id}-lakeformation-perm-sagemaker-endpoint-domain-error-{endpoint_name}",
                        )
                        raise ValueError(
                            f"LF permission references unknown SageMaker endpoint: {endpoint_name}"
                        )

                key = (resolved_principal, str(resource))
                if key in perm_keys:
                    self.logger.error(
                        f"Duplicate LF permission for resource: {resolved_principal}/{resource}"
                    )
                    CfnOutput(
                        self,
                        f"{construct_id}PermDuplicateError{hash(str(resource))}",
                        value=f"Duplicate LF permission for resource: {resolved_principal}/{resource}",
                        export_name=f"{construct_id}-lakeformation-perm-duplicate-error-{hash(str(resource))}",
                    )
                    raise ValueError(
                        f"Duplicate LF permission for resource: {resolved_principal}/{resource}"
                    )
                perm_keys.add(key)
                perm = lakeformation.CfnPermissions(
                    self,
                    f"{construct_id}LakeFormationPerm{sanitize_export_name(str(resolved_principal))}{hash(str(resource))}",
                    data_lake_principal={
                        "dataLakePrincipalIdentifier": resolved_principal
                    },
                    resource=resource,
                    permissions=actions,
                )
                sanitized_principal = sanitize_export_name(str(resolved_principal))
                self._export_resource(
                    f"LakeFormationPerm{sanitized_principal}{hash(str(resource))}Principal",
                    resolved_principal,
                )
                self.permissions.append(perm)
                self.shared_permissions[sanitized_principal] = perm
            except Exception as e:
                self.logger.error(f"LakeFormation permission error: {e}")
                CfnOutput(
                    self,
                    f"{construct_id}PermGeneralError{hash(str(perm_cfg))}",
                    value=str(e),
                    export_name=f"{construct_id}-lakeformation-perm-general-error-{hash(str(perm_cfg))}",
                )
                raise

    def _validate_cross_stack_resources(self, config):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        if not isinstance(config, dict):
            raise ValueError("LakeFormationStack requires a valid config dict.")
        lf_cfg = config.get("lakeformation", {})
        if not isinstance(lf_cfg, dict):
            raise ValueError("lakeformation config must be a dict.")
        buckets = lf_cfg.get("buckets", [])
        if not isinstance(buckets, list) or not buckets:
            raise ValueError("LakeFormation buckets must be a non-empty list.")
        for bucket_cfg in buckets:
            name = bucket_cfg.get("name")
            arn = bucket_cfg.get("arn")
            if not name or not arn:
                raise ValueError(
                    f"LakeFormation bucket config must include name and arn. Got: {bucket_cfg}"
                )
        permissions = lf_cfg.get("permissions", [])
        if not isinstance(permissions, list):
            raise ValueError("LakeFormation permissions must be a list.")

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")
        # Add vault secret to shared_resources for downstream stacks
        self.shared_resources["vault_secret"] = self.secrets_manager_secret
