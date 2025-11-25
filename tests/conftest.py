from __future__ import annotations

from tests._shim import install_shims

_SHIMS_INSTALLED = False


def pytest_configure(config):  # type: ignore[unused-argument]
    global _SHIMS_INSTALLED
    if _SHIMS_INSTALLED:
        return
    install_shims()
    _SHIMS_INSTALLED = True
