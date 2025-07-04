from aws_cdk import (
    Stack,
    aws_sagemaker as sagemaker,
)
from constructs import Construct
from pydantic import BaseModel, Field, ValidationError
import re

def arn_validator(v: str) -> str:
    import re
    arn_regex = r"^arn:aws:iam::\d{12}:role/.+"
    if not re.match(arn_regex, v):
        raise ValueError("execution_role_arn must be a valid IAM role ARN")
    return v

from typing import List
class SageMakerConfig(BaseModel):
    model_config = {'protected_namespaces': ()}
    model_name: str = Field(default="shieldcraft-model", min_length=1)
    image_uri: str
    model_artifact_s3: str
    execution_role_arn: str = Field(..., description="IAM role ARN", validation_alias="execution_role_arn")
    instance_type: str = Field(default="ml.m5.large")
    endpoint_name: str | None = None
    initial_instance_count: int = Field(default=1, ge=1)
    initial_variant_weight: float = Field(default=1.0, ge=0.0, le=1.0)
    alarm_threshold_status_failed: int = Field(default=2, ge=1)
    alarm_threshold_invocation_4xx: int = Field(default=1, ge=0)
    alarm_threshold_latency_ms: int = Field(default=1000, ge=1)
    alarm_threshold_cpu_utilization: float = Field(default=90.0, ge=0.0, le=100.0)
    alarm_threshold_memory_utilization: float = Field(default=90.0, ge=0.0, le=100.0)
    enable_sns_alerts: bool = Field(default=False)
    sns_topic_arn: str | None = None
    kms_key_arn: str | None = Field(default=None, description="KMS key ARN for encryption")
    vpc_id: str | None = Field(default=None, description="VPC ID for endpoint network isolation")
    subnet_ids: List[str] = Field(default_factory=list, description="Subnet IDs for endpoint network isolation")
    security_group_ids: List[str] = Field(default_factory=list, description="Security group IDs for endpoint network isolation")
    s3_lifecycle_days: int | None = Field(default=None, description="Days until S3 model artifacts expire (lifecycle rule)")
    enable_cost_alarm: bool = Field(default=False)
    cost_alarm_threshold_usd: float = Field(default=100.0, ge=0.0)
    cost_alarm_sns_topic_arn: str | None = None

    # Custom validation for execution_role_arn
    @classmethod
    def validate_execution_role_arn(cls, v):
        return arn_validator(v)

    def model_post_init(self, __context):
        self.execution_role_arn = self.validate_execution_role_arn(self.execution_role_arn)
class AppConfig(BaseModel):
    env: str = Field(default="dev")
    owner: str | None = None
    data_classification: str | None = None
    component: str | None = None
class SageMakerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict = None, sagemaker_role_arn: str = None, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        config = config or {}
        try:
            sm_cfg = SageMakerConfig(**config.get('sagemaker', {}))
        except ValidationError as e:
            raise ValueError(f"Invalid SageMaker config: {e}")
        try:
            app_cfg = AppConfig(**config.get('app', {}))
        except ValidationError as e:
            raise ValueError(f"Invalid app config: {e}")

        env = app_cfg.env
        # Standard tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        # Advanced/cost/compliance tags
        if app_cfg.owner:
            self.tags.set_tag("Owner", app_cfg.owner)
        if app_cfg.data_classification:
            self.tags.set_tag("DataClassification", app_cfg.data_classification)
        if app_cfg.component:
            self.tags.set_tag("Component", app_cfg.component)

        # --- SageMaker Model, EndpointConfig, and Endpoint (single-model, real-time) ---
        model_name = sm_cfg.model_name
        image_uri = sm_cfg.image_uri
        model_artifact_s3 = sm_cfg.model_artifact_s3
        # Use sagemaker_role_arn if provided, else config value
        execution_role_arn = sagemaker_role_arn or sm_cfg.execution_role_arn

        instance_type = sm_cfg.instance_type
        endpoint_name = sm_cfg.endpoint_name or f"{model_name}-endpoint"
        initial_instance_count = sm_cfg.initial_instance_count
        initial_variant_weight = sm_cfg.initial_variant_weight
        alarm_threshold_status_failed = sm_cfg.alarm_threshold_status_failed
        alarm_threshold_invocation_4xx = sm_cfg.alarm_threshold_invocation_4xx
        alarm_threshold_latency_ms = sm_cfg.alarm_threshold_latency_ms

        from aws_cdk import RemovalPolicy, CfnOutput, aws_cloudwatch as cloudwatch, Duration

        sanitized_model_name = self.sanitize_export_name(model_name)

        # --- S3 Lifecycle Policy for Model Artifacts (if enabled) ---
        if sm_cfg.s3_lifecycle_days and model_artifact_s3 and model_artifact_s3.startswith("s3://"):
            # CDK limitation: cannot add lifecycle rules to imported buckets
            # Emit a warning for operator awareness
            import warnings
            bucket_name = model_artifact_s3.split("/", 3)[2]
            warnings.warn(f"[ShieldCraftAI] S3 lifecycle rule for model artifacts not applied: bucket '{bucket_name}' is imported. Set lifecycle policy manually if required.")

        # 1. Model
        model_kwargs = dict(
            execution_role_arn=execution_role_arn,
            primary_container={
                "image": image_uri,
                "modelDataUrl": model_artifact_s3
            },
            model_name=model_name
        )
        # Note: CfnModel does not support kms_key_id/kms_key_arn directly. If needed, pass as env var or use CfnEndpointConfig.
        # VPC config for network isolation
        if sm_cfg.vpc_id and sm_cfg.subnet_ids and sm_cfg.security_group_ids:
            model_kwargs["vpc_config"] = {
                "subnets": sm_cfg.subnet_ids,
                "securityGroupIds": sm_cfg.security_group_ids
            }
        model = sagemaker.CfnModel(
            self, f"{model_name}Model",
            **model_kwargs
        )
        model.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{sanitized_model_name}ModelName", value=model.model_name, export_name=f"{sanitized_model_name}-model-name")
        model_arn = f"arn:aws:sagemaker:{self.region}:{self.account}:model/{model_name}"
        CfnOutput(self, f"{sanitized_model_name}ModelArn", value=model_arn, export_name=f"{sanitized_model_name}-model-arn")

        # 2. EndpointConfig
        endpoint_config_kwargs = dict(
            production_variants=[{
                "modelName": model_name,
                "variantName": "AllTraffic",
                "initialInstanceCount": initial_instance_count,
                "instanceType": instance_type,
                "initialVariantWeight": initial_variant_weight
            }],
            endpoint_config_name=f"{model_name}-config"
        )
        if sm_cfg.kms_key_arn:
            endpoint_config_kwargs["kms_key_id"] = sm_cfg.kms_key_arn
        endpoint_config = sagemaker.CfnEndpointConfig(
            self, f"{model_name}EndpointConfig",
            **endpoint_config_kwargs
        )
        endpoint_config.add_dependency(model)
        endpoint_config.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{sanitized_model_name}EndpointConfigName", value=endpoint_config.endpoint_config_name, export_name=f"{sanitized_model_name}-endpoint-config-name")
        endpoint_config_arn = f"arn:aws:sagemaker:{self.region}:{self.account}:endpoint-config/{endpoint_config.endpoint_config_name}"
        CfnOutput(self, f"{sanitized_model_name}EndpointConfigArn", value=endpoint_config_arn, export_name=f"{sanitized_model_name}-endpoint-config-arn")

        # 3. Endpoint
        endpoint = sagemaker.CfnEndpoint(
            self, f"{model_name}Endpoint",
            endpoint_name=endpoint_name,
            endpoint_config_name=endpoint_config.endpoint_config_name
        )
        endpoint.add_dependency(endpoint_config)
        endpoint.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{sanitized_model_name}EndpointName", value=endpoint.endpoint_name, export_name=f"{sanitized_model_name}-endpoint-name")
        endpoint_arn = f"arn:aws:sagemaker:{self.region}:{self.account}:endpoint/{endpoint.endpoint_name}"
        CfnOutput(self, f"{sanitized_model_name}EndpointArn", value=endpoint_arn, export_name=f"{sanitized_model_name}-endpoint-arn")

        # --- CloudWatch Alarms for SageMaker Endpoint Monitoring ---
        alarm_resources = {}

        # Endpoint InService/Failed
        endpoint_status_alarm = cloudwatch.Alarm(
            self, f"{model_name}EndpointStatusFailedAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="EndpointStatus",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Maximum"
            ),
            threshold=alarm_threshold_status_failed,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint status is Failed",
            alarm_name=f"{model_name}-endpoint-status-failed-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_status = sns.Topic.from_topic_arn(self, "AlarmTopicStatusFailed", sm_cfg.sns_topic_arn)
            endpoint_status_alarm.add_alarm_action(SnsAction(alarm_topic_status))
        CfnOutput(self, f"{sanitized_model_name}EndpointStatusFailedAlarmArn", value=endpoint_status_alarm.alarm_arn, export_name=f"{sanitized_model_name}-endpoint-status-failed-alarm-arn")
        alarm_resources["endpoint_status_failed_alarm"] = endpoint_status_alarm

        # Invocation errors
        invocation_errors_alarm = cloudwatch.Alarm(
            self, f"{model_name}InvocationErrorsAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="Invocation4XXErrors",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Sum"
            ),
            threshold=alarm_threshold_invocation_4xx,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint invocation 4XX errors",
            alarm_name=f"{model_name}-invocation-4xx-errors-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_invocation = sns.Topic.from_topic_arn(self, "AlarmTopicInvocationErrors", sm_cfg.sns_topic_arn)
            invocation_errors_alarm.add_alarm_action(SnsAction(alarm_topic_invocation))
        CfnOutput(self, f"{sanitized_model_name}Invocation4XXErrorsAlarmArn", value=invocation_errors_alarm.alarm_arn, export_name=f"{sanitized_model_name}-invocation-4xx-errors-alarm-arn")
        alarm_resources["invocation_4xx_errors_alarm"] = invocation_errors_alarm

        # Model latency
        model_latency_alarm = cloudwatch.Alarm(
            self, f"{model_name}ModelLatencyAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="ModelLatency",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Average"
            ),
            threshold=alarm_threshold_latency_ms,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint model latency > 1s",
            alarm_name=f"{model_name}-model-latency-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_latency = sns.Topic.from_topic_arn(self, "AlarmTopicModelLatency", sm_cfg.sns_topic_arn)
            model_latency_alarm.add_alarm_action(SnsAction(alarm_topic_latency))
        CfnOutput(self, f"{sanitized_model_name}ModelLatencyAlarmArn", value=model_latency_alarm.alarm_arn, export_name=f"{sanitized_model_name}-model-latency-alarm-arn")
        alarm_resources["model_latency_alarm"] = model_latency_alarm

        # CPU Utilization (optional, if metric available)
        cpu_alarm = cloudwatch.Alarm(
            self, f"{model_name}CPUUtilizationAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="CPUUtilization",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Average"
            ),
            threshold=sm_cfg.alarm_threshold_cpu_utilization,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint CPU utilization high",
            alarm_name=f"{model_name}-cpu-utilization-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_cpu = sns.Topic.from_topic_arn(self, "AlarmTopicCPUUtilization", sm_cfg.sns_topic_arn)
            cpu_alarm.add_alarm_action(SnsAction(alarm_topic_cpu))
        CfnOutput(self, f"{sanitized_model_name}CPUUtilizationAlarmArn", value=cpu_alarm.alarm_arn, export_name=f"{sanitized_model_name}-cpu-utilization-alarm-arn")
        alarm_resources["cpu_utilization_alarm"] = cpu_alarm

        # Memory Utilization (optional, if metric available)
        memory_alarm = cloudwatch.Alarm(
            self, f"{model_name}MemoryUtilizationAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="MemoryUtilization",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Average"
            ),
            threshold=sm_cfg.alarm_threshold_memory_utilization,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint memory utilization high",
            alarm_name=f"{model_name}-memory-utilization-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_mem = sns.Topic.from_topic_arn(self, "AlarmTopicMemoryUtilization", sm_cfg.sns_topic_arn)
            memory_alarm.add_alarm_action(SnsAction(alarm_topic_mem))
        CfnOutput(self, f"{sanitized_model_name}MemoryUtilizationAlarmArn", value=memory_alarm.alarm_arn, export_name=f"{sanitized_model_name}-memory-utilization-alarm-arn")
        alarm_resources["memory_utilization_alarm"] = memory_alarm

        # --- Cost Anomaly/Usage Alarm (optional) ---
        if sm_cfg.enable_cost_alarm and sm_cfg.cost_alarm_sns_topic_arn:
            from aws_cdk import aws_cloudwatch as cloudwatch, aws_budgets as budgets
            cost_alarm = budgets.CfnBudget(
                self,
                f"{model_name}CostBudget",
                budget={
                    "budgetType": "COST",
                    "timeUnit": "MONTHLY",
                    "budgetLimit": {"amount": sm_cfg.cost_alarm_threshold_usd, "unit": "USD"},
                    "costFilters": {},
                    "costTypes": {"IncludeTax": True, "IncludeSubscription": True, "UseBlended": False},
                    "name": f"{model_name}-monthly-cost-budget"
                },
                notifications_with_subscribers=[{
                    "notification": {
                        "notificationType": "ACTUAL",
                        "comparisonOperator": "GREATER_THAN",
                        "threshold": 100.0,
                        "thresholdType": "PERCENTAGE"
                    },
                    "subscribers": [{"subscriptionType": "SNS", "address": sm_cfg.cost_alarm_sns_topic_arn}]
                }]
            )
            CfnOutput(self, f"{sanitized_model_name}CostBudgetId", value=cost_alarm.ref, export_name=f"{sanitized_model_name}-cost-budget-id")

        # Shared resources dict for downstream stacks
        self.shared_resources = {
            "model": model,
            "endpoint_config": endpoint_config,
            "endpoint": endpoint,
            **alarm_resources
        }
    @staticmethod
    def sanitize_export_name(name: str) -> str:
        # Only allow alphanumeric, colon, hyphen
        return re.sub(r'[^A-Za-z0-9:-]', '-', name)


    def __init__(self, scope: Construct, construct_id: str, config: dict = None, sagemaker_role_arn: str = None, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        config = config or {}
        try:
            sm_cfg = SageMakerConfig(**config.get('sagemaker', {}))
        except ValidationError as e:
            raise ValueError(f"Invalid SageMaker config: {e}")
        try:
            app_cfg = AppConfig(**config.get('app', {}))
        except ValidationError as e:
            raise ValueError(f"Invalid app config: {e}")

        env = app_cfg.env
        # Standard tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        # Advanced/cost/compliance tags
        if app_cfg.owner:
            self.tags.set_tag("Owner", app_cfg.owner)
        if app_cfg.data_classification:
            self.tags.set_tag("DataClassification", app_cfg.data_classification)
        if app_cfg.component:
            self.tags.set_tag("Component", app_cfg.component)

        # --- SageMaker Model, EndpointConfig, and Endpoint (single-model, real-time) ---
        model_name = sm_cfg.model_name
        image_uri = sm_cfg.image_uri
        model_artifact_s3 = sm_cfg.model_artifact_s3
        # Use sagemaker_role_arn if provided, else fall back to config
        execution_role_arn = sagemaker_role_arn if sagemaker_role_arn is not None else sm_cfg.execution_role_arn

        instance_type = sm_cfg.instance_type
        endpoint_name = sm_cfg.endpoint_name or f"{model_name}-endpoint"
        initial_instance_count = sm_cfg.initial_instance_count
        initial_variant_weight = sm_cfg.initial_variant_weight
        alarm_threshold_status_failed = sm_cfg.alarm_threshold_status_failed
        alarm_threshold_invocation_4xx = sm_cfg.alarm_threshold_invocation_4xx
        alarm_threshold_latency_ms = sm_cfg.alarm_threshold_latency_ms

        from aws_cdk import RemovalPolicy, CfnOutput, aws_cloudwatch as cloudwatch, Duration

        sanitized_model_name = self.sanitize_export_name(model_name)

        # --- S3 Lifecycle Policy for Model Artifacts (if enabled) ---
        if sm_cfg.s3_lifecycle_days and model_artifact_s3 and model_artifact_s3.startswith("s3://"):
            # CDK limitation: cannot add lifecycle rules to imported buckets
            # Emit a warning for operator awareness
            import warnings
            bucket_name = model_artifact_s3.split("/", 3)[2]
            warnings.warn(f"[ShieldCraftAI] S3 lifecycle rule for model artifacts not applied: bucket '{bucket_name}' is imported. Set lifecycle policy manually if required.")

        # 1. Model
        model_kwargs = dict(
            execution_role_arn=execution_role_arn,
            primary_container={
                "image": image_uri,
                "modelDataUrl": model_artifact_s3
            },
            model_name=model_name
        )
        # Note: CfnModel does not support kms_key_id/kms_key_arn directly. If needed, pass as env var or use CfnEndpointConfig.
        # VPC config for network isolation
        if sm_cfg.vpc_id and sm_cfg.subnet_ids and sm_cfg.security_group_ids:
            model_kwargs["vpc_config"] = {
                "subnets": sm_cfg.subnet_ids,
                "securityGroupIds": sm_cfg.security_group_ids
            }
        model = sagemaker.CfnModel(
            self, f"{model_name}Model",
            **model_kwargs
        )
        model.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{sanitized_model_name}ModelName", value=model.model_name, export_name=f"{sanitized_model_name}-model-name")
        model_arn = f"arn:aws:sagemaker:{self.region}:{self.account}:model/{model_name}"
        CfnOutput(self, f"{sanitized_model_name}ModelArn", value=model_arn, export_name=f"{sanitized_model_name}-model-arn")

        # 2. EndpointConfig
        endpoint_config_kwargs = dict(
            production_variants=[{
                "modelName": model_name,
                "variantName": "AllTraffic",
                "initialInstanceCount": initial_instance_count,
                "instanceType": instance_type,
                "initialVariantWeight": initial_variant_weight
            }],
            endpoint_config_name=f"{model_name}-config"
        )
        if sm_cfg.kms_key_arn:
            endpoint_config_kwargs["kms_key_id"] = sm_cfg.kms_key_arn
        endpoint_config = sagemaker.CfnEndpointConfig(
            self, f"{model_name}EndpointConfig",
            **endpoint_config_kwargs
        )
        endpoint_config.add_dependency(model)
        endpoint_config.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{sanitized_model_name}EndpointConfigName", value=endpoint_config.endpoint_config_name, export_name=f"{sanitized_model_name}-endpoint-config-name")
        endpoint_config_arn = f"arn:aws:sagemaker:{self.region}:{self.account}:endpoint-config/{endpoint_config.endpoint_config_name}"
        CfnOutput(self, f"{sanitized_model_name}EndpointConfigArn", value=endpoint_config_arn, export_name=f"{sanitized_model_name}-endpoint-config-arn")

        # 3. Endpoint
        endpoint = sagemaker.CfnEndpoint(
            self, f"{model_name}Endpoint",
            endpoint_name=endpoint_name,
            endpoint_config_name=endpoint_config.endpoint_config_name
        )
        endpoint.add_dependency(endpoint_config)
        endpoint.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{sanitized_model_name}EndpointName", value=endpoint.endpoint_name, export_name=f"{sanitized_model_name}-endpoint-name")
        endpoint_arn = f"arn:aws:sagemaker:{self.region}:{self.account}:endpoint/{endpoint.endpoint_name}"
        CfnOutput(self, f"{sanitized_model_name}EndpointArn", value=endpoint_arn, export_name=f"{sanitized_model_name}-endpoint-arn")

        # --- CloudWatch Alarms for SageMaker Endpoint Monitoring ---
        alarm_resources = {}

        # Endpoint InService/Failed
        endpoint_status_alarm = cloudwatch.Alarm(
            self, f"{model_name}EndpointStatusFailedAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="EndpointStatus",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Maximum"
            ),
            threshold=alarm_threshold_status_failed,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint status is Failed",
            alarm_name=f"{model_name}-endpoint-status-failed-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_status = sns.Topic.from_topic_arn(self, "AlarmTopicStatusFailed", sm_cfg.sns_topic_arn)
            endpoint_status_alarm.add_alarm_action(SnsAction(alarm_topic_status))
        CfnOutput(self, f"{sanitized_model_name}EndpointStatusFailedAlarmArn", value=endpoint_status_alarm.alarm_arn, export_name=f"{sanitized_model_name}-endpoint-status-failed-alarm-arn")
        alarm_resources["endpoint_status_failed_alarm"] = endpoint_status_alarm

        # Invocation errors
        invocation_errors_alarm = cloudwatch.Alarm(
            self, f"{model_name}InvocationErrorsAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="Invocation4XXErrors",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Sum"
            ),
            threshold=alarm_threshold_invocation_4xx,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint invocation 4XX errors",
            alarm_name=f"{model_name}-invocation-4xx-errors-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_invocation = sns.Topic.from_topic_arn(self, "AlarmTopicInvocationErrors", sm_cfg.sns_topic_arn)
            invocation_errors_alarm.add_alarm_action(SnsAction(alarm_topic_invocation))
        CfnOutput(self, f"{sanitized_model_name}Invocation4XXErrorsAlarmArn", value=invocation_errors_alarm.alarm_arn, export_name=f"{sanitized_model_name}-invocation-4xx-errors-alarm-arn")
        alarm_resources["invocation_4xx_errors_alarm"] = invocation_errors_alarm

        # Model latency
        model_latency_alarm = cloudwatch.Alarm(
            self, f"{model_name}ModelLatencyAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="ModelLatency",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Average"
            ),
            threshold=alarm_threshold_latency_ms,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint model latency > 1s",
            alarm_name=f"{model_name}-model-latency-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_latency = sns.Topic.from_topic_arn(self, "AlarmTopicModelLatency", sm_cfg.sns_topic_arn)
            model_latency_alarm.add_alarm_action(SnsAction(alarm_topic_latency))
        CfnOutput(self, f"{sanitized_model_name}ModelLatencyAlarmArn", value=model_latency_alarm.alarm_arn, export_name=f"{sanitized_model_name}-model-latency-alarm-arn")
        alarm_resources["model_latency_alarm"] = model_latency_alarm

        # CPU Utilization (optional, if metric available)
        cpu_alarm = cloudwatch.Alarm(
            self, f"{model_name}CPUUtilizationAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="CPUUtilization",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Average"
            ),
            threshold=sm_cfg.alarm_threshold_cpu_utilization,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint CPU utilization high",
            alarm_name=f"{model_name}-cpu-utilization-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_cpu = sns.Topic.from_topic_arn(self, "AlarmTopicCPUUtilization", sm_cfg.sns_topic_arn)
            cpu_alarm.add_alarm_action(SnsAction(alarm_topic_cpu))
        CfnOutput(self, f"{sanitized_model_name}CPUUtilizationAlarmArn", value=cpu_alarm.alarm_arn, export_name=f"{sanitized_model_name}-cpu-utilization-alarm-arn")
        alarm_resources["cpu_utilization_alarm"] = cpu_alarm

        # Memory Utilization (optional, if metric available)
        memory_alarm = cloudwatch.Alarm(
            self, f"{model_name}MemoryUtilizationAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="MemoryUtilization",
                dimensions_map={"EndpointName": endpoint_name},
                period=Duration.minutes(1),
                statistic="Average"
            ),
            threshold=sm_cfg.alarm_threshold_memory_utilization,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="SageMaker endpoint memory utilization high",
            alarm_name=f"{model_name}-memory-utilization-alarm"
        )
        if sm_cfg.enable_sns_alerts and sm_cfg.sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic_mem = sns.Topic.from_topic_arn(self, "AlarmTopicMemoryUtilization", sm_cfg.sns_topic_arn)
            memory_alarm.add_alarm_action(SnsAction(alarm_topic_mem))
        CfnOutput(self, f"{sanitized_model_name}MemoryUtilizationAlarmArn", value=memory_alarm.alarm_arn, export_name=f"{sanitized_model_name}-memory-utilization-alarm-arn")
        alarm_resources["memory_utilization_alarm"] = memory_alarm

        # --- Cost Anomaly/Usage Alarm (optional) ---
        if sm_cfg.enable_cost_alarm and sm_cfg.cost_alarm_sns_topic_arn:
            from aws_cdk import aws_cloudwatch as cloudwatch, aws_budgets as budgets
            cost_alarm = budgets.CfnBudget(
                self,
                f"{model_name}CostBudget",
                budget={
                    "budgetType": "COST",
                    "timeUnit": "MONTHLY",
                    "budgetLimit": {"amount": sm_cfg.cost_alarm_threshold_usd, "unit": "USD"},
                    "costFilters": {},
                    "costTypes": {"IncludeTax": True, "IncludeSubscription": True, "UseBlended": False},
                    "name": f"{model_name}-monthly-cost-budget"
                },
                notifications_with_subscribers=[{
                    "notification": {
                        "notificationType": "ACTUAL",
                        "comparisonOperator": "GREATER_THAN",
                        "threshold": 100.0,
                        "thresholdType": "PERCENTAGE"
                    },
                    "subscribers": [{"subscriptionType": "SNS", "address": sm_cfg.cost_alarm_sns_topic_arn}]
                }]
            )
            CfnOutput(self, f"{sanitized_model_name}CostBudgetId", value=cost_alarm.ref, export_name=f"{sanitized_model_name}-cost-budget-id")

        # Shared resources dict for downstream stacks
        self.shared_resources = {
            "model": model,
            "endpoint_config": endpoint_config,
            "endpoint": endpoint,
            **alarm_resources
        }
