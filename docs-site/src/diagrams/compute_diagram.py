import os
from diagrams import Cluster, Diagram
from diagram_style import graph_attr, node_attr
from diagrams.aws.ml import Sagemaker
from diagrams.aws.compute import Lambda
from diagrams.aws.analytics import ElasticsearchService as OpenSearchService
from diagrams.aws.network import ELB, VPC
from diagrams.aws.compute import ECS, EKS
from diagrams.aws.storage import S3
from diagrams.aws.security import IAM

try:
    from diagrams.aws.integration import MSK
except ImportError:
    from diagrams.aws.general import (
        General as MSK,
    )  # Fallback: generic AWS node for MSK

# Output diagrams to the Docusaurus static assets directory (always docs-site/static/diagrams)
STATIC_DIAGRAMS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static", "diagrams")
)
os.makedirs(STATIC_DIAGRAMS_DIR, exist_ok=True)
output_path = os.path.join(STATIC_DIAGRAMS_DIR, "compute_diagram.png")

with Diagram(
    "Compute & Model Hosting Architecture",
    direction="TB",
    show=False,
    filename=output_path[:-4],  # Diagrams adds .png automatically
    outformat="png",
    graph_attr=graph_attr,
    node_attr=node_attr,
):
    # Foundational resources
    vpc = VPC("VPC")
    s3 = S3("S3 Bucket")
    iam = IAM("IAM Role")

    with Cluster("SageMaker ML Stack"):
        sm_notebook = Sagemaker("Notebook")
        sm_training = Sagemaker("Training Job")
        sm_model = Sagemaker("Model Artifact")
        sm_endpoint = Sagemaker("Model Endpoint")
        sm_monitor = Sagemaker("Model Monitor")
        # Show SageMaker consuming VPC, S3, IAM
        vpc >> sm_notebook
        s3 >> sm_training
        iam >> sm_endpoint

    with Cluster("Event-Driven & Serverless"):
        inference_lambda = Lambda("Lambda Inference")
        msk_cluster = MSK("Amazon MSK (Kafka)")
        kafka_lambda = Lambda("Kafka Processor")
        # Show Lambda and MSK consuming VPC, S3, IAM
        vpc >> inference_lambda
        vpc >> msk_cluster
        iam >> inference_lambda
        iam >> kafka_lambda
        s3 >> inference_lambda

    with Cluster("Search & Vector Store"):
        os_ingest = OpenSearchService("OpenSearch Ingestion")
        os_domain = OpenSearchService("OpenSearch Domain")
        os_dash = OpenSearchService("Kibana Dashboard")

    with Cluster("Containerized App Runtime"):
        api_eks = EKS("EKS - FastAPI / Node.js")
        ecs_fargate = ECS("ECS Fargate")
        app_elb = ELB("App Load Balancer")

    # Relationships
    sm_notebook >> sm_training >> sm_model >> sm_endpoint
    sm_endpoint >> sm_monitor
    inference_lambda >> sm_endpoint
    msk_cluster >> kafka_lambda >> sm_model
    os_ingest >> os_domain >> os_dash
    app_elb >> [api_eks, ecs_fargate]
