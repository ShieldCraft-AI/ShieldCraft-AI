"""
Test environment-aware CloudFormation templates.
"""

from pathlib import Path
import pytest
import yaml


TEMPLATES = [
    "airbyte-service-template.yaml",
    "msk-service-template.yaml",
    "opensearch-service-template.yaml",
    "glue-service-template.yaml",
    "lambda-service-template.yaml",
    "stepfunctions-service-template.yaml",
    "eventbridge-service-template.yaml",
    "s3-service-template.yaml",
    "sagemaker-service-template.yaml",
    "iam-service-template.yaml",
    "lakeformation-service-template.yaml",
]


@pytest.mark.parametrize("template_name", TEMPLATES)
def test_env_parameters_present(template_name):
    template_path = Path("proton") / template_name
    with template_path.open(encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)

    assert "Parameters" in template, f"Parameters missing in {template_name}"
    params = template["Parameters"]
    # Common env-aware parameters
    for p in ["AppName", "Domain", "EnvironmentName"]:
        assert p in params, f"Missing param {p} in {template_name}"
        assert params[p]["Type"] == "String"

    allowed = params["EnvironmentName"].get("AllowedValues")
    assert isinstance(allowed, list), f"AllowedValues should be list in {template_name}"
    for v in ["dev", "staging", "prod"]:
        assert v in allowed, f"{v} not in AllowedValues for {template_name}"


@pytest.mark.parametrize("template_name", TEMPLATES)
def test_environment_tag_literal_present(template_name):
    template_path = Path("proton") / template_name
    with template_path.open(encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)

    resources = template.get("Resources", {})
    assert (
        isinstance(resources, dict) and resources
    ), f"Resources missing in {template_name}"

    def has_env_literal(tags):
        return any(
            tag.get("Key") == "Environment" and tag.get("Value") == "EnvironmentName"
            for tag in tags or []
        )

    # Scan all resource Tags and ensure at least one resource uses the literal Environment tag value
    found = False
    for res in resources.values():
        props = res.get("Properties", {}) if isinstance(res, dict) else {}
        if has_env_literal(props.get("Tags")):
            found = True
            break
    assert (
        found
    ), f"No Environment literal tag found in any resource for {template_name}"


@pytest.mark.parametrize("template_name", TEMPLATES)
def test_outputs_have_descriptions_and_values(template_name):
    template_path = Path("proton") / template_name
    with template_path.open(encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)

    outputs = template.get("Outputs", {})
    assert isinstance(
        outputs, dict
    ), f"Outputs missing or not a dict in {template_name}"
    # Each output must have Description and Value keys
    for name, out in outputs.items():
        assert (
            "Description" in out
        ), f"Output {name} missing Description in {template_name}"
        assert "Value" in out, f"Output {name} missing Value in {template_name}"


@pytest.mark.parametrize("template_name", TEMPLATES)
def test_standard_tags_present_somewhere(template_name):
    template_path = Path("proton") / template_name
    with template_path.open(encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)

    resources = template.get("Resources", {})
    assert (
        isinstance(resources, dict) and resources
    ), f"Resources missing in {template_name}"

    def has_keys(tags, keys):
        present = {k: False for k in keys}
        for t in tags or []:
            key = t.get("Key")
            if key in present:
                present[key] = True
        return all(present.values())

    found = False
    for res in resources.values():
        props = res.get("Properties", {}) if isinstance(res, dict) else {}
        if has_keys(props.get("Tags"), ["App", "Domain", "Env"]):
            found = True
            break
    assert found, f"App/Domain/Env tags not found on any resource in {template_name}"


# Ensure env-safe naming on selected resources
NAMING_EXPECTATIONS = [
    ("airbyte-service-template.yaml", "AirbyteECSService", "ServiceName"),
    ("msk-service-template.yaml", "MSKCluster", "ClusterName"),
    ("opensearch-service-template.yaml", "OpenSearchDomain", "DomainName"),
    ("lambda-service-template.yaml", "LambdaFunction", "FunctionName"),
    ("stepfunctions-service-template.yaml", "StateMachine", "StateMachineName"),
]


@pytest.mark.parametrize("template_name,resource,prop", NAMING_EXPECTATIONS)
def test_env_suffix_present_in_names(template_name, resource, prop):
    template_path = Path("proton") / template_name
    with template_path.open(encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)

    res = template.get("Resources", {}).get(resource, {})
    assert res, f"Resource {resource} missing in {template_name}"
    val = (
        res.get("Properties", {}).get(prop)
        if isinstance(res.get("Properties", {}), dict)
        else None
    )
    assert isinstance(
        val, str
    ), f"{resource}.{prop} should be a string in {template_name}"
    assert (
        "EnvironmentName" in val
    ), f"{resource}.{prop} should include EnvironmentName for env-safe naming in {template_name}"


@pytest.mark.parametrize("template_name", TEMPLATES)
def test_parameter_types_are_valid(template_name):
    template_path = Path("proton") / template_name
    with template_path.open(encoding="utf-8") as f:
        template = yaml.load(f, Loader=yaml.BaseLoader)

    params = template.get("Parameters", {})
    assert isinstance(params, dict) and params, f"Parameters missing in {template_name}"
    allowed_types = {"String", "Number", "List<String>", "Json"}
    for name, spec in params.items():
        assert (
            spec.get("Type") in allowed_types
        ), f"Parameter {name} has unexpected Type {spec.get('Type')} in {template_name}"
