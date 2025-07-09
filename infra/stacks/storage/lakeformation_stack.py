from aws_cdk import (
    Stack,
    aws_lakeformation as lakeformation,
)
from constructs import Construct


class LakeFormationStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: dict,
        s3_buckets: dict = None,
        shared_tags: dict = None,
        lakeformation_admin_role_arn: str = None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        lf_cfg = config.get("lakeformation", {})
        env = config.get("app", {}).get("env", "dev")

        # Tagging for traceability and custom tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in lf_cfg.get("tags", {}).items():
            self.tags.set_tag(k, v)
        if shared_tags:
            for k, v in shared_tags.items():
                self.tags.set_tag(k, v)

        from aws_cdk import RemovalPolicy, CfnOutput

        # --- Lake Formation S3 Resources ---
        buckets = lf_cfg.get("buckets", [])
        self.shared_resources = {}
        self.resources = []
        if s3_buckets:
            bucket_items = s3_buckets.items() if isinstance(s3_buckets, dict) else []
            if not bucket_items:
                raise ValueError(
                    "s3_buckets must be a non-empty dict of bucket constructs."
                )
            for bucket_id, bucket in bucket_items:
                name = getattr(bucket, "bucket_name", None)
                arn = getattr(bucket, "bucket_arn", None)
                if not name or not arn:
                    raise ValueError(
                        f"S3 bucket construct must have bucket_name and bucket_arn. Got: {bucket}"
                    )
                import re
                from aws_cdk import Token

                if not Token.is_unresolved(name):
                    if not isinstance(name, str) or not re.match(
                        r"^[a-z0-9.-]{3,63}$", name
                    ):
                        raise ValueError(
                            f"Invalid S3 bucket name for LakeFormation: {name}"
                        )
                resource = lakeformation.CfnResource(
                    self,
                    f"{construct_id}LakeFormationResource{bucket_id}",
                    resource_arn=arn,
                    use_service_linked_role=True,
                )
                CfnOutput(
                    self,
                    f"{construct_id}LakeFormationResource{bucket_id}Arn",
                    value=arn,
                    export_name=f"{construct_id}-lakeformation-resource-{bucket_id}-arn",
                )
                self.resources.append(resource)
                self.shared_resources[bucket_id] = resource
        else:
            if not isinstance(buckets, list) or not buckets:
                raise ValueError("LakeFormation buckets must be a non-empty list.")
            bucket_names = set()
            for bucket_cfg in buckets:
                name = bucket_cfg.get("name")
                arn = bucket_cfg.get("arn")
                removal_policy = bucket_cfg.get("removal_policy", None)
                if isinstance(removal_policy, str):
                    removal_policy = getattr(
                        RemovalPolicy, removal_policy.upper(), None
                    )
                if removal_policy is None:
                    removal_policy = (
                        RemovalPolicy.DESTROY if env == "dev" else RemovalPolicy.RETAIN
                    )
                if not name or not arn:
                    raise ValueError(
                        f"LakeFormation bucket config must include name and arn. Got: {bucket_cfg}"
                    )
                if name in bucket_names:
                    raise ValueError(f"Duplicate LakeFormation bucket name: {name}")
                bucket_names.add(name)
                import re
                from aws_cdk import Token

                if not Token.is_unresolved(name):
                    if not isinstance(name, str) or not re.match(
                        r"^[a-z0-9.-]{3,63}$", name
                    ):
                        raise ValueError(
                            f"Invalid S3 bucket name for LakeFormation: {name}"
                        )
                resource = lakeformation.CfnResource(
                    self,
                    f"{construct_id}LakeFormationResource{name}",
                    resource_arn=arn,
                    use_service_linked_role=True,
                )
                if hasattr(resource, "apply_removal_policy"):
                    resource.apply_removal_policy(removal_policy)
                CfnOutput(
                    self,
                    f"{construct_id}LakeFormationResource{name}Arn",
                    value=arn,
                    export_name=f"{construct_id}-lakeformation-resource-{name}-arn",
                )
                self.resources.append(resource)
                self.shared_resources[name] = resource
        # --- Basic Monitoring: CloudTrail event rule for Lake Formation failures (optional, best effort) ---
        self.event_rule = None
        try:
            from aws_cdk import aws_events as events

            self.event_rule = events.Rule(
                self,
                f"{construct_id}LakeFormationFailureRule",
                event_pattern=events.EventPattern(
                    source=["aws.lakeformation"],
                    detail_type=["AWS API Call via CloudTrail"],
                    detail={"errorCode": [{"exists": True}]},
                ),
                description="Alert on Lake Formation API errors via CloudTrail",
                enabled=True,
            )
        except ImportError:
            pass

        # --- Lake Formation Permissions ---
        permissions = lf_cfg.get("permissions", [])
        if not isinstance(permissions, list):
            raise ValueError("LakeFormation permissions must be a list.")
        perm_keys = set()
        self.permissions = []
        self.shared_permissions = {}
        import re

        def sanitize_export_name(s):
            return re.sub(r"[^A-Za-z0-9:-]", "-", s)

        for perm_cfg in permissions:
            principal = perm_cfg.get("principal")
            resource = perm_cfg.get("resource")
            perms = perm_cfg.get("permissions")
            # If principal is a placeholder for admin, use the provided role ARN
            if (
                principal == "LAKEFORMATION_ADMIN_ROLE_ARN"
                and lakeformation_admin_role_arn
            ):
                principal = lakeformation_admin_role_arn
            if not principal or not resource or not perms:
                raise ValueError(
                    f"LakeFormation permission config must include principal, resource, and permissions. Got: {perm_cfg}"
                )
            key = (principal, str(resource))
            if key in perm_keys:
                raise ValueError(
                    f"Duplicate LakeFormation permission for principal/resource: {principal}/{resource}"
                )
            perm_keys.add(key)
            perm = lakeformation.CfnPermissions(
                self,
                f"{construct_id}LakeFormationPerm{sanitize_export_name(str(principal))}{hash(str(resource))}",
                data_lake_principal={"dataLakePrincipalIdentifier": principal},
                resource=resource,
                permissions=perms,
            )
            sanitized_principal = sanitize_export_name(str(principal))
            CfnOutput(
                self,
                f"{construct_id}LakeFormationPerm{sanitized_principal}{hash(str(resource))}Principal",
                value=principal,
                export_name=f"{construct_id}-lakeformation-perm-{sanitized_principal}-principal",
            )
            self.permissions.append(perm)
            self.shared_permissions[sanitized_principal] = perm
