"""
DataQualityStack: AWS CDK Stack for Data Quality Monitoring
"""

from typing import Any, Dict, Optional
import logging
from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack, aws_cloudwatch
from aws_cdk import aws_glue as glue
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import aws_iam as iam  # pylint: disable=unused-import
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs
from constructs import Construct
from pydantic import BaseModel, Field, ValidationError


# Pydantic config model for Data Quality stack
class DataQualityConfig(BaseModel):
    tags: Dict[str, str] = Field(default_factory=dict)
    removal_policy: Optional[str] = None
    lambda_: Optional[dict] = Field(default=None, alias="lambda")
    glue_job: Optional[dict] = None


def validate_dq_config(cfg: dict) -> DataQualityConfig:
    try:
        return DataQualityConfig(**cfg)
    except ValidationError as e:
        raise ValueError(f"Invalid Data Quality config: {e}") from e


class DataQualityStack(Stack):
    logger = logging.getLogger("DataQualityStack")

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: dict,
        shared_resources: Optional[dict] = None,
        shared_tags: Optional[dict] = None,
        dq_lambda_role_arn: Optional[str] = None,
        dq_glue_role_arn: Optional[str] = None,
        secrets_manager_arn: Optional[str] = None,
        **kwargs,
    ):
        stack_kwargs = {k: kwargs[k] for k in ("env", "description") if k in kwargs}
        super().__init__(scope, construct_id, **stack_kwargs)
        # Vault integration: import the main secrets manager secret if provided
        self.secrets_manager_arn = secrets_manager_arn
        self.secrets_manager_secret = None
        if self.secrets_manager_arn:
            from aws_cdk import aws_secretsmanager as secretsmanager

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

        # Grant read access to Lambda and Glue roles if present and vault secret is imported
        if self.secrets_manager_secret:
            from aws_cdk import aws_iam as iam

            for role_arn, role_name in [
                (dq_lambda_role_arn, "ImportedDQStackLambdaRole"),
                (dq_glue_role_arn, "ImportedDQStackGlueRole"),
            ]:
                if role_arn:
                    role = iam.Role.from_role_arn(self, role_name, role_arn)
                    self.secrets_manager_secret.grant_read(role)
        dq_cfg_raw = config.get("data_quality", {})
        env = config.get("app", {}).get("env", "dev")
        try:
            dq_cfg = validate_dq_config(dq_cfg_raw)
        except Exception as e:
            self.logger.error(f"Config validation failed: {e}")
            raise
        try:
            self._validate_cross_stack_resources(
                dq_cfg, dq_lambda_role_arn, dq_glue_role_arn
            )
        except Exception as e:
            self.logger.error(f"Cross-stack resource validation failed: {e}")
            raise
        self._apply_tags(env, dq_cfg, shared_tags)
        removal_policy = self._resolve_removal_policy(dq_cfg, env)
        self.shared_resources = {}

        lambda_cfg = dq_cfg.lambda_
        if lambda_cfg is not None and not isinstance(lambda_cfg, dict):
            try:
                lambda_cfg = lambda_cfg.model_dump(exclude_none=True)
            except AttributeError:
                lambda_cfg = None
        if isinstance(lambda_cfg, dict) and lambda_cfg.get("enabled"):
            self.logger.info(f"Creating Data Quality Lambda for {construct_id}")
            # Provide defaults for handler and code_path if missing
            if "handler" not in lambda_cfg or lambda_cfg["handler"] is None:
                lambda_cfg["handler"] = "index.handler"
            if "code_path" not in lambda_cfg or lambda_cfg["code_path"] is None:
                lambda_cfg["code_path"] = "lambda/dataquality"
            self.dq_lambda = self._create_lambda(
                construct_id,
                lambda_cfg,
                removal_policy,
                shared_resources,
                dq_lambda_role_arn,
            )
            self.shared_resources["dq_lambda"] = self.dq_lambda

        glue_cfg = dq_cfg.glue_job
        if glue_cfg is not None and not isinstance(glue_cfg, dict):
            try:
                glue_cfg = glue_cfg.model_dump(exclude_none=True)
            except AttributeError:
                glue_cfg = None
        if isinstance(glue_cfg, dict) and glue_cfg.get("enabled"):
            self.logger.info(f"Creating Data Quality Glue Job for {construct_id}")
            self.dq_glue_job = self._create_glue_job(
                construct_id, glue_cfg, removal_policy, dq_glue_role_arn
            )
            self.shared_resources["dq_glue_job"] = self.dq_glue_job

    def _validate_cross_stack_resources(
        self, dq_cfg, dq_lambda_role_arn, dq_glue_role_arn
    ):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        if not isinstance(dq_cfg, DataQualityConfig):
            raise ValueError(
                "DataQualityStack requires a valid DataQualityConfig object."
            )
        lambda_cfg = dq_cfg.lambda_
        if lambda_cfg is not None:
            if not isinstance(lambda_cfg, dict):
                try:
                    lambda_cfg = lambda_cfg.model_dump(exclude_none=True)
                except AttributeError:
                    lambda_cfg = None
            if isinstance(lambda_cfg, dict) and lambda_cfg.get("enabled"):
                if not dq_lambda_role_arn:
                    raise ValueError(
                        "dq_lambda_role_arn must be provided for Data Quality Lambda."
                    )
                # Provide defaults for handler and code_path if missing
                handler = lambda_cfg.get("handler", "index.handler")
                code_path = lambda_cfg.get("code_path", "lambda/dataquality")
                if handler == "":
                    raise ValueError("Lambda handler is required if lambda is enabled.")
                if code_path == "":
                    raise ValueError(
                        "Lambda code_path is required if lambda is enabled."
                    )
                if (
                    not isinstance(lambda_cfg.get("timeout", 60), int)
                    or lambda_cfg.get("timeout", 60) < 1
                ):
                    raise ValueError("Lambda timeout must be a positive integer.")
                if (
                    not isinstance(lambda_cfg.get("memory", 256), int)
                    or lambda_cfg.get("memory", 256) < 128
                ):
                    raise ValueError("Lambda memory must be >= 128 MB.")
        glue_cfg = dq_cfg.glue_job
        if glue_cfg is not None:
            if not isinstance(glue_cfg, dict):
                try:
                    glue_cfg = glue_cfg.model_dump(exclude_none=True)
                except AttributeError:
                    glue_cfg = None
            if isinstance(glue_cfg, dict) and glue_cfg.get("enabled"):
                if not dq_glue_role_arn:
                    raise ValueError(
                        "dq_glue_role_arn must be provided for Data Quality Glue job."
                    )
                if not glue_cfg.get("name"):
                    raise ValueError(
                        "Glue job 'name' is required if glue_job is enabled."
                    )
                if not glue_cfg.get("command_name"):
                    raise ValueError(
                        "Glue job 'command_name' is required if glue_job is enabled."
                    )
                if not glue_cfg.get("script_location"):
                    raise ValueError(
                        "Glue job 'script_location' is required if glue_job is enabled."
                    )

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")

    def _apply_tags(
        self, env: str, dq_cfg: DataQualityConfig, shared_tags: Optional[dict]
    ):
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in dq_cfg.tags.items():
            self.tags.set_tag(k, v)
        if shared_tags:
            for k, v in shared_tags.items():
                self.tags.set_tag(k, v)

    def _resolve_removal_policy(self, dq_cfg: DataQualityConfig, env: str):
        removal_policy = dq_cfg.removal_policy
        if isinstance(removal_policy, str):
            removal_policy = getattr(RemovalPolicy, removal_policy.upper(), None)
        if removal_policy is None:
            removal_policy = (
                RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
            )
        return removal_policy

    def _create_lambda(
        self,
        construct_id: str,
        lambda_cfg: dict,
        removal_policy: Any,
        shared_resources: Optional[dict],
        dq_lambda_role_arn: Optional[str],
    ) -> _lambda.Function:
        handler = lambda_cfg.get("handler", "index.handler")
        code_path = lambda_cfg.get("code_path", "lambda/dataquality")
        if handler is None:
            handler = "index.handler"
        if code_path is None:
            code_path = "lambda/dataquality"
        lambda_env = lambda_cfg.get("environment", {})
        timeout = lambda_cfg.get("timeout", 60)
        memory = lambda_cfg.get("memory", 256)
        log_retention = lambda_cfg.get("log_retention", 7)
        lambda_vpc = None
        lambda_security_groups = None
        if shared_resources:
            lambda_vpc = shared_resources.get("vpc")
            lambda_security_groups = (
                [shared_resources.get("default_sg")]
                if shared_resources.get("default_sg")
                else None
            )
        secrets = lambda_cfg.get("secrets", {})
        environment_vars = lambda_env.copy()
        retention_map = {
            1: aws_logs.RetentionDays.ONE_DAY,
            3: aws_logs.RetentionDays.THREE_DAYS,
            5: aws_logs.RetentionDays.FIVE_DAYS,
            7: aws_logs.RetentionDays.ONE_WEEK,
            14: aws_logs.RetentionDays.TWO_WEEKS,
            30: aws_logs.RetentionDays.ONE_MONTH,
            60: aws_logs.RetentionDays.TWO_MONTHS,
            90: aws_logs.RetentionDays.THREE_MONTHS,
            120: aws_logs.RetentionDays.FOUR_MONTHS,
            150: aws_logs.RetentionDays.FIVE_MONTHS,
            180: aws_logs.RetentionDays.SIX_MONTHS,
            365: aws_logs.RetentionDays.ONE_YEAR,
            400: aws_logs.RetentionDays.THIRTEEN_MONTHS,
            545: aws_logs.RetentionDays.EIGHTEEN_MONTHS,
            731: aws_logs.RetentionDays.TWO_YEARS,
            1827: aws_logs.RetentionDays.FIVE_YEARS,
            3653: aws_logs.RetentionDays.TEN_YEARS,
        }
        log_retention_enum = retention_map.get(
            log_retention, aws_logs.RetentionDays.ONE_WEEK
        )
        for env_name, secret_arn in secrets.items():
            if not (
                isinstance(secret_arn, str)
                and secret_arn.startswith("arn:aws:secretsmanager:")
            ):
                self.logger.error(f"Invalid secret ARN for {env_name}: {secret_arn}")
                raise ValueError(f"Invalid secret ARN for {env_name}: {secret_arn}")
            environment_vars[env_name] = secret_arn
        if not handler or not code_path:
            self.logger.error(
                "Lambda handler and code_path are required if lambda is enabled."
            )
            raise ValueError(
                "Lambda handler and code_path are required if lambda is enabled."
            )
        if not isinstance(timeout, int) or timeout < 1:
            self.logger.error("Lambda timeout must be a positive integer.")
            raise ValueError("Lambda timeout must be a positive integer.")
        if not isinstance(memory, int) or memory < 128:
            self.logger.error("Lambda memory must be >= 128 MB.")
            raise ValueError("Lambda memory must be >= 128 MB.")
        log_group_name = f"/aws/lambda/{construct_id}DataQualityLambda"
        lambda_log_group = aws_logs.LogGroup(
            self,
            f"{construct_id}DataQualityLambdaLogGroup",
            log_group_name=log_group_name,
            retention=log_retention_enum,
            removal_policy=removal_policy,
        )
        lambda_kwargs = {
            "runtime": _lambda.Runtime.PYTHON_3_11,
            "handler": handler,
            "code": _lambda.Code.from_asset(code_path),
            "environment": environment_vars,
            "timeout": Duration.seconds(timeout),
            "memory_size": memory,
            "log_group": lambda_log_group,
        }
        if lambda_vpc:
            lambda_kwargs["vpc"] = lambda_vpc
        if lambda_security_groups:
            lambda_kwargs["security_groups"] = lambda_security_groups
        if not dq_lambda_role_arn:
            self.logger.error(
                "dq_lambda_role_arn must be provided for Data Quality Lambda"
            )
            raise ValueError(
                "dq_lambda_role_arn must be provided for Data Quality Lambda"
            )
        lambda_role = iam.Role.from_role_arn(
            self,
            f"{construct_id}DQImportedLambdaRole",
            dq_lambda_role_arn,
            mutable=False,
        )
        lambda_kwargs["role"] = lambda_role
        dq_lambda = _lambda.Function(
            self, f"{construct_id}DataQualityLambda", **lambda_kwargs
        )
        dq_lambda.apply_removal_policy(removal_policy)
        CfnOutput(
            self,
            f"{construct_id}DataQualityLambdaArn",
            value=dq_lambda.function_arn,
            export_name=f"{construct_id}-dq-lambda-arn",
        )
        # Monitoring: Lambda error alarm
        self.lambda_error_alarm = aws_cloudwatch.Alarm(
            self,
            f"{construct_id}DataQualityLambdaErrorAlarm",
            metric=dq_lambda.metric_errors(),
            threshold=1,
            evaluation_periods=1,
            alarm_description="Lambda function errors detected",
            comparison_operator=aws_cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        # Anomaly detection band for Lambda errors
        lambda_anomaly_detector = aws_cloudwatch.CfnAnomalyDetector(
            self,
            f"{construct_id}DataQualityLambdaErrorAnomalyDetector",
            metric_name="Errors",
            namespace="AWS/Lambda",
            stat="Sum",
            dimensions=[
                aws_cloudwatch.CfnAnomalyDetector.DimensionProperty(
                    name="FunctionName",
                    value=dq_lambda.function_name,
                )
            ],
        )
        # Anomaly detection alarm for Lambda errors
        self.lambda_anomaly_alarm = aws_cloudwatch.CfnAlarm(
            self,
            f"{construct_id}DataQualityLambdaAnomalyAlarm",
            comparison_operator="GreaterThanUpperThreshold",
            evaluation_periods=1,
            threshold=0,
            alarm_description="Anomaly detected in Lambda function errors",
            metrics=[
                aws_cloudwatch.CfnAlarm.MetricDataQueryProperty(
                    id="m1",
                    metric_stat=aws_cloudwatch.CfnAlarm.MetricStatProperty(
                        metric=aws_cloudwatch.CfnAlarm.MetricProperty(
                            namespace="AWS/Lambda",
                            metric_name="Errors",
                            dimensions=[
                                aws_cloudwatch.CfnAlarm.DimensionProperty(
                                    name="FunctionName",
                                    value=dq_lambda.function_name,
                                )
                            ],
                        ),
                        period=300,
                        stat="Sum",
                    ),
                    return_data=True,
                ),
                aws_cloudwatch.CfnAlarm.MetricDataQueryProperty(
                    id="ad1",
                    expression="ANOMALY_DETECTION_BAND(m1, 2)",
                    label="LambdaErrorAnomalyBand",
                    return_data=True,
                ),
            ],
        )
        CfnOutput(
            self,
            f"{construct_id}DataQualityLambdaErrorAlarmArn",
            value=self.lambda_error_alarm.alarm_arn,
            export_name=f"{construct_id}-dq-lambda-error-alarm-arn",
        )
        CfnOutput(
            self,
            f"{construct_id}DataQualityLambdaAnomalyAlarmArn",
            value=self.lambda_anomaly_alarm.ref,
            export_name=f"{construct_id}-dq-lambda-anomaly-alarm-arn",
        )
        return dq_lambda

    def _create_glue_job(
        self,
        construct_id: str,
        glue_cfg: dict,
        removal_policy: Any,  # pylint: disable=unused-argument
        dq_glue_role_arn: Optional[str],
    ) -> glue.CfnJob:
        glue_job_name = glue_cfg.get("name")
        glue_command_name = glue_cfg.get("command_name")
        glue_script_location = glue_cfg.get("script_location")
        if not glue_job_name or not glue_command_name or not glue_script_location:
            raise ValueError(
                "Glue job 'name', 'command_name', and 'script_location' are required if glue_job is enabled."
            )
        if not dq_glue_role_arn:
            raise ValueError(
                "dq_glue_role_arn must be provided for Data Quality Glue job"
            )
        glue_command = {
            "name": glue_command_name,
            "scriptLocation": glue_script_location,
        }
        glue_default_args = glue_cfg.get("default_arguments", {})
        dq_glue_job = glue.CfnJob(
            self,
            f"{construct_id}DataQualityGlueJob",
            name=glue_job_name,
            role=dq_glue_role_arn,
            command=glue_command,
            default_arguments=glue_default_args,
        )
        CfnOutput(
            self,
            f"{construct_id}DataQualityGlueJobName",
            value=glue_job_name,
            export_name=f"{construct_id}-dq-glue-job-name",
        )
        # Monitoring: Glue job failure alarm
        glue_failure_alarm = aws_cloudwatch.Alarm(
            self,
            f"{construct_id}DataQualityGlueJobFailureAlarm",
            metric=aws_cloudwatch.Metric(
                namespace="AWS/Glue",
                metric_name="FailedJobs",
                dimensions_map={"JobName": glue_job_name},
                statistic="Sum",
                period=Duration.minutes(5),
            ),
            threshold=1,
            evaluation_periods=1,
            alarm_description="Glue job failures detected",
            comparison_operator=aws_cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        # Anomaly detection band for Glue job failures
        glue_anomaly_detector = aws_cloudwatch.CfnAnomalyDetector(
            self,
            f"{construct_id}DataQualityGlueJobAnomalyDetector",
            metric_name="FailedJobs",
            namespace="AWS/Glue",
            stat="Sum",
            dimensions=[
                aws_cloudwatch.CfnAnomalyDetector.DimensionProperty(
                    name="JobName",
                    value=glue_job_name,
                )
            ],
        )
        # Anomaly detection alarm for Glue job failures
        glue_anomaly_alarm = aws_cloudwatch.CfnAlarm(
            self,
            f"{construct_id}DataQualityGlueJobAnomalyAlarm",
            comparison_operator="GreaterThanUpperThreshold",
            evaluation_periods=1,
            threshold=0,
            alarm_description="Anomaly detected in Glue job failures",
            metrics=[
                aws_cloudwatch.CfnAlarm.MetricDataQueryProperty(
                    id="m1",
                    metric_stat=aws_cloudwatch.CfnAlarm.MetricStatProperty(
                        metric=aws_cloudwatch.CfnAlarm.MetricProperty(
                            namespace="AWS/Glue",
                            metric_name="FailedJobs",
                            dimensions=[
                                aws_cloudwatch.CfnAlarm.DimensionProperty(
                                    name="JobName",
                                    value=glue_job_name,
                                )
                            ],
                        ),
                        period=300,
                        stat="Sum",
                    ),
                    return_data=True,
                ),
                aws_cloudwatch.CfnAlarm.MetricDataQueryProperty(
                    id="ad1",
                    expression="ANOMALY_DETECTION_BAND(m1, 2)",
                    label="GlueFailedJobsAnomalyBand",
                    return_data=True,
                ),
            ],
        )
        CfnOutput(
            self,
            f"{construct_id}DataQualityGlueJobFailureAlarmArn",
            value=glue_failure_alarm.alarm_arn,
            export_name=f"{construct_id}-dq-glue-failure-alarm-arn",
        )
        CfnOutput(
            self,
            f"{construct_id}DataQualityGlueJobAnomalyAlarmArn",
            value=glue_anomaly_alarm.ref,
            export_name=f"{construct_id}-dq-glue-anomaly-alarm-arn",
        )
        return dq_glue_job
