from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct

class NetworkingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict = None, shared_tags: dict = None, flow_logs_bucket=None, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        config = config or {}
        net_cfg = config.get('networking', {})
        env = config.get('app', {}).get('env', 'dev')
        # Tagging
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in net_cfg.get('tags', {}).items():
            self.tags.set_tag(k, v)
        if shared_tags:
            for k, v in shared_tags.items():
                self.tags.set_tag(k, v)

        # Validation and config
        vpc_cidr = net_cfg.get('vpc_cidr', '10.0.0.0/16')
        import re
        from aws_cdk import Token, RemovalPolicy
        if not Token.is_unresolved(vpc_cidr):
            if not isinstance(vpc_cidr, str) or not re.match(r"^\d+\.\d+\.\d+\.\d+/\d+$", vpc_cidr):
                raise ValueError(f"Invalid VPC CIDR: {vpc_cidr}")
        subnets_cfg = net_cfg.get('subnets', [
            {"cidr": "10.0.1.0/24", "type": "PUBLIC"},
            {"cidr": "10.0.2.0/24", "type": "PRIVATE"}
        ])
        if not isinstance(subnets_cfg, list) or not subnets_cfg:
            raise ValueError("subnets must be a non-empty list.")
        subnet_types = {
            "PUBLIC": ec2.SubnetType.PUBLIC,
            "PRIVATE": ec2.SubnetType.PRIVATE_WITH_EGRESS,
            "ISOLATED": ec2.SubnetType.PRIVATE_ISOLATED
        }
        subnet_config = []
        for i, s in enumerate(subnets_cfg):
            cidr = s.get('cidr')
            stype = s.get('type')
            if not cidr or not stype:
                raise ValueError(f"Each subnet must have 'cidr' and 'type'. Got: {s}")
            if stype not in subnet_types:
                raise ValueError(f"Invalid subnet type: {stype}. Must be one of {list(subnet_types.keys())}")
            if not Token.is_unresolved(cidr):
                if not isinstance(cidr, str) or not re.match(r"^\d+\.\d+\.\d+\.\d+/\d+$", cidr):
                    raise ValueError(f"Invalid subnet CIDR: {cidr}")
            subnet_config.append(ec2.SubnetConfiguration(
                name=f"{env}-{stype.lower()}-{i+1}",
                subnet_type=subnet_types[stype],
                cidr_mask=int(cidr.split('/')[-1])
            ))
        max_azs = net_cfg.get('max_azs', 2)
        nat_gateways = net_cfg.get('nat_gateways', max_azs)
        if not isinstance(max_azs, int) or max_azs < 1:
            raise ValueError("max_azs must be a positive integer.")
        if not isinstance(nat_gateways, int) or nat_gateways < 0:
            raise ValueError("nat_gateways must be a non-negative integer.")
        removal_policy = net_cfg.get('removal_policy', None)
        if isinstance(removal_policy, str):
            removal_policy = getattr(RemovalPolicy, removal_policy.upper(), None)
        if removal_policy is None:
            removal_policy = RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN

        # VPC
        self.vpc = ec2.Vpc(
            self, f"{construct_id}Vpc",
            cidr=vpc_cidr,
            max_azs=max_azs,
            nat_gateways=nat_gateways,
            subnet_configuration=subnet_config
        )
        # Default Security Group (restrict outbound by default, allow override)
        self.default_sg = ec2.SecurityGroup(
            self, f"{construct_id}DefaultSG",
            vpc=self.vpc,
            description="Default security group for ShieldCraftAI shared resources",
            allow_all_outbound=net_cfg.get('allow_all_outbound', False)
        )
        self.default_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc_cidr),
            connection=ec2.Port.all_traffic(),
            description="Allow all traffic within VPC CIDR"
        )
        # VPC Flow Logs (to provided or new S3 bucket)
        from aws_cdk import aws_logs as logs, aws_s3 as s3
        if flow_logs_bucket is None:
            flow_logs_bucket = s3.Bucket(
                self, f"{construct_id}FlowLogsBucket",
                removal_policy=removal_policy,
                encryption=s3.BucketEncryption.S3_MANAGED,
                enforce_ssl=True
            )
        self.flow_logs_bucket = flow_logs_bucket
        self.flow_log = ec2.FlowLog(
            self, f"{construct_id}VpcFlowLog",
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            destination=ec2.FlowLogDestination.to_s3(flow_logs_bucket),
            traffic_type=ec2.FlowLogTrafficType.ALL
        )
        # Monitoring: CloudWatch alarms for NAT gateway metrics (if any NAT gateways)
        from aws_cdk import aws_cloudwatch as cloudwatch, Duration
        self.nat_alarms = []
        if nat_gateways > 0:
            for idx, ngw in enumerate(self.vpc.node.find_all()):
                if hasattr(ngw, 'ref') and 'NatGateway' in str(type(ngw)):
                    alarm = cloudwatch.Alarm(
                        self, f"{construct_id}NatGw{idx+1}Alarm",
                        metric=cloudwatch.Metric(
                            namespace="AWS/NATGateway",
                            metric_name="ErrorPortAllocation",
                            dimensions_map={"NatGatewayId": ngw.ref},
                            statistic="Sum",
                            period=Duration.minutes(5)
                        ),
                        threshold=1,
                        evaluation_periods=1,
                        alarm_description="NAT Gateway port allocation errors detected",
                        comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
                    )
                    self.nat_alarms.append(alarm)
        # Outputs for cross-stack reference
        CfnOutput(self, f"{construct_id}VpcId", value=self.vpc.vpc_id, export_name=f"{construct_id}-vpc-id")
        for idx, subnet in enumerate(self.vpc.public_subnets + self.vpc.private_subnets + self.vpc.isolated_subnets):
            CfnOutput(self, f"{construct_id}Subnet{idx+1}Id", value=subnet.subnet_id, export_name=f"{construct_id}-subnet-{idx+1}-id")
        CfnOutput(self, f"{construct_id}DefaultSGId", value=self.default_sg.security_group_id, export_name=f"{construct_id}-default-sg-id")
        CfnOutput(self, f"{construct_id}FlowLogsBucketArn", value=self.flow_logs_bucket.bucket_arn, export_name=f"{construct_id}-flowlogs-bucket-arn")
        # Expose for downstream stacks
        self.shared_resources = {
            "vpc": self.vpc,
            "default_sg": self.default_sg,
            "flow_logs_bucket": self.flow_logs_bucket,
            "subnets": self.vpc.public_subnets + self.vpc.private_subnets + self.vpc.isolated_subnets,
            "nat_alarms": self.nat_alarms
        }
