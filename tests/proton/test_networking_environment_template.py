"""
Test the Proton networking environment CloudFormation template.
"""

import os
import yaml
import pytest

TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "../../proton/networking-environment-template.yaml"
)


@pytest.mark.unit
def test_networking_template_loads():
    """Template should load as valid YAML."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    assert isinstance(template, dict)
    assert "Resources" in template
    assert "VPC" in template["Resources"]
    assert "PublicSubnet1" in template["Resources"]
    assert "PrivateSubnet1" in template["Resources"]


@pytest.mark.unit
def test_networking_template_parameters():
    """Template should define all required parameters."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    params = template.get("Parameters", {})
    required = [
        "VpcCidr",
        "PublicSubnet1Cidr",
        "PrivateSubnet1Cidr",
        "EnvironmentName",
    ]
    for p in required:
        assert p in params, f"Missing parameter: {p}"


@pytest.mark.unit
def test_networking_template_outputs():
    """Template should define VpcId, PublicSubnet1Id, PrivateSubnet1Id outputs."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    outputs = template.get("Outputs", {})
    for out in ["VpcId", "PublicSubnet1Id", "PrivateSubnet1Id"]:
        assert out in outputs
        assert "Value" in outputs[out]


@pytest.mark.unit
def test_vpc_resource_properties():
    """VPC resource should have required properties."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    vpc = template["Resources"]["VPC"]
    assert vpc.get("Type") == "AWS::EC2::VPC"
    props = vpc.get("Properties", {})
    assert "CidrBlock" in props
    assert props.get("EnableDnsSupport") is not None
    assert props.get("EnableDnsHostnames") is not None
    assert "Tags" in props


@pytest.mark.unit
def test_subnet_resource_properties():
    """Subnet resources should have required properties."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    for subnet_name in ["PublicSubnet1", "PrivateSubnet1"]:
        subnet = template["Resources"][subnet_name]
        assert subnet.get("Type") == "AWS::EC2::Subnet"
        props = subnet.get("Properties", {})
        assert "VpcId" in props
        assert "CidrBlock" in props
        assert "MapPublicIpOnLaunch" in props
        assert "AvailabilityZone" in props
        assert "Tags" in props


@pytest.mark.unit
def test_tag_values_and_structure():
    """Tags for VPC and subnets should reference EnvironmentName and follow naming convention."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    vpc_tags = template["Resources"]["VPC"]["Properties"]["Tags"]
    assert any(
        t["Value"] == "!Ref EnvironmentName" or "EnvironmentName" in t["Value"]
        for t in vpc_tags
    )
    for subnet_name, suffix in [
        ("PublicSubnet1", "public-1"),
        ("PrivateSubnet1", "private-1"),
    ]:
        tags = template["Resources"][subnet_name]["Properties"]["Tags"]
        assert any("public-1" in t["Value"] or "private-1" in t["Value"] for t in tags)


@pytest.mark.unit
def test_default_parameter_values():
    """Parameters should have expected default values for CIDRs."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    params = template.get("Parameters", {})
    assert params["VpcCidr"]["Default"] == "10.0.0.0/16"
    assert params["PublicSubnet1Cidr"]["Default"] == "10.0.1.0/24"
    assert params["PrivateSubnet1Cidr"]["Default"] == "10.0.2.0/24"


@pytest.mark.unit
def test_output_descriptions():
    """Outputs should have non-empty descriptions."""
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)
    outputs = template.get("Outputs", {})
    for out in outputs.values():
        assert "Description" in out
        assert isinstance(out["Description"], str)
        assert out["Description"].strip() != ""
