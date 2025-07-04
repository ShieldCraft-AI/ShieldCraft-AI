from diagrams import Cluster, Diagram
from diagrams.aws.analytics import Glue
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import SecretsManager
from diagrams.aws.compute import EC2
from diagrams.aws.devtools import Codebuild
from diagrams.aws.integration import SSM
from diagrams.aws.network import ELB
from diagrams.generic.compute import Rack
from diagrams.generic.monitoring import Monitor

with Diagram("Data Processing & ETL Architecture", direction="TB", show=False):
    with Cluster("ETL Frameworks"):
        glue_jobs = Glue("AWS Glue Jobs")
        glue_crawlers = Glue("Glue Crawlers")
        glue_catalog = Glue("Glue Data Catalog")
        databrew = Glue("DataBrew (if used)")

    with Cluster("Data Quality"):
        dq_tool = Monitor("Deequ / Great Expectations")

    with Cluster("Airbyte Ingestion Stack"):
        airbyte_ec2 = EC2("Airbyte on EC2")
        airbyte_elb = ELB("ELBv2")
        airbyte_logs = Cloudwatch("CloudWatch Logs")
        airbyte_secrets = SecretsManager("Secrets Manager")
        airbyte_ssm = SSM("SSM Parameters")

    # Relationships
    glue_jobs >> dq_tool
    glue_jobs >> glue_catalog
    databrew >> glue_catalog
    airbyte_ec2 >> airbyte_logs
    airbyte_ec2 >> airbyte_ssm
    airbyte_ec2 >> airbyte_secrets
    airbyte_elb >> airbyte_ec2
