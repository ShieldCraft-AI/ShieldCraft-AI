import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def security_template():
    template_path = Path("proton/security-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(security_template):
    assert isinstance(security_template, dict)
    assert "AWSTemplateFormatVersion" in security_template
    assert "Description" in security_template
    assert "Resources" in security_template
    assert "Parameters" in security_template
    assert "Outputs" in security_template
    assert "Conditions" in security_template


def test_parameters(security_template):
    params = security_template["Parameters"]
    for p in [
        "LogGroupName",
        "AlarmName",
        "AlarmThreshold",
        "GuardDutyEnable",
        "EnvironmentName",
    ]:
        assert p in params
    assert params["LogGroupName"]["Type"] == "String"
    assert params["AlarmName"]["Type"] == "String"
    assert params["AlarmThreshold"]["Type"] == "Number"
    assert params["GuardDutyEnable"]["Type"] == "String"
    assert params["GuardDutyEnable"]["AllowedValues"] == ["true", "false"]
    assert params["GuardDutyEnable"]["Default"] == "true"
    assert params["EnvironmentName"]["Type"] == "String"


def test_resources(security_template):
    resources = security_template["Resources"]
    assert "CloudWatchLogGroup" in resources
    assert "CloudWatchAlarm" in resources
    assert "GuardDutyDetector" in resources
    log_group = resources["CloudWatchLogGroup"]
    alarm = resources["CloudWatchAlarm"]
    detector = resources["GuardDutyDetector"]
    assert log_group["Type"] == "AWS::Logs::LogGroup"
    assert alarm["Type"] == "AWS::CloudWatch::Alarm"
    assert detector["Type"] == "AWS::GuardDuty::Detector"
    log_group_props = log_group["Properties"]
    alarm_props = alarm["Properties"]
    detector_props = detector["Properties"]
    assert "LogGroupName" in log_group_props
    assert "Tags" in log_group_props
    assert any(tag["Key"] == "Environment" for tag in log_group_props["Tags"])
    assert "AlarmName" in alarm_props
    assert "MetricName" in alarm_props
    assert "Namespace" in alarm_props
    assert "Threshold" in alarm_props
    assert "Dimensions" in alarm_props
    assert any(tag["Key"] == "Environment" for tag in alarm_props["Tags"])
    assert "Enable" in detector_props


def test_outputs(security_template):
    outputs = security_template["Outputs"]
    for o in ["LogGroupName", "AlarmName", "GuardDutyDetectorId"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_conditions(security_template):
    conditions = security_template["Conditions"]
    assert "EnableGuardDuty" in conditions
    # Should be a list with two elements (Ref, value)
    assert isinstance(conditions["EnableGuardDuty"], list)
    assert len(conditions["EnableGuardDuty"]) == 2
    assert conditions["EnableGuardDuty"][0] == "GuardDutyEnable"
    assert conditions["EnableGuardDuty"][1] == "true"


def test_tags_environment(security_template):
    log_group_tags = security_template["Resources"]["CloudWatchLogGroup"]["Properties"][
        "Tags"
    ]
    alarm_tags = security_template["Resources"]["CloudWatchAlarm"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in log_group_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in alarm_tags
    )


def test_guardduty_enable(security_template):
    detector_props = security_template["Resources"]["GuardDutyDetector"]["Properties"]
    assert detector_props["Enable"] is True or detector_props["Enable"] == "true"


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"LogGroupName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
        "Conditions": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
