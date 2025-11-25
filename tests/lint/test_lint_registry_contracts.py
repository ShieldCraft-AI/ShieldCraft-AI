from __future__ import annotations

import json

import pytest

from scripts.lint import lint_registry


def _feature_matrix() -> dict[str, bool]:
    return {
        "contracts": True,
        "snapshots": True,
        "resilience_layer": True,
        "health_checks": True,
        "formatting": True,
        "events_unified": True,
        "lint_all_quiet_retry": True,
    }


def _registry_entry(*, capabilities: list[str]) -> dict:
    return {
        "enabled": True,
        "tier": "core",
        "owner": "platform",
        "capabilities": capabilities,
    }


def _write_registry(tmp_path, data) -> str:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_validate_capabilities_success():
    registry = {
        "lint_contract": _registry_entry(capabilities=["contracts"]),
    }
    ok, reason = lint_registry.validate_capabilities(registry, _feature_matrix())
    assert ok is True
    assert reason is None


def test_validate_capabilities_unknown_capability():
    registry = {
        "lint_contract": _registry_entry(capabilities=["unknown"]),
    }
    ok, reason = lint_registry.validate_capabilities(registry, _feature_matrix())
    assert ok is False
    assert reason.startswith("unknown-capability:lint_contract:")


def test_validate_capabilities_deprecated(monkeypatch):
    registry = {
        "lint_contract": _registry_entry(capabilities=["contracts"]),
    }
    matrix = _feature_matrix()
    monkeypatch.setattr(lint_registry, "DEPRECATED_CAPABILITIES", {"contracts"})

    ok, reason = lint_registry.validate_capabilities(registry, matrix)
    assert ok is False
    assert reason == "deprecated-capability:lint_contract:contracts"


def test_lint_registry_contract_check_success(monkeypatch, tmp_path):
    registry_path = _write_registry(
        tmp_path,
        {
            "lint_contract": _registry_entry(capabilities=["contracts"]),
        },
    )
    monkeypatch.setattr(lint_registry, "load_feature_matrix", _feature_matrix)

    event = lint_registry.lint_registry_contract_check(registry_path)
    assert event["status"] == "ok"


def test_lint_registry_contract_check_unknown(monkeypatch, tmp_path):
    registry_path = _write_registry(
        tmp_path,
        {
            "lint_contract": _registry_entry(capabilities=["unknown"]),
        },
    )
    monkeypatch.setattr(lint_registry, "load_feature_matrix", _feature_matrix)

    event = lint_registry.lint_registry_contract_check(registry_path)
    assert event["status"] == "error"
    assert "unknown-capability" in event["diagnostic"]


def test_lint_registry_contract_check_missing_feature_matrix(monkeypatch, tmp_path):
    registry_path = _write_registry(
        tmp_path,
        {
            "lint_contract": _registry_entry(capabilities=["contracts"]),
        },
    )

    def _raise():
        raise ValueError("feature-matrix-missing")

    monkeypatch.setattr(lint_registry, "load_feature_matrix", _raise)

    event = lint_registry.lint_registry_contract_check(registry_path)
    assert event["status"] == "error"
    assert event["diagnostic"] == "feature-matrix-missing"


def test_lint_registry_contract_check_verbose_diagnostics(monkeypatch, tmp_path):
    registry_path = _write_registry(
        tmp_path,
        {
            "lint_contract": _registry_entry(capabilities=["unknown"]),
        },
    )
    monkeypatch.setattr(lint_registry, "load_feature_matrix", _feature_matrix)

    quiet_event = lint_registry.lint_registry_contract_check(
        registry_path, verbose=False
    )
    verbose_event = lint_registry.lint_registry_contract_check(
        registry_path, verbose=True
    )

    assert quiet_event.get("diagnostic", "").startswith("unknown-capability")
    assert "module-count=1" in (verbose_event.get("diagnostic") or "")


def test_detect_schema_drift_handles_matching_snapshot(monkeypatch, tmp_path):
    registry = {
        "lint_contract": _registry_entry(capabilities=["contracts"]),
        "lint_registry": _registry_entry(capabilities=[]),
    }
    monkeypatch.setattr(lint_registry, "REGISTRY", registry)
    snapshot_path = tmp_path / "registry.json"
    lint_registry.persist_registry_snapshot(snapshot_path)

    ok, event = lint_registry.detect_schema_drift(snapshot_path, snapshot_update=False)

    assert ok is True
    assert event is None


def test_detect_schema_drift_emits_failure_when_mismatched(monkeypatch, tmp_path):
    registry = {
        "lint_contract": _registry_entry(capabilities=["contracts"]),
    }
    monkeypatch.setattr(lint_registry, "REGISTRY", registry)
    snapshot_path = tmp_path / "registry.json"
    snapshot_path.write_text(
        json.dumps({"legacy": _registry_entry(capabilities=[])}),
        encoding="utf-8",
    )

    ok, event = lint_registry.detect_schema_drift(snapshot_path, snapshot_update=False)

    assert ok is False
    assert event is not None
    assert event["target"] == "lint-registry-schema"
    assert event["diagnostic"].startswith(lint_registry.SCHEMA_DRIFT_DIAGNOSTIC)


def test_detect_schema_drift_updates_snapshot_when_allowed(monkeypatch, tmp_path):
    registry = {
        "lint_contract": _registry_entry(capabilities=["contracts"]),
    }
    monkeypatch.setattr(lint_registry, "REGISTRY", registry)
    snapshot_path = tmp_path / "registry.json"
    snapshot_path.write_text(
        json.dumps({"legacy": _registry_entry(capabilities=[])}),
        encoding="utf-8",
    )

    ok, event = lint_registry.detect_schema_drift(snapshot_path, snapshot_update=True)

    assert ok is True
    assert event is None
    persisted = lint_registry.load_registry_snapshot(snapshot_path)
    assert persisted == lint_registry.get_registry_snapshot()


def test_load_registry_snapshot_raises_on_ioerror(monkeypatch, tmp_path):
    target = tmp_path / "registry.json"
    target.write_text("{}", encoding="utf-8")

    def boom(*_args, **_kwargs):  # noqa: D401
        raise OSError("boom")

    monkeypatch.setattr(lint_registry.Path, "read_text", boom)

    with pytest.raises(ValueError) as exc:
        lint_registry.load_registry_snapshot(target)
    assert str(exc.value) == "registry-snapshot-unreadable"


def test_load_registry_snapshot_detects_malformed_entry(tmp_path):
    target = tmp_path / "registry.json"
    target.write_text(json.dumps({"lint_contract": "bad"}), encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        lint_registry.load_registry_snapshot(target)
    assert str(exc.value) == "metadata-must-be-dict"


def test_load_registry_snapshot_detects_partial_capabilities(tmp_path):
    target = tmp_path / "registry.json"
    payload = {
        "lint_contract": {
            "enabled": True,
            "tier": "core",
            "owner": "platform",
            "capabilities": [""],
        }
    }
    target.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        lint_registry.load_registry_snapshot(target)
    assert str(exc.value) == "capabilities-invalid"
