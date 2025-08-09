import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def eventbridge_template():
    template_path = Path("proton/eventbridge-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(eventbridge_template):
    assert isinstance(eventbridge_template, dict)
    assert "AWSTemplateFormatVersion" in eventbridge_template
    assert "Description" in eventbridge_template
    assert "Resources" in eventbridge_template
    assert "Parameters" in eventbridge_template
    assert "Outputs" in eventbridge_template


def test_parameters(eventbridge_template):
    params = eventbridge_template["Parameters"]
    for p in ["EventBusName", "RuleName", "TargetArn", "EnvironmentName"]:
        assert p in params
        assert params[p]["Type"] == "String"


def test_resources(eventbridge_template):
    resources = eventbridge_template["Resources"]
    assert "EventBus" in resources
    assert "EventRule" in resources
    bus = resources["EventBus"]
    rule = resources["EventRule"]
    assert bus["Type"] == "AWS::Events::EventBus"
    assert rule["Type"] == "AWS::Events::Rule"
    bus_props = bus["Properties"]
    rule_props = rule["Properties"]
    assert "Name" in bus_props
    assert "Tags" in bus_props
    assert any(tag["Key"] == "Environment" for tag in bus_props["Tags"])
    assert "Name" in rule_props
    assert "EventBusName" in rule_props
    assert "EventPattern" in rule_props
    assert "State" in rule_props
    assert rule_props["State"] == "ENABLED"
    assert "Targets" in rule_props
    assert isinstance(rule_props["Targets"], list)
    assert "Arn" in rule_props["Targets"][0]
    assert "Id" in rule_props["Targets"][0]
    assert "Tags" in rule_props
    assert any(tag["Key"] == "Environment" for tag in rule_props["Tags"])


def test_outputs(eventbridge_template):
    outputs = eventbridge_template["Outputs"]
    for o in ["EventBusName", "EventRuleName"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(eventbridge_template):
    bus_tags = eventbridge_template["Resources"]["EventBus"]["Properties"]["Tags"]
    rule_tags = eventbridge_template["Resources"]["EventRule"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in bus_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in rule_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"EventBusName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
