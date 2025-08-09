import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def opensearch_template():
    template_path = Path("proton/opensearch-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(opensearch_template):
    assert isinstance(opensearch_template, dict)
    assert "AWSTemplateFormatVersion" in opensearch_template
    assert "Description" in opensearch_template
    assert "Resources" in opensearch_template
    assert "Parameters" in opensearch_template
    assert "Outputs" in opensearch_template


def test_parameters(opensearch_template):
    params = opensearch_template["Parameters"]
    for p in [
        "DomainName",
        "InstanceType",
        "InstanceCount",
        "VaultSecretArn",
        "EnvironmentName",
    ]:
        assert p in params
    assert params["DomainName"]["Type"] == "String"
    assert params["InstanceType"]["Type"] == "String"
    assert params["InstanceCount"]["Type"] == "Number"
    assert params["VaultSecretArn"]["Type"] == "String"
    assert params["EnvironmentName"]["Type"] == "String"


def test_resources(opensearch_template):
    resources = opensearch_template["Resources"]
    assert "OpenSearchDomain" in resources
    assert "VaultSecret" in resources
    domain = resources["OpenSearchDomain"]
    secret = resources["VaultSecret"]
    assert domain["Type"] == "AWS::OpenSearchService::Domain"
    assert secret["Type"] == "AWS::SecretsManager::Secret"
    domain_props = domain["Properties"]
    secret_props = secret["Properties"]
    assert "DomainName" in domain_props
    assert "EngineVersion" in domain_props
    assert "ClusterConfig" in domain_props
    cluster = domain_props["ClusterConfig"]
    assert "InstanceType" in cluster
    assert "InstanceCount" in cluster
    assert "EBSOptions" in domain_props
    ebs = domain_props["EBSOptions"]
    assert ebs["EBSEnabled"] is True or ebs["EBSEnabled"] == "true"
    assert "VolumeSize" in ebs
    assert "VolumeType" in ebs
    assert "NodeToNodeEncryptionOptions" in domain_props
    assert (
        domain_props["NodeToNodeEncryptionOptions"]["Enabled"] is True
        or domain_props["NodeToNodeEncryptionOptions"]["Enabled"] == "true"
    )
    assert "EncryptionAtRestOptions" in domain_props
    assert (
        domain_props["EncryptionAtRestOptions"]["Enabled"] is True
        or domain_props["EncryptionAtRestOptions"]["Enabled"] == "true"
    )
    assert "Tags" in domain_props
    assert any(tag["Key"] == "Environment" for tag in domain_props["Tags"])
    assert "Name" in secret_props
    assert "Description" in secret_props
    assert "SecretString" in secret_props
    assert "Tags" in secret_props
    assert any(tag["Key"] == "Environment" for tag in secret_props["Tags"])


def test_outputs(opensearch_template):
    outputs = opensearch_template["Outputs"]
    for o in ["OpenSearchDomainName", "VaultSecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(opensearch_template):
    domain_tags = opensearch_template["Resources"]["OpenSearchDomain"]["Properties"][
        "Tags"
    ]
    secret_tags = opensearch_template["Resources"]["VaultSecret"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in domain_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in secret_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"DomainName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
