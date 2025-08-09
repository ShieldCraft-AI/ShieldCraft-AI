import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def iam_template():
    template_path = Path("proton/iam-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(iam_template):
    assert isinstance(iam_template, dict)
    assert "AWSTemplateFormatVersion" in iam_template
    assert "Description" in iam_template
    assert "Resources" in iam_template
    assert "Parameters" in iam_template
    assert "Outputs" in iam_template


def test_parameters(iam_template):
    params = iam_template["Parameters"]
    for p in [
        "RoleName",
        "PolicyName",
        "ServicePrincipal",
        "PolicyDocument",
        "EnvironmentName",
    ]:
        assert p in params
    assert params["RoleName"]["Type"] == "String"
    assert params["PolicyName"]["Type"] == "String"
    assert params["ServicePrincipal"]["Type"] == "String"
    assert params["PolicyDocument"]["Type"] == "Json"
    assert params["EnvironmentName"]["Type"] == "String"


def test_resources(iam_template):
    resources = iam_template["Resources"]
    assert "IAMRole" in resources
    assert "IAMPolicy" in resources
    role = resources["IAMRole"]
    policy = resources["IAMPolicy"]
    assert role["Type"] == "AWS::IAM::Role"
    assert policy["Type"] == "AWS::IAM::Policy"
    role_props = role["Properties"]
    policy_props = policy["Properties"]
    assert "RoleName" in role_props
    assert "AssumeRolePolicyDocument" in role_props
    assert "Policies" in role_props
    assert "Tags" in role_props
    assert any(tag["Key"] == "Environment" for tag in role_props["Tags"])
    assert "PolicyName" in policy_props
    assert "PolicyDocument" in policy_props
    assert "Roles" in policy_props
    assert any(tag["Key"] == "Environment" for tag in policy_props["Tags"])


def test_outputs(iam_template):
    outputs = iam_template["Outputs"]
    for o in ["IAMRoleName", "IAMRoleArn", "IAMPolicyName", "IAMPolicyArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_assume_role_policy_structure(iam_template):
    role_props = iam_template["Resources"]["IAMRole"]["Properties"]
    # Should be a string (YAML loader doesn't parse JSON)
    assert isinstance(role_props["AssumeRolePolicyDocument"], str)
    # Should contain ServicePrincipal reference
    assert "${ServicePrincipal}" in role_props["AssumeRolePolicyDocument"]
    assert "sts:AssumeRole" in role_props["AssumeRolePolicyDocument"]


def test_tags_environment(iam_template):
    role_tags = iam_template["Resources"]["IAMRole"]["Properties"]["Tags"]
    policy_tags = iam_template["Resources"]["IAMPolicy"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in role_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in policy_tags
    )


def test_roles_reference(iam_template):
    policy_props = iam_template["Resources"]["IAMPolicy"]["Properties"]
    # Should reference IAMRole by name
    assert isinstance(policy_props["Roles"], list)
    assert policy_props["Roles"][0] == "IAMRole"


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"RoleName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)


def test_policy_document_type(iam_template):
    params = iam_template["Parameters"]
    assert params["PolicyDocument"]["Type"] == "Json"
