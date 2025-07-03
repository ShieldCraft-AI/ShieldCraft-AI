from aws_cdk import (
    Stack,
    aws_lakeformation as lakeformation,
)
from constructs import Construct

class LakeFormationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, s3_buckets: dict = None, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        lf_cfg = config.get('lakeformation', {})
        env = config.get('app', {}).get('env', 'dev')

        # Tagging for traceability and custom tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in lf_cfg.get('tags', {}).items():
            self.tags.set_tag(k, v)

        from aws_cdk import RemovalPolicy, CfnOutput

        # --- Lake Formation S3 Resources ---
        buckets = lf_cfg.get('buckets', [])
        if not isinstance(buckets, list):
            raise ValueError("LakeFormation buckets must be a list.")
        bucket_names = set()
        self.resources = []
        for bucket_cfg in buckets:
            name = bucket_cfg.get('name')
            arn = bucket_cfg.get('arn')
            if not name or not arn:
                raise ValueError(f"LakeFormation bucket config must include name and arn. Got: {bucket_cfg}")
            if name in bucket_names:
                raise ValueError(f"Duplicate LakeFormation bucket name: {name}")
            bucket_names.add(name)
            resource = lakeformation.CfnResource(
                self, f"{construct_id}LakeFormationResource{name}",
                resource_arn=arn,
                use_service_linked_role=True
            )
            # Manual ARN output
            CfnOutput(self, f"{construct_id}LakeFormationResource{name}Arn", value=arn, export_name=f"{construct_id}-lakeformation-resource-{name}-arn")
            self.resources.append(resource)

        # --- Lake Formation Permissions ---
        permissions = lf_cfg.get('permissions', [])
        if not isinstance(permissions, list):
            raise ValueError("LakeFormation permissions must be a list.")
        perm_keys = set()
        self.permissions = []
        import re
        def sanitize_export_name(s):
            return re.sub(r'[^A-Za-z0-9:-]', '-', s)

        for perm_cfg in permissions:
            principal = perm_cfg.get('principal')
            resource = perm_cfg.get('resource')
            perms = perm_cfg.get('permissions')
            if not principal or not resource or not perms:
                raise ValueError(f"LakeFormation permission config must include principal, resource, and permissions. Got: {perm_cfg}")
            key = (principal, str(resource))
            if key in perm_keys:
                raise ValueError(f"Duplicate LakeFormation permission for principal/resource: {principal}/{resource}")
            perm_keys.add(key)
            perm = lakeformation.CfnPermissions(
                self, f"{construct_id}LakeFormationPerm{principal}{hash(str(resource))}",
                data_lake_principal={"dataLakePrincipalIdentifier": principal},
                resource=resource,
                permissions=perms
            )
            # Output principal/resource for traceability, sanitize export name
            sanitized_principal = sanitize_export_name(principal)
            CfnOutput(
                self,
                f"{construct_id}LakeFormationPerm{sanitized_principal}{hash(str(resource))}Principal",
                value=principal,
                export_name=f"{construct_id}-lakeformation-perm-{sanitized_principal}-principal"
            )
            self.permissions.append(perm)
