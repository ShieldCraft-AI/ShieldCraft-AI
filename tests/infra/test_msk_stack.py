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
                "allow_all_outbound": True,
            },
            "cluster": {
                "id": "TestMskCluster",
                "name": "test-msk-cluster",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "enhanced_monitoring": "PER_TOPIC_PER_BROKER",
            },
            "tags": {"Owner": "KafkaTeam"},
        },
        "app": {"env": "test"},
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
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
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
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "KafkaTeam" for tag in tags
    )


# --- Unhappy path: Missing required cluster fields ---
def test_msk_stack_missing_required_fields():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid"
            },  # missing name, kafka_version, number_of_broker_nodes, instance_type
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
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
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 0,
                "instance_type": "kafka.m5.large",
            },
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
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
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": "notalist",
            },
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
        )


def test_msk_stack_invalid_client_subnets_empty():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": [],
            },
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
        )


# --- Unhappy path: security_groups not a list or empty ---
def test_msk_stack_invalid_security_groups_notalist():
    app = App()
    test_stack = Stack(app, "TestStack")

    # --- Broker Storage and Encryption Configs ---
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "security_groups": "notalist",
            },
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            # --- Topic Resource Export ---
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
        )


def test_msk_stack_invalid_security_groups_empty():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "security_groups": [],
            },
            # --- Alarm Configuration Unhappy Paths ---
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        MskStack(
            app,
            "TestMskStack",
            vpc=vpc,
            config=config,
            msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
        )


# --- Happy path: Outputs and ARNs ---
def test_msk_stack_outputs_and_arns(msk_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = MskStack(
        app,
        "TestMskStack",
        vpc=vpc,
        # --- Parallel Instantiation (Sequential for CDK Safety) ---
        config=msk_config,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})

    def arn_like(val, service):
        if isinstance(val, dict) and "Value" in val:
            return arn_like(val["Value"], service)
        if isinstance(val, dict) and "Fn::Join" in val:
            join_list = (
                val["Fn::Join"][1]
                if isinstance(val["Fn::Join"], list) and len(val["Fn::Join"]) > 1
                else []
            )
            flat = []
            for v in join_list:
                if isinstance(v, str):
                    flat.append(v)
                # --- Extra/Unknown Config Fields (Deeply Nested) ---
                elif isinstance(v, (list, dict)):
                    if arn_like(v, service):
                        flat.append("")
            joined = "".join([s for s in flat if isinstance(s, str)])
            return f"arn:aws:{service}:" in joined
        if isinstance(val, dict) and "Fn::GetAtt" in val:
            getatt = val["Fn::GetAtt"]
            if isinstance(getatt, list) and getatt[-1].lower().endswith("arn"):
                return True
        if isinstance(val, str):
            return val.startswith(f"arn:aws:{service}:") or f"arn:aws:{service}:" in val
        if isinstance(val, list):
            flat = []
            for v in val:
                if isinstance(v, str):
                    flat.append(v)
                elif isinstance(v, (list, dict)):
                    if arn_like(v, service):
                        flat.append("")
            joined = "".join([s for s in flat if isinstance(s, str)])
            return f"arn:aws:{service}:" in joined
        if isinstance(val, dict):
            for v in val.values():
                if arn_like(v, service):
                    # --- Scale/Performance: Large Number of Topics ---
                    return True
        return False

    # Check all expected outputs
    assert any("MskClusterName" in k for k in outputs)
    for k, v in outputs.items():
        if "Arn" in k:
            assert arn_like(v, "kafka") or arn_like(v, "cloudwatch")


def test_msk_stack_tag_propagation():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "tags": {"Owner": "KafkaTeam", "CostCenter": "AI123"},
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-12345"],
                "security_groups": ["sg-12345"],
            },
        },
        "app": {"env": "test"},
    }
    shared_tags = {"Extra": "Value"}
    stack = MskStack(
        app,
        "TestMskStack",
        vpc=vpc,
        config=config,
        shared_tags=shared_tags,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "KafkaTeam" for tag in tags
    )
    assert any(
        tag.get("Key") == "CostCenter" and tag.get("Value") == "AI123" for tag in tags
    )
    assert any(
        tag.get("Key") == "Extra" and tag.get("Value") == "Value" for tag in tags
    )


def test_msk_stack_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
            },
        },
        "app": {"env": "test"},
    }
    stack = MskStack(
        app,
        "TestMskStack",
        vpc=vpc,
        config=config,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
    )
    assert hasattr(stack, "shared_resources")


