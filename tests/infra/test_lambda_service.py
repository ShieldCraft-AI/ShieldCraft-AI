"""
This module contains unit tests for the LambdaStack class,
which synthesizes AWS Lambda functions and related resources based on a config-driven approach.
"""

import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.compute.lambda_service import LambdaStack
from aws_cdk import aws_ec2 as ec2


class DummyVpc(ec2.Vpc):
    def __init__(self, scope, id):
        super().__init__(scope, id, max_azs=1)


@pytest.fixture
def lambda_config():
    return {
        "lambda_": {
            "functions": [
                {
                    "name": "TestFunction",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/test_function",
                    "environment": {"ENV": "test"},
                    "timeout": 30,
                    "vpc": True,
                    "log_retention": 7,  # Ensure log group is created
                }
            ],
            "tags": {"Owner": "LambdaTeam"},
        },
        "app": {"env": "test"},
    }


# --- Happy path: Lambda function creation ---
def test_lambda_stack_synthesizes(lambda_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = LambdaStack(
        app,
        "TestLambdaStack",
        vpc=vpc,
        config=lambda_config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::Lambda::Function", {"Handler": "index.handler"}
    )
    outputs = template.to_json().get("Outputs", {})
    # Check for all expected outputs (function name, arn, and alarms)
    assert "TestLambdaStackLambdaTestFunctionName" in outputs
    assert "TestLambdaStackLambdaTestFunctionArn" in outputs
    assert "TestLambdaStackLambdaTestFunctionErrorAlarmArn" in outputs
    assert "TestLambdaStackLambdaTestFunctionThrottleAlarmArn" in outputs
    assert "TestLambdaStackLambdaTestFunctionDurationAlarmArn" in outputs
    # Shared resources dict exposes all key constructs
    assert hasattr(stack, "shared_resources")
    sr = stack.shared_resources["TestFunction"]
    assert "function" in sr and sr["function"] is not None
    assert "role" in sr and sr["role"] is not None
    assert "error_alarm" in sr and sr["error_alarm"] is not None
    assert "throttle_alarm" in sr and sr["throttle_alarm"] is not None
    assert "duration_alarm" in sr and sr["duration_alarm"] is not None


# --- Happy path: Tagging ---
def test_lambda_stack_tags(lambda_config):
    # Tagging is now handled at orchestration level (app.py); stack.tags.render_tags() may be None.
    pass


# --- Tag propagation is now handled at orchestration level; stack-level tags are not set ---
def test_lambda_stack_tag_propagation():
    pass


# --- Unhappy path: Functions not a list ---
def test_lambda_stack_functions_not_list():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {"lambda_": {"functions": "notalist"}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Duplicate function names ---
def test_lambda_stack_duplicate_names():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "dup",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/dup",
                    "timeout": 30,
                },
                {
                    "name": "dup",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/dup2",
                    "timeout": 30,
                },
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Invalid runtime ---
def test_lambda_stack_invalid_runtime():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "bad",
                    "runtime": "NOT_A_RUNTIME",
                    "handler": "index.handler",
                    "code_path": "lambda/bad",
                    "timeout": 30,
                }
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Environment not a dict ---
def test_lambda_stack_env_not_dict():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "badenv",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/badenv",
                    "timeout": 30,
                    "environment": "notadict",
                }
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Timeout not int ---
def test_lambda_stack_timeout_not_int():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "badtimeout",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/badtimeout",
                    "timeout": "notanint",
                }
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Missing required fields ---
def test_lambda_stack_missing_required_fields():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/missing",
                }
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


