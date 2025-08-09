import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def budget_template():
    template_path = Path("proton/budget-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(budget_template):
    assert isinstance(budget_template, dict)
    assert "AWSTemplateFormatVersion" in budget_template
    assert "Description" in budget_template
    assert "Resources" in budget_template
    assert "Parameters" in budget_template
    assert "Outputs" in budget_template


def test_parameters(budget_template):
    params = budget_template["Parameters"]
    for p in [
        "BudgetName",
        "BudgetLimit",
        "SNSAlertTopicArn",
        "VaultSecretArn",
        "EnvironmentName",
    ]:
        assert p in params
    assert params["BudgetName"]["Type"] == "String"
    assert params["BudgetLimit"]["Type"] == "Number"
    assert params["SNSAlertTopicArn"]["Type"] == "String"
    assert params["VaultSecretArn"]["Type"] == "String"
    assert params["EnvironmentName"]["Type"] == "String"


def test_resources(budget_template):
    resources = budget_template["Resources"]
    assert "Budget" in resources
    assert "VaultSecret" in resources
    budget = resources["Budget"]
    secret = resources["VaultSecret"]
    assert budget["Type"] == "AWS::Budgets::Budget"
    assert secret["Type"] == "AWS::SecretsManager::Secret"
    budget_props = budget["Properties"]
    secret_props = secret["Properties"]
    assert "Budget" in budget_props
    assert "NotificationsWithSubscribers" in budget_props
    assert "BudgetName" in budget_props["Budget"]
    assert "BudgetLimit" in budget_props["Budget"]
    assert "TimeUnit" in budget_props["Budget"]
    assert "BudgetType" in budget_props["Budget"]
    assert budget_props["Budget"]["BudgetType"] == "COST"
    assert "Amount" in budget_props["Budget"]["BudgetLimit"]
    assert "Unit" in budget_props["Budget"]["BudgetLimit"]
    assert budget_props["Budget"]["BudgetLimit"]["Unit"] == "USD"
    assert "Name" in secret_props
    assert "Description" in secret_props
    assert "SecretString" in secret_props
    assert "Tags" in secret_props
    assert any(tag["Key"] == "Environment" for tag in secret_props["Tags"])


def test_outputs(budget_template):
    outputs = budget_template["Outputs"]
    for o in ["BudgetName", "SNSAlertTopicArn", "VaultSecretArn"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(budget_template):
    secret_tags = budget_template["Resources"]["VaultSecret"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in secret_tags
    )


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"BudgetName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
