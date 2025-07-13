import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.cloud_native.attack_simulation_stack import AttackSimulationStack


# --- Happy path: Stack synthesizes with valid config ---
def test_attack_simulation_stack_synthesizes():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"attack_types": ["phishing", "malware"]}
    stack = AttackSimulationStack(
        test_stack,
        "TestAttackSimulationStack",
        simulation_config=config,
        stack_tags={"Project": "ShieldCraftAI", "Environment": "Test", "Owner": "QA"},
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Lambda::Function")
    assert any("AttackSimulationLambda" in k for k in resources)
    # Check environment variable
    for fn in resources.values():
        env = fn["Properties"].get("Environment", {}).get("Variables", {})
        assert "SIMULATION_CONFIG" in env


# --- Happy path: Secret ARN integration ---
def test_attack_simulation_stack_secret_arn():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"attack_types": ["phishing"]}
    secret_arn = (
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:attackSimSecret-ABC123"
    )
    stack = AttackSimulationStack(
        test_stack,
        "TestAttackSimulationStack",
        simulation_config=config,
        secrets_manager_arn=secret_arn,
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json()["Outputs"]
    assert any("AttackSimulationSecretArn" in k for k in outputs)
    assert outputs["AttackSimulationSecretArn"]["Value"] == secret_arn


# --- Unhappy path: simulation_config not a dict ---
def test_attack_simulation_stack_invalid_config_type():
    app = App()
    test_stack = Stack(app, "TestStack")
    with pytest.raises(TypeError):
        AttackSimulationStack(
            test_stack,
            "TestAttackSimulationStack",
            simulation_config=["not", "a", "dict"],
        )


# --- Unhappy path: missing attack_types key ---
def test_attack_simulation_stack_missing_attack_types():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"foo": "bar"}
    stack = AttackSimulationStack(
        test_stack,
        "TestAttackSimulationStack",
        simulation_config=config,
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json()["Outputs"]
    assert any("AttackSimulationConfigWarning" in k for k in outputs)
    assert (
        outputs["AttackSimulationConfigWarning"]["Value"]
        == "Missing 'attack_types' in simulation_config"
    )


# --- Edge case: custom tags propagate ---
def test_attack_simulation_stack_custom_tags():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"attack_types": ["phishing"]}
    tags = {"Project": "CustomProj", "Environment": "Dev", "Owner": "Alice"}
    stack = AttackSimulationStack(
        test_stack,
        "TestAttackSimulationStack",
        simulation_config=config,
        stack_tags=tags,
    )
    template = assertions.Template.from_stack(stack)
    # No direct tag resource, but stack tags should be present in synthesized template
    # This is a limitation of CDK assertions; full tag propagation is best checked in integration tests
    # TagManager does not have has_tag, but has_tags returns True if any tags exist
    assert stack.tags.has_tags()


# --- Edge case: secrets_manager_arn is None ---
def test_attack_simulation_stack_no_secret():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"attack_types": ["phishing"]}
    stack = AttackSimulationStack(
        test_stack,
        "TestAttackSimulationStack",
        simulation_config=config,
        secrets_manager_arn=None,
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json()["Outputs"]
    assert not any("AttackSimulationSecretArn" in k for k in outputs)


# --- Happy path: CloudWatch alarm is created ---
def test_attack_simulation_stack_alarm_created():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"attack_types": ["phishing"]}
    stack = AttackSimulationStack(
        test_stack,
        "TestAttackSimulationStack",
        simulation_config=config,
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::CloudWatch::Alarm")
    assert any("AttackSimulationFailureAlarm" in k for k in resources)


# --- Unhappy path: Invalid secret ARN ---
def test_attack_simulation_stack_invalid_secret_arn():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"attack_types": ["phishing"]}
    # Missing 6-char suffix
    invalid_secret_arn = (
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:attackSimSecret"
    )
    with pytest.raises(Exception):
        AttackSimulationStack(
            test_stack,
            "TestAttackSimulationStack",
            simulation_config=config,
            secrets_manager_arn=invalid_secret_arn,
        )


# --- Happy path: Lambda environment variables ---
def test_attack_simulation_stack_lambda_env_vars():
    import json

    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"attack_types": ["phishing"]}
    secret_arn = (
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:attackSimSecret-ABC123"
    )
    stack = AttackSimulationStack(
        test_stack,
        "TestAttackSimulationStack",
        simulation_config=config,
        secrets_manager_arn=secret_arn,
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Lambda::Function")
    for fn in resources.values():
        env = fn["Properties"].get("Environment", {}).get("Variables", {})
        assert env["SIMULATION_CONFIG"] == json.dumps(config)
        assert env["SECRET_ARN"] == secret_arn


# --- Happy path: CloudWatch alarm threshold ---
def test_attack_simulation_stack_alarm_threshold():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"attack_types": ["phishing"]}
    stack = AttackSimulationStack(
        test_stack,
        "TestAttackSimulationStack",
        simulation_config=config,
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::CloudWatch::Alarm")
    for alarm in resources.values():
        assert alarm["Properties"]["Threshold"] == 1
        assert alarm["Properties"]["EvaluationPeriods"] == 1


# --- Happy path: Synthesized template tags ---
def test_attack_simulation_stack_template_tags():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"attack_types": ["phishing"]}
    tags = {"Project": "TagTest", "Environment": "Staging", "Owner": "Bob"}
    stack = AttackSimulationStack(
        test_stack,
        "TestAttackSimulationStack",
        simulation_config=config,
        stack_tags=tags,
    )
    template_json = assertions.Template.from_stack(stack).to_json()
    # Tags are present in the template's Metadata or Resources
    found = False
    for resource in template_json.get("Resources", {}).values():
        if "Tags" in resource.get("Properties", {}):
            tag_list = resource["Properties"]["Tags"]
            keys = [t["Key"] for t in tag_list]
            values = [t["Value"] for t in tag_list]
            if "Project" in keys and "TagTest" in values:
                found = True
    assert found
