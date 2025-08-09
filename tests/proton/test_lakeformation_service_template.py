import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def lakeformation_template():
    template_path = Path("proton/lakeformation-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(lakeformation_template):
    assert isinstance(lakeformation_template, dict)
    assert "AWSTemplateFormatVersion" in lakeformation_template
    assert "Description" in lakeformation_template
    assert "Resources" in lakeformation_template
    assert "Parameters" in lakeformation_template
    assert "Outputs" in lakeformation_template


def test_parameters(lakeformation_template):
    params = lakeformation_template["Parameters"]
    for p in ["DataLakeAdmins", "DatabaseName", "S3Location", "EnvironmentName"]:
        assert p in params
    assert params["DataLakeAdmins"]["Type"] == "List<String>"
    assert params["DatabaseName"]["Type"] == "String"
    assert params["S3Location"]["Type"] == "String"
    assert params["EnvironmentName"]["Type"] == "String"


def test_resources(lakeformation_template):
    resources = lakeformation_template["Resources"]
    assert "LakeFormationDataLakeSettings" in resources
    assert "LakeFormationResource" in resources
    assert "GlueDatabase" in resources
    lf_settings = resources["LakeFormationDataLakeSettings"]
    lf_resource = resources["LakeFormationResource"]
    glue_db = resources["GlueDatabase"]
    assert lf_settings["Type"] == "AWS::LakeFormation::DataLakeSettings"
    assert lf_resource["Type"] == "AWS::LakeFormation::Resource"
    assert glue_db["Type"] == "AWS::Glue::Database"
    lf_settings_props = lf_settings["Properties"]
    lf_resource_props = lf_resource["Properties"]
    glue_db_props = glue_db["Properties"]
    assert "Admins" in lf_settings_props
    assert "ResourceArn" in lf_resource_props
    assert "UseServiceLinkedRole" in lf_resource_props
    assert lf_resource_props["UseServiceLinkedRole"] == "true"
    assert "CatalogId" in glue_db_props
    assert "DatabaseInput" in glue_db_props
    assert "Name" in glue_db_props["DatabaseInput"]
    assert "Description" in glue_db_props["DatabaseInput"]
    assert "Tags" in glue_db_props
    assert any(tag["Key"] == "Environment" for tag in glue_db_props["Tags"])


def test_outputs(lakeformation_template):
    outputs = lakeformation_template["Outputs"]
    for o in ["LakeFormationAdmins", "LakeFormationResourceArn", "GlueDatabaseName"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(lakeformation_template):
    glue_db_tags = lakeformation_template["Resources"]["GlueDatabase"]["Properties"][
        "Tags"
    ]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in glue_db_tags
    )


def test_admins_type(lakeformation_template):
    params = lakeformation_template["Parameters"]
    assert params["DataLakeAdmins"]["Type"] == "List<String>"


def test_use_service_linked_role_true(lakeformation_template):
    lf_resource_props = lakeformation_template["Resources"]["LakeFormationResource"][
        "Properties"
    ]
    assert lf_resource_props["UseServiceLinkedRole"] == "true"


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"DatabaseName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
