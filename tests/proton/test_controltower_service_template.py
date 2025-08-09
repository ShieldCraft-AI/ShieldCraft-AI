import pytest
import yaml
from pathlib import Path


# Allow parsing of CloudFormation intrinsic tags like !Ref, !GetAtt, etc.
def unknown_tag(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return node.value
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


yaml.SafeLoader.add_multi_constructor("!", unknown_tag)

TEMPLATE_PATH = (
    Path(__file__).parent.parent.parent
    / "proton"
    / "controltower-service-template.yaml"
)


@pytest.fixture(scope="module")
def template():
    with open(TEMPLATE_PATH, "r") as f:
        return yaml.safe_load(f)


def test_template_format(template):
    assert template["AWSTemplateFormatVersion"] == "2010-09-09"
    assert "Parameters" in template
    assert "Resources" in template
    assert "Outputs" in template


def test_parameters_present(template):
    params = template["Parameters"]
    for key in [
        "LandingZoneName",
        "OrganizationUnitName",
        "GuardrailName",
        "EnvironmentName",
    ]:
        assert key in params
        assert params[key]["Type"] == "String"


def test_resources_present(template):
    resources = template["Resources"]
    assert "ControlTowerLandingZone" in resources
    assert (
        resources["ControlTowerLandingZone"]["Type"] == "AWS::ControlTower::LandingZone"
    )
    assert "ControlTowerGuardrail" in resources
    assert resources["ControlTowerGuardrail"]["Type"] == "AWS::ControlTower::Guardrail"


def test_landing_zone_properties(template):
    props = template["Resources"]["ControlTowerLandingZone"]["Properties"]
    assert props["Name"] in (
        {"Ref": "LandingZoneName"},
        "!Ref LandingZoneName",
        "LandingZoneName",
    )
    assert "OrganizationalUnits" in props
    assert isinstance(props["OrganizationalUnits"], list)
    assert "Tags" in props
    assert any(tag["Key"] == "Environment" for tag in props["Tags"])


def test_guardrail_properties(template):
    props = template["Resources"]["ControlTowerGuardrail"]["Properties"]
    assert props["Name"] in (
        {"Ref": "GuardrailName"},
        "!Ref GuardrailName",
        "GuardrailName",
    )
    assert props["LandingZone"] in (
        {"Ref": "ControlTowerLandingZone"},
        "!Ref ControlTowerLandingZone",
        "ControlTowerLandingZone",
    )
    assert "Tags" in props
    assert any(tag["Key"] == "Environment" for tag in props["Tags"])


def test_outputs_present(template):
    outputs = template["Outputs"]
    assert "LandingZoneName" in outputs
    assert "GuardrailName" in outputs
    assert outputs["LandingZoneName"]["Value"] in (
        {"Ref": "ControlTowerLandingZone"},
        "!Ref ControlTowerLandingZone",
        "ControlTowerLandingZone",
    )
    assert outputs["GuardrailName"]["Value"] in (
        {"Ref": "ControlTowerGuardrail"},
        "!Ref ControlTowerGuardrail",
        "ControlTowerGuardrail",
    )
