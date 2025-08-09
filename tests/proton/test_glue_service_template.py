import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def glue_template():
    template_path = Path("proton/glue-service-template.yaml")
    with template_path.open() as f:
        # Use BaseLoader to avoid parsing CloudFormation intrinsic tags
        return yaml.load(f, Loader=yaml.BaseLoader)


def test_template_structure(glue_template):
    assert isinstance(glue_template, dict)
    assert "AWSTemplateFormatVersion" in glue_template
    assert "Description" in glue_template
    assert "Resources" in glue_template
    assert "Parameters" in glue_template
    assert "Outputs" in glue_template


def test_parameters(glue_template):
    params = glue_template["Parameters"]
    for p in [
        "DatabaseName",
        "CrawlerName",
        "CrawlerRoleArn",
        "TargetPath",
        "EnvironmentName",
    ]:
        assert p in params
        assert params[p]["Type"] == "String"


def test_resources(glue_template):
    resources = glue_template["Resources"]
    assert "GlueDatabase" in resources
    assert "GlueCrawler" in resources
    db = resources["GlueDatabase"]
    crawler = resources["GlueCrawler"]
    assert db["Type"] == "AWS::Glue::Database"
    assert crawler["Type"] == "AWS::Glue::Crawler"
    db_props = db["Properties"]
    crawler_props = crawler["Properties"]
    assert "CatalogId" in db_props
    assert "DatabaseInput" in db_props
    assert "Name" in db_props["DatabaseInput"]
    assert "Description" in db_props["DatabaseInput"]
    assert "Tags" in db_props
    assert any(tag["Key"] == "Environment" for tag in db_props["Tags"])
    assert "Name" in crawler_props
    assert "Role" in crawler_props
    assert "DatabaseName" in crawler_props
    assert "Targets" in crawler_props
    assert "S3Targets" in crawler_props["Targets"]
    assert isinstance(crawler_props["Targets"]["S3Targets"], list)
    assert "Path" in crawler_props["Targets"]["S3Targets"][0]
    assert "Tags" in crawler_props
    assert any(tag["Key"] == "Environment" for tag in crawler_props["Tags"])


def test_outputs(glue_template):
    outputs = glue_template["Outputs"]
    for o in ["GlueDatabaseName", "GlueCrawlerName"]:
        assert o in outputs
        assert outputs[o]["Description"]
        assert outputs[o]["Value"]


def test_tags_environment(glue_template):
    db_tags = glue_template["Resources"]["GlueDatabase"]["Properties"]["Tags"]
    crawler_tags = glue_template["Resources"]["GlueCrawler"]["Properties"]["Tags"]
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in db_tags
    )
    assert any(
        tag["Key"] == "Environment" and tag["Value"] == "EnvironmentName"
        for tag in crawler_tags
    )


def test_s3_targets_path(glue_template):
    crawler_props = glue_template["Resources"]["GlueCrawler"]["Properties"]
    s3_targets = crawler_props["Targets"]["S3Targets"]
    assert isinstance(s3_targets, list)
    assert "Path" in s3_targets[0]
    assert s3_targets[0]["Path"] == "TargetPath"


def test_missing_required_parameters():
    # Unhappy path: missing required parameter
    incomplete = {
        "Parameters": {"DatabaseName": {"Type": "String"}},
        "Resources": {},
        "Outputs": {},
    }
    with pytest.raises(AssertionError):
        test_template_structure(incomplete)
