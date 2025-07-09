import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.data.airbyte_stack import AirbyteStack
from aws_cdk import aws_ec2 as ec2


class DummyVpc(ec2.Vpc):
    def __init__(self, scope, id):
        super().__init__(scope, id, max_azs=1)


@pytest.fixture
def airbyte_config():
    return {
        "app": {"env": "test"},
        "airbyte": {"instance_type": "t3.medium", "desired_count": 1},
    }


# --- Happy path: Outputs ---


# --- Happy path: Secret injection ---
def test_airbyte_stack_secret_injection(monkeypatch, airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    from aws_cdk import aws_secretsmanager as secretsmanager

    secret = secretsmanager.Secret(test_stack, "DummySecret")
    config = airbyte_config.copy()
    config["airbyte"]["db_secret_arn"] = secret.secret_arn
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::ECS::TaskDefinition")
    found = False
    for td in resources.values():
        container_defs = td["Properties"].get("ContainerDefinitions", [])
        for cdef in container_defs:
            if "Secrets" in cdef:
                found = True
    assert found


# --- Happy path: Monitoring outputs ---
def test_airbyte_stack_monitoring_outputs(airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=airbyte_config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    # Monitoring resources present
    assert hasattr(stack, "ecs_task_alarm")
    assert hasattr(stack, "alb_5xx_alarm")
    assert stack.ecs_task_alarm.alarm_arn is not None
    assert stack.alb_5xx_alarm.alarm_arn is not None
    # Shared resources dict exposes alarms
    assert stack.shared_resources["task_alarm"] == stack.ecs_task_alarm
    assert stack.shared_resources["alb_5xx_alarm"] == stack.alb_5xx_alarm


# --- Happy path: Security group ingress config ---


# --- Happy path: Minimal config ---
def test_airbyte_stack_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    minimal_config = {"airbyte": {}}
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=minimal_config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    assert hasattr(stack, "cluster")


# --- Happy path: Environment-specific config ---
import copy
import pytest


@pytest.mark.parametrize("env", ["dev", "staging", "prod"])
def test_airbyte_stack_env_config(env):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "app": {"env": env},
        "airbyte": {"instance_type": "t3.medium", "desired_count": 1},
    }
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    assert hasattr(stack, "cluster")


# --- Unhappy path: Unknown config keys (should not raise) ---
def test_airbyte_stack_unknown_config_keys():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "app": {"env": "test"},
        "airbyte": {
            "instance_type": "t3.medium",
            "desired_count": 1,
            "unknown_key": 123,
        },
    }
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    assert hasattr(stack, "cluster")


# --- Happy path: Tagging (if implemented) ---
def test_airbyte_stack_tags(airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=airbyte_config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )


