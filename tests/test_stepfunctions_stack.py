def test_stack_multiple_state_machines():
    config = {
        "state_machines": [
            {
                "id": "SM1",
                "name": "sm1",
                "role_arn": "arn:aws:iam::123456789012:role/DummyRole1",
                "definition": [{"id": "Pass1", "type": "Pass", "end": True}],
            },
            {
                "id": "SM2",
                "name": "sm2",
                "role_arn": "arn:aws:iam::123456789012:role/DummyRole2",
                "definition": [{"id": "Pass2", "type": "Pass", "end": True}],
            },
        ]
    }
    app = App()
    stack = StepFunctionsStack(app, "TestStack", env_name="dev", config=config)
    template = app.synth().get_stack_by_name("TestStack").template
    resources = template.get("Resources", {})
    sm_resources = [
        r for r in resources.values() if r["Type"] == "AWS::StepFunctions::StateMachine"
    ]
    assert (
        len(sm_resources) == 2
    ), f"Expected 2 state machines, found: {len(sm_resources)}"


def test_stack_missing_definition():
    config = {
        "state_machines": [
            {
                "id": "SM1",
                "name": "sm1",
                "role_arn": "arn:aws:iam::123456789012:role/DummyRole1",
                # No definition key
            },
            {
                "id": "SM2",
                "name": "sm2",
                "role_arn": "arn:aws:iam::123456789012:role/DummyRole2",
                "definition": [],  # Empty definition
            },
        ]
    }
    app = App()
    stack = StepFunctionsStack(app, "TestStack", env_name="dev", config=config)
    template = app.synth().get_stack_by_name("TestStack").template
    resources = template.get("Resources", {})
    sm_resources = [
        r for r in resources.values() if r["Type"] == "AWS::StepFunctions::StateMachine"
    ]
    assert (
        not sm_resources
    ), f"No state machines should be synthesized for missing/empty definitions, found: {sm_resources}"


def test_stack_minimal_pass_state():
    config = {
        "state_machines": [
            {
                "id": "MinimalSM",
                "name": "minimal-sm",
                "role_arn": "arn:aws:iam::123456789012:role/DummyRole",
                "definition": [{"id": "OnlyPass", "type": "Pass", "end": True}],
            }
        ]
    }
    app = App()
    stack = StepFunctionsStack(app, "TestStack", env_name="dev", config=config)
    template = app.synth().get_stack_by_name("TestStack").template
    resources = template.get("Resources", {})
    sm_resources = [
        r for r in resources.values() if r["Type"] == "AWS::StepFunctions::StateMachine"
    ]
    assert sm_resources, "Minimal Pass state machine not synthesized"
    definition = sm_resources[0]["Properties"]["DefinitionString"]

    def flatten_join(parts):
        out = []
        for p in parts:
            if isinstance(p, str):
                out.append(p)
            elif isinstance(p, dict):
                out.append(str(p))
            elif isinstance(p, list):
                out.append(flatten_join(p))
            else:
                out.append(str(p))
        return "".join(out)

    if isinstance(definition, dict) and "Fn::Join" in definition:
        joined = flatten_join(definition["Fn::Join"][1])
    else:
        joined = definition
    assert "OnlyPass" in joined


def test_stack_no_state_machines_key():
    config = {}  # No 'state_machines' key
    app = App()
    stack = StepFunctionsStack(app, "TestStack", env_name="dev", config=config)
    template = app.synth().get_stack_by_name("TestStack").template
    resources = template.get("Resources", {})
    sm_resources = [
        r for r in resources.values() if r["Type"] == "AWS::StepFunctions::StateMachine"
    ]
    assert (
        not sm_resources
    ), "No state machines should be synthesized if 'state_machines' key is missing"


