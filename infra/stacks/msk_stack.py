
from aws_cdk import (
    Stack,
    aws_msk as msk,
    aws_ec2 as ec2,
)
from constructs import Construct

class MskStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, config: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        msk_cfg = config.get('msk', {})
        env = config.get('app', {}).get('env', 'dev')

        # Tagging for traceability and custom tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in msk_cfg.get('tags', {}).items():
            self.tags.set_tag(k, v)

        from aws_cdk import RemovalPolicy, CfnOutput

        # --- Security Group ---
        sg_cfg = msk_cfg.get('security_group', {})
        sg_id = sg_cfg.get('id', 'MskSecurityGroup')
        sg_desc = sg_cfg.get('description', 'Security group for MSK brokers')
        allow_all_outbound = sg_cfg.get('allow_all_outbound', True)
        msk_sg = ec2.SecurityGroup(
            self, sg_id,
            vpc=vpc,
            description=sg_desc,
            allow_all_outbound=allow_all_outbound
        )
        msk_sg.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{construct_id}MskSecurityGroupId", value=msk_sg.security_group_id, export_name=f"{construct_id}-msk-sg-id")

        # --- MSK Cluster ---
        cluster_cfg = msk_cfg.get('cluster', {})
        cluster_id = cluster_cfg.get('id')
        cluster_name = cluster_cfg.get('name')
        kafka_version = cluster_cfg.get('kafka_version')
        num_brokers = cluster_cfg.get('number_of_broker_nodes')
        instance_type = cluster_cfg.get('instance_type')
        client_subnets = cluster_cfg.get('client_subnets')
        security_groups = cluster_cfg.get('security_groups')
        encryption_info = cluster_cfg.get('encryption_info', {
            "encryptionInTransit": {"clientBroker": "TLS", "inCluster": True}
        })
        enhanced_monitoring = cluster_cfg.get('enhanced_monitoring', 'PER_TOPIC_PER_BROKER')

        # Validation
        if not cluster_id or not cluster_name or not kafka_version or num_brokers is None or not instance_type:
            raise ValueError("MSK cluster config must include id, name, kafka_version, number_of_broker_nodes, and instance_type.")
        if not isinstance(num_brokers, int) or num_brokers < 1:
            raise ValueError("number_of_broker_nodes must be a positive integer.")
        if client_subnets is None:
            client_subnets = [subnet.subnet_id for subnet in vpc.private_subnets]
        if not isinstance(client_subnets, list) or not client_subnets:
            raise ValueError("client_subnets must be a non-empty list.")
        if security_groups is None:
            security_groups = [msk_sg.security_group_id]
        if not isinstance(security_groups, list) or not security_groups:
            raise ValueError("security_groups must be a non-empty list.")

        self.cluster = msk.CfnCluster(
            self, cluster_id,
            cluster_name=cluster_name,
            kafka_version=kafka_version,
            number_of_broker_nodes=num_brokers,
            broker_node_group_info={
                "instanceType": instance_type,
                "clientSubnets": client_subnets,
                "securityGroups": security_groups
            },
            encryption_info=encryption_info,
            enhanced_monitoring=enhanced_monitoring
        )
        self.cluster.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
        CfnOutput(self, f"{construct_id}MskClusterName", value=cluster_name, export_name=f"{construct_id}-msk-cluster-name")
        # Manual ARN construction for MSK cluster
        cluster_arn = f"arn:aws:kafka:{self.region}:{self.account}:cluster/{cluster_name}/*"
        CfnOutput(self, f"{construct_id}MskClusterArn", value=cluster_arn, export_name=f"{construct_id}-msk-cluster-arn")
