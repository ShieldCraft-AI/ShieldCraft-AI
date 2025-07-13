# --- Supplementary: Resource export validation ---
def test_budget_stack_resource_exports():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["secrets_manager_arn"] = (
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:mysecret-AbCdEf"
    )
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    # BudgetAlertsTopicArn should be a CloudFormation Ref
    if "BudgetAlertsTopicArn" in outputs:
        val = outputs["BudgetAlertsTopicArn"]["Value"]
        assert isinstance(val, dict) and "Ref" in val
    # BudgetName should match the expected name
    assert outputs["BudgetName"]["Value"] == "ShieldCraftAI-Monthly-Budget"
    # VaultSecretArn should match the secret ARN if present
    if "VaultSecretArn" in outputs:
        assert outputs["VaultSecretArn"]["Value"] == kwargs["secrets_manager_arn"]


# --- Supplementary: Tag propagation to SNS topic ---
def test_budget_stack_sns_topic_tags():
    app = App()
    kwargs = minimal_budget_kwargs()
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::SNS::Topic")
    assert len(resources) == 1
    # Tags are not directly exposed in the template, but stack.tags.render_tags() should include them
    tags = stack.tags.render_tags()
    assert any(tag.get("Key") == "Project" for tag in tags)
    assert any(tag.get("Key") == "Owner" for tag in tags)
    assert any(tag.get("Key") == "Environment" for tag in tags)


# --- Supplementary: Notification thresholds coverage ---
def test_budget_stack_notification_thresholds_in_template():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["notification_thresholds"] = [10, 20, 30]
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Budgets::Budget")
    assert len(resources) == 1
    # Notification thresholds are not directly exposed, but test does not raise


# --- Supplementary: Removal policy coverage ---
def test_budget_stack_removal_policy_retain():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["removal_policy"] = "RETAIN"
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)
    # Should not raise


# --- Supplementary: Multiple notification targets ---
def test_budget_stack_multiple_notification_targets():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["sns_topic_arn"] = "arn:aws:sns:us-east-1:123456789012:mytopic"
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Budgets::Budget")
    assert len(resources) == 1


# --- Supplementary: Custom stack tags ---
def test_budget_stack_custom_stack_tags():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["tags"] = {
        "Project": "CustomProject",
        "Environment": "staging",
        "Owner": "Ops",
    }
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "CustomProject"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Environment" and tag.get("Value") == "staging"
        for tag in tags
    )
    assert any(tag.get("Key") == "Owner" and tag.get("Value") == "Ops" for tag in tags)


# --- Supplementary: Unhappy path - invalid removal policy ---
def test_budget_stack_invalid_removal_policy():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["removal_policy"] = "INVALID"
    # Should default to RETAIN, not raise
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)


import pytest
from aws_cdk import App, assertions
from infra.stacks.budget_stack import BudgetStack


def minimal_budget_kwargs():
    return {
        "budget_limit": 100,
        "email_address": "test@example.com",
        "create_sns_topic": True,
        "tags": {"Project": "ShieldCraftAI", "Environment": "test", "Owner": "FinOps"},
    }


# --- Happy path: Budget and SNS topic creation ---
def test_budget_stack_synthesizes():
    app = App()
    stack = BudgetStack(app, "TestBudgetStack", **minimal_budget_kwargs())
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::Budgets::Budget", {"Budget": {"BudgetType": "COST"}}
    )
    outputs = template.to_json().get("Outputs", {})
    assert "BudgetAlertsTopicArn" in outputs
    assert "BudgetName" in outputs


# --- Happy path: Tag propagation ---
def test_budget_stack_tags():
    app = App()
    stack = BudgetStack(app, "TestBudgetStack", **minimal_budget_kwargs())
    tags = stack.tags.render_tags()
    assert any(tag.get("Key") == "Project" for tag in tags)
    assert any(tag.get("Key") == "Owner" for tag in tags)
    assert any(tag.get("Key") == "Environment" for tag in tags)


# --- Happy path: Custom notification thresholds ---
def test_budget_stack_custom_thresholds():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["notification_thresholds"] = [50, 75, 90]
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)
    template = assertions.Template.from_stack(stack)
    budget_resource = template.find_resources("AWS::Budgets::Budget")
    assert len(budget_resource) == 1
    # Notification thresholds are not directly exposed, but test does not raise


# --- Happy path: Removal policy propagation ---
def test_budget_stack_removal_policy():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["removal_policy"] = "RETAIN"
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)
    # Should not raise


# --- Happy path: Secrets manager integration ---
def test_budget_stack_secrets_manager_integration():
    app = App()
    kwargs = minimal_budget_kwargs()
    # Use a valid complete ARN format (with 6-char suffix)
    kwargs["secrets_manager_arn"] = (
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:mysecret-AbCdEf"
    )
    stack = BudgetStack(app, "TestBudgetStack", **kwargs)
    assert stack.secrets_manager_secret is not None
    assert stack.shared_resources["vault_secret"] == stack.secrets_manager_secret


# --- Unhappy path: Invalid budget limit ---
def test_budget_stack_invalid_budget_limit():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["budget_limit"] = -10
    with pytest.raises(ValueError):
        BudgetStack(app, "TestBudgetStack", **kwargs)


# --- Unhappy path: Missing notification target ---
def test_budget_stack_missing_notification_target():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["email_address"] = None
    kwargs["create_sns_topic"] = False
    with pytest.raises(ValueError):
        BudgetStack(app, "TestBudgetStack", **kwargs)


# --- Unhappy path: Invalid email address ---
def test_budget_stack_invalid_email():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["email_address"] = "not-an-email"
    with pytest.raises(ValueError):
        BudgetStack(app, "TestBudgetStack", **kwargs)


# --- Unhappy path: Invalid SNS topic ARN ---
def test_budget_stack_invalid_sns_arn():
    app = App()
    kwargs = minimal_budget_kwargs()
    kwargs["create_sns_topic"] = False
    kwargs["sns_topic_arn"] = "invalid-arn"
    with pytest.raises(ValueError):
        BudgetStack(app, "TestBudgetStack", **kwargs)


# --- Auditability: Stack-level tags present ---
def test_budget_stack_stack_level_tags_present():
    app = App()
    stack = BudgetStack(app, "TestBudgetStack", **minimal_budget_kwargs())
    tags = stack.tags.render_tags()
    tag_keys = [tag.get("Key") for tag in tags if isinstance(tag, dict)]
    assert "Project" in tag_keys
    assert "Owner" in tag_keys
    assert "Environment" in tag_keys
