import os
from diagrams import Diagram
from diagram_style import graph_attr, node_attr
from diagrams.aws.compute import ECS
from diagrams.aws.network import ELB
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import SecretsManager

try:
    from diagrams.aws.integration import SSM
except ImportError:
    from diagrams.aws.general import General as SSM

STATIC_DIAGRAMS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static", "diagrams")
)
os.makedirs(STATIC_DIAGRAMS_DIR, exist_ok=True)
output_path = os.path.join(STATIC_DIAGRAMS_DIR, "airbyte_stack_diagram.png")

with Diagram(
    "Airbyte Ingestion Stack",
    direction="TB",
    show=False,
    filename=output_path[:-4],
    outformat="png",
    graph_attr=graph_attr,
    node_attr=node_attr,
):
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
