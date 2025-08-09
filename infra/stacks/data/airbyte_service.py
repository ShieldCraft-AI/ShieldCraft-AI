"""
ShieldCraftAI AirbyteStack: Airbyte deployment on ECS Fargate with config validation and monitoring.
"""

from typing import Dict, Optional
from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import aws_iam as iam  # pylint: disable=unused-import
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_logs as logs
from constructs import Construct  # pylint: disable=unused-import
from pydantic import BaseModel, Field, ValidationError


# --- Config Validation Model ---
class AirbyteConfig(BaseModel):
    desired_count: int = Field(default=1, ge=1)
    cpu: int = Field(default=1024, ge=256)
    memory: int = Field(default=2048, ge=512)
    db_secret_arn: Optional[str] = None
    image: str = Field(default="airbyte/airbyte:0.50.2")
    container_port: int = Field(default=8000, ge=1)
    log_group: Optional[str] = None
    subnet_type: str = Field(default="PRIVATE_WITH_EGRESS")
    health_check_path: str = Field(default="/api/v1/health")
    health_check_codes: str = Field(default="200")
    allowed_cidr: str = Field(default="0.0.0.0/0")
    removal_policy: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    environment: Dict[str, str] = Field(default_factory=dict)


class _AirbyteStackDoc:
    """CDK Stack for deploying Airbyte on ECS Fargate with best practices, config validation, and monitoring."""


def validate_airbyte_config(cfg: dict) -> AirbyteConfig:
    try:
        return AirbyteConfig(**cfg)
    except ValidationError as e:
        raise ValueError(f"Invalid Airbyte config: {e}") from e


