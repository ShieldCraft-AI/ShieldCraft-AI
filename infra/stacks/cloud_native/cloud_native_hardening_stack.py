"""
Cloud-Native Hardening and Cross-Stack Integration scaffolding for ShieldCraft AI.
This module will include:
- CloudWatch alarms/metrics for critical resources (MSK, Lambda, OpenSearch)
- Granular IAM boundaries and session policies
- AWS Config rules for drift detection and compliance
- Cross-stack references for tightly coupled resources
"""

# Cloud-Native Hardening Stack: Lambda CloudWatch Alarms (scaffold)
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_lambda as _lambda,
    aws_iam as iam,
    Stack
)
from constructs import Construct


class CloudNativeHardeningStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        self.config = config
        self.alarms = {}

        self._add_lambda_alarms()
        self._add_msk_alarms()
        self._add_opensearch_alarms()
        self._add_config_rules()
    def _add_config_rules(self):
        config_rules = self.config.get('aws_config_rules', [])
        if not config_rules:
            return
        from aws_cdk import aws_config as config
        # List of AWS managed Config rule identifiers (partial, extend as needed)
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
            # ...add more as needed...
        }
        self.config_rules = {}
        for rule_cfg in config_rules:
            rule_type = rule_cfg.get('type', 'managed')
            rule_name = rule_cfg['name']
            if rule_type == 'managed':
                identifier = rule_cfg['identifier']
                if identifier not in managed_rule_identifiers:
                    raise ValueError(f"Unknown or unsupported AWS Config managed rule identifier: {identifier}")
                managed_rule = config.ManagedRule(
                    self, f"{rule_name}ManagedRule",
                    identifier=identifier,
                    input_parameters=rule_cfg.get('input_parameters'),
                    rule_scope=config.RuleScope.from_resource(
                        resource_type=rule_cfg.get('resource_type'),
                        resource_id=rule_cfg.get('resource_id')
                    ) if rule_cfg.get('resource_type') else None
                )
                self.config_rules[rule_name] = managed_rule.config_rule_arn
            # Custom rules can be added here as needed

    def _add_lambda_alarms(self):
        lambda_configs = self.config.get('lambda_functions', [])
        for fn_cfg in lambda_configs:
            fn_name = fn_cfg['function_name']
            error_threshold = fn_cfg.get('error_threshold', 1)
            duration_threshold = fn_cfg.get('duration_threshold_ms', 3000)
            # Cross-stack reference: import Lambda by name
            lambda_fn = _lambda.Function.from_function_name(self, f"Imported{fn_name}", fn_name)

            # Parameterized IAM policy statements
            policy_statements = fn_cfg.get('iam_policy_statements', [])
            if policy_statements:
                policy = iam.Policy(self, f"{fn_name}CustomPolicy")
                for stmt in policy_statements:
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
            self.alarms[fn_name] = {
                'error_alarm_arn': error_alarm.alarm_arn,
                'duration_alarm_arn': duration_alarm.alarm_arn
            }

    def _add_msk_alarms(self):
        msk_configs = self.config.get('msk_clusters', [])
        for msk_cfg in msk_configs:
            cluster_name = msk_cfg['cluster_name']
            under_replicated_threshold = msk_cfg.get('under_replicated_threshold', 1)
            broker_count_threshold = msk_cfg.get('broker_count_threshold', 1)
            # MSK metrics are in CloudWatch namespace 'AWS/Kafka', cluster name as dimension
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
            self.alarms[cluster_name] = {
                'under_replicated_alarm_arn': under_replicated_alarm.alarm_arn,
                'broker_count_alarm_arn': broker_count_alarm.alarm_arn
            }

    def _add_opensearch_alarms(self):
        opensearch_configs = self.config.get('opensearch_domains', [])
        for os_cfg in opensearch_configs:
            domain_name = os_cfg['domain_name']
            status_red_threshold = os_cfg.get('status_red_threshold', 1)
            cpu_util_threshold = os_cfg.get('cpu_util_threshold', 90)
            # OpenSearch metrics are in 'AWS/ES' namespace (legacy, still used for OpenSearch)
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
            self.alarms[domain_name] = {
                'status_red_alarm_arn': status_red_alarm.alarm_arn,
                'cpu_util_alarm_arn': cpu_util_alarm.alarm_arn
            }

def define_cloud_native_hardening_stack(scope, id, config, **kwargs):
    return CloudNativeHardeningStack(scope, id, config, **kwargs)
