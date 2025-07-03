import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.dataquality_stack import DataQualityStack
from aws_cdk import aws_ec2 as ec2

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
                "default_arguments": {}
            }
        },
        "app": {"env": "test"}
    }


# --- Happy path: Glue Job creation ---
def test_dataquality_stack_synthesizes(dq_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = DataQualityStack(test_stack, "TestDataQualityStack", config=dq_config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::Glue::Job", 1)

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
                "log_retention": 3
            }
        },
        "app": {"env": "test"}
    }
    stack = DataQualityStack(test_stack, "TestDataQualityStack", config=config)
    assert hasattr(stack, "dq_lambda")

# --- Happy path: Outputs ---
def test_dataquality_stack_outputs(dq_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = DataQualityStack(test_stack, "TestDataQualityStack", config=dq_config)
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    # The output key is f"TestDataQualityStackDataQualityGlueJobName" if using default test stack/construct id
    assert "TestDataQualityStackDataQualityGlueJobName" in outputs, f"Outputs: {outputs.keys()}"

# --- Happy path: Tagging ---
def test_dataquality_stack_tags(dq_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = DataQualityStack(test_stack, "TestDataQualityStack", config=dq_config)
    tags = stack.tags.render_tags()
    assert any(tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI" for tag in tags)

# --- Unhappy path: Missing required Glue Job config ---
@pytest.mark.parametrize("bad_config", [
    {"data_quality": {"glue_job": {"enabled": True}}},
    {"data_quality": {"glue_job": {"enabled": True, "name": ""}}},
])
def test_dataquality_stack_invalid_glue_config(bad_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    with pytest.raises(Exception):
        DataQualityStack(test_stack, "TestDataQualityStack", config=bad_config)

# --- Unhappy path: Invalid Lambda config ---
@pytest.mark.parametrize("bad_config", [
    {"data_quality": {"lambda": {"enabled": True, "handler": "", "code_path": ""}}},
    {"data_quality": {"lambda": {"enabled": True, "timeout": -1}}},
])
def test_dataquality_stack_invalid_lambda_config(bad_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    with pytest.raises(Exception):
        DataQualityStack(test_stack, "TestDataQualityStack", config=bad_config)

# --- Happy path: Unknown config keys (should not raise) ---
def test_dataquality_stack_unknown_config_keys():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"app": {"env": "test"}, "data_quality": {"lambda": {"enabled": True, "unknown_key": 123}}}
    stack = DataQualityStack(test_stack, "TestDataQualityStack", config=config)
    assert hasattr(stack, "tags")

# --- Happy path: Minimal config (no resources) ---
def test_dataquality_stack_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"data_quality": {}}
    stack = DataQualityStack(test_stack, "TestDataQualityStack", config=config)
    assert hasattr(stack, "tags")
