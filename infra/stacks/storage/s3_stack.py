from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudwatch as cloudwatch,
    Duration,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct

from typing import Dict, Optional, Any

class S3Stack(Stack):
    """
    ShieldCraftAI S3Stack

    Parameters:
        config: Project configuration dictionary, must include 's3' section with 'buckets' list.
        shared_tags: Optional dictionary of tags to apply to all buckets.
        kms_key: Optional KMS key for bucket encryption (applies to all buckets if provided).

    Attributes:
        buckets: Dict of all created buckets by ID.
        raw_bucket, processed_bucket, analytics_bucket: Common buckets for backward compatibility.
    """
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: dict,
        shared_tags: Optional[Dict[str, str]] = None,
        kms_key: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        s3_cfg = config.get('s3', {})
        env = config.get('app', {}).get('env', 'dev')

        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in s3_cfg.get('tags', {}).items():
            self.tags.set_tag(k, v)
        if shared_tags:
            for k, v in shared_tags.items():
                self.tags.set_tag(k, v)

        buckets_cfg = s3_cfg.get('buckets', [])
        if not isinstance(buckets_cfg, list) or not buckets_cfg:
            raise ValueError("buckets must be a non-empty list.")
        bucket_ids = set()
        self.buckets: Dict[str, s3.Bucket] = {}
        for bucket_cfg in buckets_cfg:
            bucket_id = bucket_cfg.get('id') or bucket_cfg.get('name')
            bucket_name = bucket_cfg.get('name')
            if not bucket_id or not bucket_name:
                raise ValueError(f"Each bucket must have 'id' and 'name'. Got: {bucket_cfg}")
            if bucket_id in bucket_ids:
                raise ValueError(f"Duplicate bucket id: {bucket_id}")
            bucket_ids.add(bucket_id)
            # Validate bucket name (AWS S3 naming rules)
            import re
            if not isinstance(bucket_name, str) or not re.match(r"^[a-z0-9.-]{3,63}$", bucket_name):
                raise ValueError(f"Invalid S3 bucket name: {bucket_name}")
            removal_policy = bucket_cfg.get('removal_policy')
            if isinstance(removal_policy, str):
                removal_policy = getattr(RemovalPolicy, removal_policy.upper(), None)
            if removal_policy is None:
                removal_policy = RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN
            encryption = (
                kms_key if kms_key
                else getattr(s3.BucketEncryption, bucket_cfg.get('encryption', 'S3_MANAGED').upper(), s3.BucketEncryption.S3_MANAGED)
            )
            block_public_access = getattr(
                s3.BlockPublicAccess,
                bucket_cfg.get('block_public_access', 'BLOCK_ALL').upper(),
                s3.BlockPublicAccess.BLOCK_ALL
            )
            versioned = bucket_cfg.get('versioned', True)
            # Enforce versioning and encryption in prod
            if env == 'prod':
                versioned = True
                if not kms_key:
                    encryption = s3.BucketEncryption.S3_MANAGED
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

            # CloudWatch Alarms and Metrics
            # Alarm: 4xx errors (access denied, not found, etc.)
            cloudwatch.Alarm(
                self, f"{bucket_id}S3_4xxErrorsAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/S3",
                    metric_name="4xxErrors",
                    dimensions_map={"BucketName": bucket.bucket_name, "StorageType": "AllStorageTypes"},
                    period=Duration.minutes(5),
                    statistic="Sum"
                ),
                threshold=1,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                alarm_description=f"4xx errors detected on S3 bucket {bucket.bucket_name}",
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
            )
            # Alarm: 5xx errors (server errors)
            cloudwatch.Alarm(
                self, f"{bucket_id}S3_5xxErrorsAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/S3",
                    metric_name="5xxErrors",
                    dimensions_map={"BucketName": bucket.bucket_name, "StorageType": "AllStorageTypes"},
                    period=Duration.minutes(5),
                    statistic="Sum"
                ),
                threshold=1,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                alarm_description=f"5xx errors detected on S3 bucket {bucket.bucket_name}",
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
            )
            # Metrics: Number of objects and bucket size (for monitoring growth and cost)
            cloudwatch.Metric(
                namespace="AWS/S3",
                metric_name="NumberOfObjects",
                dimensions_map={"BucketName": bucket.bucket_name, "StorageType": "AllStorageTypes"},
                period=Duration.hours(1),
                statistic="Average"
            )
            cloudwatch.Metric(
                namespace="AWS/S3",
                metric_name="BucketSizeBytes",
                dimensions_map={"BucketName": bucket.bucket_name, "StorageType": "StandardStorage"},
                period=Duration.hours(1),
                statistic="Average"
            )

        # For backward compatibility, expose common buckets if present
        self.raw_bucket = self.buckets.get('RawDataBucket')
        self.processed_bucket = self.buckets.get('ProcessedDataBucket')
        self.analytics_bucket = self.buckets.get('AnalyticsDataBucket')
