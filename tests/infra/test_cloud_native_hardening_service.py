import pytest
from aws_cdk import App
from infra.stacks.cloud_native.cloud_native_hardening_service import (
    define_cloud_native_hardening_stack,
)


def test_lambda_cloudwatch_alarms_and_shared_resources():
    config = {
        "lambda_functions": [
            {
                "function_name": "my-test-lambda",
                "error_threshold": 2,
                "duration_threshold_ms": 2500,
            }
        ],
        "app": {
            "env": "test",
            "owner": "alice",
            "data_classification": "internal",
            "component": "ml-inference",
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
        },
    }
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestCloudNativeHardeningStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    # Check shared_resources for alarm ARNs
    sr = stack.shared_resources
    assert (
        "my-test-lambda-error-alarm-arn" in sr
        or "my-test-lambda_error_alarm_arn_arn" in sr
    )
    assert (
        "my-test-lambda-duration-alarm-arn" in sr
        or "my-test-lambda_duration_alarm_arn_arn" in sr
    )
    # Check tagging
    tags = stack.tags.render_tags() or []
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "alice" for tag in tags
    )
    # Remove unused variable warning
    pass


def test_msk_cloudwatch_alarms_and_shared_resources():
    config = {
        "msk_clusters": [
            {
                "cluster_name": "my-msk-cluster",
                "under_replicated_threshold": 2,
                "broker_count_threshold": 3,
            }
        ],
        "app": {
            "env": "test",
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
        },
    }
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestMSKCloudNativeHardeningStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    # Remove unused variable warning
    _ = stack
    sr = stack.shared_resources
    assert (
        "my-msk-cluster-under-replicated-alarm-arn" in sr
        or "my-msk-cluster_under_replicated_alarm_arn_arn" in sr
    )
    assert (
        "my-msk-cluster-broker-count-alarm-arn" in sr
        or "my-msk-cluster_broker_count_alarm_arn_arn" in sr
    )


def test_opensearch_cloudwatch_alarms_and_shared_resources():
    config = {
        "opensearch_domains": [
            {
                "domain_name": "my-os-domain",
                "status_red_threshold": 1,
                "cpu_util_threshold": 80,
            }
        ],
        "app": {
            "env": "test",
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
        },
    }
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestOSCloudNativeHardeningStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    sr = stack.shared_resources
    assert (
        "my-os-domain-status-red-alarm-arn" in sr
        or "my-os-domain_status_red_alarm_arn_arn" in sr
    )
    assert (
        "my-os-domain-cpu-util-alarm-arn" in sr
        or "my-os-domain_cpu_util_alarm_arn_arn" in sr
    )


def test_invalid_config_raises():
    # Missing required field in lambda_functions
    config = {"lambda_functions": [{"error_threshold": 2}], "app": {"env": "test"}}
    app = App()
    with pytest.raises(Exception):
        define_cloud_native_hardening_stack(
            app,
            "TestInvalidConfigStack",
            config,
            lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
            msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
            opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
        )


def test_tagging_consistency():
    config = {
        "app": {
            "env": "prod",
            "owner": "bob",
            "data_classification": "confidential",
            "component": "api",
        }
    }
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestTaggingStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    tags = stack.tags.render_tags() or []
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Environment" and tag.get("Value") == "prod" for tag in tags
    )
    assert any(tag.get("Key") == "Owner" and tag.get("Value") == "bob" for tag in tags)
    assert any(
        tag.get("Key") == "DataClassification" and tag.get("Value") == "confidential"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Component" and tag.get("Value") == "api" for tag in tags
    )


def test_lambda_alarm_has_sns_action():
    config = {
        "lambda_functions": [
            {
                "function_name": "my-sns-lambda",
                "error_threshold": 1,
                "duration_threshold_ms": 1000,
            }
        ],
        "app": {
            "env": "test",
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
        },
    }
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestSNSAlarmStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    # Remove unused variable warning
    _ = stack
    template = app.synth().get_stack_by_name("TestSNSAlarmStack").template
    alarm_resources = [
        r
        for r in template["Resources"].values()
        if r["Type"] == "AWS::CloudWatch::Alarm"
    ]
    # There should be 2 alarms (error, duration)
    assert len(alarm_resources) == 2
    # Both alarms should have an AlarmActions property referencing the SNS topic
    for alarm in alarm_resources:
        actions = alarm["Properties"].get("AlarmActions", [])
        assert any("sns" in str(a).lower() for a in actions)


