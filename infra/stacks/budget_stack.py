"""
ShieldCraftAI BudgetStack: AWS Budgets integration for cost monitoring and alerting.
"""

from typing import Optional  # pylint: disable=unused-import
from constructs import Construct  # pylint: disable=unused-import
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_budgets as budgets,
    aws_secretsmanager as secretsmanager,
    aws_sns as sns,
)


class BudgetStack(Stack):
    """
    CDK Stack for AWS Budgets, SNS notifications, and cross-stack secret integration.
    """

    def __init__(self, scope, construct_id, *args, **kwargs):
        """
        CDK Stack for AWS Budgets, SNS notifications, and cross-stack secret integration.
        """
        import logging

        # Only pass CDK-supported args to super().__init__
        stack_args = {}
        for k in ("env", "tags", "description"):
            if k in kwargs:
                stack_args[k] = kwargs[k]
        super().__init__(scope, construct_id, **stack_args)

        budget_limit = kwargs.get("budget_limit", 50)
        email_address = kwargs.get("email_address", None)
        sns_topic_arn = kwargs.get("sns_topic_arn", None)
        create_sns_topic = kwargs.get("create_sns_topic", False)
        secrets_manager_arn = kwargs.get("secrets_manager_arn", None)
        notification_thresholds = kwargs.get("notification_thresholds", [80, 100])
        stack_tags = kwargs.get(
            "tags",
            {"Project": "ShieldCraftAI", "Environment": "prod", "Owner": "FinOps"},
        )
        # Set stack-level tags for auditability
        for k, v in stack_tags.items():
            self.tags.set_tag(k, v)
        try:
            self._validate_cross_stack_resources(
                budget_limit, email_address, sns_topic_arn, create_sns_topic
            )
        except Exception as e:
            logging.error(f"BudgetStack config error: {e}")
            raise
        # Vault integration: import the main secrets manager secret if provided
        self.secrets_manager_arn = secrets_manager_arn
        self.secrets_manager_secret = None
        self.shared_resources = {}
        if self.secrets_manager_arn:
            self.secrets_manager_secret = (
                secretsmanager.Secret.from_secret_complete_arn(
                    self, "ImportedVaultSecret", self.secrets_manager_arn
                )
            )
            CfnOutput(
                self,
                f"{construct_id}VaultSecretArn",
                value=self.secrets_manager_arn,
                export_name=f"{construct_id}-vault-secret-arn",
            )
            self.shared_resources["vault_secret"] = self.secrets_manager_secret

        if create_sns_topic:
            topic = sns.Topic(self, "BudgetAlertsTopic")
            topic.apply_removal_policy(self._get_removal_policy(kwargs))
            # Propagate stack tags to SNS topic
            for k, v in stack_tags.items():
                self.tags.set_tag(k, v)
        elif sns_topic_arn:
            topic = sns.Topic.from_topic_arn(self, "BudgetSNSTopic", sns_topic_arn)
        else:
            topic = None

        subscribers = []
        if email_address:
            subscribers.append(
                budgets.CfnBudget.SubscriberProperty(
                    subscription_type="EMAIL",
                    address=email_address,
                )
            )
        if topic:
            subscribers.append(
                budgets.CfnBudget.SubscriberProperty(
                    subscription_type="SNS",
                    address=topic.topic_arn,
                )
            )

        notifications = []
        for threshold in notification_thresholds:
            notifications.append(
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        notification_type="ACTUAL",
                        comparison_operator="GREATER_THAN",
                        threshold=threshold,
                        threshold_type="PERCENTAGE",
                    ),
                    subscribers=subscribers,
                )
            )

        budget_resource = budgets.CfnBudget(
            self,
            "ShieldCraftBudget",
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_type="COST",
                time_unit="MONTHLY",
                budget_limit=budgets.CfnBudget.SpendProperty(
                    amount=budget_limit,
                    unit="USD",
                ),
                budget_name="ShieldCraftAI-Monthly-Budget",
            ),
            notifications_with_subscribers=notifications,
        )
        # Set removal policy for budget resource
        budget_resource.apply_removal_policy(self._get_removal_policy(kwargs))
        # Export budget resource name for cross-stack use
        self._export_resource("BudgetName", "ShieldCraftAI-Monthly-Budget")

        # Output the SNS topic ARN if created
        if create_sns_topic and topic:
            self._export_resource("BudgetAlertsTopicArn", topic.topic_arn)

    def _get_removal_policy(self, kwargs):
        from aws_cdk import RemovalPolicy

        # Default to RETAIN for production safety
        policy = kwargs.get("removal_policy", "RETAIN")
        if isinstance(policy, str):
            return getattr(RemovalPolicy, policy.upper(), RemovalPolicy.RETAIN)
        return RemovalPolicy.RETAIN

    def _validate_cross_stack_resources(
        self, budget_limit, email_address, sns_topic_arn, create_sns_topic
    ):
        """
        Validate budget stack parameters for correctness and completeness.
        Raises ValueError if any required parameter is missing or misconfigured.
        """
        if not isinstance(budget_limit, (int, float)) or budget_limit <= 0:
            raise ValueError("budget_limit must be a positive number.")
        if not email_address and not sns_topic_arn and not create_sns_topic:
            raise ValueError("BudgetStack requires at least one notification target")
        if email_address and (
            not isinstance(email_address, str) or "@" not in email_address
        ):
            raise ValueError(f"Invalid email address: {email_address}")
        if sns_topic_arn and (
            not isinstance(sns_topic_arn, str)
            or not sns_topic_arn.startswith("arn:aws:sns:")
        ):
            raise ValueError(f"Invalid SNS topic ARN: {sns_topic_arn}")

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")
