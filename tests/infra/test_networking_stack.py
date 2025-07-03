# --- Fixtures and helpers ---
import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.networking_stack import NetworkingStack
# from infra.utils.config_loader import load_config  # Uncomment if config-driven

@pytest.fixture
def test_config():
    return {
        "networking": {
            "vpc_cidr": "10.0.0.0/16",
            "max_azs": 1,
            "subnets": [
                {"cidr": "10.0.1.0/24", "type": "PUBLIC"},
                {"cidr": "10.0.2.0/24", "type": "PRIVATE"},
                {"cidr": "10.0.3.0/24", "type": "PRIVATE"},
                {"cidr": "10.0.4.0/24", "type": "PUBLIC"},
            ]
        }
    }

# --- Happy path: Synthesis and resource counts ---
def test_networking_stack_synthesizes(test_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = NetworkingStack(test_stack, "TestNetworkingStack", config=test_config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::EC2::VPC", 1)
    template.resource_count_is("AWS::EC2::Subnet", 4)
    outputs = template.to_json().get("Outputs", {})
    assert "TestNetworkingStackVpcId" in outputs
    assert "TestNetworkingStackSubnet1Id" in outputs

# --- Happy path: VPC and subnet property assertions ---
def test_vpc_properties(test_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = NetworkingStack(test_stack, "TestNetworkingStack", config=test_config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::EC2::VPC")
    assert any(
        r["Properties"].get("EnableDnsSupport", True) is True and
        r["Properties"].get("EnableDnsHostnames", True) is True
        for r in resources.values()
    )

def test_subnet_types(test_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = NetworkingStack(test_stack, "TestNetworkingStack", config=test_config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::EC2::Subnet")
    subnet_types = [r["Properties"].get("MapPublicIpOnLaunch") for r in resources.values()]
    # At least one public and one private subnet
    assert True in subnet_types
    assert False in subnet_types

# --- Unhappy path: Invalid config ---
def test_invalid_config_missing_type():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {
        "networking": {
            "vpc_cidr": "10.0.0.0/16",
            "subnets": [
                {"cidr": "10.0.1.0/24"}  # Missing 'type'
            ]
        }
    }
    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)

def test_invalid_config_missing_cidr():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {
        "networking": {
            "vpc_cidr": "10.0.0.0/16",
            "subnets": [
                {"type": "PUBLIC"}  # Missing 'cidr'
            ]
        }
    }
    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)

def test_invalid_config_invalid_type():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {
        "networking": {
            "vpc_cidr": "10.0.0.0/16",
            "subnets": [
                {"cidr": "10.0.1.0/24", "type": "FOO"}
            ]
        }
    }
    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)

def test_invalid_config_subnets_not_list():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {
        "networking": {
            "vpc_cidr": "10.0.0.0/16",
            "subnets": "notalist"
        }
    }
    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)

def test_invalid_config_subnets_empty():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {
        "networking": {
            "vpc_cidr": "10.0.0.0/16",
            "subnets": []
        }
    }
    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)

# --- Inter-stack dependency tests (placeholder) ---
def test_networking_stack_outputs():
    # TODO: If NetworkingStack exports outputs, assert they are present and correct
    pass
