import nox
import os
from datetime import datetime
from nox_sessions.utils import nox_session_guard

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)

PYTHON_VERSIONS = ["3.11"]


@nox.session(name="bootstrap", python=PYTHON_VERSIONS)
@nox_session_guard
def bootstrap(session):
    """Install all dependencies (with dev) and create marker file. Run this ONCE before all other sessions."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[BOOTSTRAP] Session started at {datetime.now()}\n")
    try:
        session.install("poetry")
        session.run("poetry", "install", "--with", "dev", external=True)
        # Write both marker files for dev and non-dev
        from nox_sessions.utils import file_hash

        lock_hash = file_hash("poetry.lock") if os.path.exists("poetry.lock") else ""
        py_hash = (
            file_hash("pyproject.toml") if os.path.exists("pyproject.toml") else ""
        )
        with open(".nox-poetry-installed", "w") as f2:
            f2.write(f"{lock_hash}|{py_hash}")
        with open(".nox-poetry-installed-dev", "w") as f2:
            f2.write(f"{lock_hash}|{py_hash}")
        session.log("Poetry install complete. Marker files written.")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[BOOTSTRAP] Poetry install and marker files written.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[BOOTSTRAP][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[BOOTSTRAP] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def meta(session):
    """Validate pyproject.toml and check for lock drift."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[META] Session started at {datetime.now()}\n")
    try:
        session.install("poetry")
        session.run("poetry", "check", external=True)
        session.run("poetry", "lock", external=True)
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[META] poetry check and lock complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[META][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[META] Session ended at {datetime.now()}\n")


@nox.session
@nox_session_guard
def clean(session):
    """Remove build, cache, and Python artifacts."""
    import shutil

    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[CLEAN] Session started at {datetime.now()}\n")
    try:
        for path in [".pytest_cache", ".nox", "dist", "build", "__pycache__"]:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
        for root, dirs, files in os.walk("."):
            for d in dirs:
                if d == "__pycache__":
                    shutil.rmtree(os.path.join(root, d), ignore_errors=True)
            for f2 in files:
                if f2.endswith(".pyc") or f2.endswith(".pyo"):
                    try:
                        os.remove(os.path.join(root, f2))
                    except Exception:
                        pass
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[CLEAN] Cleaned build/cache artifacts.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[CLEAN][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[CLEAN] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def dev(session):
    """Start a Python REPL with all dev dependencies installed."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[DEV] Session started at {datetime.now()}\n")
    try:
        session.install("poetry")
        session.run("poetry", "run", "python")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[DEV] Python REPL started.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DEV][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DEV] Session ended at {datetime.now()}\n")