def test_config_rule_outputs():
    config = {
        "aws_config_rules": [
            {
                "name": "s3-bucket-versioning",
                "identifier": "S3_BUCKET_VERSIONING_ENABLED",
                "type": "managed",
            }
        ],
        "app": {"env": "test"},
    }
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestConfigRuleStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    assert "s3-bucket-versioning" in stack.config_rules
    assert stack.config_rules["s3-bucket-versioning"]


def test_shared_resources_keys_mixed():
    config = {
        "lambda_functions": [{"function_name": "l1"}, {"function_name": "l2"}],
        "msk_clusters": [
            {"cluster_name": "m1"},
        ],
        "opensearch_domains": [{"domain_name": "os1"}],
        "app": {
            "env": "test",
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
        },
    }
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestSharedResourcesStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    sr = stack.shared_resources
    expected_keys = [
        "l1-error-alarm-arn",
        "l1-duration-alarm-arn",
        "l2-error-alarm-arn",
        "l2-duration-alarm-arn",
        "m1-under-replicated-alarm-arn",
        "m1-broker-count-alarm-arn",
        "os1-status-red-alarm-arn",
        "os1-cpu-util-alarm-arn",
    ]
    legacy_keys = [
        "l1_error_alarm_arn_arn",
        "l1_duration_alarm_arn_arn",
        "l2_error_alarm_arn_arn",
        "l2_duration_alarm_arn_arn",
        "m1_under_replicated_alarm_arn_arn",
        "m1_broker_count_alarm_arn_arn",
        "os1_status_red_alarm_arn_arn",
        "os1_cpu_util_alarm_arn_arn",
    ]
    for key in expected_keys:
        assert key in sr or legacy_keys[expected_keys.index(key)] in sr
        # Ensure the value is present
        assert sr.get(key) or sr.get(legacy_keys[expected_keys.index(key)])