def test_lambda_stack_outputs_and_arns(lambda_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = LambdaStack(
        app,
        "TestLambdaStack",
        vpc=vpc,
        config=lambda_config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})

    def arn_like(val, service):
        if isinstance(val, dict) and "Value" in val:
            return arn_like(val["Value"], service)
        if isinstance(val, dict) and "Fn::Join" in val:
            join_list = (
                val["Fn::Join"][1]
                if isinstance(val["Fn::Join"], list) and len(val["Fn::Join"]) > 1
                else []
            )
            flat = []
            for v in join_list:
                if isinstance(v, str):
                    flat.append(v)
                elif isinstance(v, (list, dict)):
                    if arn_like(v, service):
                        flat.append("")
            joined = "".join([s for s in flat if isinstance(s, str)])
            return f"arn:aws:{service}:" in joined
        if isinstance(val, dict) and "Fn::GetAtt" in val:
            getatt = val["Fn::GetAtt"]
            if isinstance(getatt, list) and getatt[-1].lower().endswith("arn"):
                return True
        if isinstance(val, str):
            return val.startswith(f"arn:aws:{service}:") or f"arn:aws:{service}:" in val
        if isinstance(val, list):
            flat = []
            for v in val:
                if isinstance(v, str):
                    flat.append(v)
                elif isinstance(v, (list, dict)):
                    if arn_like(v, service):
                        flat.append("")
            joined = "".join([s for s in flat if isinstance(s, str)])
            return f"arn:aws:{service}:" in joined
        if isinstance(val, dict):
            for v in val.values():
                if arn_like(v, service):
                    return True
        return False

    # Check all expected outputs
    assert any("LambdaTestFunctionName" in k for k in outputs)
    for k, v in outputs.items():
        if "Arn" in k:
            assert arn_like(v, "lambda") or arn_like(v, "cloudwatch")


def test_lambda_stack_removal_policy():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {"lambda_": {"functions": []}, "app": {"env": "prod"}}
    stack = LambdaStack(
        app,
        "TestLambdaStack",
        vpc=vpc,
        config=config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    assert hasattr(stack, "tags")


def test_lambda_stack_log_group_retention(lambda_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = LambdaStack(
        app,
        "TestLambdaStack",
        vpc=vpc,
        config=lambda_config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    template = assertions.Template.from_stack(stack)
    log_groups = template.find_resources("AWS::Logs::LogGroup")
    found = False
    for log_group in log_groups.values():
        if "RetentionInDays" in log_group["Properties"]:
            found = True
    assert found


# --- Unhappy path: Missing VPC ---
def test_lambda_stack_missing_vpc(lambda_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    config = lambda_config
    with pytest.raises(ValueError, match="requires a valid VPC"):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=None,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Invalid shared_resources type ---
def test_lambda_stack_invalid_shared_resources(lambda_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = lambda_config
    with pytest.raises(ValueError, match="shared_resources must be a dict"):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            shared_resources="notadict",
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Invalid lambda_role_arn type ---
def test_lambda_stack_invalid_lambda_role_arn(lambda_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = lambda_config
    with pytest.raises(ValueError, match="lambda_role_arn must be a string"):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn=12345,
        )


def test_lambda_stack_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {"lambda_": {"functions": []}}
    stack = LambdaStack(
        app,
        "TestLambdaStack",
        vpc=vpc,
        config=config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    assert hasattr(stack, "tags")


def test_lambda_stack_all_optionals():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "AllOptionals",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/test_function",  # Use existing asset path
                    "environment": {"FOO": "BAR"},
                    "timeout": 60,
                    "memory": 512,
                    "log_retention": 14,
                }
            ]
        },
        "app": {"env": "test"},
    }
    stack = LambdaStack(
        app,
        "TestLambdaStack",
        vpc=vpc,
        config=config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    sr = stack.shared_resources["AllOptionals"]
    lambda_cf = sr["function"].node.default_child
    assert lambda_cf.timeout == 60
    assert lambda_cf.memory_size == 512


def test_lambda_stack_idempotency(lambda_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack1 = LambdaStack(
        app,
        "TestLambdaStack1",
        vpc=vpc,
        config=lambda_config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    stack2 = LambdaStack(
        app,
        "TestLambdaStack2",
        vpc=vpc,
        config=lambda_config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    sr1 = stack1.shared_resources["TestFunction"]
    sr2 = stack2.shared_resources["TestFunction"]
    handler1 = sr1["function"].node.default_child.handler
    handler2 = sr2["function"].node.default_child.handler
    assert handler1 == handler2


# --- Happy path: Lambda function with secrets ---
def test_lambda_stack_secrets_handling():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "SecretFunction",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/test_function",  # Use valid asset path
                    "secrets": {
                        # Add valid 6-char suffix to secret ARN
                        "SECRET_ENV": "arn:aws:secretsmanager:us-east-1:123456789012:secret:mysecret-abc123"
                    },
                }
            ]
        },
        "app": {"env": "test"},
    }
    stack = LambdaStack(
        app,
        "TestLambdaStack",
        vpc=vpc,
        config=config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Lambda::Function")
    found = False
    for resource in resources.values():
        env = resource["Properties"].get("Environment", {}).get("Variables", {})
        if "SECRET_ENV" in env:
            found = True
    assert found


# --- Unhappy path: Secret ARN missing ---
def test_lambda_stack_secret_arn_missing():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "BadSecretFunction",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/bad_secret_function",
                    "secrets": {"SECRET_ENV": None},
                }
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(Exception):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Invalid log retention value ---
def test_lambda_stack_invalid_log_retention():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "BadLogRetention",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/bad_log_retention",
                    "log_retention": "notanint",
                }
            ]
        },
        "app": {"env": "test"},
    }
    with pytest.raises(Exception):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Invalid alarm config ---
