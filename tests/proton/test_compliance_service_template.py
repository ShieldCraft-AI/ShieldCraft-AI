import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def compliance_template():
    template_path = Path("proton/compliance-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(compliance_template):
    assert isinstance(compliance_template, dict)
    assert "AWSTemplateFormatVersion" in compliance_template
    assert "Description" in compliance_template
    assert "Resources" in compliance_template
    assert "Parameters" in compliance_template
    assert "Outputs" in compliance_template


def test_parameters(compliance_template):
    params = compliance_template["Parameters"]
    for p in ["ReportLambdaName", "VaultSecretArn", "EnvironmentName"]:
        assert p in params
        assert params[p]["Type"] == "String"


def test_resources(compliance_template):
    resources = compliance_template["Resources"]
    assert "ComplianceReportLambda" in resources
    assert "VaultSecret" in resources
    lambda_fn = resources["ComplianceReportLambda"]
    secret = resources["VaultSecret"]
    assert lambda_fn["Type"] == "AWS::Lambda::Function"
    assert secret["Type"] == "AWS::SecretsManager::Secret"
    lambda_props = lambda_fn["Properties"]
    secret_props = secret["Properties"]
    assert "FunctionName" in lambda_props
    assert "Handler" in lambda_props
    assert "Runtime" in lambda_props
    assert lambda_props["Runtime"] == "python3.12"
    assert "Role" in lambda_props
    assert "Tags" in lambda_props
    assert any(tag["Key"] == "Environment" for tag in lambda_props["Tags"])
    assert "Name" in secret_props
    assert "Description" in secret_props
    assert "SecretString" in secret_props
    assert "Tags" in secret_props
    assert any(tag["Key"] == "Environment" for tag in secret_props["Tags"])


def test_outputs(compliance_template):
    outputs = compliance_template["Outputs"]
    for o in ["ComplianceReportLambdaName", "VaultSecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(compliance_template):
    lambda_tags = compliance_template["Resources"]["ComplianceReportLambda"][
        "Properties"
    ]["Tags"]
    secret_tags = compliance_template["Resources"]["VaultSecret"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in lambda_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in secret_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"ReportLambdaName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
