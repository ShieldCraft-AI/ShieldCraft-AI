import nox
import os
from datetime import datetime
from nox_sessions.utils import nox_session_guard
from .bootstrap import PYTHON_VERSIONS

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def notebooks(session):
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[NOTEBOOKS] Session started at {datetime.now()}\n")
    try:
        session.install("nbval")
        session.run("nbval", "--disable-warnings", "notebooks/")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[NOTEBOOKS] nbval run complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[NOTEBOOKS][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[NOTEBOOKS] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def notebook_lint(session):
    """Lint and format Jupyter notebooks with nbqa, ruff, and black."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[NOTEBOOK_LINT] Session started at {datetime.now()}\n")
    try:
        session.install("nbqa")
        session.install("ruff")
        session.install("black")
        session.run("nbqa", "ruff", "notebooks/")
        session.run("nbqa", "black", "notebooks/")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[NOTEBOOK_LINT] nbqa ruff and black complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[NOTEBOOK_LINT][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[NOTEBOOK_LINT] Session ended at {datetime.now()}\n")
