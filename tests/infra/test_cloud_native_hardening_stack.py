import pytest
def test_lambda_iam_policy_invalid_action():
    config = {
        'lambda_functions': [
            {
                'function_name': 'my-test-lambda',
                'iam_policy_statements': [
                    {
                        'actions': ['invalid:Action'],
                        'resources': ['*']
                    }
                ]
            }
        ]
    }
    app = App()
    with pytest.raises(Exception):
        define_cloud_native_hardening_stack(app, "TestLambdaIAMInvalid", config)

def test_aws_config_rule_invalid_identifier():
    config = {
        'aws_config_rules': [
            {
                'name': 'invalid-rule',
                'identifier': 'NON_EXISTENT_RULE',
                'type': 'managed',
            }
        ]
    }
    app = App()
    with pytest.raises(Exception):
        define_cloud_native_hardening_stack(app, "TestConfigRuleInvalid", config)
def test_aws_config_rule_synth():
    config = {
        'aws_config_rules': [
            {
                'name': 's3-bucket-versioning',
                'identifier': 'S3_BUCKET_VERSIONING_ENABLED',
                'type': 'managed',
                # Optionally add input_parameters, resource_type, resource_id
            }
        ]
    }
    app = App()
    stack = define_cloud_native_hardening_stack(app, "TestConfigRuleStack", config)
    template = app.synth().get_stack_by_name("TestConfigRuleStack").template
    resources = template['Resources']
    config_rules = [r for r in resources.values() if r['Type'] == 'AWS::Config::ConfigRule']
    assert len(config_rules) == 1
    assert config_rules[0]['Properties']['Source']['Owner'] == 'AWS'
    assert config_rules[0]['Properties']['Source']['SourceIdentifier'] == 'S3_BUCKET_VERSIONING_ENABLED'
"""
Test scaffolding for Cloud-Native Hardening and Cross-Stack Integration stack.
"""
import pytest

# Placeholder for future tests

from aws_cdk import App
from infra.stacks.cloud_native.cloud_native_hardening_stack import define_cloud_native_hardening_stack

def test_lambda_cloudwatch_alarms_synth():
    config = {
        'lambda_functions': [
            {
                'function_name': 'my-test-lambda',
                'error_threshold': 2,
                'duration_threshold_ms': 2500
            }
        ]
    }
    app = App()
    stack = define_cloud_native_hardening_stack(app, "TestCloudNativeHardeningStack", config)
    template = app.synth().get_stack_by_name("TestCloudNativeHardeningStack").template
    resources = template['Resources']
    alarm_types = [r for r in resources.values() if r['Type'] == 'AWS::CloudWatch::Alarm']
    assert len(alarm_types) == 2
    alarm_names = [r['Properties']['AlarmDescription'] for r in alarm_types]
    assert any('errors' in desc for desc in alarm_names)
    assert any('duration' in desc for desc in alarm_names)


def test_msk_cloudwatch_alarms_synth():
    config = {
        'msk_clusters': [
            {
                'cluster_name': 'my-msk-cluster',
                'under_replicated_threshold': 2,
                'broker_count_threshold': 3
            }
        ]
    }
    app = App()
    stack = define_cloud_native_hardening_stack(app, "TestMSKCloudNativeHardeningStack", config)
    template = app.synth().get_stack_by_name("TestMSKCloudNativeHardeningStack").template
    resources = template['Resources']
    alarm_types = [r for r in resources.values() if r['Type'] == 'AWS::CloudWatch::Alarm']
    assert len(alarm_types) == 2
    alarm_names = [r['Properties']['AlarmDescription'] for r in alarm_types]
    assert any('under-replicated' in desc for desc in alarm_names)
    assert any('broker count' in desc for desc in alarm_names)


def test_opensearch_cloudwatch_alarms_synth():
    config = {
        'opensearch_domains': [
            {
                'domain_name': 'my-os-domain',
                'status_red_threshold': 1,
                'cpu_util_threshold': 80
            }
        ]
    }
    app = App()
    stack = define_cloud_native_hardening_stack(app, "TestOSCloudNativeHardeningStack", config)
    template = app.synth().get_stack_by_name("TestOSCloudNativeHardeningStack").template
    resources = template['Resources']
    alarm_types = [r for r in resources.values() if r['Type'] == 'AWS::CloudWatch::Alarm']
    assert len(alarm_types) == 2
    alarm_names = [r['Properties']['AlarmDescription'] for r in alarm_types]
    assert any('cluster status red' in desc for desc in alarm_names)
    assert any('CPU utilization' in desc for desc in alarm_names)
