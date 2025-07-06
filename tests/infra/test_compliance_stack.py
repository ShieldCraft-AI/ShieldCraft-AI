import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.compliance_stack import ComplianceStack


def minimal_compliance_config():
    return {"required_tag_keys": ["Project", "Environment", "Owner"]}


# --- Happy path: Required tags rule created ---
def test_compliance_stack_required_tags_rule():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = minimal_compliance_config()
    stack = ComplianceStack(
        test_stack,
        "TestComplianceStack",
        config_dict=config,
        compliance_lambda_role_arn="arn:aws:iam::123456789012:role/MockComplianceLambdaRole",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Config::ConfigRule")
    assert any("RequiredTagsRule" in k for k in resources)
    # Check input parameters
    for rule in resources.values():
        params = rule["Properties"].get("InputParameters", {})
        assert params.get("tag1Key") == "Project"
        assert params.get("tag2Key") == "Environment"
        assert params.get("tag3Key") == "Owner"


# --- Happy path: Custom required tag keys ---
def test_compliance_stack_custom_tag_keys():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"required_tag_keys": ["CostCenter", "Team", "Purpose"]}
    stack = ComplianceStack(
        test_stack,
        "TestComplianceStack",
        config_dict=config,
        compliance_lambda_role_arn="arn:aws:iam::123456789012:role/MockComplianceLambdaRole",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Config::ConfigRule")
    for rule in resources.values():
        params = rule["Properties"].get("InputParameters", {})
        assert params.get("tag1Key") == "CostCenter"
        assert params.get("tag2Key") == "Team"
        assert params.get("tag3Key") == "Purpose"


# --- Happy path: Lambda role ARN wiring (future extensibility) ---
def test_compliance_stack_lambda_role_arn_wiring():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = minimal_compliance_config()
    # Should not raise or break if compliance_lambda_role_arn is provided
    stack = ComplianceStack(
        test_stack,
        "TestComplianceStack",
        config_dict=config,
        compliance_lambda_role_arn="arn:aws:iam::123456789012:role/MockComplianceLambdaRole",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Config::ConfigRule")
    assert resources


# --- Unhappy path: Missing required_tag_keys (should fallback to default) ---
def test_compliance_stack_missing_tag_keys():
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = ComplianceStack(
        test_stack,
        "TestComplianceStack",
        config_dict={},
        compliance_lambda_role_arn="arn:aws:iam::123456789012:role/MockComplianceLambdaRole",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Config::ConfigRule")
    for rule in resources.values():
        params = rule["Properties"].get("InputParameters", {})
        assert params.get("tag1Key") == "Project"
        assert params.get("tag2Key") == "Environment"
        assert params.get("tag3Key") == "Owner"


# --- Unhappy path: Too few tag keys (should raise IndexError) ---
def test_compliance_stack_too_few_tag_keys():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"required_tag_keys": ["OnlyOne"]}
    with pytest.raises(IndexError):
        ComplianceStack(
            test_stack,
            "TestComplianceStack",
            config_dict=config,
            compliance_lambda_role_arn="arn:aws:iam::123456789012:role/MockComplianceLambdaRole",
        )
