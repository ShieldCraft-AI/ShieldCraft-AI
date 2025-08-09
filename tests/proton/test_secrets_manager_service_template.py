import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def secrets_manager_template():
    template_path = Path("proton/secrets_manager-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(secrets_manager_template):
    assert isinstance(secrets_manager_template, dict)
    assert "AWSTemplateFormatVersion" in secrets_manager_template
    assert "Description" in secrets_manager_template
    assert "Resources" in secrets_manager_template
    assert "Parameters" in secrets_manager_template
    assert "Outputs" in secrets_manager_template


def test_parameters(secrets_manager_template):
    params = secrets_manager_template["Parameters"]
    for p in ["SecretName", "SecretString", "ResourcePolicy", "EnvironmentName"]:
        assert p in params
    assert params["SecretName"]["Type"] == "String"
    assert params["SecretString"]["Type"] == "String"
    assert params["ResourcePolicy"]["Type"] == "Json"
    assert params["EnvironmentName"]["Type"] == "String"


def test_resources(secrets_manager_template):
    resources = secrets_manager_template["Resources"]
    assert "SecretsManagerSecret" in resources
    secret = resources["SecretsManagerSecret"]
    assert secret["Type"] == "AWS::SecretsManager::Secret"
    props = secret["Properties"]
    assert "Name" in props
    assert "Description" in props
    assert "SecretString" in props
    assert "Tags" in props
    assert any(tag["Key"] == "Environment" for tag in props["Tags"])
    assert "ResourcePolicy" in props


def test_outputs(secrets_manager_template):
    outputs = secrets_manager_template["Outputs"]
    for o in ["SecretName", "SecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(secrets_manager_template):
    tags = secrets_manager_template["Resources"]["SecretsManagerSecret"]["Properties"][
        "Tags"
    ]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in tags
    )


def test_resource_policy_type(secrets_manager_template):
    params = secrets_manager_template["Parameters"]
    assert params["ResourcePolicy"]["Type"] == "Json"


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"SecretName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
