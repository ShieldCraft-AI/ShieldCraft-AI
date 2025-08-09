import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def attack_sim_template():
    template_path = Path("proton/attack_simulation-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(attack_sim_template):
    assert isinstance(attack_sim_template, dict)
    assert "AWSTemplateFormatVersion" in attack_sim_template
    assert "Description" in attack_sim_template
    assert "Resources" in attack_sim_template
    assert "Parameters" in attack_sim_template
    assert "Outputs" in attack_sim_template


def test_parameters(attack_sim_template):
    params = attack_sim_template["Parameters"]
    for p in ["FunctionName", "AlarmName", "SecretArn", "EnvironmentName"]:
        assert p in params
        assert params[p]["Type"] == "String"


def test_resources(attack_sim_template):
    resources = attack_sim_template["Resources"]
    assert "AttackSimulationLambda" in resources
    assert "AttackSimulationAlarm" in resources
    lambda_fn = resources["AttackSimulationLambda"]
    alarm = resources["AttackSimulationAlarm"]
    assert lambda_fn["Type"] == "AWS::Lambda::Function"
    assert alarm["Type"] == "AWS::CloudWatch::Alarm"
    lambda_props = lambda_fn["Properties"]
    alarm_props = alarm["Properties"]
    assert "FunctionName" in lambda_props
    assert "Handler" in lambda_props
    assert "Runtime" in lambda_props
    assert lambda_props["Runtime"] == "python3.12"
    assert "Role" in lambda_props
    assert "Tags" in lambda_props
    assert any(tag["Key"] == "Environment" for tag in lambda_props["Tags"])
    assert "AlarmName" in alarm_props
    assert "MetricName" in alarm_props
    assert "Namespace" in alarm_props
    assert "Threshold" in alarm_props
    assert "Dimensions" in alarm_props
    assert any(tag["Key"] == "Environment" for tag in alarm_props["Tags"])


def test_outputs(attack_sim_template):
    outputs = attack_sim_template["Outputs"]
    for o in ["LambdaFunctionName", "AlarmName", "SecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(attack_sim_template):
    lambda_tags = attack_sim_template["Resources"]["AttackSimulationLambda"][
        "Properties"
    ]["Tags"]
    alarm_tags = attack_sim_template["Resources"]["AttackSimulationAlarm"][
        "Properties"
    ]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in lambda_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in alarm_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"FunctionName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
