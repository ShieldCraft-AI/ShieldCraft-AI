from diagrams import Cluster, Diagram
from diagrams.aws.ml import Sagemaker
from diagrams.aws.compute import Lambda
from diagrams.aws.analytics import OpensearchService
from diagrams.aws.integration import MSK
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import ELB
from diagrams.aws.compute import ECS, EKS
from diagrams.aws.devtools import Codebuild
from diagrams.generic.compute import Rack
from diagrams.generic.database import SQL

with Diagram("Compute & Model Hosting Architecture", direction="TB", show=False):
    with Cluster("SageMaker ML Stack"):
        sm_notebook = Sagemaker("Notebook")
        sm_training = Sagemaker("Training Job")
        sm_model = Sagemaker("Model Artifact")
        sm_endpoint = Sagemaker("Model Endpoint")
        sm_monitor = Sagemaker("Model Monitor")

    with Cluster("Event-Driven & Serverless"):
        inference_lambda = Lambda("Lambda Inference")
        msk_cluster = MSK("Amazon MSK (Kafka)")
        kafka_lambda = Lambda("Kafka Processor")

    with Cluster("Search & Vector Store"):
        os_ingest = OpensearchService("OpenSearch Ingestion")
        os_domain = OpensearchService("OpenSearch Domain")
        os_dash = OpensearchService("Kibana Dashboard")

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
