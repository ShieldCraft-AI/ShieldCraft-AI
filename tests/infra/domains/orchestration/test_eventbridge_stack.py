import pytest
from unittest.mock import patch
import aws_cdk as core
import aws_cdk.assertions as assertions
from infra.domains.orchestration.eventbridge_stack import EventBridgeStack
from infra.utils.config_loader import get_config_loader


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_no_eventbridge_config(mock_get_config_loader):
    # No eventbridge config: stack should not synthesize any EventBus
    test_config = {
        "eventbridge": {"lambda_export_name": "DevMskTopicCreatorLambdaArn"},
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    stack = EventBridgeStack(
        app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
    )
    template = assertions.Template.from_stack(stack)
    resources = template.to_json().get("Resources", {})
    assert (
        not resources
    ), "No resources should be synthesized if eventbridge config is missing"


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_missing_lambda_section(mock_get_config_loader):
    # eventbridge config present, but lambda_ section missing
    test_config = {
        "eventbridge": {
            "data_bus_name": "test-data-bus",
            "security_bus_name": "test-security-bus",
            "lambda_export_name": "DevMskTopicCreatorLambdaArn",
            "data_event_source": "test.source",
        }
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    with pytest.raises(
        ValueError, match="lambda_ section or lambda_export_name missing in config"
    ):
        EventBridgeStack(
            app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
        )


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_missing_lambda_export_name(mock_get_config_loader):
    # eventbridge config present, lambda_ present, but lambda_export_name missing
    test_config = {
        "eventbridge": {
            "data_bus_name": "test-data-bus",
            "security_bus_name": "test-security-bus",
            # no lambda_export_name
            "data_event_source": "test.source",
        },
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    with pytest.raises(
        ValueError, match="lambda_ section or lambda_export_name missing in config"
    ):
        EventBridgeStack(
            app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
        )


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_missing_lambda_arn(mock_get_config_loader):
    # eventbridge config present, lambda_ present, lambda_export_name present, but no arn
    test_config = {
        "eventbridge": {
            "data_bus_name": "test-data-bus",
            "security_bus_name": "test-security-bus",
            "lambda_export_name": "DevMskTopicCreatorLambdaArn",
            "data_event_source": "test.source",
        },
        "lambda_": {"functions": [{"id": "DevMskTopicCreatorLambdaArn"}]},  # no arn
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    with pytest.raises(ValueError, match="not found in config or missing ARN"):
        EventBridgeStack(
            app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
        )


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_multiple_buses(mock_get_config_loader):
    # Test that multiple event buses are synthesized and outputs are present
    test_config = {
        "eventbridge": {
            "data_bus_name": "bus1",
            "security_bus_name": "bus2",
            "lambda_export_name": "DevMskTopicCreatorLambdaArn",
            "data_event_source": "test.source",
        },
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    stack = EventBridgeStack(
        app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
    )
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties("AWS::Events::EventBus", {"Name": "bus1"})
    template.has_resource_properties("AWS::Events::EventBus", {"Name": "bus2"})
    outputs = template.to_json().get("Outputs", {})
    assert "DataEventBusArn" in outputs
    assert "SecurityEventBusArn" in outputs


import aws_cdk as core
import aws_cdk.assertions as assertions

from infra.domains.orchestration.eventbridge_stack import EventBridgeStack
from infra.utils.config_loader import get_config_loader


import pytest
from unittest.mock import patch


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_resources(mock_get_config_loader):
    # Minimal deterministic config for EventBridgeStack
    test_config = {
        "eventbridge": {
            "data_bus_name": "test-data-bus",
            "security_bus_name": "test-security-bus",
            "lambda_export_name": "DevMskTopicCreatorLambdaArn",
            "data_event_source": "test.source",
        },
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)

    app = core.App()
    stack = EventBridgeStack(
        app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
    )
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::Events::EventBus", {"Name": "test-data-bus"})
    template.has_resource_properties(
        "AWS::Events::EventBus", {"Name": "test-security-bus"}
    )

    # Check outputs dynamically
    outputs = template.to_json().get("Outputs", {})
    assert "DataEventBusArn" in outputs
    assert "SecurityEventBusArn" in outputs
    assert "DataEventRuleArn" in outputs

    # Find the AWS::Events::Rule resource and check EventPattern contains the expected source
    rules = template.find_resources("AWS::Events::Rule")
    assert rules, "No AWS::Events::Rule resources found"
    found = False
    for rule in rules.values():
        pattern = rule["Properties"].get("EventPattern", {})
        if isinstance(pattern, str):
            import json

            pattern = json.loads(pattern)
        sources = pattern.get("source", [])
        if "test.source" in sources:
            found = True
            break
    assert (
        found
    ), f"No EventBridge Rule with source test.source found. Actual patterns: {[r['Properties'].get('EventPattern', {}) for r in rules.values()]}"


# --- Supplemental Tests for EventBridgeStack ---


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_missing_both_bus_names(mock_get_config_loader):
    # Both bus names missing: no resources
    test_config = {
        "eventbridge": {"lambda_export_name": "DevMskTopicCreatorLambdaArn"},
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    stack = EventBridgeStack(
        app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
    )
    template = assertions.Template.from_stack(stack)
    assert not template.to_json().get("Resources", {})


@patch("infra.utils.config_loader.get_config_loader")
@pytest.mark.parametrize(
    "data_bus,security_bus",
    [
        ("", "bus2"),
        (None, "bus2"),
        ("bus1", ""),
        ("bus1", None),
        ("   ", "bus2"),
        ("bus1", "   "),
    ],
)
def test_eventbridge_stack_one_bus_missing(
    mock_get_config_loader, data_bus, security_bus
):
    # Only one bus name present or valid: no resources
    test_config = {
        "eventbridge": {
            "data_bus_name": data_bus,
            "security_bus_name": security_bus,
            "lambda_export_name": "DevMskTopicCreatorLambdaArn",
        },
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    stack = EventBridgeStack(
        app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
    )
    template = assertions.Template.from_stack(stack)
    assert not template.to_json().get("Resources", {})


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_empty_lambda_functions(mock_get_config_loader):
    # lambda_ present, but functions list empty
    test_config = {
        "eventbridge": {
            "data_bus_name": "bus1",
            "security_bus_name": "bus2",
            "lambda_export_name": "DevMskTopicCreatorLambdaArn",
        },
        "lambda_": {"functions": []},
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    with pytest.raises(ValueError, match="not found in config or missing ARN"):
        EventBridgeStack(
            app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
        )


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_no_matching_lambda_id(mock_get_config_loader):
    # lambda_ present, functions present, but no function matches lambda_export_name
    test_config = {
        "eventbridge": {
            "data_bus_name": "bus1",
            "security_bus_name": "bus2",
            "lambda_export_name": "NonExistentLambda",
        },
        "lambda_": {
            "functions": [
                {
                    "id": "SomeOtherLambda",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:SomeOtherLambda",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    with pytest.raises(ValueError, match="not found in config or missing ARN"):
        EventBridgeStack(
            app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
        )


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_missing_eventbridge_section(mock_get_config_loader):
    # eventbridge config missing entirely
    test_config = {
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    stack = EventBridgeStack(
        app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
    )
    template = assertions.Template.from_stack(stack)
    assert not template.to_json().get("Resources", {})


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_extra_irrelevant_keys(mock_get_config_loader):
    # Extra keys in config should not break stack
    test_config = {
        "eventbridge": {
            "data_bus_name": "bus1",
            "security_bus_name": "bus2",
            "lambda_export_name": "DevMskTopicCreatorLambdaArn",
            "irrelevant": "foo",
        },
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                },
                {
                    "id": "OtherLambda",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:OtherLambda",
                },
            ],
            "extra": 123,
        },
        "foo": {"bar": 1},
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    stack = EventBridgeStack(
        app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
    )
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties("AWS::Events::EventBus", {"Name": "bus1"})
    template.has_resource_properties("AWS::Events::EventBus", {"Name": "bus2"})
    outputs = template.to_json().get("Outputs", {})
    assert "DataEventBusArn" in outputs
    assert "SecurityEventBusArn" in outputs


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_missing_event_pattern_source(mock_get_config_loader):
    # event_pattern_source missing: should default
    test_config = {
        "eventbridge": {
            "data_bus_name": "bus1",
            "security_bus_name": "bus2",
            "lambda_export_name": "DevMskTopicCreatorLambdaArn",
        },
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app = core.App()
    stack = EventBridgeStack(
        app, "TestEventBridgeStack", config_loader=DummyLoader(test_config)
    )
    template = assertions.Template.from_stack(stack)
    # Should have default event pattern source
    rules = template.find_resources("AWS::Events::Rule")
    found = False
    for rule in rules.values():
        pattern = rule["Properties"].get("EventPattern", {})
        if isinstance(pattern, str):
            import json

            pattern = json.loads(pattern)
        sources = pattern.get("source", [])
        if "shieldcraft.data" in sources:
            found = True
            break
    assert found, "Default event pattern source not set"


@patch("infra.utils.config_loader.get_config_loader")
def test_eventbridge_stack_determinism(mock_get_config_loader):
    # Repeated runs with same config yield same template
    test_config = {
        "eventbridge": {
            "data_bus_name": "bus1",
            "security_bus_name": "bus2",
            "lambda_export_name": "DevMskTopicCreatorLambdaArn",
            "data_event_source": "test.source",
        },
        "lambda_": {
            "functions": [
                {
                    "id": "DevMskTopicCreatorLambdaArn",
                    "arn": "arn:aws:lambda:us-east-1:123456789012:function:DevMskTopicCreatorLambdaArn",
                }
            ]
        },
    }

    class DummyLoader:
        def __init__(self, config):
            self.config = config

        def get(self, key, default=None):
            keys = key.split(".")
            val = self.config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    mock_get_config_loader.return_value = DummyLoader(test_config)
    app1 = core.App()
    app2 = core.App()
    stack1 = EventBridgeStack(app1, "Stack1", config_loader=DummyLoader(test_config))
    stack2 = EventBridgeStack(app2, "Stack2", config_loader=DummyLoader(test_config))
    template1 = assertions.Template.from_stack(stack1).to_json()
    template2 = assertions.Template.from_stack(stack2).to_json()
    assert template1 == template2, "Synthesized templates differ for same config"
