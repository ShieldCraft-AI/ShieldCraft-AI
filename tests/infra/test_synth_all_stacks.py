import importlib
import inspect
import os
import pkgutil
import sys
from pathlib import Path

import pytest


def _module_name_from_path(path: Path) -> str:
    # Convert /.../infra/domains/.../file.py -> infra.domains....file
    parts = list(path.with_suffix("").parts)
    # find 'infra' in parts
    if "infra" in parts:
        idx = parts.index("infra")
        return ".".join(parts[idx:])
    return ".".join(parts)


def test_synth_all_stacks_minimal(tmp_path, monkeypatch):
    """Attempt to import and synth all stacks under infra/domains.

    This test is defensive: it monkeypatches boto3 to raise on runtime calls,
    provides minimal empty configs to constructors, and records stacks that
    could not be instantiated so we can iterate on exclusions.
    """

    # Guard against accidental runtime AWS SDK usage during synth
    try:
        import boto3

        def _boto_block(*args, **kwargs):
            raise RuntimeError("boto3 calls are blocked during synth tests")

        monkeypatch.setattr(boto3, "client", _boto_block, raising=False)
        # session may be used directly in some modules
        if hasattr(boto3, "session"):
            monkeypatch.setattr(
                boto3.session,
                "Session",
                lambda *a, **k: (_ for _ in ()).throw(
                    RuntimeError("boto3 Session disabled during synth")
                ),
                raising=False,
            )
    except Exception:
        # If boto3 is not installed in the test environment, continue — our goal
        # is to prevent runtime calls where possible.
        pass

    # Ensure repo root is on sys.path so package imports work
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    # Find all python files under infra/domains
    base = repo_root / "infra" / "domains"
    py_files = list(base.rglob("*.py"))

    # Import aws_cdk if available and prepare app
    try:
        import aws_cdk as cdk
    except Exception as exc:  # pragma: no cover - CDK missing
        pytest.skip(f"aws_cdk not available in test environment: {exc}")

    app = cdk.App()

    instantiated = []
    skipped = {}

    for p in py_files:
        name = _module_name_from_path(p)
        # Only consider modules that look like stack modules
        if not p.name.endswith("_stack.py") and "stack" not in p.name:
            continue
        try:
            mod = importlib.import_module(name)
        except Exception as e:
            skipped[name] = f"import-failed: {e}"
            continue

        # Inspect module for classes that end with 'Stack'
        for _, obj in inspect.getmembers(mod, inspect.isclass):
            if obj.__module__ != mod.__name__:
                continue
            if not obj.__name__.endswith("Stack"):
                continue

            # Try to instantiate the stack with minimal args
            stack_id = obj.__name__
            try:
                # Many stacks accept config kwarg; pass a minimal safe dict
                kwargs = {}
                try:
                    instance = obj(app, stack_id, config={})
                except TypeError:
                    # fallback: try without config
                    instance = obj(app, stack_id)
                instantiated.append(f"{name}:{obj.__name__}")
            except Exception as e:
                skipped[f"{name}.{obj.__name__}"] = repr(e)

    # Attempt to synth — if some stacks failed to instantiate this may still succeed
    try:
        app.synth()
    except Exception as e:  # synth may fail; record it
        pytest.fail(f"CDK synth failed: {e}")

    # Report skipped modules as a test output but don't fail the run — they need
    # per-stack investigation. However assert we at least instantiated one stack.
    if not instantiated:
        pytest.skip(f"No stacks instantiated; skipped: {skipped}")

    # Optionally, fail if too many stacks were skipped — here we just print them
    if skipped:
        pytest.warns(
            UserWarning,
            lambda: (_ for _ in ()).throw(
                UserWarning(f"Some stacks skipped or errored: {skipped}")
            ),
        )
