import pytest
from aws_cdk import App, assertions
from infra.stacks.compute.sagemaker_stack import SageMakerStack


@pytest.fixture
def sagemaker_config():
    return {
        "sagemaker": {
            "model_name": "shieldcraft-model",
            "image_uri": "123456789012.dkr.ecr.af-south-1.amazonaws.com/shieldcraft:latest",
            "model_artifact_s3": "s3://bucket/model.tar.gz",
            "execution_role_arn": "arn:aws:iam::123456789012:role/SageMakerExecutionRole",
            "instance_type": "ml.m5.large",
            "endpoint_name": "shieldcraft-model-endpoint",
            "initial_instance_count": 2,
            "initial_variant_weight": 0.5,
            "alarm_threshold_status_failed": 3,
            "alarm_threshold_invocation_4xx": 2,
            "alarm_threshold_latency_ms": 2000,
            "alarm_threshold_cpu_utilization": 80.0,
            "alarm_threshold_memory_utilization": 85.0,
            "enable_sns_alerts": True,
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
            "kms_key_arn": "arn:aws:kms:af-south-1:123456789012:key/abcd-1234",
            "vpc_id": "vpc-12345678",
            "subnet_ids": ["subnet-1111", "subnet-2222"],
            "security_group_ids": ["sg-1234"],
            "s3_lifecycle_days": 30,
            "enable_cost_alarm": True,
            "cost_alarm_threshold_usd": 50.0,
            "cost_alarm_sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:CostTopic",
        },
        "app": {
            "env": "test",
            "owner": "alice",
            "data_classification": "internal",
            "component": "ml-inference",
        },
    }


# --- Happy path: SageMaker stack creation and outputs ---
def test_sagemaker_stack_synthesizes(sagemaker_config):
    app = App()
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=sagemaker_config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    template = assertions.Template.from_stack(stack)
    # Resource counts
    template.resource_count_is("AWS::SageMaker::Model", 1)
    template.resource_count_is("AWS::SageMaker::EndpointConfig", 1)
    template.resource_count_is("AWS::SageMaker::Endpoint", 1)
    # Outputs
    outputs = template.to_json().get("Outputs", {})
    assert "shieldcraftmodelModelName" in outputs
    assert "shieldcraftmodelModelArn" in outputs
    assert "shieldcraftmodelEndpointConfigName" in outputs
    assert "shieldcraftmodelEndpointConfigArn" in outputs
    assert "shieldcraftmodelEndpointName" in outputs
    assert "shieldcraftmodelEndpointArn" in outputs
    assert "shieldcraftmodelEndpointStatusFailedAlarmArn" in outputs
    assert "shieldcraftmodelInvocation4XXErrorsAlarmArn" in outputs
    assert "shieldcraftmodelModelLatencyAlarmArn" in outputs
    # Shared resources
    assert hasattr(stack, "shared_resources")
    sr = stack.shared_resources
    for key in [
        "model",
        "endpoint_config",
        "endpoint",
        "endpoint_status_failed_alarm",
        "invocation_4xx_errors_alarm",
        "model_latency_alarm",
    ]:
        assert key in sr and sr[key] is not None


def test_sagemaker_stack_outputs_are_correct(sagemaker_config):
    app = App()
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=sagemaker_config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})

    # Check that ARNs are well-formed (handle dict or string or Fn::Sub)
    def arn_like(val):
        v = val["Value"] if isinstance(val, dict) and "Value" in val else val
        if isinstance(v, str):
            return "sagemaker" in v
        if isinstance(v, dict):
            # Accept Fn::Sub, Fn::Join, etc.
            return any("sagemaker" in str(x) for x in v.values())
        return False

    assert arn_like(outputs["shieldcraftmodelModelArn"])
    assert arn_like(outputs["shieldcraftmodelEndpointConfigArn"])
    assert arn_like(outputs["shieldcraftmodelEndpointArn"])

    # Check that names match config
    def get_val(val):
        return val["Value"] if isinstance(val, dict) and "Value" in val else val

    assert (
        get_val(outputs["shieldcraftmodelModelName"])
        == sagemaker_config["sagemaker"]["model_name"]
    )
    assert (
        get_val(outputs["shieldcraftmodelEndpointConfigName"])
        == "shieldcraft-model-config"
    )
    assert (
        get_val(outputs["shieldcraftmodelEndpointName"])
        == sagemaker_config["sagemaker"]["endpoint_name"]
    )


# --- Happy path: Tagging ---
def test_sagemaker_stack_tags(sagemaker_config):
    app = App()
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=sagemaker_config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Environment" and tag.get("Value") == "test" for tag in tags
    )


