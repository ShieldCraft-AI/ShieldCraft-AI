"""
ShieldCraftAI SageMakerStack: AWS SageMaker model and endpoint deployment,
monitoring, and cross-stack integration.
"""

import re
from typing import List, Optional, cast
from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import aws_iam as iam  # pylint: disable=unused-import
from aws_cdk import aws_sagemaker as sagemaker
from constructs import Construct  # pylint: disable=unused-import
from pydantic import BaseModel, Field, ValidationError  # pylint: disable=unused-import


def arn_validator(v: str) -> str:
    arn_regex = r"^arn:aws:iam::\d{12}:role/.+"
    if not re.match(arn_regex, v):
        raise ValueError("execution_role_arn must be a valid IAM role ARN")
    return v


class SageMakerConfig(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_name: str = Field(default="shieldcraft-model", min_length=1)
    image_uri: str
    model_artifact_s3: str
    execution_role_arn: str = Field(..., description="IAM role ARN")
    instance_type: str = Field(default="ml.m5.large")
    endpoint_name: Optional[str] = None
    initial_instance_count: int = Field(default=1, ge=1)
    initial_variant_weight: float = Field(default=1.0, ge=0.0, le=1.0)
    alarm_threshold_status_failed: int = Field(default=2, ge=1)
    alarm_threshold_invocation_4xx: int = Field(default=1, ge=0)
    alarm_threshold_latency_ms: int = Field(default=1000, ge=1)
    alarm_threshold_cpu_utilization: float = Field(default=90.0, ge=0.0, le=100.0)
    alarm_threshold_memory_utilization: float = Field(default=90.0, ge=0.0, le=100.0)
    enable_sns_alerts: bool = Field(default=False)
    sns_topic_arn: Optional[str] = None
    kms_key_arn: Optional[str] = Field(
        default=None, description="KMS key ARN for encryption"
    )
    vpc_id: Optional[str] = Field(
        default=None, description="VPC ID for endpoint network isolation"
    )
    subnet_ids: List[str] = Field(
        default_factory=list, description="Subnet IDs for endpoint network isolation"
    )
    security_group_ids: List[str] = Field(
        default_factory=list,
        description="Security group IDs for endpoint network isolation",
    )
    s3_lifecycle_days: Optional[int] = Field(
        default=None,
        description="Days until S3 model artifacts expire (lifecycle rule)",
    )
    enable_cost_alarm: bool = Field(default=False)
    cost_alarm_threshold_usd: float = Field(default=100.0, ge=0.0)
    cost_alarm_sns_topic_arn: Optional[str] = None

    @classmethod
    def validate_execution_role_arn(cls, v):
        return arn_validator(v)

    def model_post_init(self, __context):
        self.execution_role_arn = self.validate_execution_role_arn(
            self.execution_role_arn
        )


class AppConfig(BaseModel):
    env: str = Field(default="dev")
    owner: Optional[str] = None
    data_classification: Optional[str] = None
    component: Optional[str] = None


class SageMakerStack(Stack):
    """
    CDK Stack for deploying and monitoring AWS SageMaker models and endpoints with robust config validation and tagging.
    """

    def _create_endpoint(self, sm_cfg: SageMakerConfig, endpoint_config, env: str):
        model_name = sm_cfg.model_name
        endpoint_name = sm_cfg.endpoint_name or f"{model_name}-endpoint"
        sanitized_model_name = SageMakerStack.sanitize_export_name(model_name)
        endpoint = sagemaker.CfnEndpoint(
            self,
            f"{model_name}Endpoint",
            endpoint_name=endpoint_name,
            endpoint_config_name=endpoint_config.endpoint_config_name,
        )
        endpoint.apply_removal_policy(
            RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
        )
        CfnOutput(
            self,
            f"{sanitized_model_name}EndpointName",
            value=str(endpoint.endpoint_name),
            export_name=f"{sanitized_model_name}-endpoint-name",
        )
        endpoint_arn = (
            f"arn:aws:sagemaker:{self.region}:{self.account}:endpoint/{endpoint_name}"
        )
        CfnOutput(
            self,
            f"{sanitized_model_name}EndpointArn",
            value=endpoint_arn,
            export_name=f"{sanitized_model_name}-endpoint-arn",
        )
        return endpoint, endpoint_arn

    """CDK Stack for deploying and monitoring AWS SageMaker
    models and endpoints with robust config validation and tagging."""

    def __init__(
        self,
        scope,
        construct_id,
        config=None,
        *args,
        sagemaker_role_arn=None,
        secrets_manager_arn=None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)
        if secrets_manager_arn:
            self.secrets_manager_arn = secrets_manager_arn
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
        if (
            hasattr(self, "secrets_manager_secret")
            and self.secrets_manager_secret
            and sagemaker_role_arn
        ):
            role = iam.Role.from_role_arn(self, "SageMakerRole", sagemaker_role_arn)
            if hasattr(self.secrets_manager_secret, "grant_read"):
                self.secrets_manager_secret.grant_read(role)
        config = config or {}
        sm_cfg = self._validate_sagemaker_config(config)
        app_cfg = self._validate_app_config(config)
        env = app_cfg.env
        self._validate_cross_stack_resources(sm_cfg)
        self._apply_tags(app_cfg)
        model_tuple = self._create_model(
            sm_cfg, sagemaker_role_arn or sm_cfg.execution_role_arn, env
        )
        model = model_tuple[0]
        sanitized_model_name = (
            model_tuple[2] if len(model_tuple) > 2 else model_tuple[1]
        )
        endpoint_config_tuple = self._create_endpoint_config(sm_cfg, model, env)
        endpoint_config = (
            endpoint_config_tuple[0]
            if isinstance(endpoint_config_tuple, tuple)
            else endpoint_config_tuple
        )
        endpoint_tuple = self._create_endpoint(sm_cfg, endpoint_config, env)
        endpoint = (
            endpoint_tuple[0] if isinstance(endpoint_tuple, tuple) else endpoint_tuple
        )
        endpoint_name = getattr(endpoint, "endpoint_name", None) or (
            endpoint_tuple[1]
            if isinstance(endpoint_tuple, tuple) and len(endpoint_tuple) > 1
            else ""
        )
        alarm_resources = self._create_alarms(sm_cfg, endpoint_name)
        if (
            sm_cfg.enable_cost_alarm
            and sm_cfg.cost_alarm_threshold_usd
            and sm_cfg.cost_alarm_sns_topic_arn
        ):
            pass
        self.shared_resources = {
            "model": model,
            "endpoint_config": endpoint_config,
            "endpoint": endpoint,
            **alarm_resources,
        }

    def _validate_cross_stack_resources(self, sm_cfg):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        if not sm_cfg.model_name:
            raise ValueError("SageMakerStack requires a valid model_name.")
        if not sm_cfg.image_uri:
            raise ValueError("SageMakerStack requires a valid image_uri.")
        if not sm_cfg.model_artifact_s3:
            raise ValueError("SageMakerStack requires a valid model_artifact_s3.")
        if not sm_cfg.execution_role_arn:
            raise ValueError("SageMakerStack requires a valid execution_role_arn.")
        if not sm_cfg.instance_type:
            raise ValueError("SageMakerStack requires a valid instance_type.")
        if sm_cfg.vpc_id:
            if (
                not sm_cfg.subnet_ids
                or not isinstance(sm_cfg.subnet_ids, list)
                or len(sm_cfg.subnet_ids) == 0
            ):
                raise ValueError(
                    "SageMakerStack vpc_id provided but subnet_ids missing."
                )
            if (
                not sm_cfg.security_group_ids
                or not isinstance(sm_cfg.security_group_ids, list)
                or len(sm_cfg.security_group_ids) == 0
            ):
                raise ValueError(
                    "SageMakerStack vpc_id provided but security_group_ids missing."
                )

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")

    def _validate_sagemaker_config(self, config: dict) -> SageMakerConfig:
        try:
            return SageMakerConfig(**config.get("sagemaker", {}))
        except ValidationError as e:
            raise ValueError(f"Invalid SageMaker config: {e}") from e

    def _validate_app_config(self, config: dict) -> AppConfig:
        try:
            return AppConfig(**config.get("app", {}))
        except ValidationError as e:
            raise ValueError(f"Invalid app config: {e}") from e

    def _apply_tags(self, app_cfg: AppConfig) -> None:
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", app_cfg.env)
        if app_cfg.owner is not None:
            self.tags.set_tag("Owner", app_cfg.owner)
        if app_cfg.data_classification is not None:
            self.tags.set_tag("DataClassification", app_cfg.data_classification)
        if app_cfg.component is not None:
            self.tags.set_tag("Component", app_cfg.component)

    def _create_model(self, sm_cfg: SageMakerConfig, sagemaker_role_arn: str, env: str):
        model_name = sm_cfg.model_name
        image_uri = sm_cfg.image_uri
        model_artifact_s3 = sm_cfg.model_artifact_s3
        execution_role_arn = (
            sagemaker_role_arn
            if sagemaker_role_arn is not None
            else sm_cfg.execution_role_arn
        )
        sanitized_model_name = self.sanitize_export_name(model_name)

        # S3 Lifecycle Policy for Model Artifacts (if enabled)
        if (
            sm_cfg.s3_lifecycle_days
            and model_artifact_s3
            and model_artifact_s3.startswith("s3://")
        ):
            import warnings

            bucket_name = model_artifact_s3.split("/", 3)[2]

        primary_container = {
            "image": image_uri,
            "modelDataUrl": model_artifact_s3,
        }
        model_kwargs = {
            "execution_role_arn": execution_role_arn,
            "primary_container": primary_container,
            "model_name": model_name,
        }
        if sm_cfg.vpc_id and sm_cfg.subnet_ids and sm_cfg.security_group_ids:
            model_kwargs["vpc_config"] = cast(
                dict,
                {
                    "subnets": list(sm_cfg.subnet_ids),
                    "securityGroupIds": list(sm_cfg.security_group_ids),
                },
            )  # type: ignore
        model = sagemaker.CfnModel(
            self,
            f"{model_name}Model",
            execution_role_arn=execution_role_arn,
            primary_container=primary_container,
            model_name=model_name,
            vpc_config=model_kwargs.get("vpc_config"),
        )  # type: ignore
        model.apply_removal_policy(
            RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
        )
        CfnOutput(
            self,
            f"{sanitized_model_name}ModelName",
            value=str(model.model_name or model_name),
            export_name=f"{sanitized_model_name}-model-name",
        )
        model_arn = f"arn:aws:sagemaker:{self.region}:{self.account}:model/{model_name}"
        CfnOutput(
            self,
            f"{sanitized_model_name}ModelArn",
            value=model_arn,
            export_name=f"{sanitized_model_name}-model-arn",
        )
        return model, model_arn, sanitized_model_name

    def _create_endpoint_config(self, sm_cfg: SageMakerConfig, model, env: str):
        model_name = sm_cfg.model_name
        instance_type = sm_cfg.instance_type
        initial_instance_count = sm_cfg.initial_instance_count
        initial_variant_weight = sm_cfg.initial_variant_weight
        sanitized_model_name = SageMakerStack.sanitize_export_name(model_name)
        production_variant = {
            "modelName": model_name,
            "variantName": f"{model_name}-variant",
            "initialInstanceCount": initial_instance_count,
            "instanceType": instance_type,
            "initialVariantWeight": initial_variant_weight,
        }
        endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            f"{model_name}EndpointConfig",
            production_variants=[production_variant],
            endpoint_config_name=f"{model_name}-endpoint-config",
        )
        endpoint_config.apply_removal_policy(
            RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
        )
        CfnOutput(
            self,
            f"{sanitized_model_name}EndpointConfigName",
            value=str(endpoint_config.endpoint_config_name),
            export_name=f"{sanitized_model_name}-endpoint-config-name",
        )
        endpoint_config_arn = f"arn:aws:sagemaker:{self.region}:{self.account}:endpoint-config/{model_name}-endpoint-config"
        CfnOutput(
            self,
            f"{sanitized_model_name}EndpointConfigArn",
            value=endpoint_config_arn,
            export_name=f"{sanitized_model_name}-endpoint-config-arn",
        )
        return endpoint_config, endpoint_config_arn

    def _create_alarms(self, sm_cfg: SageMakerConfig, endpoint_name: str):
        alarm_resources = {}
        model_name = sm_cfg.model_name
        sanitized_model_name = self.sanitize_export_name(model_name)
        # Endpoint InService/Failed
        endpoint_status_alarm = cloudwatch.Alarm(
            self,
            f"{model_name}EndpointStatusFailedAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="EndpointStatus",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Maximum",
            ),
            threshold=sm_cfg.alarm_threshold_status_failed,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint status is Failed",
            alarm_name=f"{model_name}-endpoint-status-failed-alarm",
        )
        alarm_resources["endpoint_status_failed_alarm"] = endpoint_status_alarm
        CfnOutput(
            self,
            f"{sanitized_model_name}EndpointStatusFailedAlarmArn",
            value=endpoint_status_alarm.alarm_arn,
            export_name=f"{sanitized_model_name}-endpoint-status-failed-alarm-arn",
        )

        # Invocation 4XX Errors
        invocation_4xx_errors_alarm = cloudwatch.Alarm(
            self,
            f"{model_name}Invocation4XXErrorsAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="Invocation4XXErrors",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Sum",
            ),
            threshold=sm_cfg.alarm_threshold_invocation_4xx,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint 4XX errors",
            alarm_name=f"{model_name}-invocation-4xx-errors-alarm",
        )
        alarm_resources["invocation_4xx_errors_alarm"] = invocation_4xx_errors_alarm
        CfnOutput(
            self,
            f"{sanitized_model_name}Invocation4XXErrorsAlarmArn",
            value=invocation_4xx_errors_alarm.alarm_arn,
            export_name=f"{sanitized_model_name}-invocation-4xx-errors-alarm-arn",
        )

        # Model Latency
        model_latency_alarm = cloudwatch.Alarm(
            self,
            f"{model_name}ModelLatencyAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="ModelLatency",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Average",
            ),
            threshold=sm_cfg.alarm_threshold_latency_ms,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker model latency above threshold",
            alarm_name=f"{model_name}-model-latency-alarm",
        )
        alarm_resources["model_latency_alarm"] = model_latency_alarm
        CfnOutput(
            self,
            f"{sanitized_model_name}ModelLatencyAlarmArn",
            value=model_latency_alarm.alarm_arn,
            export_name=f"{sanitized_model_name}-model-latency-alarm-arn",
        )

        # CPU Utilization
        cpu_utilization_alarm = cloudwatch.Alarm(
            self,
            f"{model_name}CPUUtilizationAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="CPUUtilization",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Average",
            ),
            threshold=sm_cfg.alarm_threshold_cpu_utilization,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint CPU utilization above threshold",
            alarm_name=f"{model_name}-cpu-utilization-alarm",
        )
        alarm_resources["cpu_utilization_alarm"] = cpu_utilization_alarm
        CfnOutput(
            self,
            f"{sanitized_model_name}CPUUtilizationAlarmArn",
            value=cpu_utilization_alarm.alarm_arn,
            export_name=f"{sanitized_model_name}-cpu-utilization-alarm-arn",
        )

        # Memory Utilization
        memory_utilization_alarm = cloudwatch.Alarm(
            self,
            f"{model_name}MemoryUtilizationAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="MemoryUtilization",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Average",
            ),
            threshold=sm_cfg.alarm_threshold_memory_utilization,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint memory utilization above threshold",
            alarm_name=f"{model_name}-memory-utilization-alarm",
        )
        alarm_resources["memory_utilization_alarm"] = memory_utilization_alarm
        CfnOutput(
            self,
            f"{sanitized_model_name}MemoryUtilizationAlarmArn",
            value=memory_utilization_alarm.alarm_arn,
            export_name=f"{sanitized_model_name}-memory-utilization-alarm-arn",
        )
        return alarm_resources

    @staticmethod
    def sanitize_export_name(name: str) -> str:
        # Only allow alphanumeric, colon, hyphen
        return re.sub(r"[^A-Za-z0-9:-]", "-", name)
