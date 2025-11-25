from __future__ import annotations

import importlib
import json

import pytest

from scripts.lint import lint_registry


def _meta(
    *,
    tier: str = "core",
    enabled: bool = True,
    owner: str = "platform",
    capabilities: list[str] | None = None,
) -> dict:
    return {
        "enabled": enabled,
        "tier": tier,
        "owner": owner,
        "capabilities": capabilities or [],
    }


def _core_registry(tier_overrides: dict[str, str] | None = None) -> dict:
    overrides = tier_overrides or {}
    return {
        name: _meta(tier=overrides.get(name, "core"))
        for name in lint_registry.CORE_MODULES
    }


def test_register_module_success(monkeypatch):
    monkeypatch.setattr(lint_registry, "REGISTRY", {})
    result = lint_registry.register_module("example", _meta())
    assert lint_registry.REGISTRY["example"] == result


def test_register_module_missing_metadata(monkeypatch):
    monkeypatch.setattr(lint_registry, "REGISTRY", {})
    with pytest.raises(ValueError):
        lint_registry.register_module("example", {"enabled": True, "tier": "core"})


def test_register_module_duplicate_with_changes(monkeypatch):
    monkeypatch.setattr(lint_registry, "REGISTRY", {})
    lint_registry.register_module("example", _meta())
    with pytest.raises(ValueError):
        lint_registry.register_module("example", _meta(owner="ops"))


def test_validate_registry_success(monkeypatch):
    registry = _core_registry()
    monkeypatch.setattr(lint_registry, "REGISTRY", registry)
    valid, failure = lint_registry.validate_registry()
    assert valid is True
    assert failure is None


def test_validate_registry_missing_core(monkeypatch):
    registry = _core_registry()
    registry.pop(next(iter(lint_registry.CORE_MODULES)))
    monkeypatch.setattr(lint_registry, "REGISTRY", registry)
    valid, failure = lint_registry.validate_registry()
    assert valid is False
    assert failure["target"] == "lint-registry-invalid"
    assert "missing-core" in failure["diagnostic"]


def test_validate_registry_strict_rejects_experimental(monkeypatch):
    overrides = {next(iter(lint_registry.CORE_MODULES)): "experimental"}
    registry = _core_registry(overrides)
    monkeypatch.setattr(lint_registry, "REGISTRY", registry)
    valid, failure = lint_registry.validate_registry(strict=True)
    assert valid is False
    assert "experimental-disallowed" in failure["diagnostic"]


class DummySession:
    def __init__(self, args=None):
        self.posargs = list(args or [])
        self.env = {}


def _reload_lint_module(monkeypatch):
    module = importlib.reload(importlib.import_module("nox_sessions.lint"))

    def fake_sequence(session, *, context):  # pylint: disable=unused-argument
        return None

    monkeypatch.setattr(module, "lint_all_sequence", fake_sequence)
    monkeypatch.setattr(module, "_run_lint_health_checks", lambda: None)
    monkeypatch.setattr(module, "_assert_capabilities_valid", lambda context: None)
    monkeypatch.setattr(module, "_assert_feature_flags_valid", lambda context: None)
    monkeypatch.setattr(module, "_run_registry_contract_check", lambda context: None)
    monkeypatch.setattr(module, "_enforce_registry_snapshot", lambda context: None)
    return module


def test_lint_all_prints_registry_in_verbose_mode(monkeypatch, capsys):
    lint_mod = _reload_lint_module(monkeypatch)
    calls = {"strict": None}

    def fake_validate(strict=False):
        calls["strict"] = strict
        return True, None

    snapshot = {"lint_registry": _meta()}

    monkeypatch.setattr(lint_mod, "validate_registry", fake_validate)
    monkeypatch.setattr(lint_mod, "get_registry_snapshot", lambda: snapshot)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    session = DummySession(["--verbose"])
    lint_mod.lint_all(session)

    lines = capsys.readouterr().out.strip().splitlines()
    expected = json.dumps(snapshot, sort_keys=True)
    assert expected in lines
    assert calls["strict"] is False


def test_lint_all_registry_in_ci_is_strict_and_quiet(monkeypatch, capsys):
    lint_mod = _reload_lint_module(monkeypatch)
    calls = {"strict": None}

    def fake_validate(strict=False):
        calls["strict"] = strict
        return True, None

    monkeypatch.setattr(lint_mod, "validate_registry", fake_validate)
    monkeypatch.setattr(
        lint_mod, "get_registry_snapshot", lambda: {"lint_registry": _meta()}
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    session = DummySession()
    lint_mod.lint_all(session)

    captured = capsys.readouterr().out.strip()
    assert captured == ""
    assert calls["strict"] is True
