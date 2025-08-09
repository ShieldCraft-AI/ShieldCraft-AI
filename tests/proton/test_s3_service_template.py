import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def s3_template():
    template_path = Path("proton/s3-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(s3_template):
    assert isinstance(s3_template, dict)
    assert "AWSTemplateFormatVersion" in s3_template
    assert "Description" in s3_template
    assert "Resources" in s3_template
    assert "Parameters" in s3_template
    assert "Outputs" in s3_template


def test_parameters(s3_template):
    params = s3_template["Parameters"]
    assert "BucketName" in params
    assert "EnvironmentName" in params
    assert params["BucketName"]["Type"] == "String"
    assert params["EnvironmentName"]["Type"] == "String"

    # Check allowed values and defaults for EnableVersioning, EnableEncryption, RemovalPolicy
    assert params["EnableVersioning"]["AllowedValues"] == ["true", "false"]
    assert params["EnableVersioning"]["Default"] == "true"
    assert params["EnableEncryption"]["AllowedValues"] == ["true", "false"]
    assert params["EnableEncryption"]["Default"] == "true"
    assert params["RemovalPolicy"]["AllowedValues"] == ["RETAIN", "DESTROY"]
    assert params["RemovalPolicy"]["Default"] == "RETAIN"


def test_resources(s3_template):
    resources = s3_template["Resources"]
    assert "S3Bucket" in resources
    bucket = resources["S3Bucket"]
    assert bucket["Type"] == "AWS::S3::Bucket"
    props = bucket["Properties"]
    assert "BucketName" in props
    assert "Tags" in props
    tags = props["Tags"]
    assert any(tag["Key"] == "Environment" for tag in tags)

    # Check VersioningConfiguration and BucketEncryption structure
    assert "VersioningConfiguration" in props
    assert "Status" in props["VersioningConfiguration"]
    assert "BucketEncryption" in props


def test_outputs(s3_template):
    outputs = s3_template["Outputs"]
    assert "S3BucketName" in outputs
    assert "S3BucketArn" in outputs
    out_name = outputs["S3BucketName"]
    out_arn = outputs["S3BucketArn"]
    assert out_name["Description"]
    assert out_name["Value"] == "S3Bucket"
    assert out_arn["Description"]
    assert out_arn["Value"] == "S3Bucket.Arn"


def test_intrinsic_tags_handling(s3_template):
    # Ensure BucketName is a string and matches the parameter name
    bucket = s3_template["Resources"]["S3Bucket"]
    props = bucket["Properties"]
    assert isinstance(props["BucketName"], str)
    assert props["BucketName"] == "BucketName"


def test_environment_tag(s3_template):
    tags = s3_template["Resources"]["S3Bucket"]["Properties"]["Tags"]
    env_tag = next((tag for tag in tags if tag["Key"] == "Environment"), None)
    assert env_tag is not None
    assert env_tag["Value"] == "EnvironmentName"


def test_conditions(s3_template):
    conditions = s3_template["Conditions"]
    assert "EnableVersioningTrue" in conditions
    assert "EnableEncryptionTrue" in conditions
    # Check structure: should be a list with two elements (Ref, value)
    assert isinstance(conditions["EnableVersioningTrue"], list)
    assert len(conditions["EnableVersioningTrue"]) == 2
    assert conditions["EnableVersioningTrue"][0] == "EnableVersioning"
    assert conditions["EnableVersioningTrue"][1] == "true"
    assert isinstance(conditions["EnableEncryptionTrue"], list)
    assert len(conditions["EnableEncryptionTrue"]) == 2
    assert conditions["EnableEncryptionTrue"][0] == "EnableEncryption"
    assert conditions["EnableEncryptionTrue"][1] == "true"


def test_missing_required_parameters():
    # Simulate unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"BucketName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    # Should fail structure test
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
