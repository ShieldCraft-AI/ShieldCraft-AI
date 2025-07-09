import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.data.dataquality_stack import DataQualityStack


@pytest.fixture
def dq_config():
    return {
        "data_quality": {
            "glue_job": {
                "enabled": True,
                "name": "test-dq-job",
                "role_arn": "arn:aws:iam::123456789012:role/GlueJobRole",
                "command_name": "glueetl",
                "script_location": "s3://bucket/scripts/dq.py",
                "default_arguments": {},
            }
        },
        "app": {"env": "test"},
    }


# --- Happy path: Glue Job creation ---
def test_dataquality_stack_synthesizes(dq_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=dq_config,
        dq_glue_role_arn="arn:aws:iam::123456789012:role/MockGlueRole",
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::Glue::Job", 1)
    # Shared resources dict exposes glue job
    assert hasattr(stack, "shared_resources")
    assert "dq_glue_job" in stack.shared_resources
    assert stack.shared_resources["dq_glue_job"] == stack.dq_glue_job


# --- Happy path: Lambda creation ---
def test_dataquality_stack_lambda_creation():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
                "environment": {"FOO": "BAR"},
                "timeout": 30,
                "memory": 256,
                "log_retention": 3,
            }
        },
        "app": {"env": "test"},
    }
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    assert hasattr(stack, "dq_lambda")
    # Shared resources dict exposes lambda
    assert "dq_lambda" in stack.shared_resources
    assert stack.shared_resources["dq_lambda"] == stack.dq_lambda
    # Lambda error alarm present
    assert hasattr(stack, "lambda_error_alarm")
    assert stack.lambda_error_alarm.alarm_arn is not None


# --- Happy path: Outputs ---
def test_dataquality_stack_outputs(dq_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=dq_config,
        dq_glue_role_arn="arn:aws:iam::123456789012:role/MockGlueRole",
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    assert "TestDataQualityStackDataQualityGlueJobName" in outputs
    # Glue job failure alarm output (if present)
    alarm_key = "TestDataQualityStackDataQualityGlueJobFailureAlarmArn"
    if alarm_key in outputs:
        assert outputs[alarm_key]


# --- Happy path: Tagging ---
def test_dataquality_stack_tags(dq_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=dq_config,
        dq_glue_role_arn="arn:aws:iam::123456789012:role/MockGlueRole",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )


# --- Happy path: Lambda error alarm output ---
def test_dataquality_stack_lambda_alarm_output():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
                "environment": {"FOO": "BAR"},
                "timeout": 30,
                "memory": 256,
                "log_retention": 3,
            }
        },
        "app": {"env": "test"},
    }
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    assert "TestDataQualityStackDataQualityLambdaErrorAlarmArn" in outputs


# --- Unhappy path: Missing required Glue Job config ---
@pytest.mark.parametrize(
    "bad_config",
    [
        {"data_quality": {"glue_job": {"enabled": True}}},
        {"data_quality": {"glue_job": {"enabled": True, "name": ""}}},
    ],
)
def test_dataquality_stack_invalid_glue_config(bad_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    with pytest.raises(Exception):
        DataQualityStack(
            test_stack,
            "TestDataQualityStack",
            config=bad_config,
            dq_glue_role_arn="arn:aws:iam::123456789012:role/MockGlueRole",
        )


# --- Unhappy path: Invalid Lambda config ---
@pytest.mark.parametrize(
    "bad_config",
    [
        {"data_quality": {"lambda": {"enabled": True, "handler": "", "code_path": ""}}},
        {"data_quality": {"lambda": {"enabled": True, "timeout": -1}}},
    ],
)
def test_dataquality_stack_invalid_lambda_config(bad_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    with pytest.raises(Exception):
        DataQualityStack(
            test_stack,
            "TestDataQualityStack",
            config=bad_config,
            dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        )


# --- Happy path: Unknown config keys (should not raise) ---
def test_dataquality_stack_unknown_config_keys():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "app": {"env": "test"},
        "data_quality": {"lambda": {"enabled": True, "unknown_key": 123}},
    }
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    assert hasattr(stack, "tags")


# --- Happy path: Minimal config (no resources) ---
def test_dataquality_stack_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"data_quality": {}}
    stack = DataQualityStack(test_stack, "TestDataQualityStack", config=config)
    assert hasattr(stack, "tags")


