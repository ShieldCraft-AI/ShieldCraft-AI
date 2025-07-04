from aws_cdk import aws_config as config, Stack
from constructs import Construct

class ComplianceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        required_tag_keys = ["Project", "Environment", "Owner"]

        config.ManagedRule(
            self,
            "RequiredTagsRule",
            identifier="REQUIRED_TAGS",
            input_parameters={
                "tag1Key": required_tag_keys[0],
                "tag2Key": required_tag_keys[1],
                "tag3Key": required_tag_keys[2],
            },
            rule_scope=config.RuleScope.from_resources(["AWS::AllSupported"])
        )
