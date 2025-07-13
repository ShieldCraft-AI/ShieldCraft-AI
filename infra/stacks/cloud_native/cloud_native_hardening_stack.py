"""
ShieldCraftAI CloudNativeHardeningStack: Cross-stack hardening, compliance, and monitoring.
Includes:
- CloudWatch alarms/metrics for critical resources (MSK, Lambda, OpenSearch)
- Granular IAM boundaries and session policies
- AWS Config rules for drift detection and compliance
- Cross-stack references for tightly coupled resources
"""

from typing import Any, Dict, List, Optional, cast
from aws_cdk import Stack, CfnOutput
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import aws_cloudwatch_actions as cloudwatch_actions
from aws_cdk import aws_config as cdk_config
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sns as sns
from aws_cdk.aws_cloudwatch import IAlarmAction
from constructs import Construct
from pydantic import BaseModel, Field, ValidationError

from typing import Any, Dict, List, Optional, cast
from aws_cdk import Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)  # pylint: disable=unused-import
from aws_cdk import CfnOutput  # pylint: disable=unused-import
from aws_cdk import aws_cloudwatch_actions as cloudwatch_actions
from aws_cdk import aws_config as cdk_config
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sns as sns
from aws_cdk.aws_cloudwatch import IAlarmAction
from constructs import Construct
from pydantic import BaseModel, Field, ValidationError


class LambdaFunctionConfig(BaseModel):
    """Config for Lambda alarms and IAM policies."""

    function_name: str
    error_threshold: int = 1
    duration_threshold_ms: int = 3000
    iam_policy_statements: Optional[List[Dict[str, Any]]] = None


class MSKClusterConfig(BaseModel):
    """Config for MSK cluster alarms. Set managed_by_msk_stack=True to skip alarm creation here."""

    cluster_name: str
    under_replicated_threshold: int = 1
    broker_count_threshold: int = 1
    managed_by_msk_stack: bool = False


class OpenSearchDomainConfig(BaseModel):
    """Config for OpenSearch domain alarms."""

    domain_name: str
    status_red_threshold: int = 1
    cpu_util_threshold: int = 90


class ConfigRuleConfig(BaseModel):
    """Config for AWS Config rules."""

    name: str
    identifier: str
    type: str = "managed"
    input_parameters: Optional[Dict[str, Any]] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None


class AppConfig(BaseModel):
    """App-level config for tagging and notifications."""

    env: str = Field(default="dev")
    owner: Optional[str] = None
    data_classification: Optional[str] = None
    component: Optional[str] = None
    sns_topic_arn: Optional[str] = None  # For alarm notifications


class CloudNativeHardeningConfig(BaseModel):
    """Top-level config for the hardening stack."""

    lambda_functions: List[LambdaFunctionConfig] = Field(default_factory=list)
    msk_clusters: List[MSKClusterConfig] = Field(default_factory=list)
    opensearch_domains: List[OpenSearchDomainConfig] = Field(default_factory=list)
    aws_config_rules: List[ConfigRuleConfig] = Field(default_factory=list)
    app: AppConfig = Field(default_factory=AppConfig)


