"""
Cloud-Native Hardening and Cross-Stack Integration scaffolding for ShieldCraft AI.
This module will include:
- CloudWatch alarms/metrics for critical resources (MSK, Lambda, OpenSearch)
- Granular IAM boundaries and session policies
- AWS Config rules for drift detection and compliance
- Cross-stack references for tightly coupled resources
"""


from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_lambda as _lambda,
    aws_iam as iam,
    Stack
)
from constructs import Construct

# --- Pydantic config validation ---
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict, Any

class LambdaFunctionConfig(BaseModel):
    function_name: str
    error_threshold: int = 1
    duration_threshold_ms: int = 3000
    iam_policy_statements: Optional[List[Dict[str, Any]]] = None

class MSKClusterConfig(BaseModel):
    cluster_name: str
    under_replicated_threshold: int = 1
    broker_count_threshold: int = 1

class OpenSearchDomainConfig(BaseModel):
    domain_name: str
    status_red_threshold: int = 1
    cpu_util_threshold: int = 90

class ConfigRuleConfig(BaseModel):
    name: str
    identifier: str
    type: str = "managed"
    input_parameters: Optional[Dict[str, Any]] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None

class AppConfig(BaseModel):
    env: str = Field(default="dev")
    owner: Optional[str] = None
    data_classification: Optional[str] = None
    component: Optional[str] = None
    sns_topic_arn: Optional[str] = None  # For alarm notifications

class CloudNativeHardeningConfig(BaseModel):
    lambda_functions: List[LambdaFunctionConfig] = Field(default_factory=list)
    msk_clusters: List[MSKClusterConfig] = Field(default_factory=list)
    opensearch_domains: List[OpenSearchDomainConfig] = Field(default_factory=list)
    aws_config_rules: List[ConfigRuleConfig] = Field(default_factory=list)
    app: AppConfig = Field(default_factory=AppConfig)



class CloudNativeHardeningStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        try:
            validated = CloudNativeHardeningConfig(**config)
        except ValidationError as e:
            raise ValueError(f"Invalid CloudNativeHardeningStack config: {e}")
        self.config = validated
        self.alarms = {}
        self.shared_resources = {}

        # --- Advanced Tagging ---
        app_cfg = self.config.app
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", app_cfg.env)
        if app_cfg.owner:
            self.tags.set_tag("Owner", app_cfg.owner)
        if app_cfg.data_classification:
            self.tags.set_tag("DataClassification", app_cfg.data_classification)
        if app_cfg.component:
            self.tags.set_tag("Component", app_cfg.component)

        self._add_lambda_alarms()
        self._add_msk_alarms()
        self._add_opensearch_alarms()
        self._add_config_rules()
        # Export all alarm ARNs and key resources for cross-stack use
        for k, v in self.alarms.items():
            if isinstance(v, dict):
                for subk, arn in v.items():
                    self.shared_resources[f"{k}_{subk}"] = arn
            else:
                self.shared_resources[k] = v
    def _add_config_rules(self):
        config_rules = self.config.aws_config_rules
        if not config_rules:
            return
        from aws_cdk import aws_config as config
        managed_rule_identifiers = {
            'S3_BUCKET_VERSIONING_ENABLED',
            'S3_BUCKET_PUBLIC_READ_PROHIBITED',
            'S3_BUCKET_PUBLIC_WRITE_PROHIBITED',
            'IAM_USER_NO_POLICIES_CHECK',
            'CLOUDFORMATION_STACK_DRIFT_DETECTION_CHECK',
            'ENCRYPTED_VOLUMES',
            'RDS_STORAGE_ENCRYPTED',
            'EC2_INSTANCE_NO_PUBLIC_IP',
            'CLOUD_TRAIL_ENABLED',
            'CLOUDWATCH_LOG_GROUP_ENCRYPTED',
        }
        self.config_rules = {}
        for rule_cfg in config_rules:
            rule_type = getattr(rule_cfg, 'type', 'managed')
            rule_name = rule_cfg.name
            if rule_type == 'managed':
                identifier = rule_cfg.identifier
                if identifier not in managed_rule_identifiers:
                    raise ValueError(f"Unknown or unsupported AWS Config managed rule identifier: {identifier}")
                managed_rule = config.ManagedRule(
                    self, f"{rule_name}ManagedRule",
                    identifier=identifier,
                    input_parameters=rule_cfg.input_parameters,
                    rule_scope=config.RuleScope.from_resource(
                        resource_type=rule_cfg.resource_type,
                        resource_id=rule_cfg.resource_id
                    ) if rule_cfg.resource_type else None
                )
                self.config_rules[rule_name] = managed_rule.config_rule_arn
            # Custom rules can be added here as needed

    def _add_lambda_alarms(self):
        lambda_configs = self.config.lambda_functions
        sns_topic_arn = self.config.app.sns_topic_arn
        alarm_actions = []
        if sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic = sns.Topic.from_topic_arn(self, "AlarmTopicLambda", sns_topic_arn)
            alarm_actions = [SnsAction(alarm_topic)]
        for fn_cfg in lambda_configs:
            fn_name = fn_cfg.function_name
            error_threshold = fn_cfg.error_threshold
            duration_threshold = fn_cfg.duration_threshold_ms
            # Cross-stack reference: import Lambda by name
            lambda_fn = _lambda.Function.from_function_name(self, f"Imported{fn_name}", fn_name)

            # Parameterized IAM policy statements
            if fn_cfg.iam_policy_statements:
                policy = iam.Policy(self, f"{fn_name}CustomPolicy")
                for stmt in fn_cfg.iam_policy_statements:
                    policy.add_statements(iam.PolicyStatement(**stmt))
                lambda_fn.role.attach_inline_policy(policy)

            # Error rate alarm
            error_alarm = cloudwatch.Alarm(
                self, f"{fn_name}ErrorAlarm",
                metric=lambda_fn.metric_errors(),
                threshold=error_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=f"Alarm if {fn_name} errors >= {error_threshold}"
            )
            if alarm_actions:
                for action in alarm_actions:
                    error_alarm.add_alarm_action(action)
            # Duration alarm
            duration_alarm = cloudwatch.Alarm(
                self, f"{fn_name}DurationAlarm",
                metric=lambda_fn.metric_duration(),
                threshold=duration_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=f"Alarm if {fn_name} duration >= {duration_threshold}ms"
            )
            if alarm_actions:
                for action in alarm_actions:
                    duration_alarm.add_alarm_action(action)
            self.alarms[fn_name] = {
                'error_alarm_arn': error_alarm.alarm_arn,
                'duration_alarm_arn': duration_alarm.alarm_arn
            }

    def _add_msk_alarms(self):
        msk_configs = self.config.msk_clusters
        sns_topic_arn = self.config.app.sns_topic_arn
        alarm_actions = []
        if sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic = sns.Topic.from_topic_arn(self, "AlarmTopicMSK", sns_topic_arn)
            alarm_actions = [SnsAction(alarm_topic)]
        for msk_cfg in msk_configs:
            cluster_name = msk_cfg.cluster_name
            under_replicated_threshold = msk_cfg.under_replicated_threshold
            broker_count_threshold = msk_cfg.broker_count_threshold
            under_replicated_alarm = cloudwatch.Alarm(
                self, f"{cluster_name}UnderReplicatedPartitionsAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/Kafka",
                    metric_name="UnderReplicatedPartitions",
                    dimensions_map={"Cluster Name": cluster_name},
                    statistic="Maximum"
                ),
                threshold=under_replicated_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=f"Alarm if {cluster_name} under-replicated partitions >= {under_replicated_threshold}"
            )
            if alarm_actions:
                for action in alarm_actions:
                    under_replicated_alarm.add_alarm_action(action)
            broker_count_alarm = cloudwatch.Alarm(
                self, f"{cluster_name}BrokerCountAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/Kafka",
                    metric_name="BrokerCount",
                    dimensions_map={"Cluster Name": cluster_name},
                    statistic="Minimum"
                ),
                threshold=broker_count_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                alarm_description=f"Alarm if {cluster_name} broker count < {broker_count_threshold}"
            )
            if alarm_actions:
                for action in alarm_actions:
                    broker_count_alarm.add_alarm_action(action)
            self.alarms[cluster_name] = {
                'under_replicated_alarm_arn': under_replicated_alarm.alarm_arn,
                'broker_count_alarm_arn': broker_count_alarm.alarm_arn
            }

    def _add_opensearch_alarms(self):
        opensearch_configs = self.config.opensearch_domains
        sns_topic_arn = self.config.app.sns_topic_arn
        alarm_actions = []
        if sns_topic_arn:
            from aws_cdk import aws_sns as sns
            from aws_cdk.aws_cloudwatch_actions import SnsAction
            alarm_topic = sns.Topic.from_topic_arn(self, "AlarmTopicOS", sns_topic_arn)
            alarm_actions = [SnsAction(alarm_topic)]
        for os_cfg in opensearch_configs:
            domain_name = os_cfg.domain_name
            status_red_threshold = os_cfg.status_red_threshold
            cpu_util_threshold = os_cfg.cpu_util_threshold
            status_red_alarm = cloudwatch.Alarm(
                self, f"{domain_name}ClusterStatusRedAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/ES",
                    metric_name="ClusterStatus.red",
                    dimensions_map={"DomainName": domain_name, "ClientId": "1"},
                    statistic="Maximum"
                ),
                threshold=status_red_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=f"Alarm if {domain_name} cluster status red >= {status_red_threshold}"
            )
            if alarm_actions:
                for action in alarm_actions:
                    status_red_alarm.add_alarm_action(action)
            cpu_util_alarm = cloudwatch.Alarm(
                self, f"{domain_name}CPUUtilizationAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/ES",
                    metric_name="CPUUtilization",
                    dimensions_map={"DomainName": domain_name, "ClientId": "1"},
                    statistic="Maximum"
                ),
                threshold=cpu_util_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=f"Alarm if {domain_name} CPU utilization >= {cpu_util_threshold}%"
            )
            if alarm_actions:
                for action in alarm_actions:
                    cpu_util_alarm.add_alarm_action(action)
            self.alarms[domain_name] = {
                'status_red_alarm_arn': status_red_alarm.alarm_arn,
                'cpu_util_alarm_arn': cpu_util_alarm.alarm_arn
            }

def define_cloud_native_hardening_stack(scope, id, config, **kwargs):
    return CloudNativeHardeningStack(scope, id, config, **kwargs)
