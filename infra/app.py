import aws_cdk as cdk
from stacks.networking.networking_stack import NetworkingStack
from stacks.compute.msk_stack import MskStack
from stacks.storage.s3_stack import S3Stack
from stacks.data.glue_stack import GlueStack
# from stacks.compute.lambda_stack import LambdaStack
# from stacks.data.airbyte_stack import AirbyteStack
# from stacks.storage.lakeformation_stack import LakeFormationStack
# from stacks.compute.opensearch_stack import OpenSearchStack
# from stacks.data.dataquality_stack import DataQualityStack

app = cdk.App()

# Networking (VPC, subnets, security groups)
networking = NetworkingStack(app, "NetworkingStack")

# MSK (Kafka) cluster, depends on networking
msk = MskStack(app, "MskStack", vpc=networking.vpc)

# Add more stacks as needed, passing references as required
s3 = S3Stack(app, "S3Stack")
glue = GlueStack(app, "GlueStack", vpc=networking.vpc, data_bucket=s3.data_bucket, default_sg=networking.default_sg)
# lambda_stack = LambdaStack(app, "LambdaStack", vpc=networking.vpc)
# airbyte = AirbyteStack(app, "AirbyteStack", vpc=networking.vpc)
# lakeformation = LakeFormationStack(app, "LakeFormationStack", vpc=networking.vpc)
# opensearch = OpenSearchStack(app, "OpenSearchStack", vpc=networking.vpc)
# dataquality = DataQualityStack(app, "DataQualityStack", vpc=networking.vpc)

app.synth()
