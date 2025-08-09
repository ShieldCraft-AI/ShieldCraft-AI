import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def msk_template():
    template_path = Path("proton/msk-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(msk_template):
    assert isinstance(msk_template, dict)
    assert "AWSTemplateFormatVersion" in msk_template
    assert "Description" in msk_template
    assert "Resources" in msk_template
    assert "Parameters" in msk_template
    assert "Outputs" in msk_template


def test_parameters(msk_template):
    params = msk_template["Parameters"]
    for p in [
        "ClusterName",
        "BrokerNodeGroupInstanceType",
        "NumberOfBrokerNodes",
        "VaultSecretArn",
        "EnvironmentName",
    ]:
        assert p in params
    assert params["ClusterName"]["Type"] == "String"
    assert params["BrokerNodeGroupInstanceType"]["Type"] == "String"
    assert params["NumberOfBrokerNodes"]["Type"] == "Number"
    assert params["VaultSecretArn"]["Type"] == "String"
    assert params["EnvironmentName"]["Type"] == "String"


def test_resources(msk_template):
    resources = msk_template["Resources"]
    assert "MSKCluster" in resources
    assert "VaultSecret" in resources
    cluster = resources["MSKCluster"]
    secret = resources["VaultSecret"]
    assert cluster["Type"] == "AWS::MSK::Cluster"
    assert secret["Type"] == "AWS::SecretsManager::Secret"
    cluster_props = cluster["Properties"]
    secret_props = secret["Properties"]
    assert "ClusterName" in cluster_props
    assert "KafkaVersion" in cluster_props
    assert "NumberOfBrokerNodes" in cluster_props
    assert "BrokerNodeGroupInfo" in cluster_props
    broker_info = cluster_props["BrokerNodeGroupInfo"]
    assert "InstanceType" in broker_info
    assert "ClientSubnets" in broker_info
    assert "SecurityGroups" in broker_info
    assert "EncryptionInfo" in cluster_props
    assert "Tags" in cluster_props
    assert any(tag["Key"] == "Environment" for tag in cluster_props["Tags"])
    assert "Name" in secret_props
    assert "Description" in secret_props
    assert "SecretString" in secret_props
    assert "Tags" in secret_props
    assert any(tag["Key"] == "Environment" for tag in secret_props["Tags"])


def test_outputs(msk_template):
    outputs = msk_template["Outputs"]
    for o in ["MSKClusterName", "VaultSecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(msk_template):
    cluster_tags = msk_template["Resources"]["MSKCluster"]["Properties"]["Tags"]
    secret_tags = msk_template["Resources"]["VaultSecret"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in cluster_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in secret_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"ClusterName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
