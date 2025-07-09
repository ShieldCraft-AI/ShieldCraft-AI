from aws_cdk import Stack, aws_glue as glue, aws_iam as iam
from constructs import Construct
from typing import Optional


class GlueStack(Stack):
    """
    ShieldCraftAI GlueStack

    Parameters:
        vpc: The shared VPC for Glue jobs (required for network isolation).
        data_bucket: The main S3 bucket for Glue crawlers/jobs.
        default_sg: Default security group for Glue resources (optional).
        glue_role: IAM role for Glue jobs/crawlers (optional, can be shared across stacks).
        config: Project configuration dictionary.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc,
        data_bucket,
        default_sg=None,
        glue_role_arn: Optional[str] = None,
        glue_role: Optional[iam.IRole] = None,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)
        config = config or {}
        glue_cfg = config.get("glue", {})
        env = config.get("app", {}).get("env", "dev")

        # Tagging for traceability and custom tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in glue_cfg.get("tags", {}).items():
            self.tags.set_tag(k, v)

        # --- IAM Role (shared, from ARN, or created here) ---
        if glue_role is not None:
            self.glue_role = glue_role
        elif glue_role_arn is not None:
            self.glue_role = iam.Role.from_role_arn(
                self, f"{construct_id}ImportedGlueRole", glue_role_arn
            )
        else:
            self.glue_role = iam.Role(
                self,
                f"{construct_id}GlueRole",
                assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "service-role/AWSGlueServiceRole"
                    )
                ],
            )

        # --- Glue Database ---
        db_name = glue_cfg.get("database_name")
        if not db_name:
            raise ValueError("Glue database_name is required.")
        removal_policy = glue_cfg.get("removal_policy", "destroy").upper()
        from aws_cdk import RemovalPolicy, CfnOutput

        removal_policy_enum = (
            RemovalPolicy.DESTROY
            if removal_policy == "DESTROY" or env == "dev"
            else RemovalPolicy.RETAIN
        )
        self.database = glue.CfnDatabase(
            self,
            f"{construct_id}ShieldCraftDatabase",
            catalog_id=self.account,
            database_input={"name": db_name},
        )
        self.database.apply_removal_policy(removal_policy_enum)
        CfnOutput(
            self,
            f"{construct_id}GlueDatabaseName",
            value=db_name,
            export_name=f"{construct_id}-glue-db-name",
        )
        # Glue database ARN must be constructed manually
        db_arn = f"arn:aws:glue:{self.region}:{self.account}:database/{db_name}"
        CfnOutput(
            self,
            f"{construct_id}GlueDatabaseArn",
            value=db_arn,
            export_name=f"{construct_id}-glue-db-arn",
        )

        # --- Glue Crawlers ---
        crawlers = glue_cfg.get("crawlers", [])
        if not isinstance(crawlers, list):
            raise ValueError("Glue crawlers must be a list.")
        self.crawlers = []
        crawler_names = set()
        import re

        arn_regex = re.compile(r"^arn:aws:iam::\d{12}:role/.+")
        s3_regex = re.compile(r"^s3://[\w\-\.]+(/.*)?$")
        for crawler_cfg in crawlers:
            # Validate required fields
            name = crawler_cfg.get("name")
            role_arn = crawler_cfg.get("role_arn")
            s3_path = crawler_cfg.get("s3_path")
            if not name or not s3_path:
                raise ValueError(
                    f"Crawler config must include name and s3_path. Got: {crawler_cfg}"
                )
            if name in crawler_names:
                raise ValueError(f"Duplicate crawler name: {name}")
            crawler_names.add(name)
            # Only validate ARN format if it's a real string and not a CDK Token
            if (
                role_arn
                and isinstance(role_arn, str)
                and not role_arn.startswith("${Token")
                and not arn_regex.match(role_arn)
            ):
                raise ValueError(
                    f"Invalid role_arn format for crawler {name}: {role_arn}"
                )
            # Only validate S3 path format if it's a real string and not a CDK Token or contains a Token pattern
            is_token = False
            if isinstance(s3_path, str):
                # CDK Tokens can appear as ${Token[...]}, Token[...] or contain unresolved tokens
                if (
                    s3_path.startswith("${Token[")
                    or s3_path.startswith("Token[")
                    or "${Token[" in s3_path
                    or "Token[" in s3_path
                ):
                    is_token = True
            if (
                isinstance(s3_path, str)
                and not is_token
                and not s3_regex.match(s3_path)
            ):
                raise ValueError(
                    f"Invalid s3_path format for crawler {name}: {s3_path}"
                )
            # Validate that s3_path is under the shared data_bucket
            bucket_name = (
                data_bucket.bucket_name
                if hasattr(data_bucket, "bucket_name")
                else str(data_bucket)
            )
            if (
                not s3_path.startswith(f"s3://{bucket_name}/")
                and not s3_path == f"s3://{bucket_name}"
            ):
                raise ValueError(
                    f"Crawler s3_path {s3_path} must be under the shared data_bucket {bucket_name}"
                )
            crawler_removal_policy = crawler_cfg.get(
                "removal_policy", removal_policy
            ).upper()
            crawler_removal_enum = (
                RemovalPolicy.DESTROY
                if crawler_removal_policy == "DESTROY" or env == "dev"
                else RemovalPolicy.RETAIN
            )

            # Handle schedule property: must be CfnCrawler.ScheduleProperty if present
            schedule_cfg = crawler_cfg.get("schedule")
            schedule_prop = None
            if schedule_cfg:
                if isinstance(schedule_cfg, dict):
                    # Already a dict, assume correct shape
                    schedule_prop = glue.CfnCrawler.ScheduleProperty(**schedule_cfg)
                elif isinstance(schedule_cfg, str):
                    schedule_prop = glue.CfnCrawler.ScheduleProperty(
                        schedule_expression=schedule_cfg
                    )
                else:
                    raise ValueError(
                        f"Invalid schedule type for crawler {name}: {type(schedule_cfg)}"
                    )

            crawler = glue.CfnCrawler(
                self,
                f"{construct_id}{name}",
                role=role_arn if role_arn else glue_role.role_arn,
                database_name=db_name,
                targets={"s3Targets": [{"path": s3_path}]},
                schedule=schedule_prop,
                table_prefix=crawler_cfg.get("table_prefix", ""),
            )
            crawler.apply_removal_policy(crawler_removal_enum)
            self.crawlers.append(crawler)
            CfnOutput(
                self,
                f"{construct_id}GlueCrawler{name}Name",
                value=name,
                export_name=f"{construct_id}-glue-crawler-{name}-name",
            )
            # Manually construct the ARN for the crawler
            crawler_arn = f"arn:aws:glue:{self.region}:{self.account}:crawler/{name}"
            CfnOutput(
                self,
                f"{construct_id}GlueCrawler{name}Arn",
                value=crawler_arn,
                export_name=f"{construct_id}-glue-crawler-{name}-arn",
            )
        self.database_arn = db_arn
        self.crawler_arns = [
            f"arn:aws:glue:{self.region}:{self.account}:crawler/{c.name}"
            for c in self.crawlers
        ]
        self.data_bucket = data_bucket
        self.vpc = vpc
        self.default_sg = default_sg
