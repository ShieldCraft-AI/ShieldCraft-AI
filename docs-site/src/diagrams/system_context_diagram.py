import os
from diagrams import Cluster

STATIC_DIAGRAMS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static", "diagrams")
)
os.makedirs(STATIC_DIAGRAMS_DIR, exist_ok=True)
output_path = os.path.join(STATIC_DIAGRAMS_DIR, "system_context_diagram.png")

from diagrams.generic.blank import Blank

# External actors (business-focused)
analyst = Blank("Security Analyst")
admin = Blank("Administrator")
ext_source = Blank("External Data Source/API")
consumer = Blank("Downstream Consumer/API")

# System boundary: Only the most impactful business domains, no AWS details
with Cluster("ShieldCraft AI Platform"):
    ingestion = Blank("Data Ingestion Service")
    stream = Blank("Real-time Processing Stream")
    knowledge = Blank("Threat Knowledge Base")
    anomaly = Blank("Anomaly Detection Service")
    reasoning = Blank("AI Reasoning Engine")
    query_api = Blank("Query & Analysis API")
    analyst_ui = Blank("Security Analyst UI")
    auth = Blank("Authentication & Authorization")
    admin_panel = Blank("Admin Panel")
    admin_api = Blank("Admin API")

# Main flows (minimal, business-focused)
ext_source >> ingestion
ingestion >> stream
stream >> knowledge
knowledge >> anomaly
anomaly >> reasoning
reasoning >> query_api
query_api >> analyst_ui
analyst >> analyst_ui
analyst >> query_api
admin >> admin_panel
admin_panel >> admin_api
admin_api >> ingestion
query_api >> consumer

# Auth as cross-cutting (shown as a single arrow to all UIs/APIs)
auth >> analyst_ui
auth >> admin_panel
auth >> query_api
auth >> admin_api

# Add a C4 legend (minimal, business-focused)
legend = Blank(
    "C4 Level 1: System Context\n"
    "- Shows major actors, system boundary, and business domains\n"
    "- Arrows: main data/control flows\n"
    "- Auth: cross-cutting, applies to all UIs/APIs\n"
    "- Drill down: see Level 2/3 diagrams for details"
)
analyst >> legend
