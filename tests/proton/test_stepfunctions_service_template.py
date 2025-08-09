import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def stepfunctions_template():
    template_path = Path("proton/stepfunctions-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(stepfunctions_template):
    assert isinstance(stepfunctions_template, dict)
    assert "AWSTemplateFormatVersion" in stepfunctions_template
    assert "Description" in stepfunctions_template
    assert "Resources" in stepfunctions_template
    assert "Parameters" in stepfunctions_template
    assert "Outputs" in stepfunctions_template


def test_parameters(stepfunctions_template):
    params = stepfunctions_template["Parameters"]
    for p in ["StateMachineName", "DefinitionString", "RoleArn", "EnvironmentName"]:
        assert p in params
        assert params[p]["Type"] == "String"


def test_resources(stepfunctions_template):
    resources = stepfunctions_template["Resources"]
    assert "StateMachine" in resources
    state_machine = resources["StateMachine"]
    assert state_machine["Type"] == "AWS::StepFunctions::StateMachine"
    props = state_machine["Properties"]
    assert "StateMachineName" in props
    assert "DefinitionString" in props
    assert "RoleArn" in props
    assert "Tags" in props
    assert any(tag["Key"] == "Environment" for tag in props["Tags"])


def test_outputs(stepfunctions_template):
    outputs = stepfunctions_template["Outputs"]
    for o in ["StateMachineName", "RoleArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(stepfunctions_template):
    tags = stepfunctions_template["Resources"]["StateMachine"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"StateMachineName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
