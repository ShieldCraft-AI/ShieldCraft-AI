
from aws_cdk import (
    Stack,
    aws_s3 as s3,
)
from constructs import Construct

class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        s3_cfg = config.get('s3', {})
        env = config.get('app', {}).get('env', 'dev')

        # Tagging for traceability and custom tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in s3_cfg.get('tags', {}).items():
            self.tags.set_tag(k, v)

        from aws_cdk import RemovalPolicy, CfnOutput

        buckets_cfg = s3_cfg.get('buckets', [])
        if not isinstance(buckets_cfg, list) or not buckets_cfg:
            raise ValueError("buckets must be a non-empty list.")
        bucket_names = set()
        self.buckets = {}
        for bucket_cfg in buckets_cfg:
            bucket_id = bucket_cfg.get('id') or bucket_cfg.get('name')
            bucket_name = bucket_cfg.get('name')
            if not bucket_id or not bucket_name:
                raise ValueError(f"Each bucket must have 'id' and 'name'. Got: {bucket_cfg}")
            if bucket_id in bucket_names:
                raise ValueError(f"Duplicate bucket id: {bucket_id}")
            bucket_names.add(bucket_id)
            removal_policy = bucket_cfg.get('removal_policy')
            if isinstance(removal_policy, str):
                removal_policy = getattr(RemovalPolicy, removal_policy.upper(), None)
            if removal_policy is None:
                removal_policy = RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN
            encryption = getattr(s3.BucketEncryption, bucket_cfg.get('encryption', 'S3_MANAGED').upper(), s3.BucketEncryption.S3_MANAGED)
            block_public_access = getattr(s3.BlockPublicAccess, bucket_cfg.get('block_public_access', 'BLOCK_ALL').upper(), s3.BlockPublicAccess.BLOCK_ALL)
            versioned = bucket_cfg.get('versioned', True)
            bucket = s3.Bucket(
                self, bucket_id,
                bucket_name=bucket_name,
                versioned=versioned,
                encryption=encryption,
                block_public_access=block_public_access,
                removal_policy=removal_policy
            )
            self.buckets[bucket_id] = bucket
            CfnOutput(self, f"{construct_id}S3Bucket{bucket_id}Name", value=bucket.bucket_name, export_name=f"{construct_id}-s3-bucket-{bucket_id}-name")
            CfnOutput(self, f"{construct_id}S3Bucket{bucket_id}Arn", value=bucket.bucket_arn, export_name=f"{construct_id}-s3-bucket-{bucket_id}-arn")

        # For backward compatibility, expose common buckets if present
        self.raw_bucket = self.buckets.get('RawDataBucket')
        self.processed_bucket = self.buckets.get('ProcessedDataBucket')
        self.analytics_bucket = self.buckets.get('AnalyticsDataBucket')
