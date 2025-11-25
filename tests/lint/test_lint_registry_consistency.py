from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.lint import lint_registry


def _meta(
    owner: str = "platform",
    tier: str = "core",
    capabilities: list[str] | None = None,
) -> dict:
    return {
        "enabled": True,
        "tier": tier,
        "owner": owner,
        "capabilities": capabilities or [],
    }


def test_snapshot_returns_sorted_order(monkeypatch):
    monkeypatch.setattr(
        lint_registry,
        "REGISTRY",
        {
            "beta": _meta("ops"),
            "alpha": _meta("platform"),
        },
    )

    snapshot = lint_registry.get_registry_snapshot()
    assert list(snapshot.keys()) == ["alpha", "beta"]


def test_register_module_duplicate_error(monkeypatch):
    monkeypatch.setattr(lint_registry, "REGISTRY", {"alpha": _meta()})
    with pytest.raises(ValueError) as exc:
        lint_registry.register_module("alpha", _meta(owner="ops"))
    assert "duplicate-module" in str(exc.value)


def test_persist_registry_snapshot_is_atomic(monkeypatch, tmp_path):
    target = tmp_path / "registry.json"
    registry = {
        "charlie": _meta(owner="sec"),
        "alpha": _meta(owner="platform"),
    }
    monkeypatch.setattr(lint_registry, "REGISTRY", registry)

    fsync_calls: list[int] = []

    def fake_fsync(fd):
        fsync_calls.append(fd)
        return None

    monkeypatch.setattr(lint_registry.os, "fsync", fake_fsync)

    lint_registry.persist_registry_snapshot(target)

    assert target.exists()
    data = json.loads(target.read_text(encoding="utf-8"))
    assert list(data.keys()) == ["alpha", "charlie"]
    assert fsync_calls, "fsync must be invoked for atomic write"
    assert not any(target.parent.glob("*.tmp"))


def test_persist_registry_snapshot_verbose_prints(monkeypatch, tmp_path, capsys):
    target = tmp_path / "registry.json"
    monkeypatch.setattr(
        lint_registry,
        "REGISTRY",
        {
            "alpha": _meta(),
        },
    )

    lint_registry.persist_registry_snapshot(target, verbose=True)

    output = capsys.readouterr().out.strip()
    assert json.loads(output) == {"alpha": _meta()}
    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == {"alpha": _meta()}


def test_detect_schema_drift_updates_snapshot_atomically(monkeypatch, tmp_path):
    registry = {
        "charlie": _meta(owner="sec"),
        "alpha": _meta(owner="platform"),
    }
    monkeypatch.setattr(lint_registry, "REGISTRY", registry)
    target = tmp_path / "registry.json"
    target.write_text("{}", encoding="utf-8")

    ok, event = lint_registry.detect_schema_drift(target, snapshot_update=True)

    assert ok is True
    assert event is None
    data = json.loads(target.read_text(encoding="utf-8"))
    assert list(data.keys()) == ["alpha", "charlie"]


def test_detect_schema_drift_multi_update_preserves_order(monkeypatch, tmp_path):
    registry = {
        "delta": _meta(owner="data"),
        "alpha": _meta(owner="platform"),
    }
    monkeypatch.setattr(lint_registry, "REGISTRY", registry)
    target = tmp_path / "registry.json"

    lint_registry.detect_schema_drift(target, snapshot_update=True)

    manual = {name: meta for name, meta in reversed(list(registry.items()))}
    target.write_text(json.dumps(manual), encoding="utf-8")

    lint_registry.detect_schema_drift(target, snapshot_update=True)

    restored = json.loads(target.read_text(encoding="utf-8"))
    assert restored == lint_registry.get_registry_snapshot()