# --- Happy path: Synthesis and resource count ---
def test_airbyte_stack_synthesizes(airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=airbyte_config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::ECS::Cluster", 1)


# --- Happy path: ECS Cluster and Security Group properties ---
def test_airbyte_cluster_vpc_association(airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=airbyte_config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    assert stack.cluster.vpc == vpc


def test_airbyte_security_group_properties(airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=airbyte_config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    sg = [c for c in stack.node.children if isinstance(c, ec2.SecurityGroup)]
    assert sg, "SecurityGroup not created"
    assert sg[0].allow_all_outbound is True


# --- Happy path: DB Secret optionality ---
def test_airbyte_stack_with_db_secret(monkeypatch, airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    from aws_cdk import aws_secretsmanager as secretsmanager

    secret = secretsmanager.Secret(test_stack, "DummySecret2")
    config = airbyte_config.copy()
    config["airbyte"]["db_secret_arn"] = secret.secret_arn
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    assert hasattr(stack, "cluster")


# --- Unhappy path: Missing VPC ---
def test_airbyte_stack_missing_vpc_raises(airbyte_config):
    app = App()
    with pytest.raises(AssertionError):
        AirbyteStack(
            app,
            "TestAirbyteStack",
            vpc=None,
            config=airbyte_config,
            airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
        )


# --- Unhappy path: Invalid config values ---
@pytest.mark.parametrize(
    "bad_config",
    [
        {
            "app": {"env": "test"},
            "airbyte": {"instance_type": "t3.medium", "desired_count": -1},
        },
    ],
)
def test_airbyte_stack_invalid_config(bad_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    import pytest

    with pytest.raises(ValueError):
        AirbyteStack(
            app,
            "TestAirbyteStack",
            vpc=vpc,
            config=bad_config,
            airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
        )


# --- Unhappy path: Invalid secret ARN ---
def test_airbyte_stack_invalid_secret_arn(monkeypatch, airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = airbyte_config.copy()
    config["airbyte"]["db_secret_arn"] = "invalid-arn"

    def raise_exc(*a, **k):
        raise ValueError("Invalid ARN")

    monkeypatch.setattr(
        "aws_cdk.aws_secretsmanager.Secret.from_secret_complete_arn", raise_exc
    )
    with pytest.raises(ValueError):
        AirbyteStack(
            app,
            "TestAirbyteStack",
            vpc=vpc,
            config=config,
            airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
        )


# --- Supplementary: Outputs (ALB DNS, ECS Service Name, Log Group) ---


# --- Supplementary: Secret injection into ECS task definition ---
def test_airbyte_stack_secret_env(monkeypatch, airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = airbyte_config.copy()
    config["airbyte"][
        "db_secret_arn"
    ] = "arn:aws:secretsmanager:af-south-1:123456789012:secret:dummy"
    # Patch Secret.from_secret_complete_arn to avoid AWS call
    from aws_cdk import aws_secretsmanager as secretsmanager

    secret = secretsmanager.Secret(test_stack, "DummySecret3")
    config = airbyte_config.copy()
    config["airbyte"]["db_secret_arn"] = secret.secret_arn
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::ECS::TaskDefinition")
    found = False
    for td in resources.values():
        container_defs = td["Properties"].get("ContainerDefinitions", [])
        for cdef in container_defs:
            secrets = cdef.get("Secrets", [])
            print(f"DEBUG: ContainerDefinition Secrets: {secrets}")
            if any(s.get("Name") == "AIRBYTE_DB_SECRET" for s in secrets):
                found = True
    assert found, "AIRBYTE_DB_SECRET not found in ECS container secrets."


# --- Supplementary: Health check config ---
def test_airbyte_stack_health_check_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "app": {"env": "test"},
        "airbyte": {
            "instance_type": "t3.medium",
            "desired_count": 1,
            "health_check_path": "/custom/health",
            "health_check_codes": "200-299",
        },
    }
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    # Find the ALB and listener
    alb = stack.alb
    listeners = [c for c in alb.node.children if hasattr(c, "add_targets")]
    assert listeners, "No ALB listener found"
    # We can't directly inspect the health check, but we can check the synthesized template
    template = assertions.Template.from_stack(stack)
    resources = template.to_json().get("Resources", {})
    # Find the TargetGroup and check HealthCheckPath and Matcher
    tg = [
        v
        for v in resources.values()
        if v["Type"] == "AWS::ElasticLoadBalancingV2::TargetGroup"
    ]
    assert tg, "No TargetGroup found"
    props = tg[0]["Properties"]
    assert props["HealthCheckPath"] == "/custom/health"
    assert props["Matcher"]["HttpCode"] == "200-299"


# --- Supplementary: Security group ingress (allowed CIDR) ---
def test_airbyte_stack_allowed_cidr():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "app": {"env": "test"},
        "airbyte": {
            "instance_type": "t3.medium",
            "desired_count": 1,
            "allowed_cidr": "10.0.0.0/16",
        },
    }
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::EC2::SecurityGroup")
    found = False
    for sg in resources.values():
        ingress = sg["Properties"].get("SecurityGroupIngress", [])
    for rule in ingress:
        if rule.get("CidrIp") == "10.0.0.0/16":
            found = True
    assert found


# --- Supplementary: Unhappy path for invalid cpu/memory ---
import pytest


@pytest.mark.parametrize(
    "cpu,memory",
    [
        (128, 2048),  # cpu too low
        (1024, 256),  # memory too low
        ("bad", 2048),  # cpu not int
        (1024, "bad"),  # memory not int
    ],
)
def test_airbyte_stack_invalid_cpu_memory(cpu, memory, airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = copy.deepcopy(airbyte_config)
    config["airbyte"]["cpu"] = cpu
    config["airbyte"]["memory"] = memory
    with pytest.raises(ValueError):
        AirbyteStack(
            app,
            "TestAirbyteStack",
            vpc=vpc,
            config=config,
            airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
        )


# --- Supplementary: Output ARNs and DNS ---
def test_airbyte_stack_outputs_present(airbyte_config):
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=airbyte_config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
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
                elif isinstance(v, (list, dict)):
                    if arn_like(v, service):
                        flat.append("")
            joined = "".join([s for s in flat if isinstance(s, str)])
            return f"arn:aws:{service}:" in joined
        if isinstance(val, dict) and "Fn::GetAtt" in val:
            # CDK GetAtt for ARNs
            getatt = val["Fn::GetAtt"]
            if isinstance(getatt, list) and getatt[-1] == "Arn":
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
                    return True
        return False

    # Check all expected outputs
    assert any("ALBDns" in k for k in outputs)
    assert any("ServiceName" in k for k in outputs)
    assert any("LogGroupName" in k for k in outputs)
    assert any("AlarmArn" in k for k in outputs)
    # Check ARNs are valid
    for k, v in outputs.items():
        if "AlarmArn" in k:
            assert arn_like(v, "cloudwatch")


# --- Supplementary: Removal Policy ---
def test_airbyte_stack_removal_policy_dev():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {"app": {"env": "dev"}, "airbyte": {}}
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Logs::LogGroup")
    log_group = list(resources.values())[0]
    assert log_group["DeletionPolicy"] == "Delete"


def test_airbyte_stack_removal_policy_prod():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {"app": {"env": "prod"}, "airbyte": {}}
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Logs::LogGroup")
    log_group = list(resources.values())[0]
    assert log_group["DeletionPolicy"] == "Retain"


# --- Supplementary: Invalid removal_policy and subnet_type fallback ---
def test_airbyte_stack_invalid_removal_policy_and_subnet_type():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "app": {"env": "prod"},
        "airbyte": {
            "removal_policy": "notarealpolicy",
            "subnet_type": "notarealsubnet",
        },
    }
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Logs::LogGroup")
    log_group = list(resources.values())[0]
    assert log_group["DeletionPolicy"] == "Retain"


# --- Supplementary: Tag Propagation ---
def test_airbyte_stack_tag_propagation():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "app": {"env": "test"},
        "airbyte": {"tags": {"Owner": "DataTeam", "CostCenter": "AI123"}},
    }
    shared_tags = {"Extra": "Value"}
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
        shared_tags=shared_tags,
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "DataTeam" for tag in tags
    )
    assert any(
        tag.get("Key") == "CostCenter" and tag.get("Value") == "AI123" for tag in tags
    )
    assert any(
        tag.get("Key") == "Extra" and tag.get("Value") == "Value" for tag in tags
    )


# --- Supplementary: Security Group Ingress ---
def test_airbyte_stack_security_group_ingress():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "app": {"env": "test"},
        "airbyte": {"allowed_cidr": "1.2.3.4/32"},
    }
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.to_json().get("Resources", {})
    found = False
    # Check standalone SecurityGroupIngress resources
    for res in resources.values():
        if res.get("Type") == "AWS::EC2::SecurityGroupIngress":
            props = res.get("Properties", {})
            if props.get("CidrIp") == "1.2.3.4/32":
                found = True
    # Also check SecurityGroupIngress property inside SecurityGroup resources
    for res in resources.values():
        if res.get("Type") == "AWS::EC2::SecurityGroup":
            ingress = res.get("Properties", {}).get("SecurityGroupIngress", [])
            if isinstance(ingress, dict):
                ingress = [ingress]
            for rule in ingress:
                if rule.get("CidrIp") == "1.2.3.4/32":
                    found = True
    assert found


# --- Supplementary: ALB Health Check config in template ---
def test_airbyte_stack_health_check_in_template():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = DummyVpc(test_stack, "DummyVpc")
    config = {
        "app": {"env": "test"},
        "airbyte": {
            "health_check_path": "/custom/health",
            "health_check_codes": "200-299",
        },
    }
    stack = AirbyteStack(
        app,
        "TestAirbyteStack",
        vpc=vpc,
        config=config,
        airbyte_role_arn="arn:aws:iam::123456789012:role/mock-airbyte-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.to_json().get("Resources", {})
    found_path = False
    found_codes = False
    for res in resources.values():
        props = res.get("Properties", {})
        if "HealthCheckPath" in props and props["HealthCheckPath"] == "/custom/health":
            found_path = True
        if (
            "Matcher" in props
            and "HttpCode" in props["Matcher"]
            and props["Matcher"]["HttpCode"] == "200-299"
        ):
            found_codes = True
    assert found_path
    assert found_codes
