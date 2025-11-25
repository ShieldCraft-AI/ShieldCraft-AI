from __future__ import annotations

import importlib
import sys
import types

from tests._shim import install_shims


def test_install_shims_injects_placeholder(monkeypatch):
    target = "shim_example_pkg"
    monkeypatch.delitem(sys.modules, target, raising=False)
    installed = install_shims(extra_targets=[target])
    assert target in installed
    module = importlib.import_module(target)
    assert getattr(module, "__shim__", False) is True
    monkeypatch.delitem(sys.modules, target, raising=False)


def test_install_shims_does_not_override_real_modules(monkeypatch):
    target = "shim_real_pkg"
    real_module = types.ModuleType(target)
    monkeypatch.setitem(sys.modules, target, real_module)
    installed = install_shims(extra_targets=[target])
    assert target not in installed
    assert sys.modules[target] is real_module
