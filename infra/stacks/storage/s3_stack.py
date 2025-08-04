"""
S3Stack for ShieldCraftAI
"""

import re
from typing import Any, Dict, Optional
from aws_cdk import Tags
from aws_cdk import Environment
from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import aws_s3 as s3
from constructs import Construct


class S3Stack(Stack):
    def get_stack_tags(self):
        # Always return the internal tag list for testability and auditability
        return list(self._sc_tag_list)

    """
    ShieldCraftAI S3Stack

    Parameters:
        config: Project configuration dictionary, must include 's3' section with 'buckets' list.
        shared_tags: Optional dictionary of tags to apply to all buckets.
        kms_key: Optional KMS key for bucket encryption (applies to all buckets if provided).

    Attributes:
        buckets: Dict of all created buckets by ID.
        raw_bucket, processed_bucket, analytics_bucket: Common buckets for backward compatibility.
    """

    def _validate_cross_stack_resources(self, config):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        s3_cfg = config.get("s3", {})
        buckets_cfg = s3_cfg.get("buckets", [])
        if not isinstance(buckets_cfg, list) or not buckets_cfg:
            raise ValueError("buckets must be a non-empty list.")
        bucket_ids = set()
        for bucket_cfg in buckets_cfg:
            if not isinstance(bucket_cfg, dict):
                raise ValueError(
                    f"Each bucket config must be a dict. Got: {bucket_cfg}"
                )
            bucket_id = bucket_cfg.get("id") or bucket_cfg.get("name")
            bucket_name = bucket_cfg.get("name")
            if not bucket_id or not bucket_name:
                raise ValueError(
                    f"Each bucket must have 'id' and 'name'. Got: {bucket_cfg}"
                )
            if bucket_id in bucket_ids:
                raise ValueError(f"Duplicate bucket id: {bucket_id}")
            bucket_ids.add(bucket_id)

            if not isinstance(bucket_name, str) or not re.match(
                r"^[a-z0-9.-]{3,63}$", bucket_name
            ):
                raise ValueError(f"Invalid S3 bucket name: {bucket_name}")
            # Validate block_public_access value
            block_public_access = bucket_cfg.get("block_public_access", "BLOCK_ALL")
            valid_block_public_access = [
                "BLOCK_ALL",
                "BLOCK_ACLS",
                "BLOCK_PUBLIC_POLICY",
                "BLOCK_AUTHENTICATED_USERS",
            ]
            if block_public_access not in valid_block_public_access:
                block_public_access = "BLOCK_ALL"

    @staticmethod
    def sanitize_export_name(name: str) -> str:

        # Only allow alphanumeric, colons, and hyphens
        return re.sub(r"[^A-Za-z0-9:-]", "-", name)

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        sanitized_export_name = self.sanitize_export_name(f"{self.stack_name}-{name}")
        CfnOutput(self, name, value=value, export_name=sanitized_export_name)

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: dict,
        shared_tags: Optional[Dict[str, str]] = None,
        kms_key: Optional[Any] = None,
        secrets_manager_arn: Optional[str] = None,
        **kwargs,
    ):
        # Only pass env if it is a dict or aws_cdk.Environment, not a string
        env_from_config = config.get("app", {}).get("env")
        stack_kwargs = {k: kwargs[k] for k in ("env", "description") if k in kwargs}

        if env_from_config and "env" not in stack_kwargs:
            if isinstance(env_from_config, dict) or isinstance(
                env_from_config, Environment
            ):
                stack_kwargs["env"] = env_from_config
        super().__init__(scope, construct_id, **stack_kwargs)
        self._validate_cross_stack_resources(config)
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
        s3_cfg = config.get("s3", {})
        env = config.get("app", {}).get("env", "dev")

        tags_cfg = s3_cfg.get("tags") or {}
        # Maintain an internal tag list for testability and auditability
        self._sc_tag_list = []  # List of {"Key": ..., "Value": ...}
        tag_dict = {}
        # Add required tags first (order: Project, Environment)
        tag_dict["Project"] = "ShieldCraftAI"
        tag_dict["Environment"] = env
        # Add config tags
        for k, v in tags_cfg.items():
            if v is not None:
                tag_dict[str(k)] = str(v)
        # Add shared_tags, deduplicating (shared_tags take precedence)
        if shared_tags:
            for k, v in shared_tags.items():
                if v is not None:
                    tag_dict[str(k)] = str(v)
        # Build the tag list
        for k, v in tag_dict.items():
            self._sc_tag_list.append({"Key": k, "Value": v})
        # For CDK, still add tags to the stack for resource propagation
        tags_manager = Tags.of(self)
        self._sc_tags = tags_manager
        try:
            for tag in self._sc_tag_list:
                tags_manager.add(tag["Key"], tag["Value"])
        except Exception as e:
            print(f"[WARNING] Could not apply tags to stack: {e}")
        buckets_cfg = s3_cfg.get("buckets", [])
        bucket_ids = set()
        self.buckets: Dict[str, s3.Bucket] = {}
        referenced_bucket_ids = set()

        for bucket_cfg in buckets_cfg:
            if not isinstance(bucket_cfg, dict):
                raise ValueError(
                    f"Each bucket config must be a dict. Got: {bucket_cfg}"
                )
            bucket_id = bucket_cfg.get("id") or bucket_cfg.get("name")
            bucket_name = bucket_cfg.get("name")
            if not bucket_id or not bucket_name:
                raise ValueError(
                    f"Each bucket must have 'id' and 'name'. Got: {bucket_cfg}"
                )
            if bucket_id in bucket_ids:
                raise ValueError(f"Duplicate bucket id: {bucket_id}")
            bucket_ids.add(bucket_id)
            referenced_bucket_ids.add(bucket_id)

            if not isinstance(bucket_name, str) or not re.match(
                r"^[a-z0-9.-]{3,63}$", bucket_name
            ):
                raise ValueError(f"Invalid S3 bucket name: {bucket_name}")
            removal_policy = bucket_cfg.get("removal_policy")
            if isinstance(removal_policy, str):
                removal_policy = getattr(RemovalPolicy, removal_policy.upper(), None)
            if removal_policy is None:
                removal_policy = (
                    RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
                )
            if kms_key is not None:
                encryption = s3.BucketEncryption.KMS
            else:
                encryption = getattr(
                    s3.BucketEncryption,
                    bucket_cfg.get("encryption", "S3_MANAGED").upper(),
                    s3.BucketEncryption.S3_MANAGED,
                )
            block_public_access_value = bucket_cfg.get(
                "block_public_access", "BLOCK_ALL"
            )
            valid_block_public_access = [
                "BLOCK_ALL",
                "BLOCK_ACLS",
                "BLOCK_PUBLIC_POLICY",
                "BLOCK_AUTHENTICATED_USERS",
            ]
            if block_public_access_value not in valid_block_public_access:
                block_public_access_value = "BLOCK_ALL"
            block_public_access = getattr(
                s3.BlockPublicAccess,
                block_public_access_value.upper(),
                s3.BlockPublicAccess.BLOCK_ALL,
            )
            versioned = bucket_cfg.get("versioned", True)
            if env == "prod":
                versioned = True
                if kms_key is None:
                    encryption = s3.BucketEncryption.S3_MANAGED

            # --- LIFECYCLE RULES SUPPORT ---
            lifecycle_rules_cfg = bucket_cfg.get("lifecycle_rules", [])
            lifecycle_rules = []
            for rule_cfg in lifecycle_rules_cfg:
                if not isinstance(rule_cfg, dict):
                    continue
                rule_kwargs = {
                    "id": rule_cfg.get("id"),
                    "enabled": rule_cfg.get("enabled", True),
                }
                if rule_cfg.get("prefix") is not None:
                    rule_kwargs["prefix"] = rule_cfg.get("prefix")
                if rule_cfg.get("tag_filters") is not None:
                    rule_kwargs["tag_filters"] = rule_cfg.get("tag_filters")
                # Transitions
                transitions = []
                # Map legacy/common S3 storage class names to CDK enums for robust compatibility
                storage_class_map = {
                    "STANDARD_IA": "INFREQUENT_ACCESS",
                    "ONEZONE_IA": "ONE_ZONE_INFREQUENT_ACCESS",
                    # Add more aliases as needed
                }
                for t in rule_cfg.get("transitions", []):
                    if not isinstance(t, dict):
                        continue
                    storage_class_str = t.get("storage_class", "GLACIER").upper()
                    # Map legacy/common names to CDK enum names
                    mapped_storage_class_str = storage_class_map.get(
                        storage_class_str, storage_class_str
                    )
                    storage_class = getattr(
                        s3.StorageClass, mapped_storage_class_str, None
                    )
                    if storage_class is None:
                        available = [
                            a for a in dir(s3.StorageClass) if not a.startswith("_")
                        ]
                        raise ValueError(
                            f"Unknown or unsupported storage_class '{storage_class_str}' for transition. "
                            f"Available enums in this CDK version: {available}"
                        )
                    transition = s3.Transition(
                        storage_class=storage_class,
                        transition_after=(
                            Duration.days(t.get("days", 30))
                            if t.get("days") is not None
                            else None
                        ),
                        transition_date=None,
                    )
                    transitions.append(transition)
                if transitions:
                    rule_kwargs["transitions"] = transitions
                # Expiration
                if rule_cfg.get("expiration_days") is not None:
                    rule_kwargs["expiration"] = Duration.days(
                        rule_cfg["expiration_days"]
                    )
                # Abort incomplete multipart upload
                if rule_cfg.get("abort_incomplete_multipart_upload_days") is not None:
                    rule_kwargs["abort_incomplete_multipart_upload_after"] = (
                        Duration.days(
                            rule_cfg["abort_incomplete_multipart_upload_days"]
                        )
                    )
                # Only add the rule if at least one actionable field is present
                if (
                    "transitions" in rule_kwargs
                    or "expiration" in rule_kwargs
                    or "abort_incomplete_multipart_upload_after" in rule_kwargs
                ):
                    lifecycle_rules.append(s3.LifecycleRule(**rule_kwargs))

            bucket = s3.Bucket(
                self,
                bucket_id,
                bucket_name=bucket_name,
                versioned=versioned,
                encryption=encryption,
                encryption_key=kms_key if kms_key is not None else None,
                block_public_access=block_public_access,
                removal_policy=removal_policy,
                lifecycle_rules=lifecycle_rules if lifecycle_rules else None,
            )
            self.buckets[bucket_id] = bucket

            # Propagate stack and shared tags to each bucket resource for auditability
            for tag in self._sc_tag_list:
                tag_key = tag.get("Key")
                tag_value = tag.get("Value")
                if tag_key is not None and tag_value is not None:
                    Tags.of(bucket).add(tag_key, tag_value)

            self._export_resource(
                f"{construct_id}S3Bucket{bucket_id}Name", bucket.bucket_name
            )
            self._export_resource(
                f"{construct_id}S3Bucket{bucket_id}Arn", bucket.bucket_arn
            )
            # CloudWatch Alarms and Metrics
            cloudwatch.Alarm(
                self,
                f"{bucket_id}S3_4xxErrorsAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/S3",
                    metric_name="4xxErrors",
                    dimensions_map={
                        "BucketName": bucket.bucket_name,
                        "StorageType": "AllStorageTypes",
                    },
                    period=Duration.minutes(5),
                    statistic="Sum",
                ),
                threshold=1,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                alarm_description=f"4xx errors detected on S3 bucket {bucket.bucket_name}",
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            )
            cloudwatch.Alarm(
                self,
                f"{bucket_id}S3_5xxErrorsAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/S3",
                    metric_name="5xxErrors",
                    dimensions_map={
                        "BucketName": bucket.bucket_name,
                        "StorageType": "AllStorageTypes",
                    },
                    period=Duration.minutes(5),
                    statistic="Sum",
                ),
                threshold=1,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                alarm_description=f"5xx errors detected on S3 bucket {bucket.bucket_name}",
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            )
            cloudwatch.Metric(
                namespace="AWS/S3",
                metric_name="NumberOfObjects",
                dimensions_map={
                    "BucketName": bucket.bucket_name,
                    "StorageType": "AllStorageTypes",
                },
                period=Duration.hours(1),
                statistic="Average",
            )
            cloudwatch.Metric(
                namespace="AWS/S3",
                metric_name="BucketSizeBytes",
                dimensions_map={
                    "BucketName": bucket.bucket_name,
                    "StorageType": "StandardStorage",
                },
                period=Duration.hours(1),
                statistic="Average",
            )

        # For backward compatibility, expose common buckets if present
        self.raw_bucket = self.buckets.get("RawDataBucket")
        self.processed_bucket = self.buckets.get("ProcessedDataBucket")
        self.analytics_bucket = self.buckets.get("AnalyticsDataBucket")
