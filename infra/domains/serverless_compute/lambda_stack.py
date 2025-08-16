"""
ShieldCraft AI LambdaStack: Secure, robust, and modular AWS Lambda deployment stack
with config validation, tagging, and monitoring. Hardened for best practices.
"""

import json
from typing import Any, Optional
from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_ec2 as ec2  # pylint: disable=unused-import
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import custom_resources as cr
from constructs import Construct  # pylint: disable=unused-import
from pydantic import BaseModel, Field, ValidationError


class LambdaFunctionConfig(BaseModel):
    """Pydantic model for validating Lambda function configuration."""

    name: str
    runtime: str = "PYTHON_3_11"
    handler: str = "index.handler"
    code_path: str
    environment: dict[str, Any] = Field(default_factory=dict)
    timeout: int = 60
    vpc: bool = True
    memory: int = 128
    role_arn: Optional[str] = None
    removal_policy: Optional[str] = None
    log_retention: Optional[int] = None
    secrets: Optional[dict[str, str]] = None  # key: env var, value: secret ARN


class LambdaStack(Stack):
    """CDK Stack for deploying and monitoring AWS Lambda functions with robust
    config validation and tagging."""

    def __init__(
        self,
        scope,
        construct_id,
        vpc,
        config,
        *args,
        lambda_role_arn=None,
        shared_resources=None,
        secrets_manager_arn=None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)
        self.secrets_manager_arn = secrets_manager_arn
        self.secrets_manager_secret = None
        if self.secrets_manager_arn:
            self.secrets_manager_secret = (
                secretsmanager.Secret.from_secret_complete_arn(
                    self, "ImportedVaultSecret", self.secrets_manager_arn
                )
            )
        functions_cfg = config.get("lambda_", {}).get("functions", [])
        if not isinstance(functions_cfg, list):
            raise ValueError("LambdaStack 'functions' config must be a list.")
        try:
            lambda_cfgs = [LambdaFunctionConfig(**fn) for fn in functions_cfg]
        except ValidationError as e:
            raise ValueError(f"Invalid LambdaStack config: {e}") from e
        env = config.get("app", {}).get("env", "dev")
        # Tagging is now handled at orchestration level (app.py)
        self._validate_cross_stack_resources(
            vpc, lambda_role_arn, shared_resources, lambda_cfgs
        )
        fn_names = set()
        self.functions = []
        self.shared_resources = {}
        for fn_cfg in lambda_cfgs:
            if not fn_cfg.name or not fn_cfg.code_path:
                raise ValueError(
                    "Lambda function config must include 'name' and 'code_path'."
                )
            if not fn_cfg.role_arn and lambda_role_arn:
                fn_cfg.role_arn = lambda_role_arn
            name = fn_cfg.name
            runtime = fn_cfg.runtime
            handler = fn_cfg.handler
            code_path = fn_cfg.code_path
            environment = fn_cfg.environment
            timeout = fn_cfg.timeout
            use_vpc = fn_cfg.vpc
            memory = fn_cfg.memory
            role_arn = fn_cfg.role_arn
            removal_policy_str = fn_cfg.removal_policy
            removal_policy = (
                RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
            )
            if isinstance(removal_policy_str, str):
                removal_policy = getattr(
                    RemovalPolicy, removal_policy_str.upper(), removal_policy
                )
            if name in fn_names:
                raise ValueError(f"Duplicate Lambda function name: {name}")
            fn_names.add(name)
            role = None
            if role_arn:
                role = iam.Role.from_role_arn(self, f"{name}Role", role_arn)
            elif shared_resources and shared_resources.get("lambda_role"):
                role = shared_resources["lambda_role"]
            lambda_vpc = vpc
            lambda_sgs = None
            if shared_resources and shared_resources.get("lambda_security_groups"):
                lambda_sgs = shared_resources["lambda_security_groups"]
            log_retention = fn_cfg.log_retention
            retention_enum = None
            log_group = None
            if log_retention is not None:
                retention_enum = getattr(
                    aws_logs.RetentionDays,
                    f"DAYS_{log_retention}",
                    aws_logs.RetentionDays.ONE_WEEK,
                )
                log_group = aws_logs.LogGroup(
                    self, f"{name}LogGroup", retention=retention_enum
                )
            if not hasattr(_lambda.Runtime, runtime):
                raise ValueError(f"Invalid Lambda runtime: {runtime}")
            lambda_kwargs = {
                "runtime": getattr(_lambda.Runtime, runtime),
                "handler": handler,
                "code": _lambda.Code.from_asset(code_path),
                "environment": environment,
                "timeout": Duration.seconds(timeout),
                "memory_size": memory,
                "vpc": lambda_vpc if use_vpc else None,
                "security_groups": lambda_sgs,
                "role": role,
            }
            fn = _lambda.Function(self, name, **lambda_kwargs)
            if log_group is not None:
                fn.node.add_dependency(log_group)
            if fn_cfg.secrets:
                for env_var, secret_arn in fn_cfg.secrets.items():
                    secret = secretsmanager.Secret.from_secret_complete_arn(
                        self, f"{name}{env_var}Secret", secret_arn
                    )
                    fn.add_environment(env_var, secret.secret_value.to_string())
                    secret.grant_read(fn)
            fn.apply_removal_policy(removal_policy)
            error_alarm = cloudwatch.Alarm(
                self,
                f"{construct_id}Lambda{name}ErrorAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Errors",
                    dimensions_map={"FunctionName": fn.function_name},
                    statistic="Sum",
                    period=Duration.minutes(5),
                ),
                threshold=1,
                evaluation_periods=1,
                alarm_description=f"Lambda {name} errors detected",
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            )
            throttle_alarm = cloudwatch.Alarm(
                self,
                f"{construct_id}Lambda{name}ThrottleAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Throttles",
                    dimensions_map={"FunctionName": fn.function_name},
                    statistic="Sum",
                    period=Duration.minutes(5),
                ),
                threshold=1,
                evaluation_periods=1,
                alarm_description=f"Lambda {name} throttles detected",
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            )
            timeout_seconds: float = 60.0
            if (
                hasattr(fn, "timeout")
                and fn.timeout is not None
                and hasattr(fn.timeout, "to_seconds")
            ):
                timeout_val = fn.timeout.to_seconds()  # type: ignore[call-arg]
                if isinstance(timeout_val, (int, float)):
                    timeout_seconds = float(timeout_val)
            duration_alarm = cloudwatch.Alarm(
                self,
                f"{construct_id}Lambda{name}DurationAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Duration",
                    dimensions_map={"FunctionName": fn.function_name},
                    statistic="Average",
                    period=Duration.minutes(5),
                ),
                threshold=timeout_seconds * 0.9,  # 90% of timeout
                evaluation_periods=1,
                alarm_description=f"Lambda {name} duration high",
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            )
            self._export_resource(f"{construct_id}Lambda{name}Name", fn.function_name)
            self._export_resource(f"{construct_id}Lambda{name}Arn", fn.function_arn)
            self._export_resource(
                f"{construct_id}Lambda{name}ErrorAlarmArn", error_alarm.alarm_arn
            )
            self._export_resource(
                f"{construct_id}Lambda{name}ThrottleAlarmArn", throttle_alarm.alarm_arn
            )
            self._export_resource(
                f"{construct_id}Lambda{name}DurationAlarmArn", duration_alarm.alarm_arn
            )
            self.shared_resources[name] = {
                "function": fn,
                "role": fn.role,
                "error_alarm": error_alarm,
                "throttle_alarm": throttle_alarm,
                "duration_alarm": duration_alarm,
            }
            self.functions.append(fn)

        topic_lambda_cfg = next(
            (f for f in lambda_cfgs if f.name == "msk_topic_creator"), None
        )
        if topic_lambda_cfg and shared_resources and shared_resources.get("msk"):
            msk_cluster_arn = shared_resources["msk"].get("cluster_arn")
            topic_config = config.get("msk", {}).get("topics", [])

            topic_lambda_cfg.environment.update(
                {
                    "MSK_CLUSTER_ARN": msk_cluster_arn,
                    "TOPIC_CONFIG": json.dumps(topic_config),
                }
            )

            fn = self.shared_resources["msk_topic_creator"]["function"]
            msk_arn = msk_cluster_arn
            if fn.role:
                fn.role.add_to_policy(
                    iam.PolicyStatement(
                        actions=[
                            "kafka:DescribeCluster",
                            "kafka:GetBootstrapBrokers",
                            "kafka:CreateTopic",
                            "kafka:ListTopics",
                            "kafka:DescribeTopic",
                        ],
                        resources=[msk_arn],
                    )
                )

            cr.Provider(self, "MskTopicCreatorProvider", on_event_handler=fn)
            cr.AwsCustomResource(
                self,
                "MskTopicCreatorCustomResource",
                on_create={
                    "service": "Lambda",
                    "action": "invoke",
                    "parameters": {
                        "FunctionName": fn.function_name,
                        "Payload": json.dumps(
                            {
                                "ClusterArn": msk_cluster_arn,
                                "TopicConfig": topic_config,
                            }
                        ),
                    },
                    "physicalResourceId": cr.PhysicalResourceId.of(
                        f"MskTopicCreatorCustomResource-{msk_cluster_arn}"
                    ),
                },
                policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                    resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
                ),
            )

    def _validate_cross_stack_resources(
        self, vpc, lambda_role_arn, shared_resources, lambda_cfgs
    ):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        if vpc is None:
            raise ValueError("LambdaStack requires a valid VPC reference.")
        if not isinstance(lambda_cfgs, list):
            raise ValueError(
                "LambdaStack requires a list of LambdaFunctionConfig objects."
            )
        for fn_cfg in lambda_cfgs:
            if not getattr(fn_cfg, "name", None):
                raise ValueError(f"Lambda function config missing name: {fn_cfg}")
            if not getattr(fn_cfg, "code_path", None):
                raise ValueError(f"Lambda function config missing code_path: {fn_cfg}")
        # Validate IAM role ARNs if provided
        if lambda_role_arn is not None and not isinstance(lambda_role_arn, str):
            raise ValueError(
                "LambdaStack lambda_role_arn must be a string if provided."
            )
        # Validate shared resources if provided
        if shared_resources is not None and not isinstance(shared_resources, dict):
            raise ValueError("LambdaStack shared_resources must be a dict if provided.")

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")
