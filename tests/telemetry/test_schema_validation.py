from scripts.drift_remediation import telemetry_schema as schema


def test_validate_log_success():
    payload = {
        "telemetry_type": "drift_stack",
        "stack": "TestStack",
        "comparison_status": "new_drift",
    }
    assert schema.validate_telemetry_log(payload)


def test_validate_log_missing_fields():
    payload = {"telemetry_type": "drift_stack", "stack": "OnlyStack"}
    assert not schema.validate_telemetry_log(payload)


def test_validate_artifact_success():
    payload = {
        "telemetry_type": "drift_summary",
        "stacks_scanned": 3,
        "drift_new_detected": 1,
        "drift_acknowledged": 2,
        "drift_baseline_missing": 0,
        "ci_forced": False,
    }
    assert schema.validate_telemetry_artifact(payload)


def test_validate_artifact_missing_field():
    payload = {
        "telemetry_type": "drift_summary",
        "stacks_scanned": 1,
        "drift_new_detected": 0,
        "drift_acknowledged": 0,
        "ci_forced": False,
    }
    assert not schema.validate_telemetry_artifact(payload)


def test_validators_are_total():
    assert not schema.validate_telemetry_log(None)
    assert not schema.validate_telemetry_artifact("invalid")
