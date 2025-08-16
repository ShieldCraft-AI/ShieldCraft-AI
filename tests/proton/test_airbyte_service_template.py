import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def airbyte_template():
    template_path = Path("proton/airbyte-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(airbyte_template):
    assert isinstance(airbyte_template, dict)
    assert "AWSTemplateFormatVersion" in airbyte_template
    assert "Description" in airbyte_template
    assert "Resources" in airbyte_template
    assert "Parameters" in airbyte_template
    assert "Outputs" in airbyte_template


def test_parameters(airbyte_template):
    params = airbyte_template["Parameters"]
    for p in [
        "ConnectorName",
        "ECSClusterName",
        "ExistingSecretArn",
        "EnvironmentName",
    ]:
        assert p in params
        assert params[p]["Type"] == "String"


def test_resources(airbyte_template):
    resources = airbyte_template["Resources"]
    assert "AirbyteECSService" in resources
    ecs_service = resources["AirbyteECSService"]
    assert ecs_service["Type"] == "AWS::ECS::Service"
    ecs_props = ecs_service["Properties"]
    assert "Cluster" in ecs_props
    assert "ServiceName" in ecs_props
    assert "LaunchType" in ecs_props
    assert ecs_props["LaunchType"] == "FARGATE"
    assert "Tags" in ecs_props
    assert any(tag["Key"] == "Environment" for tag in ecs_props["Tags"])


def test_outputs(airbyte_template):
    outputs = airbyte_template["Outputs"]
    for o in ["AirbyteServiceName", "ConnectorSecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(airbyte_template):
    ecs_tags = airbyte_template["Resources"]["AirbyteECSService"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in ecs_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"ConnectorName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
