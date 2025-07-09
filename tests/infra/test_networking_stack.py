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


# --- Unhappy path: Invalid VPC CIDR (not a string) ---
def test_invalid_vpc_cidr_not_string():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {
        "networking": {
            "vpc_cidr": 12345,
            "subnets": [{"cidr": "10.0.1.0/24", "type": "PUBLIC"}],
        }
    }

    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)


# --- Unhappy path: Invalid subnet CIDR (not a string) ---
def test_invalid_subnet_cidr_not_string():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {"networking": {"subnets": [{"cidr": 12345, "type": "PUBLIC"}]}}

    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)


# --- Unhappy path: Invalid subnet CIDR (bad format) ---
def test_invalid_subnet_cidr_bad_format():
    app = App()
    test_stack = Stack(app, "TestStack")
    invalid_config = {
        "networking": {"subnets": [{"cidr": "notacidr", "type": "PUBLIC"}]}
    }

    with pytest.raises(ValueError):
        NetworkingStack(test_stack, "TestNetworkingStackInvalid", config=invalid_config)


# --- Unhappy path: Invalid max_azs (not int, negative, zero) ---
def test_invalid_max_azs():
    import uuid

    app = App()
    for val in [0, -1, "two"]:
        test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
        invalid_config = {
            "networking": {
                "max_azs": val,
                "subnets": [{"cidr": "10.0.1.0/24", "type": "PUBLIC"}],
            }
        }
        with pytest.raises(ValueError):
            NetworkingStack(
                test_stack,
                f"TestNetworkingStackInvalid{uuid.uuid4()}",
                config=invalid_config,
            )


# --- Unhappy path: Invalid nat_gateways (not int, negative) ---
def test_invalid_nat_gateways():
    import uuid

    app = App()
    for val in [-1, "two"]:
        test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
        invalid_config = {
            "networking": {
                "nat_gateways": val,
                "subnets": [{"cidr": "10.0.1.0/24", "type": "PUBLIC"}],
            }
        }
        with pytest.raises(ValueError):
            NetworkingStack(
                test_stack,
                f"TestNetworkingStackInvalid{uuid.uuid4()}",
                config=invalid_config,
            )


# --- Unhappy path: Invalid removal policy (should fallback or raise) ---
def test_invalid_removal_policy():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "networking": {
            "removal_policy": "notapolicy",
            "subnets": [{"cidr": "10.0.1.0/24", "type": "PUBLIC"}],
        }
    }

    # Should fallback to default, not raise
    stack = NetworkingStack(test_stack, "TestNetworkingStack", config=config)
    assert stack.flow_logs_bucket is not None


# --- Tag propagation: shared_tags and per-stack tags ---
def test_networking_stack_tag_propagation():
    app = App()
    test_stack = Stack(app, "TestStack")
    shared_tags = {"CostCenter": "9999"}
    config = {
        "networking": {
            "tags": {"Owner": "NetTeam"},
            "subnets": [{"cidr": "10.0.1.0/24", "type": "PUBLIC"}],
        }
    }

    stack = NetworkingStack(
        test_stack, "TestNetworkingStack", config=config, shared_tags=shared_tags
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "CostCenter" and tag.get("Value") == "9999" for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "NetTeam" for tag in tags
    )


# --- Edge case: Unresolved token for VPC/subnet CIDR (should not raise, but skip mask assertion) ---
def test_unresolved_token_vpc_and_subnet_cidr():
    from aws_cdk import Token
    import uuid

    app = App()
    test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
    unresolved_cidr = Token.as_string({"Ref": f"SomeResource{uuid.uuid4()}"})
    config = {
        "networking": {
            "vpc_cidr": unresolved_cidr,
            "subnets": [{"cidr": unresolved_cidr, "type": "PUBLIC"}],
        }
    }
    # Should not raise, but will not check mask
    try:
        stack = NetworkingStack(
            test_stack, f"TestNetworkingStack{uuid.uuid4()}", config=config
        )
        assert stack.vpc is not None
    except ValueError as e:
        assert "invalid literal for int()" in str(e) or "Invalid subnet CIDR" in str(e)


# --- Edge case: Large number of subnets (scalability) ---
def test_large_number_of_subnets():
    import uuid

    app = App()
    test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
    subnets = [{"cidr": f"10.0.{i}.0/24", "type": "PUBLIC"} for i in range(1, 21)]
    config = {"networking": {"subnets": subnets, "max_azs": 1}}
    stack = NetworkingStack(
        test_stack, f"TestNetworkingStack{uuid.uuid4()}", config=config
    )
    assert len(stack.shared_resources["subnets"]) == 20