# --- Unhappy path: Missing required fields ---
def test_sagemaker_stack_missing_required_fields():
    app = App()
    config = {
        "sagemaker": {
            "model_name": "shieldcraft-model"
            # missing image_uri, model_artifact_s3, execution_role_arn
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        SageMakerStack(
            app,
            "TestSageMakerStack",
            config=config,
            sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
        )


# --- Unhappy path: Invalid instance type ---
def test_sagemaker_stack_invalid_instance_type():
    app = App()
    config = {
        "sagemaker": {
            "model_name": "shieldcraft-model",
            "image_uri": "uri",
            "model_artifact_s3": "s3://bucket/model.tar.gz",
            "execution_role_arn": "arn:aws:iam::123456789012:role/SageMakerExecutionRole",
            "instance_type": "invalid.type",
            "endpoint_name": "shieldcraft-model-endpoint",
        },
        "app": {"env": "test"},
    }
    # Should not raise at synth time, but will fail at deploy. We check resource is created.
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::SageMaker::EndpointConfig", 1)


# --- Unhappy path: Missing sagemaker config section ---
def test_sagemaker_stack_missing_sagemaker_section():
    app = App()
    config = {"app": {"env": "test"}}
    with pytest.raises(ValueError):
        SageMakerStack(
            app,
            "TestSageMakerStack",
            config=config,
            sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
        )


# --- Happy path: Shared resources dict contains all expected keys ---
def test_sagemaker_stack_shared_resources_keys(sagemaker_config):
    app = App()
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=sagemaker_config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    sr = stack.shared_resources
    expected = {
        "model",
        "endpoint_config",
        "endpoint",
        "endpoint_status_failed_alarm",
        "invocation_4xx_errors_alarm",
        "model_latency_alarm",
        "cpu_utilization_alarm",
        "memory_utilization_alarm",
    }
    assert set(expected).issubset(set(sr.keys()))


# --- Happy path: S3 lifecycle and cost alarm outputs ---
def test_sagemaker_stack_lifecycle_and_cost_alarm_outputs(sagemaker_config):
    app = App()
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=sagemaker_config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    # S3 lifecycle is not directly output, but cost alarm should be
    assert any("CostBudgetId" in k for k in outputs)


# --- Happy path: VPC config is set on model ---
def test_sagemaker_stack_vpc_config_on_model(sagemaker_config):
    app = App()
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=sagemaker_config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.to_json().get("Resources", {})
    model_resource = next(
        (r for r in resources.values() if r["Type"] == "AWS::SageMaker::Model"), None
    )
    assert model_resource is not None
    props = model_resource["Properties"]
    assert "VpcConfig" in props
    assert set(props["VpcConfig"].keys()) == {"Subnets", "SecurityGroupIds"}


# --- Happy path: Advanced tags are present ---
def test_sagemaker_stack_advanced_tags(sagemaker_config):
    app = App()
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=sagemaker_config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "alice" for tag in tags
    )
    assert any(
        tag.get("Key") == "DataClassification" and tag.get("Value") == "internal"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Component" and tag.get("Value") == "ml-inference"
        for tag in tags
    )


# --- Edge case: Alarm threshold and description ---
def test_sagemaker_stack_alarm_properties(sagemaker_config):
    app = App()
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=sagemaker_config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.to_json().get("Resources", {})
    # Find alarm resources and check their properties
    alarm_types = ["AWS::CloudWatch::Alarm"]
    alarm_props = [
        r["Properties"] for r in resources.values() if r["Type"] in alarm_types
    ]
    # There should be 5 alarms (status, 4xx, latency, cpu, memory)
    assert len(alarm_props) == 5
    # Check for expected thresholds and descriptions
    found = {
        "status": False,
        "4xx": False,
        "latency": False,
        "cpu": False,
        "memory": False,
    }
    sm_cfg = sagemaker_config["sagemaker"]
    for props in alarm_props:
        if props["AlarmName"].endswith("endpoint-status-failed-alarm"):
            assert props["Threshold"] == sm_cfg["alarm_threshold_status_failed"]
            assert "Failed" in props["AlarmDescription"]
            found["status"] = True
        if props["AlarmName"].endswith("invocation-4xx-errors-alarm"):
            assert props["Threshold"] == sm_cfg["alarm_threshold_invocation_4xx"]
            assert "4XX" in props["AlarmDescription"]
            found["4xx"] = True
        if props["AlarmName"].endswith("model-latency-alarm"):
            assert props["Threshold"] == sm_cfg["alarm_threshold_latency_ms"]
            assert "latency" in props["AlarmDescription"].lower()
            found["latency"] = True
        if props["AlarmName"].endswith("cpu-utilization-alarm"):
            assert props["Threshold"] == sm_cfg["alarm_threshold_cpu_utilization"]
            assert "cpu" in props["AlarmDescription"].lower()
            found["cpu"] = True
        if props["AlarmName"].endswith("memory-utilization-alarm"):
            assert props["Threshold"] == sm_cfg["alarm_threshold_memory_utilization"]
            assert "memory" in props["AlarmDescription"].lower()
            found["memory"] = True
    missing = [k for k, v in found.items() if not v]
    assert not missing, f"Missing alarms: {missing}"


# --- Unhappy path: Model name with special characters ---
def test_sagemaker_stack_model_name_special_chars():
    app = App()
    config = {
        "sagemaker": {
            "model_name": "shieldcraft_model@2025",
            "image_uri": "uri",
            "model_artifact_s3": "s3://bucket/model.tar.gz",
            "execution_role_arn": "arn:aws:iam::123456789012:role/SageMakerExecutionRole",
            "instance_type": "ml.m5.large",
            "endpoint_name": "shieldcraft-model-endpoint",
        },
        "app": {"env": "test"},
    }
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    # Output keys will have special chars removed in logical IDs
    assert any(
        "shieldcraft_model2025" in k or "shieldcraftmodel2025" in k for k in outputs
    )


# --- Edge case: Alarm ARNs are strings or tokens ---
def test_sagemaker_stack_alarm_arns_are_strings(sagemaker_config):
    app = App()
    stack = SageMakerStack(
        app,
        "TestSageMakerStack",
        config=sagemaker_config,
        sagemaker_role_arn="arn:aws:iam::123456789012:role/mock-sagemaker-role",
    )
    sr = stack.shared_resources
    for alarm in [
        "endpoint_status_failed_alarm",
        "invocation_4xx_errors_alarm",
        "model_latency_alarm",
    ]:
        arn = getattr(sr[alarm], "alarm_arn", None)
        assert arn is not None
        assert isinstance(arn, str) or hasattr(
            arn, "to_string"
        ), f"Alarm ARN for {alarm} is not a string or token"
