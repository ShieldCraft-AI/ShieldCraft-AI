import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from nox_sessions.bootstrap import bootstrap  # noqa: F401
from nox_sessions.lint import lint  # noqa: F401
from nox_sessions.test import tests  # noqa: F401
from nox_sessions.notebook import notebooks  # noqa: F401
from nox_sessions.docs import docs  # noqa: F401
from nox_sessions.docker import docker_build  # noqa: F401
from nox_sessions.security import security  # noqa: F401
from nox_sessions.release import bump_version  # noqa: F401
from nox_sessions.commit import commit_flow  # noqa: F401
__all__ = [
    "bootstrap",
    "lint",
    "tests",
    "notebooks",
    "docs",
    "docker_build",
    "security",
    "bump_version",
    "commit_flow",
]

# --- Debug log file for Nox sessions ---
DEBUG_LOG_FILE = os.path.join(project_root, "commit_nox_debug.log")
try:
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"--- NOXFILE import at {__file__} ---\n")
except Exception as e:
    print(f"[WARN] Could not write to debug log: {e}")