class AirbyteStack(Stack):
    """
    CDK Stack for deploying Airbyte on ECS Fargate with best practices, config validation, and monitoring.
    """

    def __init__(
        self,
        scope,
        construct_id,
        vpc,
        config,
        airbyte_role_arn,
        *args,
        secrets_manager_arn=None,
        shared_resources=None,
        shared_tags=None,
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
            CfnOutput(
                self,
                f"{construct_id}VaultSecretArn",
                value=self.secrets_manager_arn,
                export_name=f"{construct_id}-vault-secret-arn",
            )
        if self.secrets_manager_secret and airbyte_role_arn:
            role = iam.Role.from_role_arn(self, "ImportedAirbyteRole", airbyte_role_arn)
            self.secrets_manager_secret.grant_read(role)
        airbyte_cfg_raw = config.get("airbyte", {})
        env = config.get("app", {}).get("env", "dev")
        airbyte_cfg = validate_airbyte_config(airbyte_cfg_raw)
        self._validate_cross_stack_resources(vpc, airbyte_cfg, airbyte_role_arn)
        self._apply_tags(env, airbyte_cfg, shared_tags)
        removal_policy = self._resolve_removal_policy(airbyte_cfg, env)
        db_secret = None
        if airbyte_cfg.db_secret_arn:
            db_secret = secretsmanager.Secret.from_secret_complete_arn(
                self, f"{construct_id}AirbyteDbSecret", airbyte_cfg.db_secret_arn
            )
        airbyte_sg = self._create_security_group(construct_id, vpc)
        alb_sg = self._create_alb_security_group(construct_id, vpc)
        self.cluster = ecs.Cluster(self, f"{construct_id}AirbyteCluster", vpc=vpc)
        log_group = self._create_log_group(
            construct_id, airbyte_cfg, removal_policy, env
        )
        task_role = iam.Role.from_role_arn(
            self,
            f"{construct_id}AirbyteImportedTaskRole",
            airbyte_role_arn,
            mutable=False,
        )
        task_def = self._create_task_definition(construct_id, airbyte_cfg, task_role)
        container = self._add_container(
            construct_id, task_def, airbyte_cfg, log_group, db_secret
        )
        container.add_port_mappings(
            ecs.PortMapping(container_port=airbyte_cfg.container_port)
        )
        subnet_type_value = str(airbyte_cfg.subnet_type)
        subnet_type = getattr(
            ec2.SubnetType,
            subnet_type_value.upper(),
            ec2.SubnetType.PRIVATE_WITH_EGRESS,
        )
        self.service = ecs.FargateService(
            self,
            f"{construct_id}AirbyteService",
            cluster=self.cluster,
            task_definition=task_def,
            desired_count=airbyte_cfg.desired_count,
            security_groups=[airbyte_sg],
            vpc_subnets=ec2.SubnetSelection(subnet_type=subnet_type),
        )
        alb = self._create_alb(construct_id, vpc, alb_sg, subnet_type)
        self._add_alb_listener_and_targets(construct_id, alb, self.service, airbyte_cfg)
        self._restrict_ingress(airbyte_sg, airbyte_cfg, env, alb_sg)
        self.alb = alb
        self._add_monitoring_and_outputs(construct_id, alb, log_group)
        self.shared_resources = {
            "cluster": self.cluster,
            "service": self.service,
            "alb": self.alb,
            "log_group": log_group,
            "task_alarm": self.ecs_task_alarm,
            "alb_5xx_alarm": self.alb_5xx_alarm,
        }

    def _create_alb_security_group(self, construct_id, vpc):
        return ec2.SecurityGroup(
            self,
            f"{construct_id}AirbyteAlbSecurityGroup",
            vpc=vpc,
            description="Security group for Airbyte ALB",
            allow_all_outbound=True,
        )

    def _validate_cross_stack_resources(self, vpc, airbyte_cfg, airbyte_role_arn):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        if vpc is None:
            raise ValueError("AirbyteStack requires a valid VPC reference.")
        if not airbyte_cfg.image:
            raise ValueError("AirbyteStack requires a valid image.")
        if not airbyte_role_arn:
            raise ValueError("AirbyteStack requires a valid airbyte_role_arn.")
        if not airbyte_cfg.container_port or airbyte_cfg.container_port < 1:
            raise ValueError("AirbyteStack requires a valid container_port.")
        if not airbyte_cfg.cpu or airbyte_cfg.cpu < 256:
            raise ValueError("AirbyteStack requires a valid cpu value (>=256).")
        if not airbyte_cfg.memory or airbyte_cfg.memory < 512:
            raise ValueError("AirbyteStack requires a valid memory value (>=512).")

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")

    def _apply_tags(
        self, env: str, airbyte_cfg: AirbyteConfig, shared_tags: Optional[dict]
    ):
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in airbyte_cfg.tags.items():
            self.tags.set_tag(k, v)
        if shared_tags:
            for k, v in shared_tags.items():
                self.tags.set_tag(k, v)

    def _resolve_removal_policy(self, airbyte_cfg: AirbyteConfig, env: str):
        removal_policy = airbyte_cfg.removal_policy
        if isinstance(removal_policy, str):
            removal_policy = getattr(RemovalPolicy, removal_policy.upper(), None)
        if removal_policy is None:
            removal_policy = (
                RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
            )
        return removal_policy

    def _create_security_group(self, construct_id, vpc):
        return ec2.SecurityGroup(
            self,
            f"{construct_id}AirbyteSecurityGroup",
            vpc=vpc,
            description="Security group for Airbyte",
            allow_all_outbound=True,
        )

    def _create_log_group(self, construct_id, airbyte_cfg, removal_policy, env):
        log_group_name = airbyte_cfg.log_group or f"/aws/ecs/airbyte-{env}"
        return logs.LogGroup(
            self,
            f"{construct_id}AirbyteLogGroup",
            log_group_name=log_group_name,
            removal_policy=removal_policy,
        )

    def _create_task_definition(self, construct_id, airbyte_cfg, task_role):
        return ecs.FargateTaskDefinition(
            self,
            f"{construct_id}AirbyteTaskDef",
            cpu=airbyte_cfg.cpu,
            memory_limit_mib=airbyte_cfg.memory,
            task_role=task_role,
        )

    def _add_container(self, construct_id, task_def, airbyte_cfg, log_group, db_secret):
        env_vars = airbyte_cfg.environment
        container_secrets = {}
        if airbyte_cfg.db_secret_arn and db_secret is not None:
            container_secrets["AIRBYTE_DB_SECRET"] = ecs.Secret.from_secrets_manager(
                db_secret
            )
        return task_def.add_container(
            f"{construct_id}AirbyteContainer",
            image=ecs.ContainerImage.from_registry(airbyte_cfg.image),
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="airbyte", log_group=log_group
            ),
            environment=env_vars,
            secrets=container_secrets if container_secrets else None,
        )

    def _create_alb(self, construct_id, vpc, airbyte_sg, subnet_type):
        return elbv2.ApplicationLoadBalancer(
            self,
            f"{construct_id}AirbyteALB",
            vpc=vpc,
            internet_facing=True if subnet_type == ec2.SubnetType.PUBLIC else False,
            security_group=airbyte_sg,
        )

    def _add_alb_listener_and_targets(self, construct_id, alb, service, airbyte_cfg):
        listener = alb.add_listener(
            f"{construct_id}AirbyteListener", port=80, open=True
        )
        listener.add_targets(
            f"{construct_id}AirbyteTarget",
            port=airbyte_cfg.container_port,
            targets=[service],
            health_check=elbv2.HealthCheck(
                path=airbyte_cfg.health_check_path,
                healthy_http_codes=airbyte_cfg.health_check_codes,
            ),
        )

    def _restrict_ingress(self, airbyte_sg, airbyte_cfg, env, alb_sg):
        # Harden: Only allow ALB SecurityGroup to talk to ECS unless in dev/demo
        if env == "prod":
            airbyte_sg.add_ingress_rule(
                peer=ec2.Peer.security_group_id(alb_sg.security_group_id),
                connection=ec2.Port.tcp(80),
                description="Allow HTTP from ALB SecurityGroup only",
            )
        else:
            airbyte_sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(airbyte_cfg.allowed_cidr),
                connection=ec2.Port.tcp(80),
                description="Allow HTTP from allowed CIDR",
            )

    def _add_monitoring_and_outputs(self, construct_id, alb, log_group):
        # ECS Service Task Failures metric (ServiceTaskFailures)
        ecs_task_failures_metric = cloudwatch.Metric(
            namespace="AWS/ECS",
            metric_name="ServiceTaskFailures",
            dimensions_map={
                "ClusterName": self.cluster.cluster_name,
                "ServiceName": self.service.service_name,
            },
            statistic="Sum",
            period=Duration.minutes(5),
        )
        self.ecs_task_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}AirbyteTaskFailureAlarm",
            metric=ecs_task_failures_metric,
            threshold=1,
            evaluation_periods=1,
            alarm_description="ECS task failures detected",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        CfnOutput(
            self,
            f"{construct_id}AirbyteTaskFailureAlarmArn",
            value=self.ecs_task_alarm.alarm_arn,
            export_name=f"{construct_id}-task-failure-alarm-arn",
        )
        self.alb_5xx_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}AirbyteAlb5xxAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ApplicationELB",
                metric_name="HTTPCode_Target_5XX_Count",
                dimensions_map={"LoadBalancer": alb.load_balancer_full_name},
                statistic="Sum",
                period=Duration.minutes(5),
            ),
            threshold=1,
            evaluation_periods=1,
            alarm_description="ALB 5XX errors detected",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        CfnOutput(
            self,
            f"{construct_id}AirbyteAlb5xxAlarmArn",
            value=self.alb_5xx_alarm.alarm_arn,
            export_name=f"{construct_id}-alb-5xx-alarm-arn",
        )
        # --- Outputs: ALB DNS, ECS Service Name, Log Group Name ---
        CfnOutput(
            self,
            f"{construct_id}AirbyteALBDns",
            value=alb.load_balancer_dns_name,
            export_name=f"{construct_id}-alb-dns",
        )
        CfnOutput(
            self,
            f"{construct_id}AirbyteServiceName",
            value=self.service.service_name,
            export_name=f"{construct_id}-service-name",
        )
        CfnOutput(
            self,
            f"{construct_id}AirbyteLogGroupName",
            value=log_group.log_group_name,
            export_name=f"{construct_id}-log-group",
        )
