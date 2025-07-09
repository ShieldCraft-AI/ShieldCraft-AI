import os
from diagrams import Cluster, Diagram
from diagram_style import graph_attr, node_attr
from diagrams.aws.analytics import Glue
from diagrams.aws.compute import Lambda

try:
    from diagrams.generic.compute import (
        Rack as Monitor,
    )  # Use Rack as a generic node for Data Quality
except ImportError:
    from diagrams.aws.general import (
        General as Monitor,
    )  # Fallback: AWS General node if generic.compute is missing

# Output diagrams to the Docusaurus static assets directory (always docs-site/static/diagrams)
STATIC_DIAGRAMS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static", "diagrams")
)
os.makedirs(STATIC_DIAGRAMS_DIR, exist_ok=True)
output_path = os.path.join(STATIC_DIAGRAMS_DIR, "data_etl_diagram.png")

with Diagram(
    "Data Processing & ETL Architecture",
    direction="TB",
    show=False,
    filename=output_path[:-4],  # Diagrams adds .png automatically
    outformat="png",
    graph_attr=graph_attr,
    node_attr=node_attr,
):
    with Cluster("ETL Frameworks"):
        glue_jobs = Glue("AWS Glue Jobs")
        glue_crawlers = Glue("Glue Crawlers")
        glue_catalog = Glue("Glue Data Catalog")

    with Cluster("Data Quality"):
        dq_lambda = Lambda("DQ Lambda Job")
        dq_glue = Glue("DQ Glue Job")
        dq_tool = Monitor("Deequ / Great Expectations")

    # Relationships
    glue_jobs >> dq_glue >> dq_tool
    glue_jobs >> dq_lambda >> dq_tool
    glue_jobs >> glue_catalog
    # Airbyte stack moved to airbyte_stack_diagram.py
