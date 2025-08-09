"""
Test the Lambda service CloudFormation template.
"""

import os
import yaml
import pytest

TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "../../proton/lambda-service-template.yaml"
)


@pytest.mark.unit
def test_lambda_template_loads():
    """Template should load as valid YAML."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    assert isinstance(template, dict)
    assert "Resources" in template
    assert "LambdaFunction" in template["Resources"]


@pytest.mark.unit
def test_lambda_template_parameters():
    """Template should define all required parameters."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    params = template.get("Parameters", {})
    required = [
        "FunctionName",
        "Handler",
        "Runtime",
        "CodeS3Bucket",
        "CodeS3Key",
        "RoleArn",
        "VpcId",
        "SubnetIds",
        "SecurityGroupIds",
    ]
    for p in required:
        assert p in params, f"Missing parameter: {p}"


@pytest.mark.unit
def test_lambda_template_outputs():
    """Template should define LambdaFunctionArn output."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    outputs = template.get("Outputs", {})
    assert "LambdaFunctionArn" in outputs
    assert "Value" in outputs["LambdaFunctionArn"]


@pytest.mark.unit
def test_lambda_resource_properties():
    """LambdaFunction resource should have all required properties."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    resources = template.get("Resources", {})
    lambda_fn = resources.get("LambdaFunction", {})
    assert lambda_fn.get("Type") == "AWS::Lambda::Function"
    props = lambda_fn.get("Properties", {})
    required_props = [
        "FunctionName",
        "Handler",
        "Runtime",
        "Code",
        "Role",
        "VpcConfig",
        "Timeout",
        "MemorySize",
        "Environment",
    ]
    for p in required_props:
        assert p in props, f"Missing Lambda property: {p}"


@pytest.mark.unit
def test_lambda_code_and_vpc_config():
    """LambdaFunction Code and VpcConfig should have required subfields."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    props = template["Resources"]["LambdaFunction"]["Properties"]
    code = props.get("Code", {})
    assert "S3Bucket" in code
    assert "S3Key" in code
    vpc = props.get("VpcConfig", {})
    assert "SubnetIds" in vpc
    assert "SecurityGroupIds" in vpc


@pytest.mark.unit
def test_lambda_environment_variables():
    """LambdaFunction Environment should define ENVIRONMENT variable."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    env = template["Resources"]["LambdaFunction"]["Properties"]["Environment"]
    assert "Variables" in env
    assert "ENVIRONMENT" in env["Variables"]


@pytest.mark.unit
def test_lambda_timeout_and_memory():
    """LambdaFunction should have reasonable timeout and memory settings."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    props = template["Resources"]["LambdaFunction"]["Properties"]
    timeout = int(props.get("Timeout", 0))
    memory = int(props.get("MemorySize", 0))
    assert 1 <= timeout <= 900, f"Timeout out of range: {timeout}"
    assert 128 <= memory <= 10240, f"Memory out of range: {memory}"
