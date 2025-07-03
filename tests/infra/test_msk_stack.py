import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.msk_stack import MskStack
from aws_cdk import aws_ec2 as ec2

class DummyVpc(ec2.Vpc):
    def __init__(self, scope, id):
        super().__init__(scope, id, max_azs=1)

@pytest.fixture
def msk_config():
    return {
        "msk": {
            "security_group": {
                "id": "MskSecurityGroup",
                "description": "Test SG",
                "allow_all_outbound": True
            },
            "cluster": {
                "id": "TestMskCluster",
                "name": "test-msk-cluster",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "enhanced_monitoring": "PER_TOPIC_PER_BROKER"
            },
            "tags": {"Owner": "KafkaTeam"}
        },
        "app": {"env": "test"}
    }

# --- Happy path: MSK cluster creation ---
def test_msk_stack_synthesizes(msk_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=msk_config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::MSK::Cluster", 1)
    outputs = template.to_json().get("Outputs", {})
    assert "TestMskStackMskClusterName" in outputs
    assert "TestMskStackMskClusterArn" in outputs
    assert "TestMskStackMskSecurityGroupId" in outputs

# --- Happy path: Tagging ---
def test_msk_stack_tags(msk_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=msk_config)
    tags = stack.tags.render_tags()
    assert any(tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI" for tag in tags)
    assert any(tag.get("Key") == "Owner" and tag.get("Value") == "KafkaTeam" for tag in tags)

# --- Unhappy path: Missing required cluster fields ---
def test_msk_stack_missing_required_fields():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {"id": "cid"}  # missing name, kafka_version, number_of_broker_nodes, instance_type
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        MskStack(app, "TestMskStack", vpc=vpc, config=config)

# --- Unhappy path: number_of_broker_nodes not int or < 1 ---
def test_msk_stack_invalid_broker_count():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid", "name": "n", "kafka_version": "3.5.1", "number_of_broker_nodes": 0, "instance_type": "kafka.m5.large"
            }
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        MskStack(app, "TestMskStack", vpc=vpc, config=config)

# --- Unhappy path: client_subnets not a list or empty ---
def test_msk_stack_invalid_client_subnets_notalist():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid", "name": "n", "kafka_version": "3.5.1", "number_of_broker_nodes": 1, "instance_type": "kafka.m5.large", "client_subnets": "notalist"
            }
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        MskStack(app, "TestMskStack", vpc=vpc, config=config)

def test_msk_stack_invalid_client_subnets_empty():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid", "name": "n", "kafka_version": "3.5.1", "number_of_broker_nodes": 1, "instance_type": "kafka.m5.large", "client_subnets": []
            }
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        MskStack(app, "TestMskStack", vpc=vpc, config=config)

# --- Unhappy path: security_groups not a list or empty ---
def test_msk_stack_invalid_security_groups_notalist():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid", "name": "n", "kafka_version": "3.5.1", "number_of_broker_nodes": 1, "instance_type": "kafka.m5.large", "security_groups": "notalist"
            }
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        MskStack(app, "TestMskStack", vpc=vpc, config=config)

def test_msk_stack_invalid_security_groups_empty():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid", "name": "n", "kafka_version": "3.5.1", "number_of_broker_nodes": 1, "instance_type": "kafka.m5.large", "security_groups": []
            }
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        MskStack(app, "TestMskStack", vpc=vpc, config=config)
