
from aws_cdk import (
    Stack,
    aws_opensearchservice as opensearch,
    aws_ec2 as ec2,
)
from constructs import Construct

class OpenSearchStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, config: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        opensearch_cfg = config.get('opensearch', {})
        env = config.get('app', {}).get('env', 'dev')

        # Tagging for traceability and custom tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in opensearch_cfg.get('tags', {}).items():
            self.tags.set_tag(k, v)

        from aws_cdk import RemovalPolicy, CfnOutput

        # --- Security Group ---
        sg_cfg = opensearch_cfg.get('security_group', {})
        sg_id = sg_cfg.get('id', 'OpenSearchSecurityGroup')
        sg_desc = sg_cfg.get('description', 'Security group for OpenSearch')
        allow_all_outbound = sg_cfg.get('allow_all_outbound', True)
        opensearch_sg = ec2.SecurityGroup(
            self, sg_id,
            vpc=vpc,
            description=sg_desc,
            allow_all_outbound=allow_all_outbound
        )
        opensearch_sg.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{construct_id}OpenSearchSecurityGroupId", value=opensearch_sg.security_group_id, export_name=f"{construct_id}-opensearch-sg-id")

        # --- OpenSearch Domain ---
        domain_cfg = opensearch_cfg.get('domain', {})
        domain_id = domain_cfg.get('id')
        domain_name = domain_cfg.get('name')
        engine_version = domain_cfg.get('engine_version')
        subnet_ids = domain_cfg.get('subnet_ids')
        security_group_ids = domain_cfg.get('security_group_ids')
        node_to_node_encryption_options = domain_cfg.get('node_to_node_encryption_options', {"enabled": True})
        encryption_at_rest_options = domain_cfg.get('encryption_at_rest_options', {"enabled": True})
        ebs_options = domain_cfg.get('ebs_options', {"ebsEnabled": True, "volumeSize": 20, "volumeType": "gp3"})
        cluster_config = domain_cfg.get('cluster_config', {"instanceType": "m6g.large.search", "instanceCount": 2})
        advanced_security_options = domain_cfg.get('advanced_security_options', {"enabled": True, "internalUserDatabaseEnabled": True})
        access_policies = domain_cfg.get('access_policies')

        # Validation
        if not domain_id or not domain_name or not engine_version:
            raise ValueError("OpenSearch domain config must include id, name, and engine_version.")
        if subnet_ids is None:
            subnet_ids = [subnet.subnet_id for subnet in vpc.private_subnets]
        if not isinstance(subnet_ids, list) or not subnet_ids:
            raise ValueError("subnet_ids must be a non-empty list.")
        if security_group_ids is None:
            security_group_ids = [opensearch_sg.security_group_id]
        if not isinstance(security_group_ids, list) or not security_group_ids:
            raise ValueError("security_group_ids must be a non-empty list.")

        self.domain = opensearch.CfnDomain(
            self, domain_id,
            domain_name=domain_name,
            engine_version=engine_version,
            vpc_options={
                "subnetIds": subnet_ids,
                "securityGroupIds": security_group_ids
            },
            node_to_node_encryption_options=node_to_node_encryption_options,
            encryption_at_rest_options=encryption_at_rest_options,
            ebs_options=ebs_options,
            cluster_config=cluster_config,
            advanced_security_options=advanced_security_options,
            access_policies=access_policies
        )
        self.domain.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{construct_id}OpenSearchDomainName", value=domain_name, export_name=f"{construct_id}-opensearch-domain-name")
        # Manual ARN construction for OpenSearch domain
        domain_arn = f"arn:aws:es:{self.region}:{self.account}:domain/{domain_name}"
        CfnOutput(self, f"{construct_id}OpenSearchDomainArn", value=domain_arn, export_name=f"{construct_id}-opensearch-domain-arn")

        # --- CloudWatch Alarms for OpenSearch Monitoring ---
        from aws_cdk import aws_cloudwatch as cloudwatch, Duration
        alarm_resources = {}
        alarm_outputs = {}
        # ClusterStatus.red
        cluster_status_red_alarm = cloudwatch.Alarm(
            self, f"{construct_id}OpenSearchClusterStatusRedAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ES",
                metric_name="ClusterStatus.red",
                dimensions_map={"DomainName": domain_name, "ClientId": self.account},
                period=Duration.minutes(1),
                statistic="Minimum"
            ),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="OpenSearch cluster status is RED",
            alarm_name=f"{construct_id}-opensearch-cluster-status-red-alarm"
        )
        CfnOutput(self, f"{construct_id}OpenSearchClusterStatusRedAlarmArn", value=cluster_status_red_alarm.alarm_arn, export_name=f"{construct_id}-opensearch-cluster-status-red-alarm-arn")
        alarm_resources["cluster_status_red_alarm"] = cluster_status_red_alarm
        alarm_outputs["ClusterStatusRed"] = cluster_status_red_alarm.alarm_arn

        # ClusterIndexWritesBlocked
        index_writes_blocked_alarm = cloudwatch.Alarm(
            self, f"{construct_id}OpenSearchClusterIndexWritesBlockedAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ES",
                metric_name="ClusterIndexWritesBlocked",
                dimensions_map={"DomainName": domain_name, "ClientId": self.account},
                period=Duration.minutes(1),
                statistic="Minimum"
            ),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="OpenSearch index writes are blocked",
            alarm_name=f"{construct_id}-opensearch-index-writes-blocked-alarm"
        )
        CfnOutput(self, f"{construct_id}OpenSearchClusterIndexWritesBlockedAlarmArn", value=index_writes_blocked_alarm.alarm_arn, export_name=f"{construct_id}-opensearch-index-writes-blocked-alarm-arn")
        alarm_resources["index_writes_blocked_alarm"] = index_writes_blocked_alarm
        alarm_outputs["ClusterIndexWritesBlocked"] = index_writes_blocked_alarm.alarm_arn

        # FreeStorageSpace
        free_storage_space_alarm = cloudwatch.Alarm(
            self, f"{construct_id}OpenSearchFreeStorageSpaceAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ES",
                metric_name="FreeStorageSpace",
                dimensions_map={"DomainName": domain_name, "ClientId": self.account},
                period=Duration.minutes(1),
                statistic="Minimum"
            ),
            threshold=20480,  # 20GB in MB
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            alarm_description="OpenSearch free storage space below 20GB",
            alarm_name=f"{construct_id}-opensearch-free-storage-alarm"
        )
        CfnOutput(self, f"{construct_id}OpenSearchFreeStorageSpaceAlarmArn", value=free_storage_space_alarm.alarm_arn, export_name=f"{construct_id}-opensearch-free-storage-alarm-arn")
        alarm_resources["free_storage_space_alarm"] = free_storage_space_alarm
        alarm_outputs["FreeStorageSpace"] = free_storage_space_alarm.alarm_arn

        # CPUUtilization
        cpu_utilization_alarm = cloudwatch.Alarm(
            self, f"{construct_id}OpenSearchCPUUtilizationAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ES",
                metric_name="CPUUtilization",
                dimensions_map={"DomainName": domain_name, "ClientId": self.account},
                period=Duration.minutes(1),
                statistic="Average"
            ),
            threshold=80,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="OpenSearch CPU utilization above 80%",
            alarm_name=f"{construct_id}-opensearch-cpu-alarm"
        )
        CfnOutput(self, f"{construct_id}OpenSearchCPUUtilizationAlarmArn", value=cpu_utilization_alarm.alarm_arn, export_name=f"{construct_id}-opensearch-cpu-alarm-arn")
        alarm_resources["cpu_utilization_alarm"] = cpu_utilization_alarm
        alarm_outputs["CPUUtilization"] = cpu_utilization_alarm.alarm_arn

        # Shared resources dict for downstream stacks
        self.shared_resources = {
            "domain": self.domain,
            "security_group": opensearch_sg,
            **alarm_resources
        }
