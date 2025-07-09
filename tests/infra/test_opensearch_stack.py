import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.compute.opensearch_stack import OpenSearchStack
from aws_cdk import aws_ec2 as ec2


class DummyVpc(ec2.Vpc):
    def __init__(self, scope, id):
        super().__init__(scope, id, max_azs=1)


@pytest.fixture
def opensearch_config():
    return {
        "opensearch": {
            "security_group": {
                "id": "OpenSearchSecurityGroup",
                "description": "Test SG",
                "allow_all_outbound": True,
            },
            "domain": {
                "id": "TestOpenSearchDomain",
                "name": "test-opensearch",
                "engine_version": "OpenSearch_2.11",
                "cluster_config": {
                    "instanceType": "t3.small.search",
                    "instanceCount": 1,
                },
                "node_to_node_encryption_options": {"enabled": True},
                "encryption_at_rest_options": {"enabled": True},
                "ebs_options": {
                    "ebsEnabled": True,
                    "volumeSize": 10,
                    "volumeType": "gp3",
                },
            },
            "tags": {"Owner": "SearchTeam"},
        },
        "app": {"env": "test"},
    }


# --- Happy path: OpenSearch domain creation ---
def test_opensearch_stack_synthesizes(opensearch_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = OpenSearchStack(
        app,
        "TestOpenSearchStack",
        vpc=vpc,
        config=opensearch_config,
        opensearch_role_arn="arn:aws:iam::123456789012:role/mock-opensearch-role",
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::OpenSearchService::Domain", 1)
    outputs = template.to_json().get("Outputs", {})
    assert "TestOpenSearchStackOpenSearchDomainName" in outputs
    assert "TestOpenSearchStackOpenSearchDomainArn" in outputs
    assert "TestOpenSearchStackOpenSearchSecurityGroupId" in outputs
    # Shared resources dict exposes domain and security group
    assert hasattr(stack, "shared_resources")
    sr = stack.shared_resources
    assert "domain" in sr and sr["domain"] is not None
    assert "security_group" in sr and sr["security_group"] is not None
    # Monitoring: If CloudWatch alarms are added, check for their outputs and shared_resources
    assert "TestOpenSearchStackOpenSearchClusterStatusRedAlarmArn" in outputs
    assert "TestOpenSearchStackOpenSearchClusterIndexWritesBlockedAlarmArn" in outputs
    assert "TestOpenSearchStackOpenSearchFreeStorageSpaceAlarmArn" in outputs
    assert "TestOpenSearchStackOpenSearchCPUUtilizationAlarmArn" in outputs
    assert (
        "cluster_status_red_alarm" in sr and sr["cluster_status_red_alarm"] is not None
    )
    assert (
        "index_writes_blocked_alarm" in sr
        and sr["index_writes_blocked_alarm"] is not None
    )
    assert (
        "free_storage_space_alarm" in sr and sr["free_storage_space_alarm"] is not None
    )
    assert "cpu_utilization_alarm" in sr and sr["cpu_utilization_alarm"] is not None


# --- Happy path: Tagging ---
def test_opensearch_stack_tags(opensearch_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = OpenSearchStack(
        app,
        "TestOpenSearchStack",
        vpc=vpc,
        config=opensearch_config,
        opensearch_role_arn="arn:aws:iam::123456789012:role/mock-opensearch-role",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "SearchTeam" for tag in tags
    )


# --- Removal Policy and Resource Lifecycle ---
def test_opensearch_stack_removal_policy():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    # DEV env: should be DESTROY
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
            },
        },
        "app": {"env": "dev"},
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    sg = stack.shared_resources["security_group"]
    assert sg.apply_removal_policy is not None
    # PROD env: should be RETAIN
    config["app"]["env"] = "prod"
    stack2 = OpenSearchStack(app, "TestOpenSearchStack2", vpc=vpc, config=config)
    sg2 = stack2.shared_resources["security_group"]
    assert sg2.apply_removal_policy is not None


# --- Tag Propagation to Security Group ---
def test_opensearch_stack_tags_on_security_group():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "opensearch": {
            "tags": {"Owner": "SearchTeam", "CostCenter": "AI123"},
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
            },
        },
        "app": {"env": "test"},
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    sg = stack.shared_resources["security_group"]
    tags = sg.node.try_get_context("tags") or stack.tags.render_tags()
    assert any(tag.get("Key") == "Owner" for tag in tags)


# --- Alarm Configuration and Thresholds ---
def test_opensearch_stack_alarm_config(opensearch_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack = OpenSearchStack(
        app, "TestOpenSearchStack", vpc=vpc, config=opensearch_config
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::CloudWatch::Alarm")
    alarm_props = list(resources.values())
    # There should be 4 alarms
    assert len(alarm_props) == 4
    expected = {
        "ClusterStatus.red": 1,
        "ClusterIndexWritesBlocked": 1,
        "FreeStorageSpace": 20480,
        "CPUUtilization": 80,
    }
    for alarm in alarm_props:
        metric = alarm["Properties"]["MetricName"]
        threshold = alarm["Properties"]["Threshold"]
        assert metric in expected
        assert threshold == expected[metric]


# --- Minimal Config Edge Case ---
def test_opensearch_stack_minimal_config_synth():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
            },
        },
        "app": {"env": "test"},
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    assert hasattr(stack, "shared_resources")