class CloudNativeHardeningStack(
    Stack
):  # pylint: disable=too-many-arguments, too-many-positional-arguments
    """
    Modular, cloud-native hardening stack for ShieldCraft AI. Deploys alarms, config rules,
    and cross-stack resources with robust tagging, permissions boundaries, and strict config
    validation. Designed for parallel deployment and minimal blast radius.
    """

    def __init__(
        self,
        scope,
        construct_id,
        config,
        *args,
        sns_topic_secret_arn=None,
        external_api_key_arn=None,
        permissions_boundary_arn=None,
        shared_tags=None,
        lambda_role_arn=None,
        msk_client_role_arn=None,
        msk_producer_role_arn=None,
        msk_consumer_role_arn=None,
        opensearch_role_arn=None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)
        if not config:
            raise ValueError(
                "CloudNativeHardeningStack requires a non-empty config dict."
            )
        # Enforce explicit 'app' key in config dict, not just defaulted by Pydantic
        if "app" not in config:
            raise ValueError(
                "CloudNativeHardeningStack config must include an explicit 'app' section."
            )
        try:
            validated = CloudNativeHardeningConfig(**config)
        except ValidationError as e:
            raise ValueError(f"Invalid CloudNativeHardeningStack config: {e}") from e
        if not hasattr(validated, "app") or validated.app is None:
            raise ValueError(
                "CloudNativeHardeningStack config must include a valid 'app' section."
            )
        self.config = validated
        self.alarms = {}
        self.shared_resources = {}
        self.permissions_boundary_arn = permissions_boundary_arn
        self.shared_tags = shared_tags or {}
        self.sns_topic_secret_arn = sns_topic_secret_arn
        self.external_api_key_arn = external_api_key_arn
        self.lambda_role_arn = lambda_role_arn
        self.msk_client_role_arn = msk_client_role_arn
        self.msk_producer_role_arn = msk_producer_role_arn
        self.msk_consumer_role_arn = msk_consumer_role_arn
        self.opensearch_role_arn = opensearch_role_arn
        self.sns_topic_secret = None
        if self.sns_topic_secret_arn:
            self.sns_topic_secret = secretsmanager.Secret.from_secret_complete_arn(
                self, "ImportedSnsTopicSecret", self.sns_topic_secret_arn
            )
        if self.sns_topic_secret:
            self.alarm_role = iam.Role(
                self,
                "AlarmRole",
                assumed_by=cast(
                    iam.IPrincipal, iam.ServicePrincipal("lambda.amazonaws.com")
                ),
                description="Role for Lambda alarms to access SNS topic secret",
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "service-role/AWSLambdaBasicExecutionRole"
                    )
                ],
                role_name=f"{self.stack_name}-AlarmRole",
            )
            self.sns_topic_secret.grant_read(self.alarm_role)
        self._validate_cross_stack_resources()
        self._apply_tags()
        self._add_lambda_alarms()
        self._add_msk_alarms()
        self._add_opensearch_alarms()
        self._add_config_rules()
        for k, v in self.alarms.items():
            if isinstance(v, dict):
                for subk, subv in v.items():
                    py_key = f"{k}_{subk}_arn"
                    export_key = f"{k}-{subk}-arn".replace("_", "-")
                    export_name = f"{self.stack_name}:{export_key}"
                    self.shared_resources[py_key] = subv
                    self._export_resource(export_name, subv)
            else:
                py_key = f"{k}_arn"
                export_key = f"{k}-arn".replace("_", "-")
                export_name = f"{self.stack_name}:{export_key}"
                self.shared_resources[py_key] = v
                self._export_resource(export_name, v)
        if hasattr(self, "config_rules"):
            for rule_name, rule_arn in self.config_rules.items():
                self._export_resource(f"{rule_name}_config_rule_arn", rule_arn)

    def _apply_tags(self):
        app_cfg = self.config.app
        self.tags.set_tag("Project", "ShieldCraftAI")
        env = getattr(app_cfg, "env", None)
        if isinstance(env, str):
            self.tags.set_tag("Environment", env)
        owner = getattr(app_cfg, "owner", None)
        if isinstance(owner, str):
            self.tags.set_tag("Owner", owner)
        data_classification = getattr(app_cfg, "data_classification", None)
        if isinstance(data_classification, str):
            self.tags.set_tag("DataClassification", data_classification)
        component = getattr(app_cfg, "component", None)
        if isinstance(component, str):
            self.tags.set_tag("Component", component)
        if self.shared_tags:
            for k, v in self.shared_tags.items():
                if isinstance(v, str):
                    self.tags.set_tag(k, v)

    def _validate_cross_stack_resources(self):
        """
        Explicitly validate referenced cross-stack resources before creation.
        Raises ValueError if any required resource is missing or misconfigured.
        """
        app_cfg = self.config.app
        lambda_functions = (
            self.config.lambda_functions
            if isinstance(self.config.lambda_functions, list)
            else []
        )
        for fn_cfg in lambda_functions:
            if not getattr(fn_cfg, "function_name", None):
                raise ValueError("Lambda function_name must be provided in config.")
        msk_clusters = (
            self.config.msk_clusters
            if isinstance(self.config.msk_clusters, list)
            else []
        )
        for msk_cfg in msk_clusters:
            if not getattr(msk_cfg, "cluster_name", None):
                raise ValueError("MSK cluster_name must be provided in config.")
        opensearch_domains = (
            self.config.opensearch_domains
            if isinstance(self.config.opensearch_domains, list)
            else []
        )
        for os_cfg in opensearch_domains:
            if not getattr(os_cfg, "domain_name", None):
                raise ValueError("OpenSearch domain_name must be provided in config.")
        aws_config_rules = (
            self.config.aws_config_rules
            if isinstance(self.config.aws_config_rules, list)
            else []
        )
        for rule_cfg in aws_config_rules:
            if not getattr(rule_cfg, "name", None) or not getattr(
                rule_cfg, "identifier", None
            ):
                raise ValueError("Config rule name and identifier must be provided.")
        if app_cfg is not None:
            sns_topic_arn = getattr(app_cfg, "sns_topic_arn", None)
            if sns_topic_arn is not None and not sns_topic_arn:
                raise ValueError("sns_topic_arn is referenced but is empty.")

    def _export_resource(self, export_name, value):
        """
        Export a resource value (ARN, name, etc.) for cross-stack consumption and auditability.
        """
        # CDK export names must only include alphanumeric, colon, or hyphen
        sanitized_name = export_name.replace("_", "-")
        CfnOutput(self, sanitized_name, value=value, export_name=sanitized_name)

    # Sage advice: For further modularization, consider splitting alarm creation into
    # parallelizable tasks in CI/CD for large environments.

    def _apply_permissions_boundary(self, role: iam.IRole):
        """
        Attach a permissions boundary to a role if one is specified for the stack.
        """
        if self.permissions_boundary_arn:
            role.add_managed_policy(
                iam.ManagedPolicy.from_managed_policy_arn(
                    self, f"Boundary{role.node.id}", self.permissions_boundary_arn
                )
            )

    def _add_config_rules(self):
        """
        Add AWS Config rules for compliance. Uses validated config model.
        Only managed rules supported here.
        """
        if not self.config.aws_config_rules:
            return

        managed_rule_identifiers = {
            "S3_BUCKET_VERSIONING_ENABLED",
            "S3_BUCKET_PUBLIC_READ_PROHIBITED",
            "S3_BUCKET_PUBLIC_WRITE_PROHIBITED",
            "IAM_USER_NO_POLICIES_CHECK",
            "CLOUDFORMATION_STACK_DRIFT_DETECTION_CHECK",
            "ENCRYPTED_VOLUMES",
            "RDS_STORAGE_ENCRYPTED",
            "EC2_INSTANCE_NO_PUBLIC_IP",
            "CLOUD_TRAIL_ENABLED",
            "CLOUDWATCH_LOG_GROUP_ENCRYPTED",
        }
        self.config_rules = {}
        for rule_cfg in (
            list(self.config.aws_config_rules) if self.config.aws_config_rules else []
        ):
            rule_type = getattr(rule_cfg, "type", "managed")
            rule_name = rule_cfg.name
            if rule_type == "managed":
                identifier = rule_cfg.identifier
                if identifier not in managed_rule_identifiers:
                    raise ValueError(
                        f"Unknown or unsupported AWS Config managed rule identifier: "
                        f"{identifier}"
                    )
                rule_scope = None
                if rule_cfg.resource_type:
                    resource_type_obj = getattr(
                        cdk_config.ResourceType, rule_cfg.resource_type, None
                    )
                    if resource_type_obj is not None:
                        rule_scope = cdk_config.RuleScope.from_resource(
                            resource_type=resource_type_obj,
                            resource_id=rule_cfg.resource_id,
                        )
                managed_rule = cdk_config.ManagedRule(
                    self,
                    f"{rule_name}ManagedRule",
                    identifier=identifier,
                    input_parameters=rule_cfg.input_parameters,
                    rule_scope=rule_scope,
                )
                self.config_rules[rule_name] = managed_rule.config_rule_arn
            # Custom rules can be added here as needed

    def _add_lambda_alarms(self):
        """
        Add CloudWatch alarms and optional IAM policies for Lambda functions.
        Tags all created resources.
        """
        lambda_configs = (
            list(self.config.lambda_functions) if self.config.lambda_functions else []
        )
        sns_topic_arn = getattr(self.config.app, "sns_topic_arn", None)
        alarm_actions = []
        if sns_topic_arn:
            alarm_topic = sns.Topic.from_topic_arn(
                self, "AlarmTopicLambda", sns_topic_arn
            )
            alarm_actions = [
                cast(IAlarmAction, cloudwatch_actions.SnsAction(alarm_topic))
            ]
        for fn_cfg in lambda_configs:
            fn_name = fn_cfg.function_name
            error_threshold = fn_cfg.error_threshold
            duration_threshold = fn_cfg.duration_threshold_ms
            if error_threshold < 0 or duration_threshold < 0:
                raise ValueError(f"Invalid alarm threshold for {fn_name}: must be >= 0")
            if not fn_name or not isinstance(fn_name, str):
                raise ValueError("Lambda function_name must be a non-empty string.")
            lambda_fn = _lambda.Function.from_function_name(
                self, f"Imported{fn_name}", fn_name
            )
            # Parameterized IAM policy statements
            if fn_cfg.iam_policy_statements:
                policy = iam.Policy(self, f"{fn_name}CustomPolicy")
                for stmt in fn_cfg.iam_policy_statements:
                    policy.add_statements(iam.PolicyStatement(**stmt))
                if lambda_fn.role is not None:
                    lambda_fn.role.attach_inline_policy(policy)
                    self._apply_permissions_boundary(lambda_fn.role)
            # Error rate alarm
            error_alarm = cloudwatch.Alarm(
                self,
                f"{fn_name}ErrorAlarm",
                metric=lambda_fn.metric_errors(),
                threshold=error_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=(f"Alarm if {fn_name} errors >= {error_threshold}"),
                alarm_name=f"{fn_name}-error-alarm",
            )
            if alarm_actions:
                for action in alarm_actions:
                    error_alarm.add_alarm_action(action)
            duration_alarm = cloudwatch.Alarm(
                self,
                f"{fn_name}DurationAlarm",
                metric=lambda_fn.metric_duration(),
                threshold=duration_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=(
                    f"Alarm if {fn_name} duration >= {duration_threshold}ms"
                ),
                alarm_name=f"{fn_name}-duration-alarm",
            )
            if alarm_actions:
                for action in alarm_actions:
                    duration_alarm.add_alarm_action(action)
            self.alarms[fn_name] = {
                "error_alarm_arn": error_alarm.alarm_arn,
                "duration_alarm_arn": duration_alarm.alarm_arn,
            }

    def _add_msk_alarms(self):
        """
        Add CloudWatch alarms for MSK clusters not managed by MskStack. Tags all created resources.
        """
        msk_configs = list(self.config.msk_clusters) if self.config.msk_clusters else []
        sns_topic_arn = getattr(self.config.app, "sns_topic_arn", None)
        alarm_actions = []
        if sns_topic_arn:
            alarm_topic = sns.Topic.from_topic_arn(self, "AlarmTopicMSK", sns_topic_arn)
            alarm_actions = [
                cast(IAlarmAction, cloudwatch_actions.SnsAction(alarm_topic))
            ]
        for msk_cfg in msk_configs:
            if getattr(msk_cfg, "managed_by_msk_stack", False):
                continue  # Skip clusters managed by MskStack
            cluster_name = msk_cfg.cluster_name
            under_replicated_threshold = msk_cfg.under_replicated_threshold
            broker_count_threshold = msk_cfg.broker_count_threshold
            if under_replicated_threshold < 0 or broker_count_threshold < 0:
                raise ValueError(
                    f"Invalid MSK alarm threshold for {cluster_name}: must be >= 0"
                )
            under_replicated_alarm = cloudwatch.Alarm(
                self,
                f"{cluster_name}UnderReplicatedPartitionsAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/Kafka",
                    metric_name="UnderReplicatedPartitions",
                    dimensions_map={"Cluster Name": cluster_name},
                    statistic="Maximum",
                ),
                threshold=under_replicated_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=(
                    f"Alarm if {cluster_name} under-replicated partitions >= "
                    f"{under_replicated_threshold}"
                ),
                alarm_name=f"{cluster_name}-under-replicated-alarm",
            )
            if alarm_actions:
                for action in alarm_actions:
                    under_replicated_alarm.add_alarm_action(action)
            broker_count_alarm = cloudwatch.Alarm(
                self,
                f"{cluster_name}BrokerCountAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/Kafka",
                    metric_name="BrokerCount",
                    dimensions_map={"Cluster Name": cluster_name},
                    statistic="Minimum",
                ),
                threshold=broker_count_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                alarm_description=(
                    f"Alarm if {cluster_name} broker count < {broker_count_threshold}"
                ),
                alarm_name=f"{cluster_name}-broker-count-alarm",
            )
            if alarm_actions:
                for action in alarm_actions:
                    broker_count_alarm.add_alarm_action(action)
            self.alarms[cluster_name] = {
                "under_replicated_alarm_arn": under_replicated_alarm.alarm_arn,
                "broker_count_alarm_arn": broker_count_alarm.alarm_arn,
            }

    def _add_opensearch_alarms(self):
        """
        Add CloudWatch alarms for OpenSearch domains. Tags all created resources.
        """
        opensearch_configs = (
            list(self.config.opensearch_domains)
            if self.config.opensearch_domains
            else []
        )
        sns_topic_arn = getattr(self.config.app, "sns_topic_arn", None)
        alarm_actions = []
        if sns_topic_arn:
            alarm_topic = sns.Topic.from_topic_arn(self, "AlarmTopicOS", sns_topic_arn)
            alarm_actions = [
                cast(IAlarmAction, cloudwatch_actions.SnsAction(alarm_topic))
            ]
        for os_cfg in opensearch_configs:
            domain_name = os_cfg.domain_name
            status_red_threshold = os_cfg.status_red_threshold
            cpu_util_threshold = os_cfg.cpu_util_threshold
            if status_red_threshold < 0 or cpu_util_threshold < 0:
                raise ValueError(
                    f"Invalid OpenSearch alarm threshold for {domain_name}: must be >= 0"
                )
            status_red_alarm = cloudwatch.Alarm(
                self,
                f"{domain_name}StatusRedAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/ES",
                    metric_name="ClusterStatus.red",
                    dimensions_map={"DomainName": domain_name},
                    statistic="Maximum",
                ),
                threshold=status_red_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=(
                    f"Alarm if {domain_name} status red >= {status_red_threshold}"
                ),
                alarm_name=f"{domain_name}-status-red-alarm",
            )
            if alarm_actions:
                for action in alarm_actions:
                    status_red_alarm.add_alarm_action(action)
            cpu_util_alarm = cloudwatch.Alarm(
                self,
                f"{domain_name}CpuUtilAlarm",
                metric=cloudwatch.Metric(
                    namespace="AWS/ES",
                    metric_name="CPUUtilization",
                    dimensions_map={"DomainName": domain_name},
                    statistic="Maximum",
                ),
                threshold=cpu_util_threshold,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                alarm_description=(
                    f"Alarm if {domain_name} CPU util >= {cpu_util_threshold}"
                ),
                alarm_name=f"{domain_name}-cpu-util-alarm",
            )
            if alarm_actions:
                for action in alarm_actions:
                    cpu_util_alarm.add_alarm_action(action)
            self.alarms[domain_name] = {
                "status_red_alarm_arn": status_red_alarm.alarm_arn,
                "cpu_util_alarm_arn": cpu_util_alarm.alarm_arn,
            }


