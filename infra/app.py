"""
ShieldCraft AI Infrastructure Deployment Script
"""

import os
import ast
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger, ERROR
import aws_cdk as cdk
from aws_cdk import Fn
from aws_cdk import Environment
from infra.stacks.networking.networking_stack import NetworkingStack
from infra.stacks.compute.msk_stack import MskStack
from infra.stacks.storage.s3_stack import S3Stack
from infra.stacks.data.glue_stack import GlueStack
from infra.stacks.compute.lambda_stack import LambdaStack
from infra.stacks.data.airbyte_stack import AirbyteStack
from infra.stacks.storage.lakeformation_stack import LakeFormationStack
from infra.stacks.compute.opensearch_stack import OpenSearchStack
from infra.stacks.data.dataquality_stack import DataQualityStack
from infra.stacks.compute.sagemaker_stack import SageMakerStack
from infra.stacks.cloud_native.cloud_native_hardening_stack import (
    CloudNativeHardeningStack,
)
from infra.utils.config_loader import get_config_loader
from infra.utils.cdk_tagging import apply_standard_tags
from infra.stacks.iam.iam_role_stack import (
    IamRoleStack,
)  # pylint: disable=unused-import
from infra.stacks.compliance_stack import (
    ComplianceStack,
)  # pylint: disable=unused-import
from infra.stacks.budget_stack import BudgetStack
from infra.stacks.security.secrets_manager_stack import SecretsManagerStack
import yaml

logger = getLogger("shieldcraft-ai")
logger.setLevel(ERROR)


def log_and_raise(msg, exc):
    logger.error(msg)
    raise exc