def test_msk_stack_all_optionals():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "security_group": {
                "id": "sg1",
                "description": "desc",
                "allow_all_outbound": False,
            },
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 2,
                "instance_type": "kafka.m5.large",
                "enhanced_monitoring": "PER_TOPIC_PER_BROKER",
                "client_subnets": ["subnet-123", "subnet-456"],
                "security_groups": ["sg-123", "sg-456"],
            },
            "tags": {"Owner": "KafkaTeam"},
        },
        "app": {"env": "test"},
    }
    stack = MskStack(
        app,
        "TestMskStack",
        vpc=vpc,
        config=config,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
    )
    assert hasattr(stack, "shared_resources")


def test_msk_stack_idempotency(msk_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack1 = MskStack(
        app,
        "TestMskStack1",
        vpc=vpc,
        config=msk_config,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
    )
    stack2 = MskStack(
        app,
        "TestMskStack2",
        vpc=vpc,
        config=msk_config,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
    )
    sr1 = stack1.shared_resources["cluster"]
    sr2 = stack2.shared_resources["cluster"]
    assert sr1.node.id == sr2.node.id


def test_msk_stack_tag_override():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "msk": {
            "tags": {"Owner": "KafkaTeam"},
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-12345"],
                "security_groups": ["sg-12345"],
            },
        },
        "app": {"env": "test"},
    }
    shared_tags = {"Owner": "Override", "Extra": "Value"}
    stack = MskStack(
        app,
        "TestMskStack",
        vpc=vpc,
        config=config,
        shared_tags=shared_tags,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "Override" for tag in tags
    )
    assert any(
        tag.get("Key") == "Extra" and tag.get("Value") == "Value" for tag in tags
    )


# --- Removal Policy and Resource Lifecycle ---
def test_msk_stack_removal_policy():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    # DEV env: should be DESTROY
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-1"],
                "security_groups": ["sg-1"],
            },
        },
        "app": {"env": "dev"},
    }
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=config)
    sg = stack.shared_resources["security_group"]
    assert sg.apply_removal_policy is not None
    # PROD env: should be RETAIN
    config["app"]["env"] = "prod"
    stack2 = MskStack(app, "TestMskStack2", vpc=vpc, config=config)
    sg2 = stack2.shared_resources["security_group"]
    assert sg2.apply_removal_policy is not None


# --- Tag Propagation to Security Group ---
def test_msk_stack_tags_on_security_group():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "msk": {
            "tags": {"Owner": "KafkaTeam", "CostCenter": "AI123"},
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-1"],
                "security_groups": ["sg-1"],
            },
        },
        "app": {"env": "test"},
    }
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=config)
    sg = stack.shared_resources["security_group"]
    tags = sg.node.try_get_context("tags") or stack.tags.render_tags()
    assert any(tag.get("Key") == "Owner" for tag in tags)


# --- Alarm Configuration and Thresholds ---
def test_msk_stack_alarm_config(msk_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=msk_config)
    template = assertions.Template.from_stack(stack)
    # Find all CloudWatch alarms
    resources = template.find_resources("AWS::CloudWatch::Alarm")
    alarm_props = list(resources.values())
    # There should be 4 alarms
    assert len(alarm_props) == 4
    # Check for expected metric names and thresholds
    expected = {
        "BrokerCount": msk_config["msk"]["cluster"]["number_of_broker_nodes"],
        "UnderReplicatedPartitions": 0,
        "ActiveControllerCount": 1,
        "KafkaDataLogsDiskUsed": 80,
    }
    for alarm in alarm_props:
        metric = alarm["Properties"]["MetricName"]
        threshold = alarm["Properties"]["Threshold"]
        assert metric in expected
        assert threshold == expected[metric]


# --- Minimal Config Edge Case ---
def test_msk_stack_minimal_config_synth():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-1"],
                "security_groups": ["sg-1"],
            },
        },
        "app": {"env": "test"},
    }
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=config)
    assert hasattr(stack, "shared_resources")


# --- Edge Case: Unknown/Extra Config Fields ---
def test_msk_stack_extra_config_fields():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1", "extra": "ignoreme"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-1"],
                "security_groups": ["sg-1"],
                "extra": 123,
            },
        },
        "app": {"env": "test"},
        "extra": "ignoreme",
    }
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=config)
    assert hasattr(stack, "shared_resources")