def define_cloud_native_hardening_stack(scope, stack_id, config, **kwargs):
    """
    Factory for CloudNativeHardeningStack.
    Enables modular, parallel deployment in CI/CD pipelines and explicit orchestration.

    Args:
        scope: CDK construct scope.
        stack_id: Unique stack name.
        config: Validated config dict for hardening stack (must include all required keys).
        sns_topic_secret_arn: ARN for SNS topic secret (optional).
        external_api_key_arn: ARN for external API key (optional).
        permissions_boundary_arn: ARN for permissions boundary (optional).
        shared_tags: Dict of tags to apply (optional).
        lambda_role_arn, msk_client_role_arn, msk_producer_role_arn, msk_consumer_role_arn, opensearch_role_arn: ARNs for cross-stack roles (optional).
        Any additional stack kwargs.

    Returns:
        CloudNativeHardeningStack instance, ready for orchestration and dependency management.
    Raises:
        ValueError: If config is missing required keys or is invalid.
    """
    # Explicitly extract and validate known parameters
    sns_topic_secret_arn = kwargs.pop("sns_topic_secret_arn", None)
    external_api_key_arn = kwargs.pop("external_api_key_arn", None)
    permissions_boundary_arn = kwargs.pop("permissions_boundary_arn", None)
    shared_tags = kwargs.pop("shared_tags", None)
    lambda_role_arn = kwargs.pop("lambda_role_arn", None)
    msk_client_role_arn = kwargs.pop("msk_client_role_arn", None)
    msk_producer_role_arn = kwargs.pop("msk_producer_role_arn", None)
    msk_consumer_role_arn = kwargs.pop("msk_consumer_role_arn", None)
    opensearch_role_arn = kwargs.pop("opensearch_role_arn", None)

    # Validate config before instantiation
    if not config or not isinstance(config, dict):
        raise ValueError(
            "Config must be a non-empty dict for CloudNativeHardeningStack."
        )

    # Instantiate the stack with explicit parameters
    return CloudNativeHardeningStack(
        scope,
        stack_id,
        config,
        sns_topic_secret_arn=sns_topic_secret_arn,
        external_api_key_arn=external_api_key_arn,
        permissions_boundary_arn=permissions_boundary_arn,
        shared_tags=shared_tags,
        lambda_role_arn=lambda_role_arn,
        msk_client_role_arn=msk_client_role_arn,
        msk_producer_role_arn=msk_producer_role_arn,
        msk_consumer_role_arn=msk_consumer_role_arn,
        opensearch_role_arn=opensearch_role_arn,
        **kwargs,
    )