try:
    # Use ConfigLoader as source of truth for environment
    env = get_config_loader().get_section("app").get("env", "dev")
    config = get_config_loader(env=env).export()
    print("[DEBUG] Loaded app config:", config.get("app"))
    required_sections = ["networking", "s3", "app", "tags"]
    for section in required_sections:
        if section not in config:
            log_and_raise(
                f"Missing required config section: {section}",
                ValueError(f"Missing required config section: {section}"),
            )
    # Set region/account environment variables from config before CDK app instantiation
    region = config.get("app", {}).get("region")
    account = config.get("app", {}).get("account")
    if not region or not account:
        log_and_raise(
            f"Config 'app' section must include both 'region' and 'account'. Got region={region}, account={account}",
            ValueError("Missing region/account in config for CDK environment context."),
        )
    os.environ["AWS_DEFAULT_REGION"] = region
    os.environ["CDK_DEFAULT_REGION"] = region
    app = cdk.App()
    SECRETS_CONFIG_PATH = f"config/secrets.{env}.yml"
    try:
        with open(SECRETS_CONFIG_PATH, "r", encoding="utf-8") as f:
            secrets_config = yaml.safe_load(f).get("secrets", {})
    except (FileNotFoundError, yaml.YAMLError) as e:
        log_and_raise(
            f"Failed to load secrets config: {e}",
            RuntimeError(f"Failed to load secrets config: {e}"),
        )

    cdk_env = Environment(
        region=region,
        account=account,
    )

    def sanitize_tags(tags):
        if not isinstance(tags, dict):
            return {}
        return {
            str(k): str(v)
            for k, v in tags.items()
            if isinstance(v, str) and v is not None
        }

    try:
        secrets_stack = SecretsManagerStack(
            app,
            "SecretsManagerStack",
            secrets_config=secrets_config,
            env=cdk_env,
            description=f"Secrets for {env} environment",
        )
    except (ValueError, RuntimeError, yaml.YAMLError, FileNotFoundError) as e:
        log_and_raise(
            f"Failed to instantiate SecretsManagerStack: {e}",
            RuntimeError(f"Failed to instantiate SecretsManagerStack: {e}"),
        )

    stack_results = {}

    def get_shared_tags(tags):
        if isinstance(tags, dict):
            return tags
        if tags is None:
            return {}
        if isinstance(tags, str):

            try:
                parsed = ast.literal_eval(tags)
                if isinstance(parsed, dict):
                    return parsed
            except (ValueError, SyntaxError):
                pass
        return {}

    shared_tags = get_shared_tags(config.get("tags"))

    # Instantiate networking stack first to ensure vpc is available
    networking = NetworkingStack(
        app,
        "NetworkingStack",
        config=config,
        vpc_flow_logs_role_arn=Fn.import_value("IamRoleStack-vpc-flowlogs-role-arn"),
        env=cdk_env,
    )
    stack_results["networking"] = networking

    with ThreadPoolExecutor() as executor:
        futures = {
            "iam_roles": executor.submit(
                IamRoleStack, app, "IamRoleStack", config=config, env=cdk_env
            ),
            "s3": executor.submit(
                S3Stack,
                app,
                "S3Stack",
                config=config,
                shared_tags=shared_tags,
                env=cdk_env,
            ),
            "lakeformation": executor.submit(
                LakeFormationStack,
                app,
                "LakeFormationStack",
                vpc=networking.vpc,
                config=config.get("lakeformation", {}),
                lakeformation_admin_role_arn=None,
                env=cdk_env,
            ),
            "opensearch": executor.submit(
                OpenSearchStack,
                app,
                "OpenSearchStack",
                vpc=networking.vpc,
                config=config.get("opensearch", {}),
                opensearch_role_arn=None,
                env=cdk_env,
            ),
            "dataquality": executor.submit(
                DataQualityStack,
                app,
                "DataQualityStack",
                vpc=networking.vpc,
                config=config.get("data_quality", {}),
                env=cdk_env,
            ),
        }
        for name, future in futures.items():
            try:
                stack_results[name] = future.result()
            except (
                ValueError,
                RuntimeError,
                yaml.YAMLError,
                FileNotFoundError,
            ) as e:
                log_and_raise(
                    f"Failed to instantiate {name} stack: {e}",
                    RuntimeError(f"Failed to instantiate {name} stack: {e}"),
                )

    iam_roles = stack_results["iam_roles"]
    s3 = stack_results["s3"]
    lakeformation = stack_results["lakeformation"]
    opensearch = stack_results["opensearch"]
    dataquality = stack_results["dataquality"]

    glue_role_arn = Fn.import_value("IamRoleStack-glue-role-arn")
    glue_db_password_arn = (
        Fn.import_value("SecretsManagerStack-glue_db_admin_password-arn")
        if "glue_db_admin_password" in secrets_config
        else None
    )
    airbyte_source_db_password_arn = (
        Fn.import_value("SecretsManagerStack-airbyte_source_db_password-arn")
        if "airbyte_source_db_password" in secrets_config
        else None
    )
    sns_topic_secret_arn = (
        Fn.import_value("SecretsManagerStack-sns_topic_secret-arn")
        if "sns_topic_secret" in secrets_config
        else None
    )

    glue = GlueStack(
        app,
        "GlueStack",
        vpc=networking.vpc,
        buckets=s3.buckets,
        default_sg=networking.default_sg,
        glue_role_arn=glue_role_arn,
        config=config,
        db_password_arn=glue_db_password_arn,
        env=cdk_env,
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
        env=cdk_env,
    )
    lambda_role_arn = Fn.import_value("IamRoleStack-lambda-role-arn")
    lambda_stack = LambdaStack(
        app,
        "LambdaStack",
        vpc=networking.vpc,
        config=config.get("lambda_", {}),
        lambda_role_arn=lambda_role_arn,
        env=cdk_env,
    )
    airbyte_role_arn = Fn.import_value("IamRoleStack-airbyte-role-arn")
    airbyte = AirbyteStack(
        app,
        "AirbyteStack",
        vpc=networking.vpc,
        config=config.get("airbyte", {}),
        airbyte_role_arn=airbyte_role_arn,
        source_db_password_arn=airbyte_source_db_password_arn,
        env=cdk_env,
    )
    lakeformation_admin_role_arn = Fn.import_value(
        "IamRoleStack-lakeformation-admin-role-arn"
    )
    lakeformation.lakeformation_admin_role_arn = lakeformation_admin_role_arn
    opensearch_role_arn = Fn.import_value("IamRoleStack-opensearch-role-arn")
    opensearch.opensearch_role_arn = opensearch_role_arn
    dataquality.vpc = networking.vpc
    sagemaker_role_arn = Fn.import_value("IamRoleStack-sagemaker-role-arn")
    sagemaker = SageMakerStack(
        app,
        "SageMakerStack",
        vpc=networking.vpc,
        config=config,
        sagemaker_role_arn=sagemaker_role_arn,
        env=cdk_env,
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
        sns_topic_secret_arn=sns_topic_secret_arn,
        env=cdk_env,
    )
    compliance_lambda_role_arn = Fn.import_value(
        "IamRoleStack-compliance-lambda-role-arn"
    )
    compliance = ComplianceStack(
        app,
        "ComplianceStack",
        config=config.get("compliance", {}),
        lambda_role_arn=compliance_lambda_role_arn,
        env=cdk_env,
    )

    budget_email = config.get("budget_email")
    budget_limit = config.get("budget_limit", 50)
    budget_sns_arn = config.get("budget_sns_topic_arn")
    budget = BudgetStack(
        app,
        "BudgetStack",
        budget_limit=budget_limit,
        email_address=budget_email,
        sns_topic_arn=budget_sns_arn,
        env=cdk_env,
    )
    budget.add_dependency(networking)
    budget.add_dependency(msk)
    budget.add_dependency(s3)
    budget.add_dependency(glue)
    budget.add_dependency(iam_roles)
    budget.add_dependency(lambda_stack)
    budget.add_dependency(airbyte)
    budget.add_dependency(lakeformation)
    budget.add_dependency(opensearch)
    budget.add_dependency(dataquality)
    budget.add_dependency(sagemaker)
    budget.add_dependency(cloud_native_hardening)
    budget.add_dependency(compliance)

    glue.add_dependency(s3)
    glue.add_dependency(networking)
    glue.add_dependency(iam_roles)
    msk.add_dependency(networking)
    msk.add_dependency(iam_roles)
    lambda_stack.add_dependency(networking)
    lambda_stack.add_dependency(iam_roles)
    airbyte.add_dependency(networking)
    airbyte.add_dependency(iam_roles)
    lakeformation.add_dependency(networking)
    lakeformation.add_dependency(iam_roles)
    opensearch.add_dependency(networking)
    opensearch.add_dependency(iam_roles)
    dataquality.add_dependency(networking)
    dataquality.add_dependency(glue)
    dataquality.add_dependency(lambda_stack)
    sagemaker.add_dependency(networking)
    sagemaker.add_dependency(iam_roles)
    cloud_native_hardening.add_dependency(networking)
    cloud_native_hardening.add_dependency(iam_roles)
    cloud_native_hardening.add_dependency(msk)
    cloud_native_hardening.add_dependency(lambda_stack)
    cloud_native_hardening.add_dependency(opensearch)
    compliance.add_dependency(iam_roles)
    compliance.add_dependency(lambda_stack)

    standard_tags = {
        "Project": "shieldcraft-ai",
        "Environment": env,
        "Owner": config.get("owner", "mlops-team"),
        "CostCenter": config.get("cost_center", "RND"),
        "Team": config.get("team", "mlops"),
        "Compliance": config.get("compliance", "standard"),
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
        compliance,
        budget,
    ]:
        apply_standard_tags(
            stack,
            project=standard_tags["Project"],
            environment=standard_tags["Environment"],
            owner=standard_tags["Owner"],
            cost_center=standard_tags["CostCenter"],
            team=standard_tags["Team"],
            compliance=standard_tags["Compliance"],
        )

    app.synth()
except (ValueError, RuntimeError, yaml.YAMLError, FileNotFoundError) as e:
    logger.error("[ShieldCraft AI] Deployment failed: %s", e, exc_info=True)
