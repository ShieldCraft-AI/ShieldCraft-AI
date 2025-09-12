import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def sagemaker_template():
    template_path = Path("proton/sagemaker-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(sagemaker_template):
    assert isinstance(sagemaker_template, dict)
    assert "AWSTemplateFormatVersion" in sagemaker_template
    assert "Description" in sagemaker_template
    assert "Resources" in sagemaker_template
    assert "Parameters" in sagemaker_template
    assert "Outputs" in sagemaker_template


def test_parameters(sagemaker_template):
    params = sagemaker_template["Parameters"]
    for p in [
        "EndpointName",
        "ModelName",
        "InstanceType",
        "ExecutionRoleArn",
        "EnvironmentName",
    ]:
        assert p in params
    assert params["EndpointName"]["Type"] == "String"
    assert params["ModelName"]["Type"] == "String"
    assert params["InstanceType"]["Type"] == "String"
    assert params["ExecutionRoleArn"]["Type"] == "String"
    assert params["EnvironmentName"]["Type"] == "String"


def test_resources(sagemaker_template):
    resources = sagemaker_template["Resources"]
    assert "SageMakerModel" in resources
    assert "SageMakerEndpointConfig" in resources
    assert "SageMakerEndpoint" in resources
    model = resources["SageMakerModel"]
    endpoint_config = resources["SageMakerEndpointConfig"]
    endpoint = resources["SageMakerEndpoint"]
    assert model["Type"] == "AWS::SageMaker::Model"
    assert endpoint_config["Type"] == "AWS::SageMaker::EndpointConfig"
    assert endpoint["Type"] == "AWS::SageMaker::Endpoint"
    model_props = model["Properties"]
    endpoint_config_props = endpoint_config["Properties"]
    endpoint_props = endpoint["Properties"]
    assert "ModelName" in model_props
    assert "PrimaryContainer" in model_props
    assert "ExecutionRoleArn" in model_props
    assert "Tags" in model_props
    assert any(tag["Key"] == "Environment" for tag in model_props["Tags"])
    assert "EndpointConfigName" in endpoint_config_props
    assert "ProductionVariants" in endpoint_config_props
    variant = endpoint_config_props["ProductionVariants"][0]
    assert "VariantName" in variant
    assert "ModelName" in variant
    assert "InitialInstanceCount" in variant
    assert "InstanceType" in variant
    assert "Tags" in endpoint_config_props
    assert any(tag["Key"] == "Environment" for tag in endpoint_config_props["Tags"])
    assert "EndpointName" in endpoint_props
    assert "EndpointConfigName" in endpoint_props
    assert "Tags" in endpoint_props
    assert any(tag["Key"] == "Environment" for tag in endpoint_props["Tags"])


def test_outputs(sagemaker_template):
    outputs = sagemaker_template["Outputs"]
    for o in ["SageMakerEndpointName", "SageMakerModelName"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(sagemaker_template):
    model_tags = sagemaker_template["Resources"]["SageMakerModel"]["Properties"]["Tags"]
    endpoint_config_tags = sagemaker_template["Resources"]["SageMakerEndpointConfig"][
        "Properties"
    ]["Tags"]
    endpoint_tags = sagemaker_template["Resources"]["SageMakerEndpoint"]["Properties"][
        "Tags"
    ]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in model_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in endpoint_config_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in endpoint_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"EndpointName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