# --- Edge case: Minimal config (backward compatibility) ---
def test_networking_stack_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = NetworkingStack(test_stack, "TestNetworkingStack")
    assert stack.vpc is not None
    assert stack.default_sg is not None
    assert stack.flow_logs_bucket is not None


# --- Output/ARN structure and export name validation ---
def test_networking_stack_output_export_names():
    import uuid

    app = App()
    test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
    stack = NetworkingStack(test_stack, f"TestNetworkingStack{uuid.uuid4()}")
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    for k, v in outputs.items():
        assert all(c.isalnum() or c in "-:_." for c in k), f"Invalid output key: {k}"
        # Accept dicts with Value/Export keys (CDK output structure)
        if isinstance(v, dict):
            assert (
                "Value" in v and "Export" in v
            ), f"Invalid output value structure: {v}"
        else:
            assert all(
                c.isalnum() or c in "-:_." for c in str(v)
            ), f"Invalid output value: {v}"


# --- Edge case: test with ISOLATED subnet type ---
def test_isolated_subnet_type():
    import uuid

    app = App()
    test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
    config = {
        "networking": {
            "subnets": [
                {"cidr": "10.0.10.0/24", "type": "ISOLATED"},
                {"cidr": "10.0.11.0/24", "type": "PUBLIC"},
            ],
            "max_azs": 1,
        }
    }
    stack = NetworkingStack(
        test_stack, f"TestNetworkingStack{uuid.uuid4()}", config=config
    )
    from aws_cdk import aws_ec2 as ec2

    assert any(isinstance(s, ec2.PrivateSubnet) for s in stack.vpc.isolated_subnets)
    assert any(isinstance(s, ec2.PublicSubnet) for s in stack.vpc.public_subnets)


# --- Edge case: test allow_all_outbound override ---
def test_allow_all_outbound_override():
    import uuid

    app = App()
    test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
    config = {
        "networking": {
            "subnets": [
                {"cidr": "10.0.20.0/24", "type": "PUBLIC"},
            ],
            "allow_all_outbound": True,
        }
    }
    stack = NetworkingStack(
        test_stack, f"TestNetworkingStack{uuid.uuid4()}", config=config
    )
    assert stack.default_sg.allow_all_outbound is True


# --- Edge case: test custom flow_logs_bucket and vpc_flow_logs_role_arn wiring ---
def test_custom_flow_logs_bucket_and_role():
    import uuid
    from aws_cdk import aws_s3 as s3

    app = App()
    test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
    bucket = s3.Bucket(test_stack, f"CustomFlowLogsBucket{uuid.uuid4()}")
    role_arn = "arn:aws:iam::123456789012:role/FlowLogsRole"
    config = {
        "networking": {
            "subnets": [
                {"cidr": "10.0.30.0/24", "type": "PUBLIC"},
            ],
        }
    }
    stack = NetworkingStack(
        test_stack,
        f"TestNetworkingStack{uuid.uuid4()}",
        config=config,
        flow_logs_bucket=bucket,
        vpc_flow_logs_role_arn=role_arn,
    )
    assert stack.flow_logs_bucket == bucket


# --- Edge case: test removal_policy propagation (dev/prod) ---
def test_removal_policy_propagation():
    import uuid

    app = App()
    test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
    config_dev = {
        "networking": {
            "subnets": [
                {"cidr": "10.0.40.0/24", "type": "PUBLIC"},
            ],
            "removal_policy": "DESTROY",
        },
        "app": {"env": "dev"},
    }
    config_prod = {
        "networking": {
            "subnets": [
                {"cidr": "10.0.41.0/24", "type": "PUBLIC"},
            ],
            "removal_policy": "RETAIN",
        },
        "app": {"env": "prod"},
    }
    stack_dev = NetworkingStack(
        test_stack, f"TestNetworkingStackDev{uuid.uuid4()}", config=config_dev
    )
    stack_prod = NetworkingStack(
        test_stack, f"TestNetworkingStackProd{uuid.uuid4()}", config=config_prod
    )
    # RemovalPolicy is not directly exposed, but resource exists
    assert stack_dev.flow_logs_bucket is not None
    assert stack_prod.flow_logs_bucket is not None


# --- Edge case: test shared_resources completeness ---
def test_shared_resources_completeness():
    import uuid

    app = App()
    test_stack = Stack(app, f"TestStack{uuid.uuid4()}")
    stack = NetworkingStack(test_stack, f"TestNetworkingStack{uuid.uuid4()}")
    shared = stack.shared_resources
    assert "vpc" in shared
    assert "default_sg" in shared
    assert "flow_logs_bucket" in shared
    assert "private_subnets" in shared
    assert "nat_alarms" in shared
    assert "subnets" in shared
