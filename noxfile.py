"""
ShieldCraft AI Nox Session Registry
===================================
This file registers all available Nox sessions for the ShieldCraft AI project.

Run `nox -l` to list all available sessions.
The main workflow is `commit_flow`.
"""

import os
import sys
import importlib
import nox
import types
import inspect

# Ensure both project root and nox_sessions are in sys.path for robust imports
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
nox_sessions_path = os.path.join(project_root, "nox_sessions")
if nox_sessions_path not in sys.path:
    sys.path.insert(0, nox_sessions_path)


# Automatically scan and register all @nox.session functions from nox_sessions modules
def _auto_register_nox_sessions():
    sessions_dir = os.path.join(project_root, "nox_sessions")
    for fname in os.listdir(sessions_dir):
        if fname.startswith("_") or not fname.endswith(".py"):
            continue
        mod_name = f"nox_sessions.{fname[:-3]}"
        try:
            mod = importlib.import_module(mod_name)
        except ImportError as e:
            print(f"[Nox Auto-Scan] Failed to import {mod_name}: {e}")
            continue
        for name, obj in inspect.getmembers(mod):
            # Only register functions decorated with @nox.session
            if isinstance(obj, types.FunctionType) and hasattr(obj, "__nox_session__"):
                globals()[name] = obj


_auto_register_nox_sessions()


# Dynamically read Python version from .python-version
def get_python_versions():
    version_file = os.path.join(project_root, ".python-version")
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            version = f.read().strip()
            return [version]
    except (FileNotFoundError, OSError):
        return ["3.12"]  # Fallback to default


PYTHON_VERSIONS = get_python_versions()


# Nox global options
nox.options.reuse_existing_virtualenvs = True
