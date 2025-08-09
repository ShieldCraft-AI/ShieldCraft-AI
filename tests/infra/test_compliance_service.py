"""
This module contains unit tests for the ComplianceStack class,
which synthesizes AWS Config rules for compliance checks based on a config-driven approach.
"""

import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.compliance_service import ComplianceStack


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


# --- Unhappy path: required_tag_keys not a list ---
def test_compliance_stack_required_tags_not_list():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"required_tag_keys": "notalist"}
    with pytest.raises(TypeError):
        ComplianceStack(
            test_stack,
            "TestComplianceStack",
            config_dict=config,
            compliance_lambda_role_arn="arn:aws:iam::123456789012:role/MockComplianceLambdaRole",
        )


# --- Edge case: More than 3 required tags (should only use first 3) ---
def test_compliance_stack_more_than_three_tags():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"required_tag_keys": ["A", "B", "C", "D", "E"]}
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
        assert params.get("tag1Key") == "A"
        assert params.get("tag2Key") == "B"
        assert params.get("tag3Key") == "C"


# --- Edge case: config_dict is None ---
def test_compliance_stack_config_dict_none():
    app = App()
    test_stack = Stack(app, "TestStack")
    stack = ComplianceStack(
        test_stack,
        "TestComplianceStack",
        config_dict=None,
        compliance_lambda_role_arn="arn:aws:iam::123456789012:role/MockComplianceLambdaRole",
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Config::ConfigRule")
    assert any("RequiredTagsRule" in k for k in resources)