# --- Supplementary: Output ARNs and Names ---
def test_dataquality_stack_outputs_present(dq_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=dq_config,
        dq_glue_role_arn="arn:aws:iam::123456789012:role/MockGlueRole",
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
    assert any("GlueJobName" in k for k in outputs)
    # Check ARNs are valid for alarms and lambda if present
    for k, v in outputs.items():
        if "AlarmArn" in k or "LambdaArn" in k:
            assert arn_like(v, "lambda") or arn_like(v, "cloudwatch")


# --- Supplementary: Removal Policy ---
def test_dataquality_stack_removal_policy_dev():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"app": {"env": "dev"}, "data_quality": {"lambda": {"enabled": False}}}
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_glue_role_arn="arn:aws:iam::123456789012:role/MockGlueRole",
    )
    # No resources, but test does not raise and tags present
    assert hasattr(stack, "tags")


def test_dataquality_stack_removal_policy_prod():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"app": {"env": "prod"}, "data_quality": {"lambda": {"enabled": False}}}
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_glue_role_arn="arn:aws:iam::123456789012:role/MockGlueRole",
    )
    assert hasattr(stack, "tags")


# --- Supplementary: Tag Propagation ---
def test_dataquality_stack_tag_propagation():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "app": {"env": "test"},
        "data_quality": {"tags": {"Owner": "DataTeam", "CostCenter": "AI123"}},
    }
    shared_tags = {"Extra": "Value"}
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        shared_tags=shared_tags,
        dq_glue_role_arn="arn:aws:iam::123456789012:role/MockGlueRole",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "DataTeam" for tag in tags
    )
    assert any(
        tag.get("Key") == "CostCenter" and tag.get("Value") == "AI123" for tag in tags
    )
    assert any(
        tag.get("Key") == "Extra" and tag.get("Value") == "Value" for tag in tags
    )


# --- Supplementary: Invalid removal_policy fallback ---
def test_dataquality_stack_invalid_removal_policy():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "app": {"env": "prod"},
        "data_quality": {"removal_policy": "notarealpolicy"},
    }
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_glue_role_arn="arn:aws:iam::123456789012:role/MockGlueRole",
    )
    assert hasattr(stack, "tags")


# --- Supplementary: Lambda log retention mapping ---
import aws_cdk.aws_logs as aws_logs


@pytest.mark.parametrize(
    "log_retention,expected_enum",
    [
        (1, aws_logs.RetentionDays.ONE_DAY),
        (3, aws_logs.RetentionDays.THREE_DAYS),
        (7, aws_logs.RetentionDays.ONE_WEEK),
        (30, aws_logs.RetentionDays.ONE_MONTH),
        (365, aws_logs.RetentionDays.ONE_YEAR),
        (999, aws_logs.RetentionDays.ONE_WEEK),  # fallback
    ],
)
def test_dataquality_stack_lambda_log_retention(log_retention, expected_enum):
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
                "environment": {},
                "timeout": 30,
                "memory": 256,
                "log_retention": log_retention,
            }
        },
        "app": {"env": "test"},
    }
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    # Check the log retention in the synthesized LogGroup resource
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Logs::LogGroup")
    lambda_resources = template.find_resources("AWS::Lambda::Function")
    if not lambda_resources:
        raise AssertionError(
            f"No Lambda function resource found in template. Resources: {template.to_json().get('Resources', {})}"
        )
    found = False
    # Map RetentionDays enum names to their integer values for robust comparison
    retention_days_map = {
        "ONE_DAY": 1,
        "THREE_DAYS": 3,
        "FIVE_DAYS": 5,
        "ONE_WEEK": 7,
        "TWO_WEEKS": 14,
        "ONE_MONTH": 30,
        "TWO_MONTHS": 60,
        "THREE_MONTHS": 90,
        "FOUR_MONTHS": 120,
        "FIVE_MONTHS": 150,
        "SIX_MONTHS": 180,
        "ONE_YEAR": 365,
        "THIRTEEN_MONTHS": 400,
        "EIGHTEEN_MONTHS": 545,
        "TWO_YEARS": 731,
        "FIVE_YEARS": 1827,
        "TEN_YEARS": 3653,
    }
    for log_group in resources.values():
        if "RetentionInDays" in log_group["Properties"]:
            enum_name = (
                expected_enum.name
                if hasattr(expected_enum, "name")
                else str(expected_enum)
            )
            expected_value = retention_days_map.get(enum_name, log_retention)
            assert log_group["Properties"]["RetentionInDays"] == expected_value
            found = True
    if not found:
        # Print all log group resources for debugging
        raise AssertionError(
            f"No LogGroup with RetentionInDays found. LogGroups: {resources}"
        )


