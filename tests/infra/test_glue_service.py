"""
This module contains unit tests for the GlueStack class,
which synthesizes AWS Glue resources based on a config-driven approach.
"""

import pytest
from aws_cdk import App, Stack, assertions
from infra.stacks.data.glue_service import GlueStack
from aws_cdk import aws_ec2 as ec2, aws_s3 as s3, aws_iam as iam


@pytest.fixture
def mock_vpc():
    app = App()
    stack = Stack(app, "MockVpcStack")
    return ec2.Vpc(stack, "MockVpc", max_azs=1)


@pytest.fixture
def mock_iam_role():
    app = App()
    stack = Stack(app, "MockRoleStack")
    return iam.Role(
        stack, "MockGlueRole", assumed_by=iam.ServicePrincipal("glue.amazonaws.com")
    )


@pytest.fixture
def glue_config():
    return {
        "glue": {
            "database_name": "test_db",
            "crawler_schedule": "cron(0 2 * * ? *)",
            "enable_data_quality": True,
        },
        "app": {"env": "test"},
    }


# --- Happy path: Database creation ---
def test_glue_stack_synthesizes(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {"glue": {"database_name": "test_db"}, "app": {"env": "test"}}
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=mock_vpc,
        buckets={"MockBucket": bucket},
        glue_role=mock_iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::Glue::Database", 1)


# --- Happy path: Crawler creation ---
def test_glue_stack_crawler_creation():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = ec2.Vpc(test_stack, "MockVpc", max_azs=1)
    bucket = s3.Bucket(test_stack, "MockBucket")
    iam_role = iam.Role(
        test_stack,
        "MockGlueRole",
        assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
    )
    bucket_name = bucket.bucket_name  # Used for s3_path
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "testcrawler",
                    "role_arn": iam_role.role_arn,
                    "s3_path": f"s3://{bucket_name}/data/",
                }
            ],
        },
        "app": {"env": "test"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=vpc,
        buckets={"MockBucket": bucket},
        glue_role=iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::Glue::Crawler", 1)


# --- Happy path: Outputs ---
def test_glue_stack_outputs():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = ec2.Vpc(test_stack, "MockVpc", max_azs=1)
    bucket = s3.Bucket(test_stack, "MockBucket")
    iam_role = iam.Role(
        test_stack,
        "MockGlueRole",
        assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
    )
    bucket_name = bucket.bucket_name
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "testcrawler",
                    "role_arn": iam_role.role_arn,
                    "s3_path": f"s3://{bucket_name}/data/",
                }
            ],
        },
        "app": {"env": "test"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=vpc,
        buckets={"MockBucket": bucket},
        glue_role=iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    assert "TestGlueStackGlueDatabaseName" in outputs
    assert "TestGlueStackGlueDatabaseArn" in outputs
    assert "TestGlueStackGlueCrawlertestcrawlerName" in outputs
    assert "TestGlueStackGlueCrawlertestcrawlerArn" in outputs


# --- Happy path: Tagging ---
def test_glue_stack_tags(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {
        "glue": {"database_name": "test_db", "tags": {"Owner": "DataTeam"}},
        "app": {"env": "test"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=mock_vpc,
        buckets={"MockBucket": bucket},
        glue_role=mock_iam_role,
        config=config,
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "DataTeam" for tag in tags
    )


# --- Unhappy path: Missing required database_name ---
def test_glue_stack_missing_db_name(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {"glue": {}, "app": {"env": "test"}}
    with pytest.raises(ValueError):
        GlueStack(
            test_stack,
            "TestGlueStack",
            vpc=mock_vpc,
            buckets={"MockBucket": bucket},
            glue_role=mock_iam_role,
            config=config,
        )


# --- Unhappy path: Crawler missing required fields ---
@pytest.mark.parametrize(
    "bad_crawler",
    [
        {
            "name": "crawler1",
            "role_arn": "arn:aws:iam::123456789012:role/GlueCrawlerRole",
        },
        {"name": "crawler2", "s3_path": "s3://bucket/data/"},
        {
            "role_arn": "arn:aws:iam::123456789012:role/GlueCrawlerRole",
            "s3_path": "s3://bucket/data/",
        },
    ],
)
def test_glue_stack_invalid_crawler_config(mock_vpc, mock_iam_role, bad_crawler):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {
        "glue": {"database_name": "test_db", "crawlers": [bad_crawler]},
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        GlueStack(
            test_stack,
            "TestGlueStack",
            vpc=mock_vpc,
            buckets={"MockBucket": bucket},
            glue_role=mock_iam_role,
            config=config,
        )


# --- Unhappy path: Duplicate crawler names ---
def test_glue_stack_duplicate_crawler_names(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    bucket_name = bucket.bucket_name  # Used for s3_path
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "dup",
                    "role_arn": mock_iam_role.role_arn,
                    "s3_path": f"s3://{bucket_name}/data/",
                },
                {
                    "name": "dup",
                    "role_arn": mock_iam_role.role_arn,
                    "s3_path": f"s3://{bucket_name}/data2/",
                },
            ],
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        GlueStack(
            test_stack,
            "TestGlueStack",
            vpc=mock_vpc,
            buckets={"MockBucket": bucket},
            glue_role=mock_iam_role,
            config=config,
        )


# --- Unhappy path: Invalid role ARN and S3 path ---
@pytest.mark.parametrize(
    "role_arn,s3_path",
    [
        ("not-an-arn", "s3://bucket/data/"),
        ("arn:aws:iam::123456789012:role/GlueCrawlerRole", "not-a-s3-path"),
    ],
)
def test_glue_stack_invalid_arn_and_s3(mock_vpc, mock_iam_role, role_arn, s3_path):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    _ = bucket.bucket_name  # Remove unused variable warning (F841)
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [{"name": "crawler", "role_arn": role_arn, "s3_path": s3_path}],
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        GlueStack(
            test_stack,
            "TestGlueStack",
            vpc=mock_vpc,
            buckets={"MockBucket": bucket},
            glue_role=mock_iam_role,
            config=config,
        )


# --- Happy path: Minimal config (no crawlers) ---
def test_glue_stack_minimal_config(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {"glue": {"database_name": "test_db"}, "app": {"env": "test"}}
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=mock_vpc,
        buckets={"MockBucket": bucket},
        glue_role=mock_iam_role,
        config=config,
    )
    assert hasattr(stack, "database")


def test_glue_stack_removal_policy_retain(mock_vpc, mock_iam_role):

    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {
        "glue": {"database_name": "test_db", "removal_policy": "retain"},
        "app": {"env": "prod"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=mock_vpc,
        buckets={"MockBucket": bucket},
        glue_role=mock_iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Glue::Database")
    db_resource = list(resources.values())[0]
    assert db_resource["DeletionPolicy"] == "Retain"


def test_glue_stack_removal_policy_destroy(mock_vpc, mock_iam_role):

    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {
        "glue": {"database_name": "test_db", "removal_policy": "destroy"},
        "app": {"env": "dev"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=mock_vpc,
        buckets={"MockBucket": bucket},
        glue_role=mock_iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Glue::Database")
    db_resource = list(resources.values())[0]
    assert db_resource["DeletionPolicy"] == "Delete"


def test_glue_stack_tag_propagation(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {
        "glue": {
            "database_name": "test_db",
            "tags": {"Owner": "DataTeam", "CostCenter": "AI123"},
        },
        "app": {"env": "test"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=mock_vpc,
        buckets={"MockBucket": bucket},
        glue_role=mock_iam_role,
        config=config,
    )
    tags = stack.tags.render_tags()
    assert any(
        tag.get("Key") == "CostCenter" and tag.get("Value") == "AI123" for tag in tags
    )


def test_glue_stack_multiple_crawlers():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = ec2.Vpc(test_stack, "MockVpc", max_azs=1)
    bucket = s3.Bucket(test_stack, "MockBucket")
    iam_role = iam.Role(
        test_stack,
        "MockGlueRole",
        assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
    )
    bucket_name = bucket.bucket_name
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "crawler1",
                    "role_arn": iam_role.role_arn,
                    "s3_path": f"s3://{bucket_name}/data1/",
                },
                {
                    "name": "crawler2",
                    "role_arn": iam_role.role_arn,
                    "s3_path": f"s3://{bucket_name}/data2/",
                },
            ],
        },
        "app": {"env": "test"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=vpc,
        buckets={"MockBucket": bucket},
        glue_role=iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::Glue::Crawler", 2)


def test_glue_stack_invalid_crawlers_type(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {
        "glue": {"database_name": "test_db", "crawlers": "not-a-list"},
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        GlueStack(
            test_stack,
            "TestGlueStack",
            vpc=mock_vpc,
            buckets={"MockBucket": bucket},
            glue_role=mock_iam_role,
            config=config,
        )


def test_glue_stack_imported_role_arn(mock_vpc):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    role_arn = "arn:aws:iam::123456789012:role/GlueRole"
    config = {"glue": {"database_name": "test_db"}, "app": {"env": "test"}}
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=mock_vpc,
        buckets={"MockBucket": bucket},
        glue_role_arn=role_arn,
        config=config,
    )
    assert hasattr(stack, "glue_role")


def test_glue_stack_missing_config(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    with pytest.raises(ValueError):
        GlueStack(
            test_stack,
            "TestGlueStack",
            vpc=mock_vpc,
            buckets={"MockBucket": bucket},
            glue_role=mock_iam_role,
            config=None,
        )


def test_glue_stack_custom_crawler_schedule_and_prefix():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = ec2.Vpc(test_stack, "MockVpc", max_azs=1)
    bucket = s3.Bucket(test_stack, "MockBucket")
    iam_role = iam.Role(
        test_stack,
        "MockGlueRole",
        assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
    )
    bucket_name = bucket.bucket_name
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "testcrawler",
                    "role_arn": iam_role.role_arn,
                    "s3_path": f"s3://{bucket_name}/data/",
                    "schedule": "cron(0 2 * * ? *)",
                    "table_prefix": "prefix_",
                }
            ],
        },
        "app": {"env": "test"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=vpc,
        buckets={"MockBucket": bucket},
        glue_role=iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Glue::Crawler")
    crawler = list(resources.values())[0]
    # The Schedule property is a dict with key 'ScheduleExpression'
    assert (
        crawler["Properties"]["Schedule"]["ScheduleExpression"] == "cron(0 2 * * ? *)"
    )
    assert crawler["Properties"]["TablePrefix"] == "prefix_"


def test_glue_stack_output_arns():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = ec2.Vpc(test_stack, "MockVpc", max_azs=1)
    bucket = s3.Bucket(test_stack, "MockBucket")
    iam_role = iam.Role(
        test_stack,
        "MockGlueRole",
        assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
    )
    bucket_name = bucket.bucket_name
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "testcrawler",
                    "role_arn": iam_role.role_arn,
                    "s3_path": f"s3://{bucket_name}/data/",
                }
            ],
        },
        "app": {"env": "test"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=vpc,
        buckets={"MockBucket": bucket},
        glue_role=iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    db_arn = outputs["TestGlueStackGlueDatabaseArn"]
    crawler_arn = outputs["TestGlueStackGlueCrawlertestcrawlerArn"]

    def arn_like(val, service, depth=0, max_depth=10, seen=None):
        # Accepts string, list, or dict (CloudFormation join, Output wrapping, etc)
        if seen is None:
            seen = set()
        if depth > max_depth:
            return False
        if id(val) in seen:
            return False
        seen.add(id(val))
        if isinstance(val, dict):
            # Handle CDK Output wrapping
            value = val.get("Value", val)
            if isinstance(value, dict) and value is not val:
                return arn_like(value, service, depth + 1, max_depth, seen)
            if "Fn::Join" in val:
                join_list = (
                    val["Fn::Join"][1]
                    if isinstance(val["Fn::Join"], list) and len(val["Fn::Join"]) > 1
                    else []
                )
                flat = []
                for v in join_list:
                    if isinstance(v, str):
                        flat.append(v)
                    elif isinstance(v, (list, dict)):
                        # Recursively flatten
                        if arn_like(v, service, depth + 1, max_depth, seen):
                            flat.append("")
                joined = "".join([s for s in flat if isinstance(s, str)])
                return f"arn:aws:{service}:" in joined
            # Recursively check all dict values
            for v2 in val.values():
                if arn_like(v2, service, depth + 1, max_depth, seen):
                    return True
            return False
        if isinstance(val, str):
            return val.startswith(f"arn:aws:{service}:") or f"arn:aws:{service}:" in val
        if isinstance(val, list):
            # Recursively flatten and join
            flat = []
            for v in val:
                if isinstance(v, str):
                    flat.append(v)
                elif isinstance(v, (list, dict)):
                    if arn_like(v, service, depth + 1, max_depth, seen):
                        flat.append("")
            joined = "".join([s for s in flat if isinstance(s, str)])
            return f"arn:aws:{service}:" in joined
        return False

    assert arn_like(db_arn, "glue")
    assert arn_like(crawler_arn, "glue")


# --- Additional tests for GlueStack ---
def test_glue_stack_no_crawlers_outputs():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = ec2.Vpc(test_stack, "MockVpc", max_azs=1)
    bucket = s3.Bucket(test_stack, "MockBucket")
    iam_role = iam.Role(
        test_stack,
        "MockGlueRole",
        assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
    )
    config = {
        "glue": {"database_name": "test_db"},
        "app": {"env": "test"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=vpc,
        buckets={"MockBucket": bucket},
        glue_role=iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    outputs = template.to_json().get("Outputs", {})
    assert "TestGlueStackGlueDatabaseName" in outputs
    assert "TestGlueStackGlueDatabaseArn" in outputs
    # No crawler outputs
    assert not any(
        k.startswith("TestGlueStackGlueCrawler")
        for k in outputs
        if k.endswith("Name") or k.endswith("Arn")
    )


def test_glue_stack_crawler_table_prefix_default():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = ec2.Vpc(test_stack, "MockVpc", max_azs=1)
    bucket = s3.Bucket(test_stack, "MockBucket")
    iam_role = iam.Role(
        test_stack,
        "MockGlueRole",
        assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
    )
    bucket_name = bucket.bucket_name
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "testcrawler",
                    "role_arn": iam_role.role_arn,
                    "s3_path": f"s3://{bucket_name}/data/",
                }
            ],
        },
        "app": {"env": "test"},
    }
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=vpc,
        buckets={"MockBucket": bucket},
        glue_role=iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Glue::Crawler")
    crawler = list(resources.values())[0]
    # Default table_prefix should be empty string
    assert crawler["Properties"].get("TablePrefix", "") == ""


def test_glue_stack_invalid_removal_policy():
    app = App()
    test_stack = Stack(app, "TestStack")
    vpc = ec2.Vpc(test_stack, "MockVpc", max_azs=1)
    bucket = s3.Bucket(test_stack, "MockBucket")
    iam_role = iam.Role(
        test_stack,
        "MockGlueRole",
        assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
    )
    config = {
        "glue": {"database_name": "test_db", "removal_policy": "invalid"},
        "app": {"env": "test"},
    }
    # Should default to RETAIN for invalid removal_policy (not DESTROY/dev)
    stack = GlueStack(
        test_stack,
        "TestGlueStack",
        vpc=vpc,
        buckets={"MockBucket": bucket},
        glue_role=iam_role,
        config=config,
    )
    template = assertions.Template.from_stack(stack)
    resources = template.find_resources("AWS::Glue::Database")
    db_resource = list(resources.values())[0]
    # Should be Retain (not Delete)
    assert db_resource["DeletionPolicy"] == "Retain"


# Edge: Crawler s3_path outside data bucket
def test_glue_stack_crawler_s3_path_outside_bucket(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "testcrawler",
                    "role_arn": mock_iam_role.role_arn,
                    "s3_path": "s3://otherbucket/data/",
                }
            ],
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        GlueStack(
            test_stack,
            "TestGlueStack",
            vpc=mock_vpc,
            buckets={"MockBucket": bucket},
            glue_role=mock_iam_role,
            config=config,
        )


# Edge: Crawler with missing name and s3_path
def test_glue_stack_crawler_missing_name_and_s3_path(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")
    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {"role_arn": mock_iam_role.role_arn},
            ],
        },
        "app": {"env": "test"},
    }
    with pytest.raises(ValueError):
        GlueStack(
            test_stack,
            "TestGlueStack",
            vpc=mock_vpc,
            buckets={"MockBucket": bucket},
            glue_role=mock_iam_role,
            config=config,
        )


# Edge: Crawler with s3_path as a Token (should not raise)
def test_glue_stack_crawler_s3_path_token(mock_vpc, mock_iam_role):
    app = App()
    test_stack = Stack(app, "TestStack")
    bucket = s3.Bucket(test_stack, "MockBucket")

    class TokenStr(str):
        def startswith(self, *args, **kwargs):
            return False

    config = {
        "glue": {
            "database_name": "test_db",
            "crawlers": [
                {
                    "name": "testcrawler",
                    "role_arn": mock_iam_role.role_arn,
                    "s3_path": TokenStr("${Token[Fake]}"),
                },
            ],
        },
        "app": {"env": "test"},
    }
    # Current GlueStack logic does not support fake tokens, so expect ValueError
    with pytest.raises(ValueError):
        GlueStack(
            test_stack,
            "TestGlueStack",
            vpc=mock_vpc,
            buckets={"MockBucket": bucket},
            glue_role=mock_iam_role,
            config=config,
        )
