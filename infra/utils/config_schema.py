"""
This file defines the configuration schema for ShieldCraft, a cloud-native security framework.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import List, Optional, Dict, Any, Union
import re


class CrawlerConfig(BaseModel):
    """Glue Crawler configuration."""

    schedule: Optional[str] = None
    table_prefix: Optional[str] = None
    removal_policy: Optional[str] = None
    model_config = ConfigDict(extra="ignore")


class BucketConfig(BaseModel):
    """S3 bucket configuration, including Glue crawler options."""

    id: str
    name: str
    versioned: Optional[bool] = True
    encryption: Optional[str] = None
    block_public_access: Optional[str] = None
    removal_policy: Optional[str] = None
    enable_glue_crawler: Optional[bool] = False
    crawler: Optional["CrawlerConfig"] = None

    @field_validator("removal_policy")
    @classmethod
    def validate_removal_policy(cls, v):
        allowed = {"DESTROY", "RETAIN", None}
        if v not in allowed:
            raise ValueError(f"removal_policy must be one of {allowed}")
        return v

    model_config = ConfigDict(extra="ignore")


class S3Config(BaseModel):
    """S3 configuration, including bucket lifecycle and access logs."""

    buckets: List["BucketConfig"]
    lifecycle_policy_days: Optional[int] = None
    enable_access_logs: Optional[bool] = None

    # Removed prod removal policy check; now handled in ShieldCraftConfig

    model_config = ConfigDict(extra="ignore")


class GlueConfig(BaseModel):
    """Glue database and crawler configuration."""

    database_name: str
    crawler_schedule: Optional[str] = None
    enable_data_quality: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")


class AppConfig(BaseModel):
    """Application-level configuration (env, region, resource prefix, etc)."""

    env: str
    region: str
    resource_prefix: str
    log_level: Optional[str] = None
    enable_feature_x: Optional[bool] = None
    config_version: Optional[str] = None
    last_modified: Optional[str] = None
    author: Optional[str] = None
    sns_topic_secret_arn: Optional[str] = Field(
        default=None, description="ARN for SNS topic secret", secret=True
    )
    external_api_key_arn: Optional[str] = Field(
        default=None, description="ARN for external API key", secret=True
    )

    model_config = ConfigDict(extra="ignore")


class SubnetConfig(BaseModel):
    """VPC subnet configuration."""

    id: str
    cidr: str
    type: str

    @field_validator("cidr")
    @classmethod
    def validate_cidr(cls, v):
        """Validate CIDR format."""
        if not re.match(r"^\d+\.\d+\.\d+\.\d+/\d+$", v):
            raise ValueError("Invalid CIDR format")
        return v

    model_config = ConfigDict(extra="ignore")


class SecurityGroupConfig(BaseModel):
    """VPC security group configuration."""

    id: str
    description: Optional[str] = None
    allow_all_outbound: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")


class NetworkingConfig(BaseModel):
    """VPC networking configuration, including subnets and security groups."""

    vpc_id: str
    cidr: str
    subnets: List["SubnetConfig"]
    security_groups: List["SecurityGroupConfig"]
    shard: Optional[str] = None

    @model_validator(mode="after")
    def check_unique_ids(self):
        """Ensure subnet and security group IDs are unique, handling both dicts and model instances."""

        def extract_id(obj):
            if isinstance(obj, dict):
                return obj.get("id")
            return getattr(obj, "id", None)

        subnets = self.subnets if hasattr(self, "subnets") else []
        sg = self.security_groups if hasattr(self, "security_groups") else []
        subnet_ids = [extract_id(s) for s in subnets if extract_id(s) is not None]
        sg_ids = [extract_id(s) for s in sg if extract_id(s) is not None]
        if len(subnet_ids) != len(set(subnet_ids)):
            raise ValueError("Duplicate subnet IDs found")
        if len(sg_ids) != len(set(sg_ids)):
            raise ValueError("Duplicate security group IDs found")
        return self

    model_config = ConfigDict(extra="ignore")


class TagConfig(BaseModel):
    """Resource tagging and compliance configuration."""

    project: Optional[str] = None
    environment: Optional[str] = None
    owner: Optional[str] = None
    cost_center: Optional[str] = None
    team: Optional[str] = None
    compliance: Optional[str] = None
    enable_cloudwatch_alarms: Optional[bool] = None
    alarm_email: Optional[str] = None
    config_rules: Optional[List[str]] = None
    simulation_mode: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")


class MSKSecurityGroupConfig(BaseModel):
    """MSK security group configuration."""

    id: str
    description: Optional[str] = None
    allow_all_outbound: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")


class MSKClusterConfig(BaseModel):
    """MSK cluster configuration."""

    id: str
    name: str
    kafka_version: str
    number_of_broker_nodes: int
    instance_type: str
    enhanced_monitoring: Optional[str] = None
    client_authentication: Optional[Dict[str, Any]] = None
    encryption_in_transit: Optional[Dict[str, Any]] = None
    public_access: Optional[bool] = None
    vpc_subnet_ids: List[str]
    security_group_ids: List[str]

    model_config = ConfigDict(extra="ignore")


class MSKConfig(BaseModel):
    """MSK configuration, including cluster and security group."""

    security_group: Optional[MSKSecurityGroupConfig] = None
    cluster: Optional[MSKClusterConfig] = None

    model_config = ConfigDict(extra="ignore")


class LambdaFunctionConfig(BaseModel):
    """Lambda function configuration."""

    id: str
    description: Optional[str] = None
    handler: str
    runtime: str
    memory_size: int
    timeout: int
    environment: Optional[Dict[str, Any]] = None
    vpc_subnet_ids: List[str]
    security_group_ids: List[str]
    policies: Optional[List[str]] = None

    model_config = ConfigDict(extra="ignore")


class LambdaConfig(BaseModel):
    """Lambda configuration, including all functions."""

    functions: List["LambdaFunctionConfig"]

    model_config = ConfigDict(extra="ignore")


class OpenSearchSecurityGroupConfig(BaseModel):
    """OpenSearch security group configuration."""

    id: str
    description: Optional[str] = None
    allow_all_outbound: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")


class OpenSearchDomainConfig(BaseModel):
    """OpenSearch domain configuration."""

    id: str
    name: str
    engine_version: str
    cluster_config: Optional[Dict[str, Any]] = None
    node_to_node_encryption_options: Optional[Dict[str, Any]] = None
    encryption_at_rest_options: Optional[Dict[str, Any]] = None
    ebs_options: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="ignore")


class OpenSearchConfig(BaseModel):
    """OpenSearch configuration, including domain and security group."""

    security_group: OpenSearchSecurityGroupConfig
    domain: OpenSearchDomainConfig

    model_config = ConfigDict(extra="ignore")


class AirbyteConfig(BaseModel):
    """Airbyte deployment configuration."""

    deployment_type: str
    min_task_count: int
    max_task_count: int

    model_config = ConfigDict(extra="ignore")


class DataQualityConfig(BaseModel):
    """Data quality framework and schedule configuration."""

    dq_framework: str
    dq_schedule: str

    model_config = ConfigDict(extra="ignore")


class LakeFormationPermissionConfig(BaseModel):
    """LakeFormation permission configuration."""

    template: Optional[str] = None
    principal: str
    resource_type: str
    resource: Dict[str, Any]
    actions: Optional[List[str]] = None

    @field_validator("principal")
    @classmethod
    def validate_principal(cls, v):
        """Validate principal is a string."""
        if not v or not isinstance(v, str):
            raise ValueError("Principal must be a string")
        return v

    model_config = ConfigDict(extra="ignore")


class LakeFormationConfig(BaseModel):
    """LakeFormation configuration, including permissions."""

    admin_role: str
    data_lake_location: str
    permissions: List["LakeFormationPermissionConfig"]

    model_config = ConfigDict(extra="ignore")


class SageMakerConfig(BaseModel):
    """SageMaker training and inference configuration."""

    training_instance_type: str
    inference_instance_type: str
    endpoint_auto_scaling: Optional[bool] = None
    model_registry: Optional[str] = None

    model_config = ConfigDict(extra="ignore", protected_namespaces=())


class CloudNativeHardeningConfig(BaseModel):
    @model_validator(mode="after")
    def enforce_secret_fields_are_vault_refs(cls, self):
        secret_fields = ["sns_topic_secret_arn", "external_api_key_arn"]
        vault_pattern = re.compile(r"^(aws-vault:|arn:aws:secretsmanager:)")
        for field in secret_fields:
            value = getattr(self, field, None)
            if value is not None and not vault_pattern.match(str(value)):
                raise ValueError(
                    f"{field} must be a vault reference (aws-vault: or arn:aws:secretsmanager:), got: {value}"
                )
        return self

    @model_validator(mode="after")
    def enforce_secret_fields_are_vault_refs(cls, self):
        secret_fields = ["sns_topic_secret_arn", "external_api_key_arn"]
        vault_pattern = re.compile(r"^(aws-vault:|arn:aws:secretsmanager:)")
        for field in secret_fields:
            value = getattr(self, field, None)
            if value is not None and not vault_pattern.match(str(value)):
                raise ValueError(
                    f"{field} must be a vault reference (aws-vault: or arn:aws:secretsmanager:), got: {value}"
                )
        return self

    """Cloud-native hardening and compliance configuration."""

    enable_cloudwatch_alarms: Optional[bool] = None
    alarm_email: Optional[str] = None
    config_rules: Optional[List[str]] = None
    sns_topic_secret_arn: Optional[str] = Field(
        default=None, description="ARN for SNS topic secret", secret=True
    )
    external_api_key_arn: Optional[str] = Field(
        default=None, description="ARN for external API key", secret=True
    )

    model_config = ConfigDict(extra="ignore")


class ShieldCraftConfig(BaseModel):
    """Top-level ShieldCraft configuration, aggregating all sections."""

    app: "AppConfig"
    s3: "S3Config"
    glue: "GlueConfig"
    networking: Optional["NetworkingConfig"] = None
    tags: Optional["TagConfig"] = None
    msk: Optional["MSKConfig"] = None
    lambda_: Optional["LambdaConfig"] = None
    opensearch: Optional["OpenSearchConfig"] = None
    airbyte: Optional["AirbyteConfig"] = None
    data_quality: Optional["DataQualityConfig"] = None
    lakeformation: Optional["LakeFormationConfig"] = None
    sagemaker: Optional["SageMakerConfig"] = None
    cloud_native_hardening: Optional["CloudNativeHardeningConfig"] = None
    secrets: Optional[Dict[str, Dict[str, Union[str, bool]]]] = None
    audit: Optional[Dict[str, Any]] = None
    overrides: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def enforce_prod_bucket_removal_policy(cls, self):
        # Enforce RETAIN for prod buckets if env is prod
        env = getattr(self.app, "env", None) if hasattr(self, "app") else None
        if env == "prod" and hasattr(self, "s3") and self.s3:
            for bucket in self.s3.buckets:
                if getattr(bucket, "removal_policy", None) != "RETAIN":
                    raise ValueError("In production, S3 removal_policy must be RETAIN.")
        return self

    @model_validator(mode="after")
    def check_referential_integrity(cls, self):
        # Collect all subnet and security group IDs from networking
        subnet_ids = set()
        sg_ids = set()
        if self.networking:
            subnet_ids = {s.id for s in getattr(self.networking, "subnets", [])}
            sg_ids = {sg.id for sg in getattr(self.networking, "security_groups", [])}

        # Helper to check references
        def check_ids(ref_ids, valid_ids, ref_type, section):
            for rid in ref_ids:
                if rid not in valid_ids:
                    raise ValueError(
                        f"{ref_type} ID '{rid}' in {section} does not exist in networking config."
                    )

        # MSK cluster
        if self.msk and self.msk.cluster:
            check_ids(
                getattr(self.msk.cluster, "vpc_subnet_ids", []),
                subnet_ids,
                "Subnet",
                "msk.cluster",
            )
            check_ids(
                getattr(self.msk.cluster, "security_group_ids", []),
                sg_ids,
                "SecurityGroup",
                "msk.cluster",
            )

        # Lambda functions
        if self.lambda_ and getattr(self.lambda_, "functions", None):
            for fn in self.lambda_.functions:
                check_ids(
                    getattr(fn, "vpc_subnet_ids", []),
                    subnet_ids,
                    "Subnet",
                    f"lambda_.functions[{fn.id}]",
                )
                check_ids(
                    getattr(fn, "security_group_ids", []),
                    sg_ids,
                    "SecurityGroup",
                    f"lambda_.functions[{fn.id}]",
                )

        # Add similar checks for other sections as needed (e.g., opensearch, sagemaker)

        return self

    @model_validator(mode="before")
    def set_parent_on_sections(cls, values):
        # Defensive: handle ValidationInfo or dict
        if hasattr(values, "__dict__") and not isinstance(values, dict):
            # Convert ValidationInfo or similar to dict
            values = dict(getattr(values, "config", values))
        s3 = values.get("s3") if isinstance(values, dict) else None
        if s3 is not None:
            try:
                s3.parent = None  # Clear any previous parent
                s3.parent = values
            except AttributeError:
                pass
        return values

    model_config = ConfigDict(extra="ignore")
