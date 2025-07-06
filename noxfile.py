# ShieldCraft AI Noxfile: Central session registry and environment config
import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import all session entrypoints
from nox_sessions.bootstrap import bootstrap
from nox_sessions.lint import lint, format, format_check, typecheck, precommit
from nox_sessions.test import tests
from nox_sessions.notebook import notebooks
from nox_sessions.docs import docs
from nox_sessions.docker import docker_build
from nox_sessions.security import security
from nox_sessions.commit import commit_flow
import nox

__all__ = [
    "bootstrap",
    "lint",
    "format",
    "format_check",
    "typecheck",
    "precommit",
    "tests",
    "notebooks",
    "docs",
    "docker_build",
    "security",
    "commit_flow",
]


nox.options.reuse_existing_virtualenvs = True
DEBUG_LOG_FILE = os.path.join(project_root, "commit_nox_debug.log")
try:
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"--- NOXFILE import at {__file__} ---\n")
except Exception as e:
    print(f"[WARN] Could not write to debug log: {e}")
