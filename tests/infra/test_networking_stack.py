# --- Fixtures and helpers ---
import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.networking.networking_stack import NetworkingStack

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
            ],
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
    # Core outputs
    assert "TestNetworkingStackVpcId" in outputs
    assert "TestNetworkingStackSubnet1Id" in outputs
    assert "TestNetworkingStackDefaultSGId" in outputs
    assert "TestNetworkingStackFlowLogsBucketArn" in outputs
    # All subnets output
    for i in range(1, 5):
        assert f"TestNetworkingStackSubnet{i}Id" in outputs


# --- Happy path: VPC and subnet property assertions ---
def test_vpc_properties(test_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = NetworkingStack(test_stack, "TestNetworkingStack", config=test_config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::EC2::VPC")
    assert any(
        r["Properties"].get("EnableDnsSupport", True) is True
        and r["Properties"].get("EnableDnsHostnames", True) is True
        for r in resources.values()
    )
    # Shared resources dict exposes vpc
    assert hasattr(stack, "shared_resources")
    assert "vpc" in stack.shared_resources
    assert stack.shared_resources["vpc"] == stack.vpc


def test_subnet_types(test_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = NetworkingStack(test_stack, "TestNetworkingStack", config=test_config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::EC2::Subnet")
    subnet_types = [
        r["Properties"].get("MapPublicIpOnLaunch") for r in resources.values()
    ]
    # At least one public and one private subnet
    assert True in subnet_types
    assert False in subnet_types
    # Shared resources dict exposes subnets
    assert "subnets" in stack.shared_resources
    assert len(stack.shared_resources["subnets"]) == 4


# --- Happy path: Default SG and flow logs bucket ---
def test_default_sg_and_flow_logs(test_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = NetworkingStack(test_stack, "TestNetworkingStack", config=test_config)
    # Default SG
    assert hasattr(stack, "default_sg")
    assert stack.default_sg.security_group_id is not None
    # Flow logs bucket
    assert hasattr(stack, "flow_logs_bucket")
    assert stack.flow_logs_bucket.bucket_arn is not None
    # Shared resources dict exposes both
    assert stack.shared_resources["default_sg"] == stack.default_sg
    assert stack.shared_resources["flow_logs_bucket"] == stack.flow_logs_bucket


# --- Happy path: NAT gateway alarms (monitoring) ---
def test_nat_gateway_alarms():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "networking": {
            "vpc_cidr": "10.0.0.0/16",
            "max_azs": 2,
            "nat_gateways": 2,
            "subnets": [
                {"cidr": "10.0.1.0/24", "type": "PUBLIC"},
                {"cidr": "10.0.2.0/24", "type": "PRIVATE"},
                {"cidr": "10.0.3.0/24", "type": "PUBLIC"},
                {"cidr": "10.0.4.0/24", "type": "PRIVATE"},
            ],
        }
    }
    stack = NetworkingStack(test_stack, "TestNetworkingStack", config=config)
    # NAT alarms should be present if NAT gateways > 0
    assert hasattr(stack, "nat_alarms")
    assert isinstance(stack.nat_alarms, list)
    # May be 0 if no NATs, but should be a list


# --- Inter-stack dependency tests (outputs) ---
def test_networking_stack_outputs():
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = NetworkingStack(
        test_stack,
        "TestNetworkingStack",
        config={
            "networking": {
                "vpc_cidr": "10.0.0.0/16",
                "max_azs": 1,
                "subnets": [
                    {"cidr": "10.0.1.0/24", "type": "PUBLIC"},
                    {"cidr": "10.0.2.0/24", "type": "PRIVATE"},
                ],
            }
        },
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    assert "TestNetworkingStackVpcId" in outputs
    assert "TestNetworkingStackDefaultSGId" in outputs
    assert "TestNetworkingStackFlowLogsBucketArn" in outputs


# --- Unhappy path: Invalid config ---
def test_invalid_config_missing_type():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {
        "networking": {
            "vpc_cidr": "10.0.0.0/16",
            "subnets": [{"cidr": "10.0.1.0/24"}],  # Missing 'type'
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
            "subnets": [{"type": "PUBLIC"}],  # Missing 'cidr'
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
            "subnets": [{"cidr": "10.0.1.0/24", "type": "FOO"}],
        }
    }
    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)


def test_invalid_config_subnets_not_list():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {"networking": {"vpc_cidr": "10.0.0.0/16", "subnets": "notalist"}}
    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)


def test_invalid_config_subnets_empty():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {"networking": {"vpc_cidr": "10.0.0.0/16", "subnets": []}}
    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)