def test_stack_advanced_features():
    config = {
        "state_machines": [
            {
                "id": "AdvSM",
                "name": "adv-sm",
                "role_arn": "arn:aws:iam::123456789012:role/DummyRole",
                "definition": [
                    {
                        "id": "Task1",
                        "type": "Task",
                        "resource": "arn:aws:lambda:af-south-1:123456789012:function:DummyFn",
                        "next": "Choice1",
                        "retry": [
                            {
                                "interval_seconds": 2,
                                "max_attempts": 3,
                                "backoff_rate": 2.0,
                            }
                        ],
                        "catch": [{"handler": "FailState", "errors": ["States.ALL"]}],
                    },
                    {
                        "id": "Choice1",
                        "type": "Choice",
                        "choices": [
                            {
                                "condition": "string_equals",
                                "args": ["$.result", "OK"],
                                "next": "Parallel1",
                            },
                            {
                                "condition": "string_equals",
                                "args": ["$.result", "FAIL"],
                                "next": "FailState",
                            },
                        ],
                        "default": "FailState",
                    },
                    {
                        "id": "Parallel1",
                        "type": "Parallel",
                        "branches": [
                            [{"id": "PassA", "type": "Pass", "end": True}],
                            [{"id": "PassB", "type": "Pass", "end": True}],
                        ],
                        "next": "Success",
                    },
                    {"id": "Success", "type": "Pass", "end": True},
                    {"id": "FailState", "type": "Pass", "end": True},
                ],
            }
        ]
    }
    app = App()
    stack = StepFunctionsStack(app, "TestStack", env_name="dev", config=config)
    template = app.synth().get_stack_by_name("TestStack").template
    resources = template.get("Resources", {})
    sm_resources = [
        r for r in resources.values() if r["Type"] == "AWS::StepFunctions::StateMachine"
    ]
    assert sm_resources, "Advanced state machine not synthesized"
    definition = sm_resources[0]["Properties"]["DefinitionString"]

    def flatten_join(parts):
        out = []
        for p in parts:
            if isinstance(p, str):
                out.append(p)
            elif isinstance(p, dict):
                out.append(str(p))
            elif isinstance(p, list):
                out.append(flatten_join(p))
            else:
                out.append(str(p))
        return "".join(out)

    if isinstance(definition, dict) and "Fn::Join" in definition:
        joined = flatten_join(definition["Fn::Join"][1])
    else:
        joined = definition
    for state_name in [
        "Task1",
        "Choice1",
        "Parallel1",
        "PassA",
        "PassB",
        "Success",
        "FailState",
    ]:
        assert (
            state_name in joined
        ), f"State '{state_name}' not found in definition: {joined}"


"""
Unit tests for StepFunctionsStack config-driven synthesis.
"""

import pytest
from aws_cdk import App, Stack
from infra.stacks.stepfunctions_stack import StepFunctionsStack
from infra.utils.config_loader import ConfigLoader
import infra.utils.config_loader as config_loader_mod


def test_stack_synthesizes_state_machine(monkeypatch):
    # Minimal config with one Task state
    config = {
        "state_machines": [
            {
                "id": "TestSM",
                "name": "test-sm",
                "role_arn": "arn:aws:iam::123456789012:role/DummyRole",
                "definition": [
                    {
                        "id": "Task1",
                        "type": "Task",
                        "resource": "arn:aws:lambda:af-south-1:123456789012:function:DummyFn",
                        "next": "Wait1",
                    },
                    {
                        "id": "Wait1",
                        "type": "Wait",
                        "seconds": 5,
                        "next": "Pass1",
                    },
                    {
                        "id": "Pass1",
                        "type": "Pass",
                        "next": "Choice1",
                    },
                    {
                        "id": "Choice1",
                        "type": "Choice",
                        "choices": [
                            {
                                "condition": "string_equals",
                                "args": ["$.result", "OK"],
                                "next": "Success",
                            },
                            {
                                "condition": "string_equals",
                                "args": ["$.result", "FAIL"],
                                "next": "FailState",
                            },
                        ],
                        "default": "FailState",
                    },
                    {
                        "id": "Success",
                        "type": "Pass",
                        "end": True,
                    },
                    {
                        "id": "FailState",
                        "type": "Pass",
                        "end": True,
                    },
                ],
            }
        ]
    }

    app = App()
    stack = StepFunctionsStack(app, "TestStack", env_name="dev", config=config)
    template = app.synth().get_stack_by_name("TestStack").template
    resources = template.get("Resources", {})
    sm_resources = [
        r for r in resources.values() if r["Type"] == "AWS::StepFunctions::StateMachine"
    ]
    assert sm_resources, "No State Machine synthesized"
    definition = sm_resources[0]["Properties"]["DefinitionString"]

    def flatten_join(parts):
        out = []
        for p in parts:
            if isinstance(p, str):
                out.append(p)
            elif isinstance(p, dict):
                out.append(str(p))
            elif isinstance(p, list):
                out.append(flatten_join(p))
            else:
                out.append(str(p))
        return "".join(out)

    if isinstance(definition, dict) and "Fn::Join" in definition:
        joined = flatten_join(definition["Fn::Join"][1])
    else:
        joined = definition
    for state_name in ["Wait1", "Pass1", "Choice1", "Success", "FailState"]:
        assert (
            state_name in joined
        ), f"State '{state_name}' not found in definition: {joined}"


def test_stack_handles_no_state_machines():
    # Empty config
    config = {}
    app = App()
    stack = StepFunctionsStack(app, "TestStack", env_name="dev", config=config)
    template = app.synth().get_stack_by_name("TestStack").template
    resources = template.get("Resources", {})
    sm_resources = [
        r for r in resources.values() if r["Type"] == "AWS::StepFunctions::StateMachine"
    ]
    assert (
        not sm_resources
    ), f"State Machine should not be synthesized for empty config, found: {sm_resources}"