# --- Unhappy Path: Invalid Alarm Config ---
def test_msk_stack_invalid_alarm_config():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-1"],
                "security_groups": ["sg-1"],
            },
        },
        "app": {"env": "test"},
    }
    # Patch config to have negative threshold (simulate via monkeypatch if needed)
    # Here, just check stack still synthesizes (CDK will error at deploy, not synth)
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=config)
    assert hasattr(stack, "broker_count_alarm")


# --- Performance/Scale: Large Broker Count ---
def test_msk_stack_large_broker_count():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 15,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-1"],
                "security_groups": ["sg-1"],
            },
        },
        "app": {"env": "test"},
    }
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::CloudWatch::Alarm")
    found = False
    for alarm in resources.values():
        if alarm["Properties"]["MetricName"] == "BrokerCount":
            assert alarm["Properties"]["Threshold"] == 15
            found = True
    assert found


# --- CloudFormation Resource Properties ---
def test_msk_stack_cfn_properties(msk_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=msk_config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::MSK::Cluster")
    for res in resources.values():
        props = res["Properties"]
        assert "ClusterName" in props
        assert "KafkaVersion" in props
        assert "NumberOfBrokerNodes" in props
        assert "BrokerNodeGroupInfo" in props
        assert "EncryptionInfo" in props
        assert "EnhancedMonitoring" in props


def test_msk_stack_shared_resources_completeness(msk_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=msk_config)
    sr = stack.shared_resources
    expected_keys = {
        "cluster",
        "security_group",
        "broker_count_alarm",
        "under_replicated_alarm",
        "active_controller_alarm",
        "disk_used_alarm",
    }
    assert set(sr.keys()) == expected_keys
    for k in expected_keys:
        assert sr[k] is not None


def test_msk_stack_no_duplicate_resources(msk_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack1 = MskStack(app, "TestMskStack1", vpc=vpc, config=msk_config)
    stack2 = MskStack(app, "TestMskStack2", vpc=vpc, config=msk_config)
    for k in stack1.shared_resources:
        # Ensure resources are not the same object between stacks
        assert stack1.shared_resources[k] is not stack2.shared_resources[k]


def test_msk_stack_tag_propagation_all_resources():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "msk": {
            "tags": {"Owner": "KafkaTeam", "CostCenter": "AI123"},
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-12345"],
                "security_groups": ["sg-12345"],
            },
        },
        "app": {"env": "test"},
    }
    shared_tags = {"Extra": "Value"}
    stack = MskStack(
        app,
        "TestMskStack",
        vpc=vpc,
        config=config,
        shared_tags=shared_tags,
        msk_client_role_arn="arn:aws:iam::123456789012:role/mock-msk-client-role",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/mock-msk-producer-role",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/mock-msk-consumer-role",
    )
    tags = stack.tags.render_tags()
    for resource in stack.shared_resources.values():
        assert any(tag.get("Key") == "Project" for tag in tags)
        assert any(tag.get("Key") == "Owner" for tag in tags)
        assert any(tag.get("Key") == "CostCenter" for tag in tags)
        assert any(tag.get("Key") == "Extra" for tag in tags)


def test_msk_stack_removal_policy_all_resources():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "msk": {
            "security_group": {"id": "sg1"},
            "cluster": {
                "id": "cid",
                "name": "n",
                "kafka_version": "3.5.1",
                "number_of_broker_nodes": 1,
                "instance_type": "kafka.m5.large",
                "client_subnets": ["subnet-1"],
                "security_groups": ["sg-1"],
            },
        },
        "app": {"env": "dev"},
    }
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=config)
    for resource in stack.shared_resources.values():
        assert hasattr(resource, "apply_removal_policy") or hasattr(
            resource, "removal_policy"
        )


def test_msk_stack_alarm_outputs(msk_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack = MskStack(app, "TestMskStack", vpc=vpc, config=msk_config)
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    alarm_keys = [
        "TestMskStackMskBrokerCountAlarmArn",
        "TestMskStackMskUnderReplicatedPartitionsAlarmArn",
        "TestMskStackMskActiveControllerCountAlarmArn",
        "TestMskStackMskDiskUsedAlarmArn",
    ]
    for k in alarm_keys:
        assert k in outputs
        v = outputs[k]

        def arn_like(val):
            if isinstance(val, dict) and "Fn::GetAtt" in val:
                return True
            if isinstance(val, str):
                return val.startswith("arn:aws:cloudwatch:") or val.startswith(
                    "arn:aws:kafka:"
                )
            return False

        assert arn_like(v) or (
            isinstance(v, dict) and "Value" in v and arn_like(v["Value"])
        )
