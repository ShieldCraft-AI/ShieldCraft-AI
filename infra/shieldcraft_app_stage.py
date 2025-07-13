from aws_cdk import Stage
from constructs import Construct
from stacks.networking.networking_stack import NetworkingStack
from stacks.compute.msk_stack import MskStack
from stacks.storage.s3_stack import S3Stack
from stacks.data.glue_stack import GlueStack
from stacks.compute.lambda_stack import LambdaStack
from stacks.data.airbyte_stack import AirbyteStack
from stacks.storage.lakeformation_stack import LakeFormationStack
from stacks.compute.opensearch_stack import OpenSearchStack
from stacks.data.dataquality_stack import DataQualityStack
from stacks.compute.sagemaker_stack import SageMakerStack
from stacks.cloud_native.cloud_native_hardening_stack import CloudNativeHardeningStack
from stacks.iam.iam_role_stack import IamRoleStack
from infra.stacks.compliance_stack import ComplianceStack
from infra.utils.config_loader import get_config_loader
from infra.utils.cdk_tagging import apply_standard_tags
from aws_cdk import Fn


class ShieldcraftAppStage(Stage):
    def __init__(self, scope: Construct, id: str, *, env_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        config = get_config_loader(env=env_name).export()
        app = self

        vpc_flow_logs_role_arn = Fn.import_value("IamRoleStack-vpc-flowlogs-role-arn")
        networking = NetworkingStack(
            app,
            "NetworkingStack",
            config=config.get("networking", {}),
            vpc_flow_logs_role_arn=vpc_flow_logs_role_arn,
        )
        s_msk_client_role_arn = Fn.import_value("IamRoleStack-msk-client-role-arn")
        msk_producer_role_arn = Fn.import_value("IamRoleStack-msk-producer-role-arn")
        msk_consumer_role_arn = Fn.import_value("IamRoleStack-msk-consumer-role-arn")
        msk = MskStack(
            app,
            "MskStack",
            vpc=networking.vpc,
            config=config.get("msk", {}),
            msk_client_role_arn=s_msk_client_role_arn,
            msk_producer_role_arn=msk_producer_role_arn,
            msk_consumer_role_arn=msk_consumer_role_arn,
        )
        s3 = S3Stack(app, "S3Stack", config=config.get("s3", {}))
        glue_role_arn = Fn.import_value("IamRoleStack-glue-role-arn")
        glue = GlueStack(
            app,
            "GlueStack",
            vpc=networking.vpc,
            buckets=s3.buckets,
            default_sg=networking.default_sg,
            glue_role_arn=glue_role_arn,
            config=config,
        )
        iam_roles = IamRoleStack(app, "IamRoleStack", config=config)
        lambda_role_arn = Fn.import_value("IamRoleStack-lambda-role-arn")
        lambda_stack = LambdaStack(
            app,
            "LambdaStack",
            vpc=networking.vpc,
            config=config.get("lambda_", {}),
            lambda_role_arn=lambda_role_arn,
        )
        airbyte_role_arn = Fn.import_value("IamRoleStack-airbyte-role-arn")
        airbyte = AirbyteStack(
            app,
            "AirbyteStack",
            vpc=networking.vpc,
            config=config.get("airbyte", {}),
            airbyte_role_arn=airbyte_role_arn,
        )
        lakeformation_admin_role_arn = Fn.import_value(
            "IamRoleStack-lakeformation-admin-role-arn"
        )
        lakeformation = LakeFormationStack(
            app,
            "LakeFormationStack",
            vpc=networking.vpc,
            config=config.get("lakeformation", {}),
            lakeformation_admin_role_arn=lakeformation_admin_role_arn,
        )
        opensearch_role_arn = Fn.import_value("IamRoleStack-opensearch-role-arn")
        opensearch = OpenSearchStack(
            app,
            "OpenSearchStack",
            vpc=networking.vpc,
            config=config.get("opensearch", {}),
            opensearch_role_arn=opensearch_role_arn,
        )
        dataquality = DataQualityStack(
            app,
            "DataQualityStack",
            vpc=networking.vpc,
            config=config.get("data_quality", {}),
        )
        sagemaker_role_arn = Fn.import_value("IamRoleStack-sagemaker-role-arn")
        sagemaker = SageMakerStack(
            app,
            "SageMakerStack",
            vpc=networking.vpc,
            config=config,
            sagemaker_role_arn=sagemaker_role_arn,
        )
        cloud_native_hardening = CloudNativeHardeningStack(
            app,
            "CloudNativeHardeningStack",
            vpc=networking.vpc,
            config=config.get("cloud_native_hardening", {}),
            lambda_role_arn=lambda_role_arn,
            msk_client_role_arn=s_msk_client_role_arn,
            msk_producer_role_arn=msk_producer_role_arn,
            msk_consumer_role_arn=msk_consumer_role_arn,
            opensearch_role_arn=opensearch_role_arn,
        )
        standard_tags = {
            "Project": "shieldcraft-ai",
            "Environment": env_name,
            "Owner": config.get("owner", "mlops-team"),
        }
        for stack in [
            networking,
            msk,
            s3,
            glue,
            iam_roles,
            lambda_stack,
            airbyte,
            lakeformation,
            opensearch,
            dataquality,
            sagemaker,
            cloud_native_hardening,
        ]:
            apply_standard_tags(
                stack,
                project=standard_tags["Project"],
                environment=standard_tags["Environment"],
                owner=standard_tags["Owner"],
            )
        compliance_lambda_role_arn = Fn.import_value(
            "IamRoleStack-compliance-lambda-role-arn"
        )
        ComplianceStack(
            app,
            "ComplianceStack",
            config=config.get("compliance", {}),
            lambda_role_arn=compliance_lambda_role_arn,
        )
