"""
Attack Simulation Stack
"""

import json
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_lambda as _lambda,
    aws_iam as iam,
    Stack,
    Duration,
    CfnOutput,
    Tags,
)
from constructs import Construct


class AttackSimulationStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        simulation_config=None,
        secrets_manager_arn=None,
        stack_tags=None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # --- Tag propagation (cost, owner, environment) ---
        default_tags = {
            "Project": "ShieldCraftAI",
            "Environment": "Prod",
            "Owner": "MLOpsTeam",
        }
        tags_to_apply = stack_tags or default_tags
        for k, v in tags_to_apply.items():
            Tags.of(self).add(k, v)

        # --- Validate simulation_config ---
        self.simulation_config = simulation_config or {}
        if not isinstance(self.simulation_config, dict):
            raise TypeError("simulation_config must be a dict")
        # Example validation: require 'attack_types' key
        if "attack_types" not in self.simulation_config:
            CfnOutput(
                self,
                "AttackSimulationConfigWarning",
                value="Missing 'attack_types' in simulation_config",
            )

        # --- IAM role for Lambda with least privilege ---
        simulation_lambda_role = iam.Role(
            self,
            "AttackSimulationLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        # Only allow writing logs, not full CloudWatch access
        simulation_lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=["*"],
            )
        )
        # Add additional policies for simulation targets as needed

        # --- SecretsManager integration (if ARN provided) ---
        self.secrets_manager_secret = None
        if secrets_manager_arn:
            from aws_cdk import aws_secretsmanager as secretsmanager

            self.secrets_manager_secret = (
                secretsmanager.Secret.from_secret_complete_arn(
                    self, "ImportedAttackSimSecret", secrets_manager_arn
                )
            )
            CfnOutput(
                self,
                "AttackSimulationSecretArn",
                value=secrets_manager_arn,
                export_name=f"{construct_id}-attack-sim-secret-arn",
            )

        # --- Lambda function to orchestrate attack simulations ---
        self.simulation_lambda = _lambda.Function(
            self,
            "AttackSimulationLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="attack_simulation.handler",
            code=_lambda.Code.from_asset("lambda/attack_simulation"),
            environment={
                "SIMULATION_CONFIG": json.dumps(self.simulation_config),
                **({"SECRET_ARN": secrets_manager_arn} if secrets_manager_arn else {}),
            },
            timeout=Duration.seconds(300),
            role=simulation_lambda_role,
        )

        # --- CloudWatch alarm for simulation failures ---
        self.simulation_failure_alarm = cloudwatch.Alarm(
            self,
            "AttackSimulationFailureAlarm",
            metric=self.simulation_lambda.metric_errors(),
            threshold=1,
            evaluation_periods=1,
            alarm_description="Alarm for failed attack simulation runs",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )

        # --- Export Lambda ARN and alarm ARN for cross-stack usage ---
        CfnOutput(
            self, "AttackSimulationLambdaArn", value=self.simulation_lambda.function_arn
        )
        CfnOutput(
            self,
            "AttackSimulationFailureAlarmArn",
            value=self.simulation_failure_alarm.alarm_arn,
        )
