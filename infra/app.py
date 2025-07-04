import os
import aws_cdk as cdk
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
from infra.utils.config_loader import get_config_loader
from infra.utils.cdk_tagging import apply_standard_tags

from infra.stacks.compliance_stack import ComplianceStack

# Determine environment (CLI arg, env var, or default)
env = os.environ.get("ENV") or os.environ.get("APP_ENV") or "dev"
config = get_config_loader(env=env).export()


app = cdk.App()


# Instantiate stacks
networking = NetworkingStack(app, "NetworkingStack", config=config.get("networking", {}))
msk = MskStack(app, "MskStack", vpc=networking.vpc, config=config.get("msk", {}))
s3 = S3Stack(app, "S3Stack", config=config.get("s3", {}))
glue = GlueStack(
    app,
    "GlueStack",
    vpc=networking.vpc,
    data_bucket=s3.data_bucket,
    default_sg=networking.default_sg,
    config=config.get("glue", {})
)
lambda_stack = LambdaStack(app, "LambdaStack", vpc=networking.vpc, config=config.get("lambda_", {}))
airbyte = AirbyteStack(app, "AirbyteStack", vpc=networking.vpc, config=config.get("airbyte", {}))
lakeformation = LakeFormationStack(app, "LakeFormationStack", vpc=networking.vpc, config=config.get("lakeformation", {}))
opensearch = OpenSearchStack(app, "OpenSearchStack", vpc=networking.vpc, config=config.get("opensearch", {}))
dataquality = DataQualityStack(app, "DataQualityStack", vpc=networking.vpc, config=config.get("data_quality", {}))
sagemaker = SageMakerStack(app, "SageMakerStack", vpc=networking.vpc, config=config.get("sagemaker", {}))
cloud_native_hardening = CloudNativeHardeningStack(app, "CloudNativeHardeningStack", vpc=networking.vpc, config=config.get("cloud_native_hardening", {}))

# Apply standard tags to all stacks
standard_tags = {
    "Project": "shieldcraft-ai",
    "Environment": env,
    "Owner": config.get("owner", "mlops-team")
}
for stack in [networking, msk, s3, glue, lambda_stack, airbyte, lakeformation, opensearch, dataquality, sagemaker, cloud_native_hardening]:
    apply_standard_tags(stack, project=standard_tags["Project"], environment=standard_tags["Environment"], owner=standard_tags["Owner"])


# Instantiate compliance stack
compliance = ComplianceStack(app, "ComplianceStack")

app.synth()
