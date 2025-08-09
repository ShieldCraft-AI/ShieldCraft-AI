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
    for p in ["ConnectorName", "ECSClusterName", "VaultSecretArn", "EnvironmentName"]:
        assert p in params
        assert params[p]["Type"] == "String"


def test_resources(airbyte_template):
    resources = airbyte_template["Resources"]
    assert "AirbyteECSService" in resources
    assert "VaultSecret" in resources
    ecs_service = resources["AirbyteECSService"]
    secret = resources["VaultSecret"]
    assert ecs_service["Type"] == "AWS::ECS::Service"
    assert secret["Type"] == "AWS::SecretsManager::Secret"
    ecs_props = ecs_service["Properties"]
    secret_props = secret["Properties"]
    assert "Cluster" in ecs_props
    assert "ServiceName" in ecs_props
    assert "LaunchType" in ecs_props
    assert ecs_props["LaunchType"] == "FARGATE"
    assert "Tags" in ecs_props
    assert any(tag["Key"] == "Environment" for tag in ecs_props["Tags"])
    assert "Name" in secret_props
    assert "Description" in secret_props
    assert "SecretString" in secret_props
    assert "Tags" in secret_props
    assert any(tag["Key"] == "Environment" for tag in secret_props["Tags"])


def test_outputs(airbyte_template):
    outputs = airbyte_template["Outputs"]
    for o in ["AirbyteServiceName", "VaultSecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(airbyte_template):
    ecs_tags = airbyte_template["Resources"]["AirbyteECSService"]["Properties"]["Tags"]
    secret_tags = airbyte_template["Resources"]["VaultSecret"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in ecs_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in secret_tags
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
