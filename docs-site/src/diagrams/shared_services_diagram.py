import os
from diagrams import Cluster, Diagram
from diagram_style import graph_attr, node_attr
from diagrams.aws.security import SecretsManager, KMS
from diagrams.aws.management import SSM
from diagrams.aws.integration import Eventbridge
from diagrams.aws.security import IAM

# Output diagrams to the Docusaurus static assets directory (always docs-site/static/diagrams)
STATIC_DIAGRAMS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static", "diagrams")
)
os.makedirs(STATIC_DIAGRAMS_DIR, exist_ok=True)
output_path = os.path.join(STATIC_DIAGRAMS_DIR, "shared_services_diagram.png")

with Diagram(
    "Shared & Supporting Services Architecture",
    direction="TB",
    show=False,
    filename=output_path[:-4],  # Diagrams adds .png automatically
    outformat="png",
    graph_attr=graph_attr,
    node_attr=node_attr,
):
    with Cluster("Secrets & Config Management"):
        secrets_mgr = SecretsManager("Secrets Manager")
        param_store = SSM("SSM Parameter Store")

    with Cluster("Encryption & Keys"):
        shared_kms = KMS("KMS Key (Shared)")

    with Cluster("Orchestration"):
        eventbridge = Eventbridge("EventBridge (if used)")

    with Cluster("IAM & Access Control"):
        shared_iam = IAM("Shared IAM Roles / Policies")

    # Simulate cross-stack IAM role passing (arrows to other clusters)
    # These are logical, not physical, but help visualize cross-stack wiring
    # In a full system diagram, these would point to other stack clusters

    # Relationships
    shared_kms >> [secrets_mgr, param_store]
    shared_iam >> [secrets_mgr, param_store]
    eventbridge >> [secrets_mgr, param_store]

    # Cross-stack IAM role passing (visual only)
    # These would point to other diagrams in a full system view
    shared_iam >> shared_kms
    shared_iam >> eventbridge