def test_shared_resources_completeness_and_no_duplicates():
    config = {
        "lambda_functions": [
            {
                "function_name": "l1",
                "error_threshold": 1,
                "duration_threshold_ms": 1000,
            },
            {
                "function_name": "l2",
                "error_threshold": 2,
                "duration_threshold_ms": 2000,
            },
        ],
        "msk_clusters": [
            {
                "cluster_name": "m1",
                "under_replicated_threshold": 1,
                "broker_count_threshold": 2,
            },
        ],
        "opensearch_domains": [
            {"domain_name": "os1", "status_red_threshold": 1, "cpu_util_threshold": 80},
        ],
        "app": {
            "env": "test",
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
        },
    }
    app = App()
    stack1 = define_cloud_native_hardening_stack(
        app,
        "TestSharedResourcesStack1",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    stack2 = define_cloud_native_hardening_stack(
        app,
        "TestSharedResourcesStack2",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    sr1 = stack1.shared_resources
    sr2 = stack2.shared_resources
    expected_keys = [
        "l1-error-alarm-arn",
        "l1-duration-alarm-arn",
        "l2-error-alarm-arn",
        "l2-duration-alarm-arn",
        "m1-under-replicated-alarm-arn",
        "m1-broker-count-alarm-arn",
        "os1-status-red-alarm-arn",
        "os1-cpu-util-alarm-arn",
    ]
    legacy_keys = [
        "l1_error_alarm_arn_arn",
        "l1_duration_alarm_arn_arn",
        "l2_error_alarm_arn_arn",
        "l2_duration_alarm_arn_arn",
        "m1_under_replicated_alarm_arn_arn",
        "m1_broker_count_alarm_arn_arn",
        "os1_status_red_alarm_arn_arn",
        "os1_cpu_util_alarm_arn_arn",
    ]
    for key in expected_keys:
        # Check sr1
        assert (key in sr1 or legacy_keys[expected_keys.index(key)] in sr1) and (
            sr1.get(key) or sr1.get(legacy_keys[expected_keys.index(key)])
        )
        # Check sr2
        assert (key in sr2 or legacy_keys[expected_keys.index(key)] in sr2) and (
            sr2.get(key) or sr2.get(legacy_keys[expected_keys.index(key)])
        )
        # Ensure no duplicates
        val1 = sr1.get(key) or sr1.get(legacy_keys[expected_keys.index(key)])
        val2 = sr2.get(key) or sr2.get(legacy_keys[expected_keys.index(key)])
        assert val1 is not val2


def test_tag_propagation_and_override():
    config = {
        "app": {
            "env": "prod",
            "owner": "bob",
            "data_classification": "confidential",
            "component": "api",
        }
    }
    shared_tags = {"Extra": "Value", "Owner": "override"}
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestTagPropagationStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
        shared_tags=shared_tags,
    )
    tags = stack.tags.render_tags() or []
    assert any(
        tag.get("Key") == "Project" and tag.get("Value") == "ShieldCraftAI"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Environment" and tag.get("Value") == "prod" for tag in tags
    )
    assert any(
        tag.get("Key") == "Owner" and tag.get("Value") == "override" for tag in tags
    )
    assert any(
        tag.get("Key") == "Extra" and tag.get("Value") == "Value" for tag in tags
    )
    assert any(
        tag.get("Key") == "DataClassification" and tag.get("Value") == "confidential"
        for tag in tags
    )
    assert any(
        tag.get("Key") == "Component" and tag.get("Value") == "api" for tag in tags
    )


def test_alarm_outputs_and_arn_format():
    config = {
        "lambda_functions": [
            {
                "function_name": "l1",
                "error_threshold": 1,
                "duration_threshold_ms": 1000,
            },
        ],
        "app": {
            "env": "test",
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
        },
    }
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestAlarmOutputsStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    sr = stack.shared_resources
    for k, v in sr.items():
        if k.endswith("_alarm_arn"):
            assert isinstance(v, str)
            assert v.startswith("arn:") or v.startswith("${Token[")


def test_alarm_config_and_sns_action():
    config = {
        "lambda_functions": [
            {
                "function_name": "l1",
                "error_threshold": 1,
                "duration_threshold_ms": 1000,
            },
        ],
        "app": {
            "env": "test",
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
        },
    }
    app = App()
    define_cloud_native_hardening_stack(
        app,
        "TestAlarmConfigSNSStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    template = app.synth().get_stack_by_name("TestAlarmConfigSNSStack").template
    alarm_resources = [
        r
        for r in template["Resources"].values()
        if r["Type"] == "AWS::CloudWatch::Alarm"
    ]
    for alarm in alarm_resources:
        actions = alarm["Properties"].get("AlarmActions", [])
        assert any("sns" in str(a).lower() for a in actions)
        # Check threshold is as expected, only if AlarmName is present
        alarm_name = alarm["Properties"].get("AlarmName")
        if alarm_name and alarm_name.endswith("error-alarm"):
            assert alarm["Properties"]["Threshold"] == 1
        if alarm_name and alarm_name.endswith("duration-alarm"):
            assert alarm["Properties"]["Threshold"] == 1000


def test_invalid_alarm_threshold_raises():
    config = {
        "lambda_functions": [
            {
                "function_name": "l1",
                "error_threshold": -1,
                "duration_threshold_ms": 1000,
            },
        ],
        "app": {
            "env": "test",
            "sns_topic_arn": "arn:aws:sns:af-south-1:123456789012:MyTopic",
        },
    }
    app = App()
    with pytest.raises(ValueError):
        define_cloud_native_hardening_stack(
            app,
            "TestInvalidAlarmThresholdStack",
            config,
            lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
            msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
            opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
        )


def test_missing_app_config_raises():
    # App config missing entirely
    config = {
        "lambda_functions": [
            {"function_name": "l1", "error_threshold": 1, "duration_threshold_ms": 1000}
        ]
    }
    app = App()
    with pytest.raises(ValueError):
        define_cloud_native_hardening_stack(
            app,
            "TestMissingAppConfigStack",
            config,
            lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
            msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
            opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
        )


def test_invalid_msk_config_raises():
    # MSK cluster missing cluster_name
    config = {
        "msk_clusters": [
            {"under_replicated_threshold": 1, "broker_count_threshold": 2}
        ],
        "app": {"env": "test"},
    }
    app = App()
    with pytest.raises(ValueError):
        define_cloud_native_hardening_stack(
            app,
            "TestInvalidMSKConfigStack",
            config,
            lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
            msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
            opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
        )


def test_invalid_opensearch_config_raises():
    # OpenSearch domain missing domain_name
    config = {
        "opensearch_domains": [{"status_red_threshold": 1, "cpu_util_threshold": 80}],
        "app": {"env": "test"},
    }
    app = App()
    with pytest.raises(ValueError):
        define_cloud_native_hardening_stack(
            app,
            "TestInvalidOSConfigStack",
            config,
            lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
            msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
            opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
        )


def test_parallel_stack_instantiation():
    # Simulate parallel instantiation of stacks with different configs
    app = App()
    configs = [
        {
            "lambda_functions": [
                {
                    "function_name": f"l{i}",
                    "error_threshold": i,
                    "duration_threshold_ms": 1000 * i,
                }
            ],
            "app": {"env": f"env{i}", "owner": f"owner{i}"},
        }
        for i in range(1, 4)
    ]
    stacks = []
    for idx, cfg in enumerate(configs):
        stack = define_cloud_native_hardening_stack(
            app,
            f"ParallelStack{idx}",
            cfg,
            lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
            msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
            opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
        )
        stacks.append(stack)
    # Ensure each stack has unique shared_resources and tags
    for idx, stack in enumerate(stacks):
        sr = stack.shared_resources
        tags = stack.tags.render_tags() or []
        assert any(
            tag.get("Key") == "Owner" and tag.get("Value") == f"owner{idx+1}"
            for tag in tags
        )
        assert any(
            tag.get("Key") == "Environment" and tag.get("Value") == f"env{idx+1}"
            for tag in tags
        )
        assert all(isinstance(v, str) for v in sr.values())


def test_empty_lambda_functions_allowed():
    config = {
        "lambda_functions": [],
        "app": {"env": "test"},
    }
    app = App()
    stack = define_cloud_native_hardening_stack(
        app,
        "TestEmptyLambdaFunctionsStack",
        config,
        lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
        msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
        msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
        msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
        opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
    )
    assert stack.alarms == {}
    assert stack.shared_resources == {}


def test_duplicate_alarm_names_raise():
    config = {
        "lambda_functions": [
            {
                "function_name": "dup-lambda",
                "error_threshold": 1,
                "duration_threshold_ms": 1000,
            },
            {
                "function_name": "dup-lambda",
                "error_threshold": 2,
                "duration_threshold_ms": 2000,
            },
        ],
        "app": {"env": "test"},
    }
    app = App()
    with pytest.raises(Exception):
        define_cloud_native_hardening_stack(
            app,
            "TestDuplicateAlarmNamesStack",
            config,
            lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
            msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
            opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
        )


def test_invalid_config_rule_identifier_raises():
    config = {
        "aws_config_rules": [
            {"name": "bad-rule", "identifier": "NOT_A_VALID_RULE", "type": "managed"}
        ],
        "app": {"env": "test"},
    }
    app = App()
    with pytest.raises(ValueError):
        define_cloud_native_hardening_stack(
            app,
            "TestInvalidConfigRuleIdentifierStack",
            config,
            lambda_role_arn="arn:aws:iam::123456789012:role/MockLambdaRole",
            msk_client_role_arn="arn:aws:iam::123456789012:role/MockMSKClientRole",
            msk_producer_role_arn="arn:aws:iam::123456789012:role/MockMSKProducerRole",
            msk_consumer_role_arn="arn:aws:iam::123456789012:role/MockMSKConsumerRole",
            opensearch_role_arn="arn:aws:iam::123456789012:role/MockOpenSearchRole",
        )
