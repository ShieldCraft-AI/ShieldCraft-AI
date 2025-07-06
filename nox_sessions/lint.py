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
def lint(session):
    """Lint code with ruff and black (no auto-fix)."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[LINT] Session started at {datetime.now()}\n")
    try:
        session.run("poetry", "run", "ruff", "check", ".")
        session.run("poetry", "run", "black", "--check", ".")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[LINT] ruff and black checks complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[LINT][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[LINT] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def format_check(session):
    """Check code formatting only (black, ruff)."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[FORMAT_CHECK] Session started at {datetime.now()}\n")
    try:
        session.run("poetry", "run", "black", "--check", ".")
        session.run("poetry", "run", "ruff", "check", ".")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[FORMAT_CHECK] black and ruff checks complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[FORMAT_CHECK][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[FORMAT_CHECK] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def format(session):
    """Auto-format code with black and ruff."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[FORMAT] Session started at {datetime.now()}\n")
    try:
        session.run("poetry", "run", "ruff", "check", ".", "--fix")
        session.run("poetry", "run", "black", ".")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[FORMAT] ruff --fix and black complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[FORMAT][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[FORMAT] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def typecheck(session):
    """Typecheck code with mypy."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[TYPECHECK] Session started at {datetime.now()}\n")
    try:
        session.run("poetry", "run", "mypy", "src")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[TYPECHECK] mypy run complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[TYPECHECK][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[TYPECHECK] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def precommit(session):
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[PRECOMMIT] Session started at {datetime.now()}\n")
    try:
        session.run("poetry", "run", "pre-commit", "run", "--all-files")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[PRECOMMIT] pre-commit run complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[PRECOMMIT][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[PRECOMMIT] Session ended at {datetime.now()}\n")
