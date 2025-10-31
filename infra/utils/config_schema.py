"""
This file defines the configuration schema for ShieldCraft, a cloud-native security framework.
"""

import re
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class BeirConfig(BaseModel):
    datasets: List[str] = Field(default_factory=lambda: ["scifact"])
    data_path: Optional[str] = "./beir_datasets"
    output_path: Optional[str] = "beir_results.json"
    batch_size: Optional[int] = 32
    model_config = ConfigDict(extra="ignore")


class MtebConfig(BaseModel):
    tasks: Optional[List[str]] = None  # null = all tasks
    output_path: Optional[str] = "mteb_results.json"
    batch_size: Optional[int] = 32
    model_config = ConfigDict(extra="ignore")


class OrchestratorConfig(BaseModel):
    output_dir: Optional[str] = None
    max_workers: Optional[int] = 2
    retry: Optional[int] = 1
    log_level: Optional[str] = "INFO"
    model_config = ConfigDict(extra="ignore")


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

    env: str = "dev"
    region: str = "af-south-1"
    account: str = "000000000000"
    resource_prefix: str = "shieldcraft-dev"
    log_level: Optional[str] = None
    enable_feature_x: Optional[bool] = None
    config_version: Optional[str] = None
    last_modified: Optional[str] = None
    author: Optional[str] = None
    sns_topic_secret_arn: Optional[str] = Field(
        default=None,
        description="ARN for SNS topic secret",
        json_schema_extra={"secret": True},
    )
    external_api_key_arn: Optional[str] = Field(
        default=None,
        description="ARN for external API key",
        json_schema_extra={"secret": True},
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
    buckets: Optional[List[Dict[str, Any]]] = None

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
    def enforce_secret_fields_are_vault_refs(self):
        secret_fields = ["sns_topic_secret_arn", "external_api_key_arn"]
        vault_pattern = re.compile(r"^(aws-vault:|arn:aws:secretsmanager:)")
        for field in secret_fields:
            value = getattr(self, field, None)
            if value is not None and not vault_pattern.match(str(value)):
                raise ValueError(
                    f"{field} must be a vault reference (aws-vault: or arn:aws:secretsmanager:), got: {value}"
                )
        return self

    enable_cloudwatch_alarms: Optional[bool] = None
    alarm_email: Optional[str] = None
    config_rules: Optional[List[str]] = None
    sns_topic_secret_arn: Optional[str] = Field(
        default=None,
        description="ARN for SNS topic secret",
        json_schema_extra={"secret": True},
    )
    external_api_key_arn: Optional[str] = Field(
        default=None,
        description="ARN for external API key",
        json_schema_extra={"secret": True},
    )

    model_config = ConfigDict(extra="ignore")


class StepFunctionStateConfig(BaseModel):
    """Step Function state configuration (Task, Choice, Parallel, etc.)."""

    id: str
    type: str  # 'Task', 'Choice', 'Parallel', etc.
    resource: Optional[str] = None  # Lambda ARN, Glue Job name, etc.
    next: Optional[str] = None
    end: Optional[bool] = False
    parameters: Optional[Dict[str, Any]] = None
    catch: Optional[List[Dict[str, Any]]] = None
    retry: Optional[List[Dict[str, Any]]] = None
    comment: Optional[str] = None
    model_config = ConfigDict(extra="ignore")


class StepFunctionConfig(BaseModel):
    """Step Function state machine configuration."""

    id: str
    name: str
    role_arn: str
    definition: List[StepFunctionStateConfig]
    comment: Optional[str] = None
    model_config = ConfigDict(extra="ignore")


class StepFunctionsConfig(BaseModel):
    """Step Functions configuration, including all state machines."""

    state_machines: List[StepFunctionConfig]
    model_config = ConfigDict(extra="ignore")


class EventBridgeConfig(BaseModel):
    """EventBridge configuration for event bus names, Lambda export, and event source."""

    data_bus_name: str
    security_bus_name: str
    lambda_export_name: str
    data_event_source: str
    model_config = ConfigDict(extra="ignore")


class ChunkingConfig(BaseModel):
    strategy: Optional[str] = None
    fixed: Optional[Dict[str, Any]] = None
    semantic: Optional[Dict[str, Any]] = None
    recursive: Optional[Dict[str, Any]] = None
    sentence: Optional[Dict[str, Any]] = None
    token_based: Optional[Dict[str, Any]] = None
    sliding_window: Optional[Dict[str, Any]] = None
    custom_heuristic: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(extra="ignore")


class AICoreConfig(BaseModel):
    model_name: str
    quantize: Optional[bool] = False
    device: Optional[str] = "cpu"
    model_config = ConfigDict(extra="ignore", protected_namespaces=())


class EmbeddingConfig(BaseModel):
    model_name: str
    quantize: Optional[bool] = False
    device: Optional[str] = "cpu"
    batch_size: Optional[int] = 32
    model_config = ConfigDict(extra="ignore", protected_namespaces=())


class VectorStoreConfig(BaseModel):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    table_name: str
    batch_size: Optional[int] = 100
    model_config = ConfigDict(extra="ignore")

    model_config = ConfigDict(extra="allow")


class ShieldCraftConfig(BaseModel):
    drift_scan_schedule: Optional[str] = Field(
        default=None,
        description="How often to run drift scan (monthly, weekly, daily)",
    )

    @model_validator(mode="after")
    def enforce_prod_invariants_and_referential_integrity(self):
        # Enforce RETAIN for prod buckets
        if self.app and getattr(self.app, "env", None) == "prod":
            if self.s3 and hasattr(self.s3, "buckets"):
                for bucket in self.s3.buckets:
                    if getattr(bucket, "removal_policy", None) != "RETAIN":
                        raise ValueError(
                            "In production, S3 removal_policy must be RETAIN."
                        )
            if self.networking and hasattr(self.networking, "subnets"):
                subnets = getattr(self.networking, "subnets", [])
                if len(subnets) < 2:
                    raise ValueError(
                        "In production, networking.subnets must define at least two subnets for multi-AZ support."
                    )

        # Referential integrity for subnet and security group IDs
        subnet_ids = set()
        sg_ids = set()
        if self.networking:
            subnet_ids = {s.id for s in getattr(self.networking, "subnets", [])}
            sg_ids = {sg.id for sg in getattr(self.networking, "security_groups", [])}

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

        return self

    app: "AppConfig"
    s3: "S3Config"
    glue: "GlueConfig"
    orchestrator: Optional[OrchestratorConfig] = None
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
    eventbridge: Optional["EventBridgeConfig"] = None
    stepfunctions: Optional[StepFunctionsConfig] = None
    beir: Optional[BeirConfig] = None
    mteb: Optional[MtebConfig] = None
    secrets: Optional[Dict[str, Dict[str, Union[str, bool]]]] = None
    audit: Optional[Dict[str, Any]] = None
    overrides: Optional[Dict[str, Any]] = None
    ai_core: Optional[AICoreConfig] = None
    embedding: Optional[EmbeddingConfig] = None
    vector_store: Optional[VectorStoreConfig] = None
    chunking: Optional[ChunkingConfig] = None


# Register forward refs
StepFunctionStateConfig.model_rebuild()
StepFunctionConfig.model_rebuild()
StepFunctionsConfig.model_rebuild()
EventBridgeConfig.model_rebuild()
ShieldCraftConfig.model_rebuild()
