import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def hardening_template():
    template_path = Path("proton/cloud_native_hardening-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(hardening_template):
    assert isinstance(hardening_template, dict)
    assert "AWSTemplateFormatVersion" in hardening_template
    assert "Description" in hardening_template
    assert "Resources" in hardening_template
    assert "Parameters" in hardening_template
    assert "Outputs" in hardening_template


def test_parameters(hardening_template):
    params = hardening_template["Parameters"]
    for p in [
        "ConfigRuleName",
        "IAMBoundaryPolicyName",
        "VaultSecretArn",
        "EnvironmentName",
    ]:
        assert p in params
        assert params[p]["Type"] == "String"


def test_resources(hardening_template):
    resources = hardening_template["Resources"]
    assert "ConfigRule" in resources
    assert "IAMBoundaryPolicy" in resources
    assert "VaultSecret" in resources
    config_rule = resources["ConfigRule"]
    boundary_policy = resources["IAMBoundaryPolicy"]
    secret = resources["VaultSecret"]
    assert config_rule["Type"] == "AWS::Config::ConfigRule"
    assert boundary_policy["Type"] == "AWS::IAM::ManagedPolicy"
    assert secret["Type"] == "AWS::SecretsManager::Secret"
    config_props = config_rule["Properties"]
    boundary_props = boundary_policy["Properties"]
    secret_props = secret["Properties"]
    assert "ConfigRuleName" in config_props
    assert "Source" in config_props
    assert config_props["Source"]["SourceIdentifier"] == "IAM_PASSWORD_POLICY"
    assert "Tags" in config_props
    assert any(tag["Key"] == "Environment" for tag in config_props["Tags"])
    assert "ManagedPolicyName" in boundary_props
    assert "PolicyDocument" in boundary_props
    assert "Tags" in boundary_props
    assert any(tag["Key"] == "Environment" for tag in boundary_props["Tags"])
    assert "Name" in secret_props
    assert "Description" in secret_props
    assert "SecretString" in secret_props
    assert "Tags" in secret_props
    assert any(tag["Key"] == "Environment" for tag in secret_props["Tags"])


def test_outputs(hardening_template):
    outputs = hardening_template["Outputs"]
    for o in ["ConfigRuleName", "IAMBoundaryPolicyArn", "VaultSecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(hardening_template):
    config_tags = hardening_template["Resources"]["ConfigRule"]["Properties"]["Tags"]
    boundary_tags = hardening_template["Resources"]["IAMBoundaryPolicy"]["Properties"][
        "Tags"
    ]
    secret_tags = hardening_template["Resources"]["VaultSecret"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in config_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in boundary_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in secret_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"ConfigRuleName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
