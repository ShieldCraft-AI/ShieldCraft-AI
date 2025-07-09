# Robust import fallbacks for diagrams nodes (version-agnostic)
try:
    from diagrams import Cluster, Diagram
except ImportError:
    from diagrams import Cluster, Diagram


def _import_diagram_node(module, name, fallback=None):
    try:
        return getattr(__import__(module, fromlist=[name]), name)
    except (ImportError, AttributeError):
        return fallback if fallback is not None else None


# AWS Management
Cloudwatch = _import_diagram_node(
    "diagrams.aws.management", "Cloudwatch", fallback=None
)
CloudwatchLogs = _import_diagram_node(
    "diagrams.aws.management", "CloudwatchLogs", fallback=None
)
CloudwatchAlarm = _import_diagram_node(
    "diagrams.aws.management", "CloudwatchAlarm", fallback=Cloudwatch
)
Config = _import_diagram_node("diagrams.aws.management", "Config", fallback=None)
# AWS Security
IAM = _import_diagram_node("diagrams.aws.security", "IAM", fallback=None)
# AWS Notifications
SNS = _import_diagram_node("diagrams.aws.notifications", "SNS", fallback=None)
# AWS Billing
Budgets = _import_diagram_node("diagrams.aws.billing", "Budgets", fallback=None)
CostExplorer = _import_diagram_node(
    "diagrams.aws.billing", "CostExplorer", fallback=Budgets
)
# Generic Monitoring
Dashboard = _import_diagram_node(
    "diagrams.generic.monitoring", "Dashboard", fallback=Cloudwatch
)


from diagrams.aws.management import SystemsManager
import os
from diagram_style import graph_attr, node_attr

# Output diagrams to the Docusaurus static assets directory (always docs-site/static/diagrams)
STATIC_DIAGRAMS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static", "diagrams")
)
os.makedirs(STATIC_DIAGRAMS_DIR, exist_ok=True)
output_path = os.path.join(STATIC_DIAGRAMS_DIR, "monitoring_compliance_diagram.png")

with Diagram(
    "Monitoring, Compliance & Hardening Architecture",
    direction="TB",
    show=False,
    filename=output_path[:-4],  # Diagrams adds .png automatically
    outformat="png",
    graph_attr=graph_attr,
    node_attr=node_attr,
):

    def safe_node(node_class, label):
        if node_class is None:
            # Return a dummy object that mimics diagrams.node.Node API (for diagrams 0.23.x)
            class Dummy:
                def __init__(self, label):
                    self.label = label

                def __rshift__(self, other):
                    return other

                def __lshift__(self, other):
                    return self

                def __repr__(self):
                    return self.label

                def __getattr__(self, name):
                    # diagrams 0.23.x expects .forward/.backward/.connect methods
                    if name in {"forward", "backward", "connect"}:
                        return lambda *args, **kwargs: None
                    return lambda *args, **kwargs: self

            return Dummy(label)
        return node_class(label)

    with Cluster("CloudWatch Stack"):
        cw_logs = safe_node(CloudwatchLogs, "Logs")
        cw_metrics = safe_node(Cloudwatch, "Metrics")
        cw_alarms = safe_node(CloudwatchAlarm, "Alarms")
        cw_dash = safe_node(Dashboard, "Dashboards")

    with Cluster("Notifications & Triggers"):
        sns_topic = safe_node(SNS, "SNS Alerts")

    with Cluster("Governance & Compliance"):
        config_rules = safe_node(Config, "AWS Config Rules")
        iam_policies = safe_node(IAM, "IAM Roles / Policies / Boundaries")
        # Visualize config-driven extensibility
        config_param = safe_node(SystemsManager, "Compliance Config Param")

    with Cluster("FinOps & Cost Visibility"):
        budgets = safe_node(Budgets, "AWS Budgets")
        cost_exp = safe_node(CostExplorer, "Cost Explorer")

    # Connections
    try:
        cw_logs >> cw_metrics >> cw_alarms >> sns_topic
        cw_metrics >> cw_dash
        config_rules >> iam_policies
        config_param >> config_rules
        [budgets, cost_exp] >> cw_dash
        # Show that alarms/config rules are exported for use by other stacks (visual only)
        cw_alarms >> config_param
    except Exception as e:
        print(f"Diagram connection error: {e}")
