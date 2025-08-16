"""
NetworkingStack: ShieldCraft AI foundational networking resources.
Implements VPC, subnets, security groups, flow logs, and vault integration.
"""

# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
import re
from typing import Dict, Optional
from aws_cdk import RemovalPolicy, Stack, Token
from aws_cdk import aws_ec2 as ec2
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import CfnOutput, Duration  # pylint: disable=unused-import
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_iam as iam
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk.aws_ec2 import CfnNatGateway  # pylint: disable=unused-import
from constructs import Construct


class NetworkingStack(Stack):
    """
    NetworkingStack for ShieldCraft AI: VPC, subnets, security groups, flow logs and NAT monitoring
    """

    def validate_lakeformation_permissions(
        self,
        permissions,
        exported_vpc_id,
        exported_subnet_ids,
        exported_sg_id,
        exported_flow_logs_bucket_arn,
    ):
        """
        Validate LakeFormation permissions referencing networking resources (VPC, subnets, SG,
        flow logs bucket).
        Raises ValueError on any misconfiguration or reference to non-exported resources.
        """
        for perm_cfg in permissions:
            resource_type = perm_cfg.get("resource_type")
            resource = perm_cfg.get("resource")
            # VPC validation
            if resource_type == "vpc":
                vpc_id = (
                    resource.get("vpcId")
                    or resource.get("vpc_id")
                    or resource.get("id")
                )
                if not vpc_id:
                    raise ValueError(
                        f"LakeFormation permission for VPC must include vpcId. Got: {resource}"
                    )
                if vpc_id != exported_vpc_id:
                    raise ValueError(
                        f"LakeFormation permission references unknown VPC: {vpc_id}"
                    )
            # Subnet validation
            if resource_type == "subnet":
                subnet_id = (
                    resource.get("subnetId")
                    or resource.get("subnet_id")
                    or resource.get("id")
                )
                if not subnet_id:
                    raise ValueError(
                        f"LakeFormation permission for subnet must include subnetId. {resource}"
                    )
                if subnet_id not in exported_subnet_ids:
                    raise ValueError(
                        f"LakeFormation permission references unknown subnet: {subnet_id}"
                    )
            # Security Group validation
            if resource_type == "security_group":
                sg_id = (
                    resource.get("securityGroupId")
                    or resource.get("security_group_id")
                    or resource.get("id")
                )
                if not sg_id:
                    raise ValueError(
                        f"LakeFormation permission security group include securityGroupId{resource}"
                    )
                if sg_id != exported_sg_id:
                    raise ValueError(
                        f"LakeFormation permission references unknown security group: {sg_id}"
                    )
            # Flow logs bucket validation
            if resource_type == "flow_logs_bucket":
                bucket_arn = (
                    resource.get("bucketArn")
                    or resource.get("bucket_arn")
                    or resource.get("arn")
                )
                if not bucket_arn:
                    raise ValueError(
                        f"LakeFormation permission bucket must include bucketArn. Got: {resource}"
                    )
                if bucket_arn != exported_flow_logs_bucket_arn:
                    raise ValueError(
                        f"LakeFormation permission references unknown bucket: {bucket_arn}"
                    )

    def __init__(
        self,
        scope,
        construct_id,
        config=None,
        shared_tags=None,
        flow_logs_bucket=None,
        vpc_flow_logs_role_arn=None,
        secrets_manager_arn=None,
        eventbridge_bus_arn=None,
        stepfunctions_state_machine_arn=None,
        **kwargs,
    ):
        if config is None:
            config = {}
        super().__init__(scope, construct_id, **kwargs)
        # Accept config as the full config dict, not just networking
        net_cfg = config.get("networking", {}) if isinstance(config, dict) else {}
        env = (
            config.get("app", {}).get("env", "dev")
            if isinstance(config, dict)
            else "dev"
        )
        # Store EventBridge and Step Functions ARNs for downstream use
        self.eventbridge_bus_arn = eventbridge_bus_arn
        self.stepfunctions_state_machine_arn = stepfunctions_state_machine_arn
        # Centralized tagging
        tags_to_apply = {"Project": "ShieldCraftAI", "Environment": env}
        tags_to_apply.update(net_cfg.get("tags", {}))
        if shared_tags:
            tags_to_apply.update(shared_tags)
        for k, v in tags_to_apply.items():
            self.tags.set_tag(k, v)

        # Vault integration: import the main secrets manager secret if provided
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

        # Validation and config
        vpc_cidr = net_cfg.get("vpc_cidr", "10.0.0.0/16")
        if not Token.is_unresolved(vpc_cidr):
            if not isinstance(vpc_cidr, str) or not re.match(
                r"^\d+\.\d+\.\d+\.\d+/\d+$", vpc_cidr
            ):
                raise ValueError(f"Invalid VPC CIDR: {vpc_cidr}")
        subnets_cfg = net_cfg.get(
            "subnets",
            [
                {"cidr": "10.0.1.0/24", "type": "PUBLIC"},
                {"cidr": "10.0.2.0/24", "type": "PRIVATE"},
            ],
        )
        if not isinstance(subnets_cfg, list) or not subnets_cfg:
            raise ValueError("subnets must be a non-empty list.")
        subnet_types = {
            "PUBLIC": ec2.SubnetType.PUBLIC,
            "PRIVATE": ec2.SubnetType.PRIVATE_WITH_EGRESS,
            "ISOLATED": ec2.SubnetType.PRIVATE_ISOLATED,
        }
        subnet_config = []
        for i, s in enumerate(subnets_cfg):
            cidr = s.get("cidr")
            stype = s.get("type")
            if not cidr or not stype:
                raise ValueError(f"Each subnet must have 'cidr' and 'type'. Got: {s}")
            if stype not in subnet_types:
                raise ValueError(
                    f"Invalid subnet type: {stype}. Must be one of {list(subnet_types.keys())}"
                )
            if not Token.is_unresolved(cidr):
                if not isinstance(cidr, str) or not re.match(
                    r"^\d+\.\d+\.\d+\.\d+/\d+$", cidr
                ):
                    raise ValueError(f"Invalid subnet CIDR: {cidr}")
            subnet_config.append(
                ec2.SubnetConfiguration(
                    name=f"{env}-{stype.lower()}-{i+1}",
                    subnet_type=subnet_types[stype],
                    cidr_mask=int(cidr.split("/")[-1]),
                )
            )
        max_azs = net_cfg.get("max_azs", 2)
        nat_gateways = net_cfg.get("nat_gateways", max_azs)
        if not isinstance(max_azs, int) or max_azs < 1:
            raise ValueError("max_azs must be a positive integer.")
        if not isinstance(nat_gateways, int) or nat_gateways < 0:
            raise ValueError("nat_gateways must be a non-negative integer.")
        removal_policy = net_cfg.get("removal_policy", None)
        if isinstance(removal_policy, str):
            removal_policy = getattr(RemovalPolicy, removal_policy.upper(), None)
        if removal_policy is None:
            removal_policy = (
                RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
            )

        # VPC
        self.vpc = ec2.Vpc(
            self,
            f"{construct_id}Vpc",
            cidr=vpc_cidr,
            max_azs=max_azs,
            nat_gateways=nat_gateways,
            subnet_configuration=subnet_config,
        )

        # Dedicated SGs for major services (least-privilege, empty by default)
        self.sg_msk = ec2.SecurityGroup(
            self,
            f"{construct_id}MskSG",
            vpc=self.vpc,
            description="MSK SG",
            allow_all_outbound=False,
        )
        self.sg_opensearch = ec2.SecurityGroup(
            self,
            f"{construct_id}OpenSearchSG",
            vpc=self.vpc,
            description="OpenSearch SG",
            allow_all_outbound=False,
        )
        self.sg_lambda = ec2.SecurityGroup(
            self,
            f"{construct_id}LambdaSG",
            vpc=self.vpc,
            description="Lambda SG",
            allow_all_outbound=False,
        )
        self.sg_sagemaker = ec2.SecurityGroup(
            self,
            f"{construct_id}SageMakerSG",
            vpc=self.vpc,
            description="SageMaker SG",
            allow_all_outbound=False,
        )
        self.sg_glue = ec2.SecurityGroup(
            self,
            f"{construct_id}GlueSG",
            vpc=self.vpc,
            description="Glue SG",
            allow_all_outbound=False,
        )
        self.sg_airbyte = ec2.SecurityGroup(
            self,
            f"{construct_id}AirbyteSG",
            vpc=self.vpc,
            description="Airbyte SG",
            allow_all_outbound=False,
        )
        self.sg_lakeformation = ec2.SecurityGroup(
            self,
            f"{construct_id}LakeFormationSG",
            vpc=self.vpc,
            description="Lake Formation SG",
            allow_all_outbound=False,
        )

        # Default Security Group (restrict outbound by default, allow override)
        self.default_sg = ec2.SecurityGroup(
            self,
            f"{construct_id}DefaultSG",
            vpc=self.vpc,
            description="Default security group for ShieldCraftAI shared resources",
            allow_all_outbound=net_cfg.get("allow_all_outbound", False),
        )
        self.default_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc_cidr),
            connection=ec2.Port.all_traffic(),
            description="Allow all traffic within VPC CIDR",
        )

        # VPC Endpoints (S3, Secrets Manager, others as needed)
        self.vpc_endpoints = {}
        self.vpc_endpoints["s3"] = self.vpc.add_gateway_endpoint(
            "S3Endpoint", service=ec2.GatewayVpcEndpointAwsService.S3
        )
        self.vpc_endpoints["secretsmanager"] = self.vpc.add_interface_endpoint(
            "SecretsManagerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
        )
        # Add more endpoints as needed (e.g., DynamoDB, KMS, SQS, SNS)

        # VPC Flow Logs (to provided or new S3 bucket)
        if flow_logs_bucket is None:
            # Create a new S3 bucket for flow logs if not provided
            self.flow_logs_bucket = s3.Bucket(
                self,
                f"{construct_id}FlowLogsBucket",
                removal_policy=removal_policy,
                encryption=s3.BucketEncryption.S3_MANAGED,
                lifecycle_rules=[
                    s3.LifecycleRule(enabled=True, expiration=Duration.days(90))
                ],
            )
        else:
            self.flow_logs_bucket = flow_logs_bucket
        # Restrict S3 bucket policy to allow only the VPC Flow Logs role to write logs
        if vpc_flow_logs_role_arn:
            flow_logs_role = iam.Role.from_role_arn(
                self, f"{construct_id}FlowLogsRole", vpc_flow_logs_role_arn
            )
        else:
            flow_logs_role = None
        self.flow_log = ec2.FlowLog(
            self,
            f"{construct_id}VpcFlowLog",
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            destination=ec2.FlowLogDestination.to_s3(self.flow_logs_bucket),
            traffic_type=ec2.FlowLogTrafficType.ALL,
        )
        if flow_logs_role:
            self.flow_logs_bucket.grant_write(flow_logs_role)

        self.nat_alarms = []
        if nat_gateways > 0:
            for idx, ngw in enumerate(self.vpc.node.find_all()):
                if isinstance(ngw, CfnNatGateway):
                    alarm = cloudwatch.Alarm(
                        self,
                        f"{construct_id}NatGw{idx+1}Alarm",
                        metric=cloudwatch.Metric(
                            namespace="AWS/NATGateway",
                            metric_name="ErrorPortAllocation",
                            dimensions_map={"NatGatewayId": ngw.ref},
                            statistic="Sum",
                            period=Duration.minutes(5),
                        ),
                        threshold=1,
                        evaluation_periods=1,
                        alarm_description="NAT Gateway port allocation errors detected",
                        comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                    )
                    self.nat_alarms.append(alarm)

        # Outputs for cross-stack reference
        CfnOutput(
            self,
            f"{construct_id}VpcId",
            value=self.vpc.vpc_id,
            export_name=f"{construct_id}-vpc-id",
        )
        # Output all subnet IDs (public and private) for downstream use
        all_subnets = self.vpc.public_subnets + self.vpc.private_subnets
        for idx, subnet in enumerate(all_subnets):
            CfnOutput(
                self,
                f"{construct_id}Subnet{idx+1}Id",
                value=subnet.subnet_id,
                export_name=(f"{construct_id}-subnet{idx+1}-id"),
            )
        # Output default SG (for Lambda)
        CfnOutput(
            self,
            f"{construct_id}DefaultSGId",
            value=self.default_sg.security_group_id,
            export_name=f"{construct_id}-default-sg-id",
        )
        # Output flow logs bucket
        CfnOutput(
            self,
            f"{construct_id}FlowLogsBucketArn",
            value=self.flow_logs_bucket.bucket_arn,
            export_name=(f"{construct_id}-flowlogs-bucket-arn"),
        )
        # Output VPC endpoint IDs
        for ep_name, ep in self.vpc_endpoints.items():
            CfnOutput(
                self,
                f"{construct_id}{ep_name.capitalize()}EndpointId",
                value=(
                    ep.vpc_endpoint_id
                    if hasattr(ep, "vpc_endpoint_id")
                    else ep.gateway_endpoint_id
                ),
                export_name=f"{construct_id}-{ep_name}-endpoint-id",
            )
        # Output dedicated SGs
        CfnOutput(
            self,
            f"{construct_id}MskSGId",
            value=self.sg_msk.security_group_id,
            export_name=f"{construct_id}-msk-sg-id",
        )
        CfnOutput(
            self,
            f"{construct_id}OpenSearchSGId",
            value=self.sg_opensearch.security_group_id,
            export_name=f"{construct_id}-opensearch-sg-id",
        )
        CfnOutput(
            self,
            f"{construct_id}LambdaSGId",
            value=self.sg_lambda.security_group_id,
            export_name=f"{construct_id}-lambda-sg-id",
        )
        CfnOutput(
            self,
            f"{construct_id}SageMakerSGId",
            value=self.sg_sagemaker.security_group_id,
            export_name=f"{construct_id}-sagemaker-sg-id",
        )
        CfnOutput(
            self,
            f"{construct_id}GlueSGId",
            value=self.sg_glue.security_group_id,
            export_name=f"{construct_id}-glue-sg-id",
        )
        CfnOutput(
            self,
            f"{construct_id}AirbyteSGId",
            value=self.sg_airbyte.security_group_id,
            export_name=f"{construct_id}-airbyte-sg-id",
        )
        CfnOutput(
            self,
            f"{construct_id}LakeFormationSGId",
            value=self.sg_lakeformation.security_group_id,
            export_name=f"{construct_id}-lakeformation-sg-id",
        )

        # Expose for downstream stacks
        self.shared_resources = {
            "vpc": self.vpc,
            "default_sg": self.default_sg,
            "flow_logs_bucket": self.flow_logs_bucket,
            "private_subnets": self.vpc.private_subnets,
            "nat_alarms": self.nat_alarms,
            "subnets": all_subnets,
            "vault_secret": self.secrets_manager_secret,
            "vpc_endpoints": self.vpc_endpoints,
            "sg_msk": self.sg_msk,
            "sg_opensearch": self.sg_opensearch,
            "sg_lambda": self.sg_lambda,
            "sg_sagemaker": self.sg_sagemaker,
            "sg_glue": self.sg_glue,
            "sg_airbyte": self.sg_airbyte,
            "sg_lakeformation": self.sg_lakeformation,
        }