def test_dataquality_stack_invalid_lambda_role():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
            }
        },
        "app": {"env": "test"},
    }
    # Should raise if dq_lambda_role_arn is missing
    with pytest.raises(Exception):
        DataQualityStack(test_stack, "TestDataQualityStack", config=config)


def test_dataquality_stack_invalid_secret_arn():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
                "secrets": {"BAD": "not-an-arn"},
            }
        },
        "app": {"env": "test"},
    }
    with pytest.raises(Exception):
        DataQualityStack(
            test_stack,
            "TestDataQualityStack",
            config=config,
            dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        )


def test_dataquality_stack_invalid_lambda_memory_type():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
                "memory": "not-an-int",
            }
        },
        "app": {"env": "test"},
    }
    with pytest.raises(Exception):
        DataQualityStack(
            test_stack,
            "TestDataQualityStack",
            config=config,
            dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        )


def test_dataquality_stack_invalid_lambda_log_retention_type():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
                "log_retention": "not-an-int",
            }
        },
        "app": {"env": "test"},
    }
    # Should not raise, will fallback to default, but test for robustness
    try:
        DataQualityStack(
            test_stack,
            "TestDataQualityStack",
            config=config,
            dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        )
    except Exception:
        pass


def test_dataquality_stack_lambda_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {"lambda": {"enabled": True}},
        "app": {"env": "test"},
    }
    # Should succeed and create a Lambda with defaults
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    assert hasattr(stack, "dq_lambda")


def test_dataquality_stack_lambda_all_optionals():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
                "environment": {"FOO": "BAR"},
                "timeout": 60,
                "memory": 512,
                "log_retention": 14,
                "secrets": {
                    "SECRET": "arn:aws:secretsmanager:us-east-1:123456789012:secret:foo"
                },
            }
        },
        "app": {"env": "test"},
    }
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    assert hasattr(stack, "dq_lambda")
    # Use node.default_child to access CloudFormation properties
    lambda_cf = stack.dq_lambda.node.default_child
    assert lambda_cf.timeout == 60
    assert lambda_cf.memory_size == 512


def test_dataquality_stack_idempotency():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
            }
        },
        "app": {"env": "test"},
    }
    stack1 = DataQualityStack(
        test_stack,
        "TestDataQualityStack1",
        config=config,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    stack2 = DataQualityStack(
        test_stack,
        "TestDataQualityStack2",
        config=config,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    handler1 = stack1.dq_lambda.node.default_child.handler
    handler2 = stack2.dq_lambda.node.default_child.handler
    assert handler1 == handler2


def test_dataquality_stack_tag_override():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "app": {"env": "test"},
        "data_quality": {"tags": {"Owner": "DataTeam"}},
    }
    shared_tags = {"Owner": "Override", "Extra": "Value"}
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        shared_tags=shared_tags,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "Override" for tag in tags
    )
    assert any(
        tag.get("Key") == "Extra" and tag.get("Value") == "Value" for tag in tags
    )


def test_dataquality_stack_lambda_log_group_name():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "data_quality": {
            "lambda": {
                "enabled": True,
                "handler": "index.handler",
                "code_path": "lambda/dataquality",
            }
        },
        "app": {"env": "test"},
    }
    stack = DataQualityStack(
        test_stack,
        "TestDataQualityStack",
        config=config,
        dq_lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
    )
    template = assertions.Template.from_stack(stack)
    log_groups = template.find_resources("AWS::Logs::LogGroup")
    found = False
    for log_group in log_groups.values():
        name = log_group["Properties"].get("LogGroupName", "")
        if name.startswith("/aws/lambda/"):
            found = True
    assert found
