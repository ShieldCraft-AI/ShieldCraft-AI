"""
ShieldCraft AI OpenSearchStack: Secure, robust, and modular AWS OpenSearch deployment stack
with config validation, tagging, and monitoring. Hardened for best practices.
"""

from typing import Any, Optional
from aws_cdk import CfnOutput, CfnTag, Duration, RemovalPolicy, Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import aws_iam as iam  # pylint: disable=unused-import
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_opensearchservice as opensearch
from constructs import Construct  # pylint: disable=unused-import
from pydantic import BaseModel, Field, ValidationError


# --- Pydantic config validation ---
class OpenSearchDomainConfig(BaseModel):
    """Pydantic model for validating OpenSearch domain configuration."""

    id: str
    name: str
    engine_version: str
    subnet_ids: Optional[list[str]] = None
    security_group_ids: Optional[list[str]] = None
    node_to_node_encryption_options: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {"enabled": True}
    )
    encryption_at_rest_options: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {"enabled": True}
    )
    ebs_options: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {
            "ebsEnabled": True,
            "volumeSize": 20,
            "volumeType": "gp3",
        }
    )
    cluster_config: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {"instanceType": "m6g.large.search", "instanceCount": 2}
    )
    advanced_security_options: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {"enabled": True, "internalUserDatabaseEnabled": True}
    )
    access_policies: Optional[Any] = None


class OpenSearchStackConfig(BaseModel):
    """Pydantic model for validating OpenSearch stack configuration."""

    opensearch: dict = Field(default_factory=dict)
    app: dict = Field(default_factory=dict)


