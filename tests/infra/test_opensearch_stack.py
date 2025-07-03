import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.opensearch_stack import OpenSearchStack
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
                "allow_all_outbound": True
            },
            "domain": {
                "id": "TestOpenSearchDomain",
                "name": "test-opensearch",
                "engine_version": "OpenSearch_2.11",
                "cluster_config": {
                    "instanceType": "t3.small.search",
                    "instanceCount": 1
                },
                "node_to_node_encryption_options": {"enabled": True},
                "encryption_at_rest_options": {"enabled": True},
                "ebs_options": {"ebsEnabled": True, "volumeSize": 10, "volumeType": "gp3"}
            },
            "tags": {"Owner": "SearchTeam"}
        },
        "app": {"env": "test"}
    }

# --- Happy path: OpenSearch domain creation ---
def test_opensearch_stack_synthesizes(opensearch_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=opensearch_config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::OpenSearchService::Domain", 1)
    outputs = template.to_json().get("Outputs", {})
    assert "TestOpenSearchStackOpenSearchDomainName" in outputs
    assert "TestOpenSearchStackOpenSearchDomainArn" in outputs
    assert "TestOpenSearchStackOpenSearchSecurityGroupId" in outputs

# --- Happy path: Tagging ---
def test_opensearch_stack_tags(opensearch_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=opensearch_config)
    tags = stack.tags.render_tags()
    assert any(tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI" for tag in tags)
    assert any(tag.get("Key") == "Owner" and tag.get("Value") == "SearchTeam" for tag in tags)

# --- Unhappy path: Missing required domain fields ---
def test_opensearch_stack_missing_required_fields():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {"id": "did"}  # missing name, engine_version
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)

# --- Unhappy path: subnet_ids not a list or empty ---
def test_opensearch_stack_invalid_subnet_ids_notalist():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did", "name": "n", "engine_version": "OpenSearch_2.11", "subnet_ids": "notalist"
            }
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)

def test_opensearch_stack_invalid_subnet_ids_empty():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did", "name": "n", "engine_version": "OpenSearch_2.11", "subnet_ids": []
            }
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)

# --- Unhappy path: security_group_ids not a list or empty ---
def test_opensearch_stack_invalid_security_group_ids_notalist():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did", "name": "n", "engine_version": "OpenSearch_2.11", "security_group_ids": "notalist"
            }
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)

def test_opensearch_stack_invalid_security_group_ids_empty():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "opensearch": {
            "security_group": {"id": "sg1"},
            "domain": {
                "id": "did", "name": "n", "engine_version": "OpenSearch_2.11", "security_group_ids": []
            }
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        OpenSearchStack(app, "TestOpenSearchStack", vpc=vpc, config=config)
