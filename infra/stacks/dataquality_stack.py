from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_glue as glue,
    aws_iam as iam
)
from constructs import Construct

class DataQualityStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        dq_cfg = config.get('data_quality', {})
        env = config.get('app', {}).get('env', 'dev')

        # Tagging for traceability
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)

        # --- Lambda Data Quality Function ---
        dq_lambda_cfg = dq_cfg.get('lambda', {})
        dq_lambda_enabled = dq_lambda_cfg.get('enabled', False)
        if dq_lambda_enabled:
            lambda_handler = dq_lambda_cfg.get('handler', 'index.handler')
            lambda_code_path = dq_lambda_cfg.get('code_path', 'lambda/dataquality')
            lambda_env = dq_lambda_cfg.get('environment', {})
            lambda_timeout = dq_lambda_cfg.get('timeout', 60)
            lambda_memory = dq_lambda_cfg.get('memory', 256)
            lambda_log_retention = dq_lambda_cfg.get('log_retention', 7)
            # Optional: secret injection as environment variables
            lambda_secrets = dq_lambda_cfg.get('secrets', {})
            environment_vars = lambda_env.copy()
            from aws_cdk import aws_secretsmanager as secretsmanager
            from aws_cdk import aws_logs
            # Map int to aws_logs.RetentionDays
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
                3653: aws_logs.RetentionDays.TEN_YEARS
            }
            log_retention_enum = retention_map.get(lambda_log_retention, aws_logs.RetentionDays.ONE_WEEK)
            for env_name, secret_arn in lambda_secrets.items():
                # Validate secret ARN format (basic check)
                if not (isinstance(secret_arn, str) and secret_arn.startswith('arn:aws:secretsmanager:')):
                    raise ValueError(f"Invalid secret ARN for {env_name}: {secret_arn}")
                environment_vars[env_name] = secret_arn
            # Validate config
            if not lambda_handler or not lambda_code_path:
                raise ValueError("Lambda handler and code_path are required if lambda is enabled.")
            if not isinstance(lambda_timeout, int) or lambda_timeout < 1:
                raise ValueError("Lambda timeout must be a positive integer.")
            if not isinstance(lambda_memory, int) or lambda_memory < 128:
                raise ValueError("Lambda memory must be >= 128 MB.")
            from aws_cdk import Duration
            self.dq_lambda = _lambda.Function(
                self, f"{construct_id}DataQualityLambda",
                runtime=_lambda.Runtime.PYTHON_3_11,
                handler=lambda_handler,
                code=_lambda.Code.from_asset(lambda_code_path),
                environment=environment_vars,
                timeout=Duration.seconds(lambda_timeout),
                memory_size=lambda_memory,
                log_retention=log_retention_enum
            )
            from aws_cdk import CfnOutput
            CfnOutput(self, f"{construct_id}DataQualityLambdaArn", value=self.dq_lambda.function_arn, export_name=f"{construct_id}-dq-lambda-arn")

        # --- Glue Data Quality Job ---
        dq_glue_cfg = dq_cfg.get('glue_job', {})
        dq_glue_enabled = dq_glue_cfg.get('enabled', False)
        if dq_glue_enabled:
            glue_job_name = dq_glue_cfg.get('name')
            glue_role_arn = dq_glue_cfg.get('role_arn')
            glue_command_name = dq_glue_cfg.get('command_name')
            glue_script_location = dq_glue_cfg.get('script_location')
            # Validate required fields: must be explicitly set if enabled
            if not glue_job_name or not glue_command_name or not glue_script_location:
                raise ValueError("Glue job 'name', 'command_name', and 'script_location' are required if glue_job is enabled.")
            if not glue_role_arn:
                # Create a least-privilege role if not provided
                glue_role = iam.Role(
                    self, f"{construct_id}DQGlueJobRole",
                    assumed_by=iam.ServicePrincipal("glue.amazonaws.com")
                )
                glue_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"))
                glue_role_arn = glue_role.role_arn
            glue_command = {
                "name": glue_command_name,
                "scriptLocation": glue_script_location
            }
            glue_default_args = dq_glue_cfg.get('default_arguments', {})
            self.dq_glue_job = glue.CfnJob(
                self, f"{construct_id}DataQualityGlueJob",
                name=glue_job_name,
                role=glue_role_arn,
                command=glue_command,
                default_arguments=glue_default_args
            )
            from aws_cdk import CfnOutput
            CfnOutput(self, f"{construct_id}DataQualityGlueJobName", value=glue_job_name, export_name=f"{construct_id}-dq-glue-job-name")