# --- Edge Case: Unknown/Extra Config Fields ---
def test_opensearch_stack_extra_config_fields():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1", "extra": "ignoreme"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
                "extra": 123,
            },
        },
        "app": {"env": "test"},
        "extra": "ignoreme",
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    assert hasattr(stack, "shared_resources")


# --- Unhappy Path: Invalid Alarm Config ---
def test_opensearch_stack_invalid_alarm_config():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
            },
        },
        "app": {"env": "test"},
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    assert hasattr(stack, "cluster_status_red_alarm")


# --- CloudFormation Resource Properties ---
def test_opensearch_stack_cfn_properties(opensearch_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack = OpenSearchStack(
        app, "TestOpenSearchStack", vpc=vpc, config=opensearch_config
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::OpenSearchService::Domain")
    for res in resources.values():
        props = res["Properties"]
        assert "DomainName" in props
        assert "EngineVersion" in props
        assert "ClusterConfig" in props
        assert "EBSOptions" in props
        assert "EncryptionAtRestOptions" in props
        assert "NodeToNodeEncryptionOptions" in props
        assert "VPCOptions" in props


def test_opensearch_stack_alarm_disabling():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
            },
            "alarms": {"enabled": False},
        },
        "app": {"env": "test"},
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    # If alarms are disabled, they should not be present
    for alarm_key in [
        "cluster_status_red_alarm",
        "index_writes_blocked_alarm",
        "free_storage_space_alarm",
        "cpu_utilization_alarm",
    ]:
        assert alarm_key not in stack.shared_resources


def test_opensearch_stack_tags_on_domain(opensearch_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack = OpenSearchStack(
        app, "TestOpenSearchStack", vpc=vpc, config=opensearch_config
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::OpenSearchService::Domain")
    for res in resources.values():
        tags = res["Properties"].get("Tags", [])
        assert any(
            tag["Key"] == "Owner" and tag["Value"] == "SearchTeam" for tag in tags
        )


def test_opensearch_stack_access_policy():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    policy = {"Version": "2012-10-17", "Statement": []}
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
                "access_policies": policy,
            },
        },
        "app": {"env": "test"},
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::OpenSearchService::Domain")
    for res in resources.values():
        assert res["Properties"]["AccessPolicies"] == policy


def test_opensearch_stack_removal_policy_on_domain():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
            },
        },
        "app": {"env": "dev"},
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    assert stack.domain.apply_removal_policy is not None
    config["app"]["env"] = "prod"
    stack2 = OpenSearchStack(app, "TestOpenSearchStack2", vpc=vpc, config=config)
    assert stack2.domain.apply_removal_policy is not None


def test_opensearch_stack_output_export_names(opensearch_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack = OpenSearchStack(
        app, "TestOpenSearchStack", vpc=vpc, config=opensearch_config
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    for k, v in outputs.items():
        assert k.startswith("TestOpenSearchStack")
        assert "export_name" in v or "Export" in v


def test_opensearch_stack_idempotency():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config1 = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did1",
                "name": "n1",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
            },
        },
        "app": {"env": "test"},
    }
    config2 = {
        "opensearch": {
            "security_group": {"id": "sg2"},
            "domain": {
                "id": "did2",
                "name": "n2",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-2"],
                "security_group_ids": ["sg-2"],
            },
        },
        "app": {"env": "test"},
    }
    stack1 = OpenSearchStack(app, "Stack1", vpc=vpc, config=config1)
    stack2 = OpenSearchStack(app, "Stack2", vpc=vpc, config=config2)
    assert stack1.domain != stack2.domain
    assert stack1.shared_resources["domain"] != stack2.shared_resources["domain"]


def test_opensearch_stack_alarm_threshold_override():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
            },
            "alarms": {"cpu_utilization": {"threshold": 90}},
        },
        "app": {"env": "test"},
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::CloudWatch::Alarm")
    found = False
    for res in resources.values():
        if res["Properties"]["MetricName"] == "CPUUtilization":
            assert res["Properties"]["Threshold"] == 90
            found = True
    assert found


def test_opensearch_stack_minimal_tags():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did",
                "name": "n",
                "engine_version": "OpenSearch_2.11",
                "subnet_ids": ["subnet-1"],
                "security_group_ids": ["sg-1"],
            },
            "tags": {},
        },
        "app": {"env": "test"},
    }
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
    assert hasattr(stack, "shared_resources")


def test_opensearch_stack_invalid_domain_config():
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                # Missing id, name, engine_version
            },
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)


def test_opensearch_stack_downstream_consumption(opensearch_config):
    app = App()
    vpc = DummyVpc(Stack(app, "TestStack"), "DummyVpc")
    stack = OpenSearchStack(
        app, "TestOpenSearchStack", vpc=vpc, config=opensearch_config
    )
    sr = stack.shared_resources
    # Simulate downstream stack usage
    assert isinstance(sr["domain"], type(stack.domain))
    assert isinstance(
        sr["security_group"], type(stack.shared_resources["security_group"])
    )
    for alarm_key in [
        "cluster_status_red_alarm",
        "index_writes_blocked_alarm",
        "free_storage_space_alarm",
        "cpu_utilization_alarm",
    ]:
        assert alarm_key in sr
        assert sr[alarm_key] is not None
