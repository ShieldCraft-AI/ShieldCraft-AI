from __future__ import annotations

import importlib
import sys
import types

import pytest

from tests._shim import importer as shim_importer


def test_local_modules_not_shimmed(monkeypatch):
    """Non-allowed module names should still raise ModuleNotFoundError."""
    shim_importer.install_shims()
    fake_name = "shieldcraft_local_missing_module"
    monkeypatch.delitem(sys.modules, fake_name, raising=False)
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(fake_name)


def test_real_dependency_prevents_shim(monkeypatch):
    """If a real module exists, the shim should not override it."""
    real_name = "boto3"
    real_module = types.ModuleType(real_name)
    monkeypatch.setitem(sys.modules, real_name, real_module)
    missing = shim_importer.install_shims()
    assert real_name not in missing
    assert sys.modules[real_name] is real_module


def test_missing_external_dependency_gets_shim(monkeypatch):
    """Allowed dependencies that are missing should receive shim modules on demand."""
    target = "aws_cdk"
    monkeypatch.delitem(sys.modules, target, raising=False)
    shim_importer.install_shims()
    module = importlib.import_module(target)
    assert getattr(module, "__shim__", False)
