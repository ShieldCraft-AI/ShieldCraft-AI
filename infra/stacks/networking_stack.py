
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class NetworkingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict = None, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        config = config or {}
        net_cfg = config.get('networking', {})
        env = config.get('app', {}).get('env', 'dev')

        # Tagging for traceability and custom tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in net_cfg.get('tags', {}).items():
            self.tags.set_tag(k, v)

        from aws_cdk import CfnOutput

        vpc_cidr = net_cfg.get('vpc_cidr', '10.0.0.0/16')
        subnets_cfg = net_cfg.get('subnets', [
            {"cidr": "10.0.1.0/24", "type": "PUBLIC"},
            {"cidr": "10.0.2.0/24", "type": "PRIVATE"}
        ])
        if not isinstance(subnets_cfg, list) or not subnets_cfg:
            raise ValueError("subnets must be a non-empty list.")

        subnet_types = {"PUBLIC": ec2.SubnetType.PUBLIC, "PRIVATE": ec2.SubnetType.PRIVATE_WITH_EGRESS}
        subnet_config = []
        for i, s in enumerate(subnets_cfg):
            cidr = s.get('cidr')
            stype = s.get('type')
            if not cidr or not stype:
                raise ValueError(f"Each subnet must have 'cidr' and 'type'. Got: {s}")
            if stype not in subnet_types:
                raise ValueError(f"Invalid subnet type: {stype}. Must be one of {list(subnet_types.keys())}")
            subnet_config.append(ec2.SubnetConfiguration(
                name=f"{stype}{i+1}",
                subnet_type=subnet_types[stype],
                cidr_mask=int(cidr.split('/')[-1])
            ))

        max_azs = net_cfg.get('max_azs', 1)
        self.vpc = ec2.Vpc(
            self, f"{construct_id}Vpc",
            cidr=vpc_cidr,
            max_azs=max_azs,
            nat_gateways=1,
            subnet_configuration=subnet_config
        )
        CfnOutput(self, f"{construct_id}VpcId", value=self.vpc.vpc_id, export_name=f"{construct_id}-vpc-id")
        for idx, subnet in enumerate(self.vpc.public_subnets + self.vpc.private_subnets):
            CfnOutput(self, f"{construct_id}Subnet{idx+1}Id", value=subnet.subnet_id, export_name=f"{construct_id}-subnet-{idx+1}-id")
