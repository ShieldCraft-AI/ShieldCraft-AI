import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def dataquality_template():
    template_path = Path("proton/dataquality-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(dataquality_template):
    assert isinstance(dataquality_template, dict)
    assert "AWSTemplateFormatVersion" in dataquality_template
    assert "Description" in dataquality_template
    assert "Resources" in dataquality_template
    assert "Parameters" in dataquality_template
    assert "Outputs" in dataquality_template


def test_parameters(dataquality_template):
    params = dataquality_template["Parameters"]
    for p in ["QualityJobName", "VaultSecretArn", "EnvironmentName"]:
        assert p in params
        assert params[p]["Type"] == "String"


def test_resources(dataquality_template):
    resources = dataquality_template["Resources"]
    assert "DataQualityJob" in resources
    assert "VaultSecret" in resources
    job = resources["DataQualityJob"]
    secret = resources["VaultSecret"]
    assert job["Type"] == "AWS::Batch::JobDefinition"
    assert secret["Type"] == "AWS::SecretsManager::Secret"
    job_props = job["Properties"]
    secret_props = secret["Properties"]
    assert "JobDefinitionName" in job_props
    assert "Type" in job_props
    assert job_props["Type"] == "container"
    assert "ContainerProperties" in job_props
    container = job_props["ContainerProperties"]
    assert "Image" in container
    assert "Vcpus" in container
    assert "Memory" in container
    assert "Command" in container
    assert "Tags" in job_props
    assert any(tag["Key"] == "Environment" for tag in job_props["Tags"])
    assert "Name" in secret_props
    assert "Description" in secret_props
    assert "SecretString" in secret_props
    assert "Tags" in secret_props
    assert any(tag["Key"] == "Environment" for tag in secret_props["Tags"])


def test_outputs(dataquality_template):
    outputs = dataquality_template["Outputs"]
    for o in ["DataQualityJobName", "VaultSecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(dataquality_template):
    job_tags = dataquality_template["Resources"]["DataQualityJob"]["Properties"]["Tags"]
    secret_tags = dataquality_template["Resources"]["VaultSecret"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in job_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in secret_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"QualityJobName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
