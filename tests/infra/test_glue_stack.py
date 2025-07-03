import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.glue_stack import GlueStack
from aws_cdk import aws_ec2 as ec2

@pytest.fixture
def glue_config():
    return {
        "glue": {
            "database_name": "test_db",
            "crawler_schedule": "cron(0 2 * * ? *)",
            "enable_data_quality": True
        },
        "app": {"env": "test"}
    }


# --- Happy path: Database creation ---
def test_glue_stack_synthesizes():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "glue": {"database_name": "test_db"},
        "app": {"env": "test"}
    }
    stack = GlueStack(test_stack, "TestGlueStack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::Glue::Database", 1)

# --- Happy path: Crawler creation ---
def test_glue_stack_crawler_creation():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "testcrawler",
                    "role_arn": "arn:aws:iam::123456789012:role/GlueCrawlerRole",
                    "s3_path": "s3://bucket/data/"
                }
            ]
        },
        "app": {"env": "test"}
    }
    stack = GlueStack(test_stack, "TestGlueStack", config=config)
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::Glue::Crawler", 1)

# --- Happy path: Outputs ---
def test_glue_stack_outputs():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "testcrawler",
                    "role_arn": "arn:aws:iam::123456789012:role/GlueCrawlerRole",
                    "s3_path": "s3://bucket/data/"
                }
            ]
        },
        "app": {"env": "test"}
    }
    stack = GlueStack(test_stack, "TestGlueStack", config=config)
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    assert "TestGlueStackGlueDatabaseName" in outputs
    assert "TestGlueStackGlueDatabaseArn" in outputs
    assert "TestGlueStackGlueCrawlertestcrawlerName" in outputs
    assert "TestGlueStackGlueCrawlertestcrawlerArn" in outputs

# --- Happy path: Tagging ---
def test_glue_stack_tags():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "glue": {"database_name": "test_db", "tags": {"Owner": "DataTeam"}},
        "app": {"env": "test"}
    }
    stack = GlueStack(test_stack, "TestGlueStack", config=config)
    tags = stack.tags.render_tags()
    assert any(tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI" for tag in tags)
    assert any(tag.get("Key") == "Owner" and tag.get("Value") == "DataTeam" for tag in tags)

# --- Unhappy path: Missing required database_name ---
def test_glue_stack_missing_db_name():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"glue": {}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        GlueStack(test_stack, "TestGlueStack", config=config)

# --- Unhappy path: Crawler missing required fields ---
@pytest.mark.parametrize("bad_crawler", [
    {"name": "crawler1", "role_arn": "arn:aws:iam::123456789012:role/GlueCrawlerRole"},
    {"name": "crawler2", "s3_path": "s3://bucket/data/"},
    {"role_arn": "arn:aws:iam::123456789012:role/GlueCrawlerRole", "s3_path": "s3://bucket/data/"},
])
def test_glue_stack_invalid_crawler_config(bad_crawler):
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [bad_crawler]
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        GlueStack(test_stack, "TestGlueStack", config=config)

# --- Unhappy path: Duplicate crawler names ---
def test_glue_stack_duplicate_crawler_names():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {"name": "dup", "role_arn": "arn:aws:iam::123456789012:role/GlueCrawlerRole", "s3_path": "s3://bucket/data/"},
                {"name": "dup", "role_arn": "arn:aws:iam::123456789012:role/GlueCrawlerRole", "s3_path": "s3://bucket/data2/"}
            ]
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        GlueStack(test_stack, "TestGlueStack", config=config)

# --- Unhappy path: Invalid role ARN and S3 path ---
@pytest.mark.parametrize("role_arn,s3_path", [
    ("not-an-arn", "s3://bucket/data/"),
    ("arn:aws:iam::123456789012:role/GlueCrawlerRole", "not-a-s3-path"),
])
def test_glue_stack_invalid_arn_and_s3(role_arn, s3_path):
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {"name": "crawler", "role_arn": role_arn, "s3_path": s3_path}
            ]
        },
        "app": {"env": "test"}
    }
    with pytest.raises(ValueError):
        GlueStack(test_stack, "TestGlueStack", config=config)

# --- Happy path: Minimal config (no crawlers) ---
def test_glue_stack_minimal_config():
    app = App()
    test_stack = Stack(app, "TestStack")
    config = {"glue": {"database_name": "test_db"}, "app": {"env": "test"}}
    stack = GlueStack(test_stack, "TestGlueStack", config=config)
    assert hasattr(stack, "database")