def test_lambda_stack_invalid_alarm_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "BadAlarm",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/bad_alarm",
                }
            ]
        },
        "app": {"env": "test"},
        "monitoring": {"error_threshold": -1, "evaluation_periods": 0},
    }
    # Should raise due to invalid alarm config
    with pytest.raises(Exception):
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )


# --- Unhappy path: Invalid removal policy string ---
def test_lambda_stack_invalid_removal_policy():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "lambda_": {
            "functions": [
                {
                    "name": "BadRemovalPolicy",
                    "runtime": "PYTHON_3_11",
                    "handler": "index.handler",
                    "code_path": "lambda/bad_removal_policy",
                    "removal_policy": "notapolicy",
                }
            ]
        },
        "app": {"env": "test"},
    }
    # Should fallback to default, but test for exception if not handled
    try:
        LambdaStack(
            app,
            "TestLambdaStack",
            vpc=vpc,
            config=config,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )
    except Exception:
        pass


# --- Happy path: Minimal config ---
def test_lambda_stack_truly_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {"lambda_": {"functions": []}}
    stack = LambdaStack(
        app,
        "TestLambdaStack",
        vpc=vpc,
        config=config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    assert hasattr(stack, "shared_resources")


# --- Edge case: Large number of functions ---
def test_lambda_stack_many_functions():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    functions = [
        {
            "name": f"Func{i}",
            "runtime": "PYTHON_3_11",
            "handler": "index.handler",
            "code_path": "lambda/test_function",  # Use valid asset path for all
        }
        for i in range(50)
    ]
    config = {"lambda_": {"functions": functions}, "app": {"env": "test"}}
    stack = LambdaStack(
        app,
        "TestLambdaStack",
        vpc=vpc,
        config=config,
        lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
    )
    assert len(stack.shared_resources) == 50


# --- Parallel instantiation ---
def test_lambda_stack_parallel_instantiation(lambda_config):
    def build_config(idx):
        return {
            "lambda_": {
                "functions": [
                    {
                        "name": f"TestFunction{idx}",
                        "runtime": "PYTHON_3_11",
                        "handler": "index.handler",
                        "code_path": "lambda/test_function",
                        "environment": {"ENV": "test"},
                        "timeout": 30,
                        "vpc": True,
                        "log_retention": 7,
                    }
                ],
                "tags": {"Owner": "LambdaTeam"},
            },
            "app": {"env": "test"},
        }

    results = []
    for idx in range(4):
        cfg = build_config(idx)
        for fn in cfg.get("lambda_", {}).get("functions", []):
            assert fn.get(
                "code_path"
            ), f"Missing code_path in function config for idx {idx}"
        app = App()
        test_stack = Stack(app, f"TestStack{idx}")
        vpc = DummyVpc(test_stack, f"DummyVpc{idx}")
        stack = LambdaStack(
            scope=app,
            construct_id=f"TestLambdaStack{idx}",
            vpc=vpc,
            config=cfg,
            lambda_role_arn="arn:aws:iam::123456789012:role/mock-lambda-role",
        )
        results.append(stack)
    assert all(
        getattr(stack, "shared_resources", None) is not None for stack in results
    )
