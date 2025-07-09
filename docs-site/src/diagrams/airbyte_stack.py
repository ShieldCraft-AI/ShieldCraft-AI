from diagrams import Cluster
from diagrams.aws.compute import ECS
from diagrams.aws.network import ELB
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import SecretsManager

try:
    from diagrams.aws.integration import SSM
except ImportError:
    from diagrams.aws.general import General as SSM


def create_airbyte_stack():
    with Cluster("Airbyte Ingestion Stack"):
        airbyte_ecs = ECS("Airbyte on ECS")
        airbyte_connectors = ECS("Connectors")
        airbyte_elb = ELB("ELBv2")
        airbyte_logs = Cloudwatch("CloudWatch Logs")
        airbyte_secrets = SecretsManager("Secrets Manager")
        airbyte_ssm = SSM("SSM Parameters")

        airbyte_elb >> airbyte_ecs
        airbyte_ecs >> airbyte_connectors
        airbyte_ecs >> airbyte_logs
        airbyte_ecs >> airbyte_ssm
        airbyte_ecs >> airbyte_secrets

        return {
            "ecs": airbyte_ecs,
            "connectors": airbyte_connectors,
            "elb": airbyte_elb,
            "logs": airbyte_logs,
            "secrets": airbyte_secrets,
            "ssm": airbyte_ssm,
        }
