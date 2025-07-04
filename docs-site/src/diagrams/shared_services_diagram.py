from diagrams import Cluster, Diagram
from diagrams.aws.security import SecretsManager, KMS
from diagrams.aws.management import SSM
from diagrams.aws.integration import Eventbridge
from diagrams.aws.security import IAM
from diagrams.generic.compute import Rack
from diagrams.generic.storage import Storage

with Diagram("Shared & Supporting Services Architecture", direction="TB", show=False):
    with Cluster("Secrets & Config Management"):
        secrets_mgr = SecretsManager("Secrets Manager")
        param_store = SSM("SSM Parameter Store")

    with Cluster("Encryption & Keys"):
        shared_kms = KMS("KMS Key (Shared)")

    with Cluster("Orchestration"):
        eventbridge = Eventbridge("EventBridge (if used)")

    with Cluster("IAM & Access Control"):
        shared_iam = IAM("Shared IAM Roles / Policies")

    # Relationships
    shared_kms >> [secrets_mgr, param_store]
    shared_iam >> [secrets_mgr, param_store]
    eventbridge >> [secrets_mgr, param_store]