class OpenSearchStack(Stack):
    """CDK Stack for deploying and monitoring AWS OpenSearch domains
    with robust config validation and tagging."""

    def __init__(
        self,
        scope,
        construct_id,
        vpc,
        config,
        *args,
        opensearch_role_arn=None,
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
            CfnOutput(
                self,
                f"{construct_id}VaultSecretArn",
                value=self.secrets_manager_arn,
                export_name=f"{construct_id}-vault-secret-arn",
            )
        if self.secrets_manager_secret and opensearch_role_arn:
            role = iam.Role.from_role_arn(
                self, "ImportedOpenSearchRole", opensearch_role_arn
            )
            self.secrets_manager_secret.grant_read(role)
        try:
            _ = OpenSearchStackConfig(**config)
        except ValidationError as e:
            raise ValueError(f"Invalid OpenSearch stack config: {e}") from e
        opensearch_cfg = config.get("opensearch", {})
        env = config.get("app", {}).get("env", "dev")
        self._validate_cross_stack_resources(vpc, opensearch_cfg)
        tags = {"Project": "ShieldCraftAI", "Environment": env}
        tags.update(opensearch_cfg.get("tags", {}))
        for k, v in tags.items():
            self.tags.set_tag(k, v)
        opensearch_sg = self._create_security_group(
            opensearch_cfg, vpc, env, construct_id
        )
        domain_cfg = opensearch_cfg.get("domain", {})
        domain = self._create_domain(
            domain_cfg, vpc, opensearch_sg, env, construct_id, tags
        )
        self.domain = domain["domain"]
        domain_name = domain["domain_name"]
        alarms_cfg = opensearch_cfg.get("alarms", {})
        self._create_alarms(domain_name, alarms_cfg, construct_id)
        self.shared_resources = {
            "domain": self.domain,
            "security_group": opensearch_sg,
        }
        if (
            hasattr(self, "cluster_status_red_alarm")
            and self.cluster_status_red_alarm is not None
        ):
            self.shared_resources["cluster_status_red_alarm"] = (
                self.cluster_status_red_alarm
            )
        if (
            hasattr(self, "index_writes_blocked_alarm")
            and self.index_writes_blocked_alarm is not None
        ):
            self.shared_resources["index_writes_blocked_alarm"] = (
                self.index_writes_blocked_alarm
            )
        if (
            hasattr(self, "free_storage_space_alarm")
            and self.free_storage_space_alarm is not None
        ):
            self.shared_resources["free_storage_space_alarm"] = (
                self.free_storage_space_alarm
            )
        if (
            hasattr(self, "cpu_utilization_alarm")
            and self.cpu_utilization_alarm is not None
        ):
            self.shared_resources["cpu_utilization_alarm"] = self.cpu_utilization_alarm

    def _validate_cross_stack_resources(self, vpc, opensearch_cfg):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        if vpc is None:
            raise ValueError("OpenSearchStack requires a valid VPC reference.")
        if not isinstance(opensearch_cfg, dict):
            raise ValueError("OpenSearchStack requires a valid opensearch config dict.")
        domain_cfg = opensearch_cfg.get("domain", {})
        if not domain_cfg.get("name"):
            raise ValueError("OpenSearch domain config missing 'name'.")
        if not domain_cfg.get("id"):
            raise ValueError("OpenSearch domain config missing 'id'.")
        if not domain_cfg.get("engine_version"):
            raise ValueError("OpenSearch domain config missing 'engine_version'.")

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")

    def _create_security_group(
        self,
        opensearch_cfg,
        vpc,
        env,
        construct_id,
    ):
        sg_cfg = opensearch_cfg.get("security_group", {})
        sg_id = sg_cfg.get("id", "OpenSearchSecurityGroup")
        sg_desc = sg_cfg.get("description", "Security group for OpenSearch")
        allow_all_outbound = sg_cfg.get("allow_all_outbound", True)
        opensearch_sg = ec2.SecurityGroup(
            self,
            sg_id,
            vpc=vpc,
            description=sg_desc,
            allow_all_outbound=allow_all_outbound,
        )
        # Harden: restrict ingress/egress as needed
        # opensearch_sg.add_ingress_rule(...)
        opensearch_sg.apply_removal_policy(
            RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
        )
        CfnOutput(
            self,
            f"{construct_id}OpenSearchSecurityGroupId",
            value=opensearch_sg.security_group_id,
            export_name=f"{construct_id}-opensearch-sg-id",
        )
        return opensearch_sg

    def _create_domain(
        self,
        domain_cfg,
        vpc,
        opensearch_sg,
        env,
        construct_id,
        tags,
    ):
        try:
            validated = OpenSearchDomainConfig(**domain_cfg)
        except ValidationError as e:
            raise ValueError(f"Invalid OpenSearch domain config: {e}") from e
        domain_id = validated.id
        domain_name = validated.name
        engine_version = validated.engine_version
        subnet_ids = validated.subnet_ids or [
            subnet.subnet_id for subnet in vpc.private_subnets
        ]
        security_group_ids = validated.security_group_ids or [
            opensearch_sg.security_group_id
        ]
        node_to_node_encryption_options = validated.node_to_node_encryption_options
        encryption_at_rest_options = validated.encryption_at_rest_options
        ebs_options = validated.ebs_options
        cluster_config = validated.cluster_config
        advanced_security_options = validated.advanced_security_options
        access_policies = validated.access_policies
        # Tag propagation for domain (must use CfnTag for L1)
        domain_tags = [CfnTag(key=k, value=v) for k, v in tags.items()]

        self._validate_domain_config(
            domain_id, domain_name, engine_version, subnet_ids, security_group_ids
        )

        domain = opensearch.CfnDomain(
            self,
            domain_id,
            domain_name=domain_name,
            engine_version=engine_version,
            vpc_options={
                "subnetIds": subnet_ids,
                "securityGroupIds": security_group_ids,
            },
            node_to_node_encryption_options=node_to_node_encryption_options,
            encryption_at_rest_options=encryption_at_rest_options,
            ebs_options=ebs_options,
            cluster_config=cluster_config,
            advanced_security_options=advanced_security_options,
            access_policies=access_policies,
            tags=domain_tags,
        )
        domain.apply_removal_policy(
            RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
        )
        CfnOutput(
            self,
            f"{construct_id}OpenSearchDomainName",
            value=domain_name,
            export_name=f"{construct_id}-opensearch-domain-name",
        )
        domain_arn = f"arn:aws:es:{self.region}:{self.account}:domain/{domain_name}"
        CfnOutput(
            self,
            f"{construct_id}OpenSearchDomainArn",
            value=domain_arn,
            export_name=f"{construct_id}-opensearch-domain-arn",
        )
        return {"domain": domain, "domain_name": domain_name}

    def _validate_domain_config(
        self,
        domain_id,
        domain_name,
        engine_version,
        subnet_ids,
        security_group_ids,
    ):
        if not domain_id or not domain_name or not engine_version:
            raise ValueError(
                "OpenSearch domain config must include id, name, and engine_version."
            )
        if not isinstance(subnet_ids, list) or not subnet_ids:
            raise ValueError("subnet_ids must be a non-empty list.")
        if not isinstance(security_group_ids, list) or not security_group_ids:
            raise ValueError("security_group_ids must be a non-empty list.")

    def _create_alarms(
        self,
        domain_name,
        alarms_cfg,
        construct_id,
    ):
        alarms_enabled = alarms_cfg.get("enabled", True)
        if not alarms_enabled:
            return
        cpu_threshold = alarms_cfg.get("cpu_utilization", {}).get("threshold", 80)
        self.cluster_status_red_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}OpenSearchClusterStatusRedAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ES",
                metric_name="ClusterStatus.red",
                dimensions_map={
                    "DomainName": domain_name,
                    "ClientId": self.account,
                },
                period=Duration.minutes(1),
                statistic="Minimum",
            ),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="OpenSearch cluster status is RED",
            alarm_name=f"{construct_id}-opensearch-cluster-status-red-alarm",
        )
        CfnOutput(
            self,
            f"{construct_id}OpenSearchClusterStatusRedAlarmArn",
            value=self.cluster_status_red_alarm.alarm_arn,
            export_name=f"{construct_id}-opensearch-cluster-status-red-alarm-arn",
        )
        self.index_writes_blocked_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}OpenSearchClusterIndexWritesBlockedAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ES",
                metric_name="ClusterIndexWritesBlocked",
                dimensions_map={
                    "DomainName": domain_name,
                    "ClientId": self.account,
                },
                period=Duration.minutes(1),
                statistic="Minimum",
            ),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="OpenSearch index writes are blocked",
            alarm_name=f"{construct_id}-opensearch-index-writes-blocked-alarm",
        )
        CfnOutput(
            self,
            f"{construct_id}OpenSearchClusterIndexWritesBlockedAlarmArn",
            value=self.index_writes_blocked_alarm.alarm_arn,
            export_name=f"{construct_id}-opensearch-index-writes-blocked-alarm-arn",
        )
        self.free_storage_space_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}OpenSearchFreeStorageSpaceAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ES",
                metric_name="FreeStorageSpace",
                dimensions_map={
                    "DomainName": domain_name,
                    "ClientId": self.account,
                },
                period=Duration.minutes(1),
                statistic="Minimum",
            ),
            threshold=20480,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            alarm_description="OpenSearch free storage space below 20GB",
            alarm_name=f"{construct_id}-opensearch-free-storage-alarm",
        )
        CfnOutput(
            self,
            f"{construct_id}OpenSearchFreeStorageSpaceAlarmArn",
            value=self.free_storage_space_alarm.alarm_arn,
            export_name=f"{construct_id}-opensearch-free-storage-alarm-arn",
        )
        self.cpu_utilization_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}OpenSearchCPUUtilizationAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ES",
                metric_name="CPUUtilization",
                dimensions_map={
                    "DomainName": domain_name,
                    "ClientId": self.account,
                },
                period=Duration.minutes(1),
                statistic="Average",
            ),
            threshold=cpu_threshold,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="OpenSearch CPU utilization above threshold",
            alarm_name=f"{construct_id}-opensearch-cpu-alarm",
        )
        CfnOutput(
            self,
            f"{construct_id}OpenSearchCPUUtilizationAlarmArn",
            value=self.cpu_utilization_alarm.alarm_arn,
            export_name=f"{construct_id}-opensearch-cpu-alarm-arn",
        )
