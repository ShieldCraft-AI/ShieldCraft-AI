"""
ShieldCraftAI MskStack: AWS MSK cluster deployment, monitoring, and cross-stack integration.
"""

from typing import Any, Optional
from aws_cdk import aws_iam as iam  # pylint: disable=unused-import
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_msk as msk
from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from constructs import Construct
from pydantic import ConfigDict, BaseModel, Field, ValidationError


# --- Pydantic config validation ---
class MskClusterConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    """Pydantic model for validating MSK cluster configuration."""

    id: str
    name: str
    kafka_version: str
    number_of_broker_nodes: int
    instance_type: str
    client_subnets: Optional[list[str]] = None
    security_groups: Optional[list[str]] = None
    encryption_info: Optional[dict[str, Any]] = Field(default_factory=dict)
    enhanced_monitoring: Optional[str] = "PER_TOPIC_PER_BROKER"
    broker_storage: Optional[dict[str, Any]] = None
    topics: Optional[list[dict]] = Field(
        default_factory=list, description="List of MSK topics (name required)"
    )


class MskStackConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    """Pydantic model for validating MSK stack configuration."""

    msk: dict = Field(default_factory=dict)
    app: dict = Field(default_factory=dict)


class MskStack(Stack):
    """CDK Stack for deploying and monitoring AWS MSK clusters with robust config
    validation and tagging."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        config: dict,
        msk_client_role_arn: Optional[str] = None,
        msk_producer_role_arn: Optional[str] = None,
        msk_consumer_role_arn: Optional[str] = None,
        shared_tags: Optional[dict] = None,
        secrets_manager_arn: Optional[str] = None,
        enable_secrets_integration: bool = False,
        removal_policy: Optional[str] = None,
        **kwargs,
    ):
        stack_kwargs = {k: kwargs[k] for k in ("env", "description") if k in kwargs}
        super().__init__(scope, construct_id, **stack_kwargs)

        # Vault integration: only if enabled
        self.secrets_manager_arn = secrets_manager_arn
        self.secrets_manager_secret = None
        if enable_secrets_integration and self.secrets_manager_arn:
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
            # Grant read access to MSK roles if present and vault secret is imported
            for role_arn in [
                msk_client_role_arn,
                msk_producer_role_arn,
                msk_consumer_role_arn,
            ]:
                if role_arn:
                    role = iam.Role.from_role_arn(
                        self, f"ImportedMskRole{role_arn[-8:]}", role_arn
                    )
                    self.secrets_manager_secret.grant_read(role)
        try:
            _ = MskStackConfig(**config)
        except ValidationError as e:
            raise ValueError(f"Invalid MSK stack config: {e}") from e
        msk_cfg = config.get("msk", {})
        env = config.get("app", {}).get("env", "dev")
        lf_cfg = config.get("lakeformation", {})
        self._validate_cross_stack_resources(vpc, msk_cfg, lf_cfg)

        tags = {"Project": "ShieldCraftAI", "Environment": env}
        tags.update(msk_cfg.get("tags", {}))
        if shared_tags:
            tags.update(shared_tags)
        for k, v in tags.items():
            self.tags.set_tag(k, v)

        # Determine removal policy
        effective_removal_policy = (
            RemovalPolicy.DESTROY
            if (removal_policy or env) == "dev"
            else RemovalPolicy.RETAIN
        )

        msk_sg = self._create_security_group(msk_cfg, vpc, env, construct_id)
        cluster_cfg = msk_cfg.get("cluster", {})
        cluster = self._create_cluster(
            cluster_cfg, vpc, msk_sg, env, construct_id, effective_removal_policy
        )
        self.cluster = cluster["cluster"]
        cluster_name = cluster["cluster_name"]
        # Export only one cluster ARN output: prefer actual ARN if available
        actual_cluster_arn = getattr(self.cluster, "attr_arn", None)
        cluster_arn = actual_cluster_arn or (
            f"arn:aws:kafka:{self.region}:{self.account}:cluster/{cluster_name}/*"
        )
        CfnOutput(
            self,
            f"{construct_id}MskClusterArn",
            value=cluster_arn,
            export_name=f"{construct_id}-msk-cluster-arn",
        )

        topics_cfg = cluster_cfg.get("topics", [])
        self.topic_arns = {}
        for topic in topics_cfg:
            topic_name = topic.get("name")
            if not topic_name:
                raise ValueError(f"MSK topic missing 'name': {topic}")
            topic_arn = f"arn:aws:kafka:{self.region}:{self.account}:topic/{cluster_name}/{topic_name}"
            self.topic_arns[topic_name] = topic_arn
            self._export_resource(f"MskTopicArn{topic_name}", topic_arn)

        self._create_alarms(
            cluster_name, cluster_cfg.get("number_of_broker_nodes"), construct_id
        )

        # Validate empty lists for client_subnets and security_groups
        if (
            isinstance(cluster_cfg.get("client_subnets"), list)
            and len(cluster_cfg.get("client_subnets")) == 0
        ):
            raise ValueError("MSK cluster config 'client_subnets' cannot be empty.")
        if (
            isinstance(cluster_cfg.get("security_groups"), list)
            and len(cluster_cfg.get("security_groups")) == 0
        ):
            raise ValueError("MSK cluster config 'security_groups' cannot be empty.")

        # Expose only resource objects expected by contract-driven tests
        self.shared_resources = {
            "cluster": self.cluster,
            "security_group": msk_sg,
            "broker_count_alarm": getattr(self, "broker_count_alarm", None),
            "under_replicated_alarm": getattr(self, "under_replicated_alarm", None),
            "active_controller_alarm": getattr(self, "active_controller_alarm", None),
            "disk_used_alarm": getattr(self, "disk_used_alarm", None),
        }

    def _validate_cross_stack_resources(self, vpc, msk_cfg, lf_cfg):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        if vpc is None:
            raise ValueError("MskStack requires a valid VPC reference.")
        if not isinstance(msk_cfg, dict):
            raise ValueError("MskStack requires a valid MSK config dict.")
        cluster_cfg = msk_cfg.get("cluster", {})
        if not cluster_cfg.get("name"):
            raise ValueError("MSK cluster config missing 'name'.")
        if not cluster_cfg.get("id"):
            raise ValueError("MSK cluster config missing 'id'.")
        if not cluster_cfg.get("kafka_version"):
            raise ValueError("MSK cluster config missing 'kafka_version'.")
        if not cluster_cfg.get("number_of_broker_nodes"):
            raise ValueError("MSK cluster config missing 'number_of_broker_nodes'.")
        if not cluster_cfg.get("instance_type"):
            raise ValueError("MSK cluster config missing 'instance_type'.")
        # Validate LakeFormation permissions referencing MSK topics
        if lf_cfg:
            topics_cfg = cluster_cfg.get("topics", [])
            topic_names = {t.get("name") for t in topics_cfg if t.get("name")}
            for perm in lf_cfg.get("permissions", []):
                resource = perm.get("resource")
                if resource and resource.get("type") == "msk_topic":
                    topic_name = resource.get("name")
                    if topic_name not in topic_names:
                        raise ValueError(
                            f"LakeFormation permission references unknown MSK topic: {topic_name}"
                        )

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")

    def _validate_lakeformation_permissions(self, lf_cfg, msk_cfg):
        """Validate LakeFormation permissions referencing MSK resources."""
        if not lf_cfg:
            return
        topics_cfg = msk_cfg.get("topics", [])
        topic_names = {t.get("name") for t in topics_cfg if t.get("name")}
        for perm in lf_cfg.get("permissions", []):
            resource = perm.get("resource")
            if resource and resource.get("type") == "msk_topic":
                topic_name = resource.get("name")
                if topic_name not in topic_names:
                    raise ValueError(
                        f"LakeFormation permission references unknown MSK topic: {topic_name}"
                    )

    def _create_security_group(self, msk_cfg, vpc, env, construct_id):
        sg_cfg = msk_cfg.get("security_group", {})
        sg_id = sg_cfg.get("id", "MskSecurityGroup")
        sg_desc = sg_cfg.get("description", "Security group for MSK brokers")
        allow_all_outbound = sg_cfg.get("allow_all_outbound", True)
        msk_sg = ec2.SecurityGroup(
            self,
            sg_id,
            vpc=vpc,
            description=sg_desc,
            allow_all_outbound=allow_all_outbound,
        )
        # Harden: restrict ingress/egress as needed
        # msk_sg.add_ingress_rule(...)
        msk_sg.apply_removal_policy(
            RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
        )
        CfnOutput(
            self,
            f"{construct_id}MskSecurityGroupId",
            value=msk_sg.security_group_id,
            export_name=f"{construct_id}-msk-sg-id",
        )
        return msk_sg

    def _create_cluster(
        self, cluster_cfg, vpc, msk_sg, env, construct_id, removal_policy
    ):
        try:
            validated = MskClusterConfig(**cluster_cfg)
        except ValidationError as e:
            raise ValueError(f"Invalid MSK cluster config: {e}") from e
        cluster_id = validated.id
        cluster_name = validated.name
        kafka_version = validated.kafka_version
        num_brokers = validated.number_of_broker_nodes
        instance_type = validated.instance_type
        client_subnets = validated.client_subnets or [
            subnet.subnet_id for subnet in vpc.private_subnets
        ]
        security_groups = validated.security_groups or [msk_sg.security_group_id]
        # Validate empty lists
        if isinstance(client_subnets, list) and len(client_subnets) == 0:
            raise ValueError("MSK cluster config 'client_subnets' cannot be empty.")
        if isinstance(security_groups, list) and len(security_groups) == 0:
            raise ValueError("MSK cluster config 'security_groups' cannot be empty.")
        encryption_info = validated.encryption_info or {
            "encryptionInTransit": {"clientBroker": "TLS", "inCluster": True}
        }
        enhanced_monitoring = validated.enhanced_monitoring
        broker_storage = validated.broker_storage
        broker_node_group_info = {
            "instanceType": instance_type,
            "clientSubnets": client_subnets,
            "securityGroups": security_groups,
        }
        if broker_storage:
            broker_node_group_info["storageInfo"] = broker_storage
        cluster = msk.CfnCluster(
            self,
            cluster_id,
            cluster_name=cluster_name,
            kafka_version=kafka_version,
            number_of_broker_nodes=num_brokers,
            broker_node_group_info=broker_node_group_info,
            encryption_info=encryption_info,
            enhanced_monitoring=enhanced_monitoring,
        )
        # Use configurable removal policy
        cluster.apply_removal_policy(removal_policy)
        CfnOutput(
            self,
            f"{construct_id}MskClusterName",
            value=cluster_name,
            export_name=f"{construct_id}-msk-cluster-name",
        )
        return {"cluster": cluster, "cluster_name": cluster_name}

    def _create_alarms(self, cluster_name, num_brokers, construct_id):
        self.broker_count_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}MskBrokerCountAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/Kafka",
                metric_name="BrokerCount",
                dimensions_map={"Cluster Name": cluster_name},
                statistic="Minimum",
                period=Duration.minutes(5),
            ),
            threshold=num_brokers,
            evaluation_periods=1,
            alarm_description="MSK broker count below expected",
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
        )
        self.under_replicated_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}MskUnderReplicatedPartitionsAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/Kafka",
                metric_name="UnderReplicatedPartitions",
                dimensions_map={"Cluster Name": cluster_name},
                statistic="Maximum",
                period=Duration.minutes(5),
            ),
            threshold=0,
            evaluation_periods=1,
            alarm_description="MSK under-replicated partitions detected",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        )
        self.active_controller_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}MskActiveControllerCountAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/Kafka",
                metric_name="ActiveControllerCount",
                dimensions_map={"Cluster Name": cluster_name},
                statistic="Minimum",
                period=Duration.minutes(5),
            ),
            threshold=1,
            evaluation_periods=1,
            alarm_description="MSK active controller count below 1",
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
        )
        self.disk_used_alarm = cloudwatch.Alarm(
            self,
            f"{construct_id}MskDiskUsedAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/Kafka",
                metric_name="KafkaDataLogsDiskUsed",
                dimensions_map={"Cluster Name": cluster_name},
                statistic="Maximum",
                period=Duration.minutes(5),
            ),
            threshold=80,
            evaluation_periods=1,
            alarm_description="MSK broker disk usage above 80%",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        # Outputs for alarms
        CfnOutput(
            self,
            f"{construct_id}MskBrokerCountAlarmArn",
            value=self.broker_count_alarm.alarm_arn,
            export_name=f"{construct_id}-msk-broker-count-alarm-arn",
        )
        CfnOutput(
            self,
            f"{construct_id}MskUnderReplicatedPartitionsAlarmArn",
            value=self.under_replicated_alarm.alarm_arn,
            export_name=f"{construct_id}-msk-under-replicated-alarm-arn",
        )
        CfnOutput(
            self,
            f"{construct_id}MskActiveControllerCountAlarmArn",
            value=self.active_controller_alarm.alarm_arn,
            export_name=f"{construct_id}-msk-active-controller-alarm-arn",
        )
        CfnOutput(
            self,
            f"{construct_id}MskDiskUsedAlarmArn",
            value=self.disk_used_alarm.alarm_arn,
            export_name=f"{construct_id}-msk-disk-used-alarm-arn",
        )
