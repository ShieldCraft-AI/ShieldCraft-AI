from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import sys
import types
from types import ModuleType
from typing import Callable, Dict, Iterable, Optional, Sequence, Set

DEFAULT_TARGETS: Sequence[str] = (
    "aws_cdk",
    "boto3",
    "psycopg2",
    "torch",
    "nox",
)

ALLOWED_ROOTS: Set[str] = set(DEFAULT_TARGETS)
_IMPORTER: ShimImporter | None = None


class ShimObject:
    """Attribute proxy that raises when executed to flag missing deps."""

    def __init__(self, path: str):
        self._path = path

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<ShimObject {self._path}>"

    def __call__(self, *args, **kwargs):  # pragma: no cover - runtime guard
        raise RuntimeError(
            f"Shim placeholder invoked: {self._path}. Install the real dependency."
        )

    def __getattr__(self, item: str) -> "ShimObject":
        return ShimObject(f"{self._path}.{item}")


def _make_class(module_name: str, attr: str) -> type:
    return type(attr, (), {"__module__": module_name, "__shim__": True})


def _make_failing_function(label: str) -> Callable[..., object]:
    def _func(*_args, **_kwargs):
        raise RuntimeError(
            f"Shim placeholder executed: {label}. Install the dependency to use this function."
        )

    _func.__shim__ = True  # type: ignore[attr-defined]
    return _func


def _make_nox_session(
    _: str, attr: str
) -> Callable[..., Callable[[Callable[..., object]], Callable[..., object]]]:
    def decorator(*_args, **_kwargs):
        def wrapper(func):
            return func

        return wrapper

    decorator.__shim__ = True  # type: ignore[attr-defined]
    decorator.__name__ = attr
    return decorator


def _make_simple_namespace(module_name: str, attr: str) -> object:
    namespace = types.SimpleNamespace()
    namespace.__shim__ = True  # type: ignore[attr-defined]
    namespace.__module__ = module_name  # type: ignore[attr-defined]
    return namespace


_SPECIAL_ATTRS: Dict[str, Dict[str, Dict[str, Callable[[str, str], object]]]] = {
    "aws_cdk": {
        "aws_cdk": {
            "App": lambda module, attr: _make_class(module, attr),
            "Stack": lambda module, attr: _make_class(module, attr),
            "Stage": lambda module, attr: _make_class(module, attr),
            "Duration": lambda module, attr: _make_class(module, attr),
            "Environment": lambda module, attr: _make_class(module, attr),
            "Fn": lambda module, attr: _make_class(module, attr),
            "CfnOutput": lambda module, attr: _make_class(module, attr),
            "CfnTag": lambda module, attr: _make_class(module, attr),
            "RemovalPolicy": lambda module, attr: _make_class(module, attr),
            "Token": lambda module, attr: _make_class(module, attr),
            "Tags": lambda module, attr: _make_class(module, attr),
        }
    },
    "boto3": {
        "boto3": {
            "client": lambda module, attr: _make_failing_function(f"{module}.{attr}"),
            "resource": lambda module, attr: _make_failing_function(f"{module}.{attr}"),
            "session": lambda module, attr: _make_class(module, attr),
        }
    },
    "psycopg2": {
        "psycopg2": {
            "connect": lambda module, attr: _make_failing_function(f"{module}.{attr}"),
        }
    },
    "torch": {
        "torch": {
            "Tensor": lambda module, attr: _make_class(module, attr),
        },
        "torch.nn": {
            "Module": lambda module, attr: _make_class(module, attr),
        },
    },
    "nox": {
        "nox": {
            "session": _make_nox_session,
            "options": _make_simple_namespace,
        }
    },
}


def _lookup_special(
    module_name: str, attr: str
) -> Optional[Callable[[str, str], object]]:
    root = module_name.split(".")[0]
    if root not in _SPECIAL_ATTRS:
        return None
    module_attrs = _SPECIAL_ATTRS[root]
    if module_name in module_attrs and attr in module_attrs[module_name]:
        return module_attrs[module_name][attr]
    if "*" in module_attrs and attr in module_attrs["*"]:
        return module_attrs["*"][attr]
    return None


class ShimImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Meta-path importer that synthesizes placeholder modules when deps are absent."""

    def __init__(self, roots: Iterable[str]):
        self.roots: Set[str] = set(roots)

    def find_spec(self, fullname: str, path, target=None):  # type: ignore[override]
        root = fullname.split(".")[0]
        if root not in self.roots:
            return None
        if fullname in sys.modules and not getattr(
            sys.modules[fullname], "__shim__", False
        ):
            return None
        real_spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if real_spec is not None:
            self.roots.discard(root)
            return None
        return importlib.machinery.ModuleSpec(fullname, self, is_package=True)

    def create_module(self, spec):  # type: ignore[override]
        module = types.ModuleType(spec.name)
        return module

    def exec_module(self, module: ModuleType) -> None:  # type: ignore[override]
        module.__shim__ = True  # type: ignore[attr-defined]
        module.__loader__ = self
        module.__package__ = module.__name__
        module.__all__ = []
        module.__dict__.setdefault("__path__", [])
        module.__getattr__ = lambda attr, _module=module: self._resolve_attr(  # type: ignore[attr-defined]
            _module, attr
        )
        self._apply_specials(module)

    def _resolve_attr(self, module: ModuleType, attr: str):
        if attr.startswith("__") and attr.endswith("__"):
            raise AttributeError(attr)
        factory = _lookup_special(module.__name__, attr)
        if factory:
            value = factory(module.__name__, attr)
            module.__dict__[attr] = value
            return value
        if attr.islower() or "_" in attr:
            submodule_name = f"{module.__name__}.{attr}"
            if submodule_name in sys.modules:
                return sys.modules[submodule_name]
            submodule = types.ModuleType(submodule_name)
            submodule.__shim__ = True  # type: ignore[attr-defined]
            submodule.__package__ = submodule_name
            submodule.__loader__ = self
            submodule.__all__ = []
            submodule.__dict__.setdefault("__path__", [])
            submodule.__getattr__ = lambda name, _module=submodule: self._resolve_attr(  # type: ignore[attr-defined]
                _module, name
            )
            sys.modules[submodule_name] = submodule
            return submodule
        if attr[:1].isupper():
            value = _make_class(module.__name__, attr)
            module.__dict__[attr] = value
            return value
        value = ShimObject(f"{module.__name__}.{attr}")
        module.__dict__[attr] = value
        return value

    def _apply_specials(self, module: ModuleType) -> None:
        root = module.__name__.split(".")[0]
        module_overrides = _SPECIAL_ATTRS.get(root, {})
        attrs = module_overrides.get(module.__name__)
        if not attrs:
            return
        for attr, factory in attrs.items():
            module.__dict__[attr] = factory(module.__name__, attr)


def _is_available(name: str) -> bool:
    existing = sys.modules.get(name)
    if existing and not getattr(existing, "__shim__", False):
        return True
    spec = importlib.machinery.PathFinder.find_spec(name, None)
    return spec is not None


def install_shims(extra_targets: Optional[Iterable[str]] = None) -> Set[str]:
    global _IMPORTER
    targets = set(DEFAULT_TARGETS)
    if extra_targets:
        for candidate in extra_targets:
            root = candidate.split(".")[0]
            ALLOWED_ROOTS.add(root)
            targets.add(root)
    missing = {name for name in targets if not _is_available(name)}
    if not missing:
        return set()
    if _IMPORTER is None:
        _IMPORTER = ShimImporter(missing)
        sys.meta_path.insert(0, _IMPORTER)
    else:
        _IMPORTER.roots.update(missing)
    return missing


__all__ = [
    "install_shims",
    "ShimImporter",
    "ShimObject",
    "DEFAULT_TARGETS",
    "ALLOWED_ROOTS",
]
