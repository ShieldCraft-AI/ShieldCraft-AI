from diagrams import Cluster, Diagram
from diagrams.aws.storage import S3
from diagrams.aws.security import KMS
from diagrams.aws.analytics import LakeFormation
from diagrams.generic.storage import Storage

with Diagram("Storage & Data Lake Architecture", direction="TB", show=False):
    with Cluster("Amazon S3 Buckets"):
        raw_bucket = S3("Raw Data Bucket")
        processed_bucket = S3("Processed Data Bucket")
        artifacts_bucket = S3("Model Artifacts / Outputs")

    with Cluster("Governance & Security"):
        lake_formation = LakeFormation("AWS Lake Formation")
        kms_key = KMS("KMS (Encryption Key)")
        lifecycle_policies = Storage("S3 Lifecycle Policies")

    # Relationships
    lake_formation >> [raw_bucket, processed_bucket, artifacts_bucket]
    kms_key >> [raw_bucket, processed_bucket, artifacts_bucket]
    lifecycle_policies >> [raw_bucket, processed_bucket]
