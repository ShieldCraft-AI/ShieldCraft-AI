"""
ShieldCraft AI Nox Session Registry
===================================
This file registers all available Nox sessions for the ShieldCraft AI project.

Run `nox -l` to list all available sessions.
The main workflow is `commit_flow`.
"""

import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from nox_sessions.bootstrap import bootstrap
from nox_sessions.lint import lint, format, typecheck, precommit
from nox_sessions.test import tests
from nox_sessions.notebook import notebooks
from nox_sessions.docs import docs
from nox_sessions.docker import docker_build
from nox_sessions.security import security
from nox_sessions.commit import commit_flow
from nox_sessions.deploy import cdk_deploy
import nox

__all__ = [
    "bootstrap",
    "lint",
    "format",
    "typecheck",
    "precommit",
    "tests",
    "notebooks",
    "docs",
    "docker_build",
    "security",
    "commit_flow",
    "cdk_deploy",
]


# Nox global options
nox.options.reuse_existing_virtualenvs = True

# Session audit utility is currently disabled due to decorator/session issues.
# def session_audit():
#     """Print all registered Nox sessions and their docstrings for audit purposes."""
#     import importlib
#     session_names = __all__
#     print("\nRegistered Nox sessions:")
#     for name in session_names:
#         try:
#             for mod in [
#                 "nox_sessions.bootstrap",
#                 "nox_sessions.lint",
#                 "nox_sessions.test",
#                 "nox_sessions.notebook",
#                 "nox_sessions.docs",
#                 "nox_sessions.docker",
#                 "nox_sessions.security",
#                 "nox_sessions.commit",
#             ]:
#                 m = importlib.import_module(mod)
#                 if hasattr(m, name):
#                     func = getattr(m, name)
#                     doc = func.__doc__ or "(No docstring)"
#                     print(f"- {name}: {doc.strip().splitlines()[0]}")
#                     break
#             else:
#                 print(f"- {name}: (Not found in modules)")
#         except Exception as e:
#             print(f"- {name}: (Error: {e})")
