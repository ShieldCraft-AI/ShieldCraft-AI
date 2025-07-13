"""
ShieldCraftAI IamRoleStack: Centralized IAM role creation for all major services.
"""

from typing import Optional  # pylint: disable=unused-import
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from constructs import Construct  # pylint: disable=unused-import


class IamRoleStack(Stack):
    """
    CDK Stack for all ShieldCraft AI IAM roles (least privilege, cross-service, and
    environment-specific). Creates and outputs ARNs for all major execution roles
    (OpenSearch, MSK, Lambda, SageMaker, Glue, Airbyte, Lake Formation, VPC Flow Logs,
    Data Quality, Compliance).
    """

    def __init__(
        self,
        scope,
        construct_id,
        config=None,
        *args,
        secrets_manager_arn=None,
        **kwargs,
    ):
        """
        Initialize the IAM Role Stack.
        Args:
            scope: CDK construct scope.
            construct_id: Unique stack name.
            config: Project config dict (must include app.env, s3.buckets, msk.cluster, etc.).
            **kwargs: Additional CDK stack args.
        Raises:
            ValueError: If required config keys are missing or malformed.
        """
        super().__init__(scope, construct_id, **kwargs)
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
        # Defensive: config must be a dict
        if not isinstance(config, dict):
            raise ValueError("IamRoleStack requires a valid config dict.")
        env = config.get("app", {}).get("env", "dev")
        # Defensive: ensure region/account are available for ARN construction
        if (
            not hasattr(self, "region")
            or not hasattr(self, "account")
            or self.region is None
            or self.account is None
        ):
            raise ValueError(
                "Stack must have region and account context for ARN construction."
            )

        # Gather S3 bucket names and MSK cluster ARN once
        # --- Validate S3 Buckets for Downstream Stack Integration ---
        buckets_cfg = config.get("s3", {}).get("buckets", [])
        s3_buckets = []
        s3_bucket_ids = set()
        for b in buckets_cfg:
            bucket_id = b.get("id") or b.get("name")
            bucket_name = b.get("name")
            if not bucket_id or not bucket_name:
                raise ValueError(f"Each S3 bucket must have 'id' and 'name'. Got: {b}")
            if bucket_id in s3_bucket_ids:
                raise ValueError(f"Duplicate S3 bucket id in config: {bucket_id}")
            s3_bucket_ids.add(bucket_id)
            s3_buckets.append(bucket_name)
        if not s3_buckets:
            raise ValueError(
                "s3.buckets must be defined and contain at least one bucket with a name."
            )
        cluster_name = config.get("msk", {}).get("cluster", {}).get("name", None)
        if not cluster_name:
            raise ValueError("msk.cluster.name must be defined in config.")
        msk_arn = f"arn:aws:kafka:{self.region}:{self.account}:cluster/{cluster_name}/*"

        # OpenSearch execution role
        opensearch_role = iam.Role(
            self,
            f"{env.capitalize()}OpenSearchExecutionRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-opensearch-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonOpenSearchServiceFullAccess"
                )
            ],
        )
        opensearch_domain_name = (
            config.get("opensearch", {})
            .get("domain", {})
            .get("name", f"shieldcraft-opensearch-{env}")
        )
        opensearch_arn = (
            f"arn:aws:es:{self.region}:{self.account}:domain/{opensearch_domain_name}/*"
        )
        opensearch_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "es:ESHttpGet",
                    "es:ESHttpPut",
                    "es:ESHttpPost",
                    "es:ESHttpDelete",
                    "es:ESHttpHead",
                ],
                resources=[opensearch_arn],
            )
        )
        CfnOutput(
            self,
            f"{env.capitalize()}OpenSearchRoleArn",
            value=opensearch_role.role_arn,
            export_name=f"{construct_id}-opensearch-role-arn",
        )
        # MSK client/producer/consumer roles
        cluster_name = (
            config.get("msk", {})
            .get("cluster", {})
            .get("name", f"shieldcraft-msk-cluster-{env}")
        )
        if not cluster_name:
            raise ValueError("msk.cluster.name must be defined in config.")
        msk_arn = f"arn:aws:kafka:{self.region}:{self.account}:cluster/{cluster_name}/*"

        msk_client_role = iam.Role(
            self,
            f"{env.capitalize()}MskClientRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-msk-client-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonMSKReadOnlyAccess"
                )
            ],
        )
        msk_client_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "kafka:DescribeCluster",
                    "kafka:GetBootstrapBrokers",
                    "kafka:ListTopics",
                    "kafka:DescribeTopic",
                ],
                resources=[msk_arn],
            )
        )
        CfnOutput(
            self,
            f"{env.capitalize()}MskClientRoleArn",
            value=msk_client_role.role_arn,
            export_name=f"{construct_id}-msk-client-role-arn",
        )

        msk_producer_role = iam.Role(
            self,
            f"{env.capitalize()}MskProducerRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-msk-producer-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonMSKFullAccess")
            ],
        )
        msk_producer_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "kafka:DescribeCluster",
                    "kafka:GetBootstrapBrokers",
                    "kafka:CreateTopic",
                    "kafka:ListTopics",
                    "kafka:DescribeTopic",
                    "kafka:WriteData",
                ],
                resources=[msk_arn],
            )
        )
        CfnOutput(
            self,
            f"{env.capitalize()}MskProducerRoleArn",
            value=msk_producer_role.role_arn,
            export_name=f"{construct_id}-msk-producer-role-arn",
        )

        msk_consumer_role = iam.Role(
            self,
            f"{env.capitalize()}MskConsumerRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-msk-consumer-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonMSKReadOnlyAccess"
                )
            ],
        )
        msk_consumer_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "kafka:DescribeCluster",
                    "kafka:GetBootstrapBrokers",
                    "kafka:ListTopics",
                    "kafka:DescribeTopic",
                    "kafka:ReadData",
                ],
                resources=[msk_arn],
            )
        )
        CfnOutput(
            self,
            f"{env.capitalize()}MskConsumerRoleArn",
            value=msk_consumer_role.role_arn,
            export_name=f"{construct_id}-msk-consumer-role-arn",
        )
        # Lambda execution role
        lambda_role = iam.Role(
            self,
            f"{env.capitalize()}LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-lambda-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )
        # Attach least-privilege inline policies as needed
        # Use the same manual ARN construction as in MskStack for the cluster
        cluster_name = (
            config.get("msk", {})
            .get("cluster", {})
            .get("name", f"shieldcraft-msk-cluster-{env}")
        )
        msk_arn = f"arn:aws:kafka:{self.region}:{self.account}:cluster/{cluster_name}/*"
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "kafka:DescribeCluster",
                    "kafka:GetBootstrapBrokers",
                    "kafka:CreateTopic",
                    "kafka:ListTopics",
                    "kafka:DescribeTopic",
                ],
                resources=[msk_arn],
            )
        )

        # Output Lambda role ARN for downstream use
        CfnOutput(
            self,
            f"{env.capitalize()}LambdaRoleArn",
            value=lambda_role.role_arn,
            export_name=f"{construct_id}-lambda-role-arn",
        )

        # SageMaker execution role
        sagemaker_role = iam.Role(
            self,
            f"{env.capitalize()}SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-sagemaker-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSageMakerFullAccess"
                )
            ],
        )
        s3_buckets = [b.get("name") for b in config.get("s3", {}).get("buckets", [])]
        # Defensive: Ensure all buckets referenced in downstream stacks are created and exported
        for bucket_name in s3_buckets:
            sagemaker_role.add_to_policy(
                iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                    resources=[
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*",
                    ],
                )
            )
        # Output SageMaker role ARN for downstream use
        CfnOutput(
            self,
            f"{env.capitalize()}SageMakerRoleArn",
            value=sagemaker_role.role_arn,
            export_name=f"{construct_id}-sagemaker-role-arn",
        )

        # Glue execution role (least privilege)
        glue_role = iam.Role(
            self,
            f"{env.capitalize()}GlueExecutionRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-glue-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )
        # Attach least-privilege inline policies for Glue (S3, Glue, Lake Formation, Logs)
        for bucket_name in s3_buckets:
            glue_role.add_to_policy(
                iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                    resources=[
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*",
                    ],
                )
            )
        glue_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "glue:GetTable",
                    "glue:GetDatabase",
                    "glue:CreateTable",
                    "glue:UpdateTable",
                    "glue:DeleteTable",
                    "glue:GetTableVersion",
                    "glue:GetTableVersions",
                ],
                resources=[
                    f"arn:aws:glue:{self.region}:{self.account}:catalog",
                    f"arn:aws:glue:{self.region}:{self.account}:database/*",
                    f"arn:aws:glue:{self.region}:{self.account}:table/*/*",
                ],
            )
        )
        glue_role.add_to_policy(
            iam.PolicyStatement(
                actions=["lakeformation:GetDataAccess"], resources=["*"]
            )
        )
        glue_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=[
                    f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws-glue/*"
                ],
            )
        )
        # Output Glue role ARN for downstream use (unique export name)
        CfnOutput(
            self,
            f"{env.capitalize()}GlueRoleArn",
            value=glue_role.role_arn,
            export_name=f"{construct_id}-glue-role-arn",
        )

        # Airbyte execution role (for ECS or Lambda deployment)
        airbyte_role = iam.Role(
            self,
            f"{env.capitalize()}AirbyteExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-airbyte-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )
        # Attach least-privilege inline policies for Airbyte (S3, MSK, etc.)
        for bucket_name in s3_buckets:
            airbyte_role.add_to_policy(
                iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                    resources=[
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*",
                    ],
                )
            )
        airbyte_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "kafka:DescribeCluster",
                    "kafka:GetBootstrapBrokers",
                    "kafka:ListTopics",
                    "kafka:DescribeTopic",
                ],
                resources=[msk_arn],
            )
        )
        # Output Airbyte role ARN for downstream use
        CfnOutput(
            self,
            f"{env.capitalize()}AirbyteRoleArn",
            value=airbyte_role.role_arn,
            export_name=f"{construct_id}-airbyte-role-arn",
        )

        # Lake Formation admin role
        lakeformation_admin_role = iam.Role(
            self,
            f"{env.capitalize()}LakeFormationAdminRole",
            assumed_by=iam.ServicePrincipal("lakeformation.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-lakeformation-admin-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLakeFormationDataAdmin"
                )
            ],
        )
        for bucket_name in s3_buckets:
            lakeformation_admin_role.add_to_policy(
                iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                    resources=[
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*",
                    ],
                )
            )
        CfnOutput(
            self,
            f"{env.capitalize()}LakeFormationAdminRoleArn",
            value=lakeformation_admin_role.role_arn,
            export_name=f"{construct_id}-lakeformation-admin-role-arn",
        )

        # VPC Flow Logs delivery role
        vpc_flow_logs_role = iam.Role(
            self,
            f"{env.capitalize()}VpcFlowLogsRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-vpc-flowlogs-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSVPCFlowLogsDeliveryPolicy"
                )
            ],
        )
        CfnOutput(
            self,
            f"{env.capitalize()}VpcFlowLogsRoleArn",
            value=vpc_flow_logs_role.role_arn,
            export_name=f"{construct_id}-vpc-flowlogs-role-arn",
        )

        # Data Quality Lambda execution role
        dq_lambda_role = iam.Role(
            self,
            f"{env.capitalize()}DataQualityLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-dq-lambda-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )
        CfnOutput(
            self,
            f"{env.capitalize()}DataQualityLambdaRoleArn",
            value=dq_lambda_role.role_arn,
            export_name=f"{construct_id}-dq-lambda-role-arn",
        )

        # Data Quality Glue job execution role
        dq_glue_role = iam.Role(
            self,
            f"{env.capitalize()}DataQualityGlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-dq-glue-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )
        CfnOutput(
            self,
            f"{env.capitalize()}DataQualityGlueRoleArn",
            value=dq_glue_role.role_arn,
            export_name=f"{construct_id}-dq-glue-role-arn",
        )

        # Compliance Lambda execution role (for custom Config rules, if needed)
        compliance_lambda_role = iam.Role(
            self,
            f"{env.capitalize()}ComplianceLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),  # type: ignore[arg-type]
            role_name=f"shieldcraftai-compliance-lambda-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Grant read access to all major IAM roles if vault secret is imported
        if self.secrets_manager_secret:
            for role in [
                opensearch_role,
                msk_client_role,
                msk_producer_role,
                msk_consumer_role,
                lambda_role,
                sagemaker_role,
                glue_role,
                airbyte_role,
                lakeformation_admin_role,
                vpc_flow_logs_role,
                dq_lambda_role,
                dq_glue_role,
                compliance_lambda_role,
            ]:
                self.secrets_manager_secret.grant_read(role)
        CfnOutput(
            self,
            f"{env.capitalize()}ComplianceLambdaRoleArn",
            value=compliance_lambda_role.role_arn,
            export_name=f"{construct_id}-compliance-lambda-role-arn",
        )

    def _validate_cross_stack_resources(self, config):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        if not isinstance(config, dict):
            raise ValueError("IamRoleStack requires a valid config dict.")
        buckets_cfg = config.get("s3", {}).get("buckets", [])
        if not isinstance(buckets_cfg, list) or not buckets_cfg:
            raise ValueError(
                "s3.buckets must be defined and contain at least one bucket."
            )
        bucket_ids = set()
        for b in buckets_cfg:
            bucket_id = b.get("id") or b.get("name")
            bucket_name = b.get("name")
            if not bucket_id or not bucket_name:
                raise ValueError(f"Each S3 bucket must have 'id' and 'name'. Got: {b}")
            if bucket_id in bucket_ids:
                raise ValueError(f"Duplicate S3 bucket id in config: {bucket_id}")
            bucket_ids.add(bucket_id)
        cluster_name = config.get("msk", {}).get("cluster", {}).get("name", None)
        if not cluster_name:
            raise ValueError("msk.cluster.name must be defined in config.")

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")
