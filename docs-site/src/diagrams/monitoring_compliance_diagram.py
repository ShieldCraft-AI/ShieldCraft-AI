from diagrams import Cluster, Diagram
from diagrams.aws.management import Cloudwatch, CloudwatchLogs, CloudwatchAlarm, Config
from diagrams.aws.security import IAM
from diagrams.aws.notifications import SNS
from diagrams.aws.billing import Budgets, CostExplorer
from diagrams.generic.monitoring import Dashboard

with Diagram(
    "Monitoring, Compliance & Hardening Architecture", direction="TB", show=False
):
    with Cluster("CloudWatch Stack"):
        cw_logs = CloudwatchLogs("Logs")
        cw_metrics = Cloudwatch("Metrics")
        cw_alarms = CloudwatchAlarm("Alarms")
        cw_dash = Dashboard("Dashboards")

    with Cluster("Notifications & Triggers"):
        sns_topic = SNS("SNS Alerts")

    with Cluster("Governance & Compliance"):
        config_rules = Config("AWS Config Rules")
        iam_policies = IAM("IAM Roles / Policies / Boundaries")

    with Cluster("FinOps & Cost Visibility"):
        budgets = Budgets("AWS Budgets")
        cost_exp = CostExplorer("Cost Explorer")

    # Connections
    cw_logs >> cw_metrics >> cw_alarms >> sns_topic
    cw_metrics >> cw_dash
    config_rules >> iam_policies
    [budgets, cost_exp] >> cw_dash
