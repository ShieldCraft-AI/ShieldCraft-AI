import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.compute.msk_stack import MskStack
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
    stack = MskStack(
        app,
        "TestMskStack",
        vpc=vpc,
        config=msk_config,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role"
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::MSK::Cluster", 1)
    outputs = template.to_json().get("Outputs", {})
    # Check for all expected outputs (cluster, SG, and alarms)
    assert "TestMskStackMskClusterName" in outputs
    assert "TestMskStackMskClusterArn" in outputs
    assert "TestMskStackMskSecurityGroupId" in outputs
    assert "TestMskStackMskBrokerCountAlarmArn" in outputs
    assert "TestMskStackMskUnderReplicatedPartitionsAlarmArn" in outputs
    assert "TestMskStackMskActiveControllerCountAlarmArn" in outputs
    assert "TestMskStackMskDiskUsedAlarmArn" in outputs
    # Shared resources dict exposes cluster, SG, and alarms
    assert hasattr(stack, "shared_resources")
    sr = stack.shared_resources
    assert "cluster" in sr and sr["cluster"] is not None
    assert "security_group" in sr and sr["security_group"] is not None
    assert "broker_count_alarm" in sr and sr["broker_count_alarm"] is not None
    assert "under_replicated_alarm" in sr and sr["under_replicated_alarm"] is not None
    assert "active_controller_alarm" in sr and sr["active_controller_alarm"] is not None
    assert "disk_used_alarm" in sr and sr["disk_used_alarm"] is not None

# --- Happy path: Tagging ---
def test_msk_stack_tags(msk_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = MskStack(
        app,
        "TestMskStack",
        vpc=vpc,
        config=msk_config,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role"
    )
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
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role"
        )

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
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role"
        )

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
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role"
        )

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
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role"
        )

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
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role"
        )

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
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role"
        )
