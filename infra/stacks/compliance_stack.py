from aws_cdk import aws_config as config, Stack
from constructs import Construct

class ComplianceStack(Stack):
    def __init__(self, scope: Construct, id: str, config_dict: dict = None, compliance_lambda_role_arn: str = None, **kwargs):
        super().__init__(scope, id, **kwargs)
        config_dict = config_dict or {}
        required_tag_keys = config_dict.get("required_tag_keys", ["Project", "Environment", "Owner"])

        # Cross-stack IAM wiring for Lambda-backed Config rules (future extensibility)
        lambda_role = None
        if compliance_lambda_role_arn:
            from aws_cdk import aws_iam as iam
            lambda_role = iam.Role.from_role_arn(self, f"{id}ImportedComplianceLambdaRole", compliance_lambda_role_arn, mutable=False)

        config.ManagedRule(
            self,
            "RequiredTagsRule",
            identifier="REQUIRED_TAGS",
            input_parameters={
                "tag1Key": required_tag_keys[0],
                "tag2Key": required_tag_keys[1],
                "tag3Key": required_tag_keys[2],
            }
        )
