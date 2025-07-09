import os
from diagrams import Cluster, Diagram
from diagram_style import graph_attr, node_attr
from diagrams.aws.storage import S3
from diagrams.aws.security import KMS
from diagrams.aws.analytics import LakeFormation
from diagrams.generic.storage import Storage

# Output diagrams to the Docusaurus static assets directory (always docs-site/static/diagrams)
STATIC_DIAGRAMS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static", "diagrams")
)
os.makedirs(STATIC_DIAGRAMS_DIR, exist_ok=True)
output_path = os.path.join(STATIC_DIAGRAMS_DIR, "storage_diagram.png")

with Diagram(
    "Storage & Data Lake Architecture",
    direction="TB",
    show=False,
    filename=output_path[:-4],  # Diagrams adds .png automatically
    outformat="png",
    graph_attr=graph_attr,
    node_attr=node_attr,
):

    with Cluster("Amazon S3 Buckets"):
        raw_bucket = S3("Raw Data Bucket")
        processed_bucket = S3("Processed Data Bucket")
        artifacts_bucket = S3("Model Artifacts / Outputs")

    # Show Lake Formation registration of S3 buckets (dashed arrow)
    # Diagrams doesn't support dashed arrows natively, so we annotate with a comment

    with Cluster("Governance & Security"):
        lake_formation = LakeFormation("AWS Lake Formation")
        kms_key = KMS("KMS (Encryption Key)")
        lifecycle_policies = Storage("S3 Lifecycle Policies")

    # Relationships
    # S3 buckets registered with Lake Formation for governance
    raw_bucket >> lake_formation
    processed_bucket >> lake_formation
    artifacts_bucket >> lake_formation
    lake_formation >> [raw_bucket, processed_bucket, artifacts_bucket]
    kms_key >> [raw_bucket, processed_bucket, artifacts_bucket]
    lifecycle_policies >> [raw_bucket, processed_bucket]
