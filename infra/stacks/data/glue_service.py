"""
ShieldCraftAI GlueStack: Secure, robust, and modular AWS Glue deployment stack with config validation, tagging, and modular crawler creation.
"""

from typing import Optional
from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_glue as glue
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import aws_iam as iam
from constructs import Construct  # pylint: disable=unused-import
from pydantic import BaseModel, Field, ValidationError


# --- Pydantic config validation ---
class GlueCrawlerConfig(BaseModel):
    id: str
    enable_glue_crawler: bool = False
    crawler: Optional[dict] = None


class GlueStackConfig(BaseModel):
    glue: dict = Field(default_factory=dict)
    s3: dict = Field(default_factory=dict)
    app: dict = Field(default_factory=dict)


class GlueStack(Stack):
    def __init__(
        self,
        scope,
        construct_id,
        vpc,
        buckets,
        *args,
        default_sg=None,
        glue_role_arn=None,
        glue_role=None,
        config=None,
        permissions_boundary_arn=None,
        shared_tags=None,
        secrets_manager_arn=None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)
        self.secrets_manager_arn = secrets_manager_arn
        self.secrets_manager_secret = None
        if self.secrets_manager_arn:
            self.secrets_manager_secret = (
                secretsmanager.Secret.from_secret_complete_arn(
                    self, "ImportedVaultSecret", self.secrets_manager_arn
                )
            )
            CfnOutput(
                self,
                f"{construct_id}VaultSecretArn",
                value=self.secrets_manager_arn,
                export_name=f"{construct_id}-vault-secret-arn",
            )
        if self.secrets_manager_secret:
            role_arn = glue_role_arn
            if role_arn:
                role = iam.Role.from_role_arn(self, "ImportedGlueStackRole", role_arn)
                self.secrets_manager_secret.grant_read(role)
        if config is None:
            config = {}
        try:
            GlueStackConfig(**config)
        except ValidationError as e:
            raise ValueError(f"Invalid GlueStack config: {e}") from e
        glue_cfg = config.get("glue", {})
        env = config.get("app", {}).get("env", "dev")
        self.shared_tags = shared_tags or {}
        self._validate_cross_stack_resources(glue_cfg, buckets)
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in glue_cfg.get("tags", {}).items():
            self.tags.set_tag(k, v)
        for k, v in self.shared_tags.items():
            self.tags.set_tag(k, v)
        self.glue_role = self._resolve_glue_role(
            construct_id, glue_role, glue_role_arn, permissions_boundary_arn
        )
        db_name = glue_cfg.get("database_name")
        removal_policy = glue_cfg.get("removal_policy", "destroy").upper()
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
            export_name=f"{construct_id}GlueDatabaseName",
        )
        db_arn = f"arn:aws:glue:{self.region}:{self.account}:database/{db_name}"
        CfnOutput(
            self,
            f"{construct_id}GlueDatabaseArn",
            value=db_arn,
            export_name=f"{construct_id}GlueDatabaseArn",
        )
        self.crawlers: list[glue.CfnCrawler] = []
        glue_crawlers = glue_cfg.get("crawlers", None)
        if glue_crawlers is not None:
            if not isinstance(glue_crawlers, list):
                raise ValueError("GlueStack 'crawlers' config must be a list.")
            seen_names = set()
            for crawler_cfg in glue_crawlers:
                name = crawler_cfg.get("name")
                role_arn = crawler_cfg.get("role_arn")
                s3_path = crawler_cfg.get("s3_path")
                if not name or not role_arn or not s3_path:
                    raise ValueError(
                        "Each crawler must have 'name', 'role_arn', and 's3_path'."
                    )
                if name in seen_names:
                    raise ValueError(f"Duplicate crawler name: {name}")
                seen_names.add(name)

                def is_token(val):
                    return hasattr(val, "is_unresolved") or (
                        isinstance(val, str) and "${Token[" in val
                    )

                if not (
                    str(role_arn).startswith("arn:aws:iam::") or is_token(role_arn)
                ):
                    raise ValueError(f"Invalid role_arn for crawler {name}: {role_arn}")
                if not (str(s3_path).startswith("s3://") or is_token(s3_path)):
                    raise ValueError(f"Invalid s3_path for crawler {name}: {s3_path}")
                valid_bucket = False
                for b in buckets.values():
                    if str(s3_path).startswith(f"s3://{b.bucket_name}"):
                        valid_bucket = True
                        break
                if not valid_bucket:
                    raise ValueError(
                        f"s3_path {s3_path} is not within any provided bucket."
                    )
                schedule_cfg = crawler_cfg.get("schedule")
                table_prefix = crawler_cfg.get("table_prefix", "")
                crawler_removal_policy = crawler_cfg.get(
                    "removal_policy", removal_policy
                ).upper()
                crawler_removal_enum = (
                    RemovalPolicy.DESTROY
                    if crawler_removal_policy == "DESTROY" or env == "dev"
                    else RemovalPolicy.RETAIN
                )
                schedule_prop = None
                if schedule_cfg:
                    if isinstance(schedule_cfg, dict):
                        schedule_prop = glue.CfnCrawler.ScheduleProperty(**schedule_cfg)
                    elif isinstance(schedule_cfg, str):
                        schedule_prop = glue.CfnCrawler.ScheduleProperty(
                            schedule_expression=schedule_cfg
                        )
                crawler = glue.CfnCrawler(
                    self,
                    f"{construct_id}{name}",
                    role=role_arn,
                    database_name=db_name,
                    targets={"s3Targets": [{"path": s3_path}]},
                    schedule=schedule_prop,
                    table_prefix=table_prefix,
                )
                crawler.apply_removal_policy(crawler_removal_enum)
                self.crawlers.append(crawler)
                CfnOutput(
                    self,
                    f"{construct_id}GlueCrawler{name}Name",
                    value=name,
                    export_name=f"{construct_id}-glue-crawler-{name}-name",
                )
                crawler_arn = (
                    f"arn:aws:glue:{self.region}:{self.account}:crawler/{name}"
                )
                CfnOutput(
                    self,
                    f"{construct_id}GlueCrawler{name}Arn",
                    value=crawler_arn,
                    export_name=f"{construct_id}-glue-crawler-{name}-arn",
                )
                CfnOutput(
                    self,
                    f"{construct_id}GlueCrawler{name}BucketArn",
                    value=buckets[
                        next(
                            b
                            for b in buckets
                            if str(s3_path).startswith(f"s3://{buckets[b].bucket_name}")
                        )
                    ].bucket_arn,
                    export_name=f"{construct_id}-glue-crawler-{name}-bucket-arn",
                )
                table_name = f"{table_prefix}{name}"
                CfnOutput(
                    self,
                    f"{construct_id}GlueCrawler{name}TableName",
                    value=table_name,
                    export_name=f"{construct_id}-glue-crawler-{name}-table-name",
                )
                table_arn = f"arn:aws:glue:{self.region}:{self.account}:table/{db_name}/{table_name}"
                CfnOutput(
                    self,
                    f"{construct_id}GlueCrawler{name}TableArn",
                    value=table_arn,
                    export_name=f"{construct_id}-glue-crawler-{name}-table-arn",
                )
        else:
            self._add_crawlers(
                construct_id, buckets, config, db_name, removal_policy, env
            )
        self.database_arn = db_arn
        self.crawler_arns = [
            f"arn:aws:glue:{self.region}:{self.account}:crawler/{c.node.id.replace(construct_id, '')}"
            for c in self.crawlers
        ]
        self.buckets = buckets
        self.vpc = vpc
        self.default_sg = default_sg

    def _validate_cross_stack_resources(self, glue_cfg, buckets):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        if not isinstance(glue_cfg, dict):
            raise ValueError("GlueStack requires a valid glue config dict.")
        db_name = glue_cfg.get("database_name")
        if not db_name:
            raise ValueError("Glue database_name is required.")
        if not isinstance(buckets, dict):
            raise ValueError("GlueStack requires a valid buckets dict.")

    def _export_resource(self, name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        CfnOutput(self, name, value=value, export_name=f"{self.stack_name}-{name}")

    def _resolve_glue_role(
        self,
        construct_id: str,
        glue_role: Optional[iam.IRole],
        glue_role_arn: Optional[str],
        permissions_boundary_arn: Optional[str],
    ) -> iam.IRole:
        """Resolve or create the Glue IAM role, supporting permissions boundaries."""
        if glue_role is not None:
            return glue_role
        if glue_role_arn is not None:
            return iam.Role.from_role_arn(
                self, f"{construct_id}ImportedGlueRole", glue_role_arn
            )
        role = iam.Role(
            self,
            f"{construct_id}GlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),  # type: ignore[arg-type]
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )
        if permissions_boundary_arn:
            role.add_managed_policy(
                iam.ManagedPolicy.from_managed_policy_arn(
                    self, f"Boundary{role.node.id}", permissions_boundary_arn
                )
            )
        return role  # type: ignore[return-value]

    def _add_crawlers(
        self,
        construct_id: str,
        buckets: dict,
        config: dict,
        db_name: str,
        removal_policy: str,
        env: str,
    ) -> None:
        """Create Glue crawlers for all enabled buckets."""
        s3_cfg = config.get("s3", {})
        buckets_cfg = s3_cfg.get("buckets", [])
        for bucket_cfg in buckets_cfg:
            if not bucket_cfg.get("enable_glue_crawler", False):
                continue
            bucket_id = bucket_cfg.get("id") or bucket_cfg.get("name")
            bucket = buckets.get(bucket_id)
            if not bucket:
                continue
            crawler_cfg = bucket_cfg.get("crawler", {})
            name = f"{bucket_id}Crawler"
            s3_path = f"s3://{bucket.bucket_name}"
            role_arn = None  # Use default role
            schedule_cfg = crawler_cfg.get("schedule")
            table_prefix = crawler_cfg.get("table_prefix", bucket_id.lower() + "_")
            crawler_removal_policy = crawler_cfg.get(
                "removal_policy", removal_policy
            ).upper()
            crawler_removal_enum = (
                RemovalPolicy.DESTROY
                if crawler_removal_policy == "DESTROY" or env == "dev"
                else RemovalPolicy.RETAIN
            )
            schedule_prop = None
            if schedule_cfg:
                if isinstance(schedule_cfg, dict):
                    schedule_prop = glue.CfnCrawler.ScheduleProperty(**schedule_cfg)
                elif isinstance(schedule_cfg, str):
                    schedule_prop = glue.CfnCrawler.ScheduleProperty(
                        schedule_expression=schedule_cfg
                    )
            crawler = glue.CfnCrawler(
                self,
                f"{construct_id}{name}",
                role=role_arn if role_arn else self.glue_role.role_arn,
                database_name=db_name,
                targets={"s3Targets": [{"path": s3_path}]},
                schedule=schedule_prop,
                table_prefix=table_prefix,
            )
            crawler.apply_removal_policy(crawler_removal_enum)
            self.crawlers.append(crawler)
            CfnOutput(
                self,
                f"{construct_id}GlueCrawler{name}Name",
                value=name,
                export_name=f"{construct_id}-glue-crawler-{name}-name",
            )
            crawler_arn = f"arn:aws:glue:{self.region}:{self.account}:crawler/{name}"
            CfnOutput(
                self,
                f"{construct_id}GlueCrawler{name}Arn",
                value=crawler_arn,
                export_name=f"{construct_id}-glue-crawler-{name}-arn",
            )
            # Export S3 bucket ARN for LakeFormation
            CfnOutput(
                self,
                f"{construct_id}GlueCrawler{name}BucketArn",
                value=bucket.bucket_arn,
                export_name=f"{construct_id}-glue-crawler-{name}-bucket-arn",
            )
            # Export Glue table name for LakeFormation (if table is created by crawler)
            table_name = f"{table_prefix}{bucket_id.lower()}"
            CfnOutput(
                self,
                f"{construct_id}GlueCrawler{name}TableName",
                value=table_name,
                export_name=f"{construct_id}-glue-crawler-{name}-table-name",
            )
            table_arn = f"arn:aws:glue:{self.region}:{self.account}:table/{db_name}/{table_name}"
            CfnOutput(
                self,
                f"{construct_id}GlueCrawler{name}TableArn",
                value=table_arn,
                export_name=f"{construct_id}-glue-crawler-{name}-table-arn",
            )
