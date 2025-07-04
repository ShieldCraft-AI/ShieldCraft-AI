from aws_cdk import (
    Stack,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct

class IamRoleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict = None, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        config = config or {}
        env = config.get("app", {}).get("env", "dev")

        # OpenSearch execution role
        opensearch_role = iam.Role(
            self, f"{env.capitalize()}OpenSearchExecutionRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name=f"shieldcraftai-opensearch-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonOpenSearchServiceFullAccess")
            ]
        )
        opensearch_domain_name = config.get("opensearch", {}).get("domain", {}).get("name", f"shieldcraft-opensearch-{env}")
        opensearch_arn = f"arn:aws:es:{self.region}:{self.account}:domain/{opensearch_domain_name}/*"
        opensearch_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "es:ESHttpGet",
                "es:ESHttpPut",
                "es:ESHttpPost",
                "es:ESHttpDelete",
                "es:ESHttpHead"
            ],
            resources=[opensearch_arn]
        ))
        CfnOutput(self, f"{env.capitalize()}OpenSearchRoleArn", value=opensearch_role.role_arn, export_name=f"{construct_id}-opensearch-role-arn")
        # MSK client/producer/consumer roles
        cluster_name = config.get("msk", {}).get("cluster", {}).get("name", f"shieldcraft-msk-cluster-{env}")
        msk_arn = f"arn:aws:kafka:{self.region}:{self.account}:cluster/{cluster_name}/*"

        msk_client_role = iam.Role(
            self, f"{env.capitalize()}MskClientRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name=f"shieldcraftai-msk-client-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonMSKReadOnlyAccess")
            ]
        )
        msk_client_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "kafka:DescribeCluster",
                "kafka:GetBootstrapBrokers",
                "kafka:ListTopics",
                "kafka:DescribeTopic"
            ],
            resources=[msk_arn]
        ))
        CfnOutput(self, f"{env.capitalize()}MskClientRoleArn", value=msk_client_role.role_arn, export_name=f"{construct_id}-msk-client-role-arn")

        msk_producer_role = iam.Role(
            self, f"{env.capitalize()}MskProducerRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name=f"shieldcraftai-msk-producer-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonMSKFullAccess")
            ]
        )
        msk_producer_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "kafka:DescribeCluster",
                "kafka:GetBootstrapBrokers",
                "kafka:CreateTopic",
                "kafka:ListTopics",
                "kafka:DescribeTopic",
                "kafka:WriteData"
            ],
            resources=[msk_arn]
        ))
        CfnOutput(self, f"{env.capitalize()}MskProducerRoleArn", value=msk_producer_role.role_arn, export_name=f"{construct_id}-msk-producer-role-arn")

        msk_consumer_role = iam.Role(
            self, f"{env.capitalize()}MskConsumerRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name=f"shieldcraftai-msk-consumer-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonMSKReadOnlyAccess")
            ]
        )
        msk_consumer_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "kafka:DescribeCluster",
                "kafka:GetBootstrapBrokers",
                "kafka:ListTopics",
                "kafka:DescribeTopic",
                "kafka:ReadData"
            ],
            resources=[msk_arn]
        ))
        CfnOutput(self, f"{env.capitalize()}MskConsumerRoleArn", value=msk_consumer_role.role_arn, export_name=f"{construct_id}-msk-consumer-role-arn")
        # Lambda execution role
        lambda_role = iam.Role(
            self, f"{env.capitalize()}LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"shieldcraftai-lambda-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        # Attach least-privilege inline policies as needed
        # Use the same manual ARN construction as in MskStack for the cluster
        cluster_name = config.get("msk", {}).get("cluster", {}).get("name", f"shieldcraft-msk-cluster-{env}")
        msk_arn = f"arn:aws:kafka:{self.region}:{self.account}:cluster/{cluster_name}/*"
        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "kafka:DescribeCluster",
                "kafka:GetBootstrapBrokers",
                "kafka:CreateTopic",
                "kafka:ListTopics",
                "kafka:DescribeTopic"
            ],
            resources=[msk_arn]
        ))

        # Output Lambda role ARN for downstream use
        CfnOutput(self, f"{env.capitalize()}LambdaRoleArn", value=lambda_role.role_arn, export_name=f"{construct_id}-lambda-role-arn")

        # SageMaker execution role
        sagemaker_role = iam.Role(
            self, f"{env.capitalize()}SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            role_name=f"shieldcraftai-sagemaker-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )
        s3_buckets = [b.get("name") for b in config.get("s3", {}).get("buckets", [])]
        for bucket_name in s3_buckets:
            sagemaker_role.add_to_policy(iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                resources=[
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            ))
        # Output SageMaker role ARN for downstream use
        CfnOutput(self, f"{env.capitalize()}SageMakerRoleArn", value=sagemaker_role.role_arn, export_name=f"{construct_id}-sagemaker-role-arn")

        # Glue execution role
        glue_role = iam.Role(
            self, f"{env.capitalize()}GlueExecutionRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            role_name=f"shieldcraftai-glue-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
            ]
        )
        # Attach least-privilege inline policies for Glue (S3, Lake Formation, etc.)
        for bucket_name in s3_buckets:
            glue_role.add_to_policy(iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                resources=[
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            ))
        glue_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "lakeformation:GetDataAccess",
                "glue:*"
            ],
            resources=["*"]
        ))
        # Output Glue role ARN for downstream use
        CfnOutput(self, f"{env.capitalize()}GlueRoleArn", value=glue_role.role_arn, export_name=f"{construct_id}-glue-role-arn")

        # Airbyte execution role (for ECS or Lambda deployment)
        airbyte_role = iam.Role(
            self, f"{env.capitalize()}AirbyteExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name=f"shieldcraftai-airbyte-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECSTaskExecutionRolePolicy")
            ]
        )
        # Attach least-privilege inline policies for Airbyte (S3, MSK, etc.)
        for bucket_name in s3_buckets:
            airbyte_role.add_to_policy(iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                resources=[
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            ))
        airbyte_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "kafka:DescribeCluster",
                "kafka:GetBootstrapBrokers",
                "kafka:ListTopics",
                "kafka:DescribeTopic"
            ],
            resources=[msk_arn]
        ))
        # Output Airbyte role ARN for downstream use
        CfnOutput(self, f"{env.capitalize()}AirbyteRoleArn", value=airbyte_role.role_arn, export_name=f"{construct_id}-airbyte-role-arn")

        # Lake Formation admin role
        lakeformation_admin_role = iam.Role(
            self, f"{env.capitalize()}LakeFormationAdminRole",
            assumed_by=iam.ServicePrincipal("lakeformation.amazonaws.com"),
            role_name=f"shieldcraftai-lakeformation-admin-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLakeFormationDataAdmin")
            ]
        )
        for bucket_name in s3_buckets:
            lakeformation_admin_role.add_to_policy(iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                resources=[
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            ))
        CfnOutput(self, f"{env.capitalize()}LakeFormationAdminRoleArn", value=lakeformation_admin_role.role_arn, export_name=f"{construct_id}-lakeformation-admin-role-arn")

        # VPC Flow Logs delivery role
        vpc_flow_logs_role = iam.Role(
            self, f"{env.capitalize()}VpcFlowLogsRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
            role_name=f"shieldcraftai-vpc-flowlogs-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSVPCFlowLogsDeliveryPolicy")
            ]
        )
        CfnOutput(self, f"{env.capitalize()}VpcFlowLogsRoleArn", value=vpc_flow_logs_role.role_arn, export_name=f"{construct_id}-vpc-flowlogs-role-arn")

        # Data Quality Lambda execution role
        dq_lambda_role = iam.Role(
            self, f"{env.capitalize()}DataQualityLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"shieldcraftai-dq-lambda-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        CfnOutput(self, f"{env.capitalize()}DataQualityLambdaRoleArn", value=dq_lambda_role.role_arn, export_name=f"{construct_id}-dq-lambda-role-arn")

        # Data Quality Glue job execution role
        dq_glue_role = iam.Role(
            self, f"{env.capitalize()}DataQualityGlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            role_name=f"shieldcraftai-dq-glue-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
            ]
        )
        CfnOutput(self, f"{env.capitalize()}DataQualityGlueRoleArn", value=dq_glue_role.role_arn, export_name=f"{construct_id}-dq-glue-role-arn")

        # Compliance Lambda execution role (for custom Config rules, if needed)
        compliance_lambda_role = iam.Role(
            self, f"{env.capitalize()}ComplianceLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"shieldcraftai-compliance-lambda-{env}",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        CfnOutput(self, f"{env.capitalize()}ComplianceLambdaRoleArn", value=compliance_lambda_role.role_arn, export_name=f"{construct_id}-compliance-lambda-role-arn")