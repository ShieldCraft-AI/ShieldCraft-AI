"""
EventBridgeStack
"""

from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as _lambda,
    CfnOutput,
    Stack,
    Fn,
)
from constructs import Construct
from infra.utils.config_loader import get_config_loader


class EventBridgeStack(Stack):
    """
    Provisions AWS EventBridge event buses and outputs their ARNs for cross-stack integration.
    Integrate with other stacks by importing these ARNs where event publishing or consumption is required.
    """

    def __init__(
        self, scope: Construct, construct_id: str, config_loader=None, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if config_loader is None:
            config_loader = get_config_loader()
        eb_cfg = config_loader.get("eventbridge")
        # 1. If eventbridge config is missing or either bus name is missing/empty, return early (no error, no resources)
        if not eb_cfg:
            return
        data_bus_name = eb_cfg.get("data_bus_name")
        security_bus_name = eb_cfg.get("security_bus_name")
        # Treat missing, empty, or falsy bus names as missing
        if (
            not data_bus_name
            or not isinstance(data_bus_name, str)
            or not data_bus_name.strip()
        ):
            return
        if (
            not security_bus_name
            or not isinstance(security_bus_name, str)
            or not security_bus_name.strip()
        ):
            return

        lambda_export_name = eb_cfg.get("lambda_export_name")
        event_pattern_source = eb_cfg.get("data_event_source", "shieldcraft.data")

        # 2. If both bus names are present but lambda_ or lambda_export_name is missing, raise ValueError
        lambda_cfg = config_loader.get("lambda_")
        if not lambda_cfg or not lambda_export_name:
            raise ValueError("lambda_ section or lambda_export_name missing in config")

        # 3. If all config is present but the referenced Lambda is missing or lacks an ARN, raise ValueError
        lambda_fn_cfg = None
        for fn in lambda_cfg.get("functions", []):
            if fn.get("id") == lambda_export_name:
                lambda_fn_cfg = fn
                break
        if not lambda_fn_cfg or "arn" not in lambda_fn_cfg:
            raise ValueError(
                f"Lambda '{lambda_export_name}' not found in config or missing ARN"
            )

        # 4. Otherwise, synthesize all resources
        self.data_event_bus = events.EventBus(
            self, "DataEventBus", event_bus_name=data_bus_name
        )
        CfnOutput(
            self,
            "DataEventBusArn",
            value=self.data_event_bus.event_bus_arn,
            export_name="DataEventBusArn",
        )

        self.security_event_bus = events.EventBus(
            self, "SecurityEventBus", event_bus_name=security_bus_name
        )
        CfnOutput(
            self,
            "SecurityEventBusArn",
            value=self.security_event_bus.event_bus_arn,
            export_name="SecurityEventBusArn",
        )

        my_lambda = _lambda.Function.from_function_arn(
            self, "MyLambda", lambda_fn_cfg["arn"]
        )
        data_event_rule = events.Rule(
            self,
            "DataEventRule",
            event_bus=self.data_event_bus,
            event_pattern=events.EventPattern(source=[event_pattern_source]),
            targets=[targets.LambdaFunction(my_lambda)],
        )
        CfnOutput(
            self,
            "DataEventRuleArn",
            value=data_event_rule.rule_arn,
            export_name="DataEventRuleArn",
        )
