from aws_cdk import (
    Stack,
    aws_glue as glue,
    aws_s3 as s3
)
from constructs import Construct

class GlueStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, s3_buckets: dict = None, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        glue_cfg = config.get('glue', {})
        env = config.get('app', {}).get('env', 'dev')

        # Tagging for traceability and custom tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in glue_cfg.get('tags', {}).items():
            self.tags.set_tag(k, v)

        # --- Glue Database ---
        db_name = glue_cfg.get('database_name')
        if not db_name:
            raise ValueError("Glue database_name is required.")
        removal_policy = glue_cfg.get('removal_policy', 'destroy').upper()
        from aws_cdk import RemovalPolicy, CfnOutput
        removal_policy_enum = RemovalPolicy.DESTROY if removal_policy == 'DESTROY' or env == 'dev' else RemovalPolicy.RETAIN
        self.database = glue.CfnDatabase(
            self, f"{construct_id}ShieldCraftDatabase",
            catalog_id=self.account,
            database_input={"name": db_name}
        )
        self.database.apply_removal_policy(removal_policy_enum)
        CfnOutput(self, f"{construct_id}GlueDatabaseName", value=db_name, export_name=f"{construct_id}-glue-db-name")
        # Glue database ARN must be constructed manually
        db_arn = f"arn:aws:glue:{self.region}:{self.account}:database/{db_name}"
        CfnOutput(self, f"{construct_id}GlueDatabaseArn", value=db_arn, export_name=f"{construct_id}-glue-db-arn")

        # --- Glue Crawlers ---
        crawlers = glue_cfg.get('crawlers', [])
        if not isinstance(crawlers, list):
            raise ValueError("Glue crawlers must be a list.")
        self.crawlers = []
        crawler_names = set()
        import re
        arn_regex = re.compile(r"^arn:aws:iam::\d{12}:role/.+")
        s3_regex = re.compile(r"^s3://[\w\-\.]+(/.*)?$")
        for crawler_cfg in crawlers:
            # Validate required fields
            name = crawler_cfg.get('name')
            role_arn = crawler_cfg.get('role_arn')
            s3_path = crawler_cfg.get('s3_path')
            if not name or not role_arn or not s3_path:
                raise ValueError(f"Crawler config must include name, role_arn, and s3_path. Got: {crawler_cfg}")
            if name in crawler_names:
                raise ValueError(f"Duplicate crawler name: {name}")
            crawler_names.add(name)
            if not arn_regex.match(role_arn):
                raise ValueError(f"Invalid role_arn format for crawler {name}: {role_arn}")
            if not s3_regex.match(s3_path):
                raise ValueError(f"Invalid s3_path format for crawler {name}: {s3_path}")
            crawler_removal_policy = crawler_cfg.get('removal_policy', removal_policy).upper()
            crawler_removal_enum = RemovalPolicy.DESTROY if crawler_removal_policy == 'DESTROY' or env == 'dev' else RemovalPolicy.RETAIN
            crawler = glue.CfnCrawler(
                self, f"{construct_id}{name}",
                role=role_arn,
                database_name=db_name,
                targets={"s3Targets": [{"path": s3_path}]},
                schedule=crawler_cfg.get('schedule'),
                table_prefix=crawler_cfg.get('table_prefix', '')
            )
            crawler.apply_removal_policy(crawler_removal_enum)
            self.crawlers.append(crawler)
            CfnOutput(self, f"{construct_id}GlueCrawler{name}Name", value=name, export_name=f"{construct_id}-glue-crawler-{name}-name")
            # Manually construct the ARN for the crawler
            crawler_arn = f"arn:aws:glue:{self.region}:{self.account}:crawler/{name}"
            CfnOutput(self, f"{construct_id}GlueCrawler{name}Arn", value=crawler_arn, export_name=f"{construct_id}-glue-crawler-{name}-arn")
