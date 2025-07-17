import nox
import os
from nox_sessions.utils import now_str
from nox_sessions.utils import nox_session_guard
from nox_sessions.utils_color import color_log, color_error
from nox_sessions.utils_encoding import force_utf8
from nox_sessions.utils_poetry import ensure_poetry_installed


force_utf8()

# Dynamically read Python version from .python-version
import os


def get_python_versions():
    version_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), ".python-version"
    )
    try:
        with open(version_file, "r") as f:
            version = f.read().strip()
            return [version]
    except Exception:
        return ["3.12"]  # Fallback to default


PYTHON_VERSIONS = get_python_versions()

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox_session_guard
@nox.session(name="precommit_bootstrap", python=PYTHON_VERSIONS)
def precommit_bootstrap(session):
    """Ensure pre-commit is installed and hooks are up-to-sudo apt install xfce4-clipmandate."""
    color_log(
        session, "Ensuring pre-commit is installed and hooks are set up...", "cyan"
    )
    session.install("pre-commit")
    session.run("pre-commit", "install", external=True)
    # Do not autoupdate by default to avoid breaking changes; run manually if needed
    color_log(session, "pre-commit install complete.", "green")


@nox_session_guard
@nox.session(name="bootstrap", python=PYTHON_VERSIONS)
def bootstrap(session):
    """Install all dependencies (with dev) and create marker file. Run this ONCE before all other sessions."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[BOOTSTRAP] Session started at {now_str()}\n")
    try:
        color_log(session, "Ensuring poetry is installed...", "cyan")
        # Use the utility function to ensure poetry is installed
        ensure_poetry_installed()
        color_log(session, "Installing all dependencies (with dev)...", "cyan")
        session.run("poetry", "install", "--with", "dev", external=True)
        color_log(session, "Installing pre-commit hooks...", "cyan")
        session.notify("precommit_bootstrap")
        from nox_sessions.utils import file_hash

        lock_hash = file_hash("poetry.lock") if os.path.exists("poetry.lock") else ""
        py_hash = (
            file_hash("pyproject.toml") if os.path.exists("pyproject.toml") else ""
        )
        # Write both standard and dev marker files for robust environment validation
        marker_paths = [
            os.path.abspath(".nox-poetry-installed"),
            os.path.abspath(".nox-poetry-installed-dev"),
        ]
        marker_value = f"{lock_hash}|{py_hash}"
        for marker_path in marker_paths:
            with open(marker_path, "w") as f2:
                f2.write(marker_value + "\n")
            color_log(
                session, f"[DEBUG] Marker file written at: {marker_path}", "yellow"
            )
            color_log(session, f"[DEBUG] Marker value: {marker_value}", "yellow")
            try:
                with open(marker_path, "r", encoding="utf-8") as f2:
                    marker_content = f2.read().strip()
                color_log(
                    session, f"[DEBUG] Marker file content: {marker_content}", "yellow"
                )
            except Exception as e:
                color_log(session, f"[DEBUG] Error reading marker file: {e}", "red")
        color_log(session, "Environment setup complete. Marker files written.", "green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[BOOTSTRAP] Environment setup and marker files written.\n")
    except Exception as e:
        color_error(session, f"[BOOTSTRAP][ERROR] {e}", "red")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[BOOTSTRAP][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[BOOTSTRAP] Session ended at {now_str()}\n")


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def meta(session):
    """Validate pyproject.toml and check for lock drift."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[META] Session started at {now_str()}\n")
    try:
        color_log(session, "Validating pyproject.toml and poetry.lock...", "cyan")
        session.install("poetry")
        session.run("poetry", "check", external=True)
        session.run("poetry", "lock", external=True)
        color_log(session, "poetry check and lock complete.", "green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[META] poetry check and lock complete.\n")
    except Exception as e:
        color_error(session, f"[META][ERROR] {e}", "red")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[META][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[META] Session ended at {now_str()}\n")


@nox_session_guard
@nox.session()
def clean(session):
    """Remove build, cache, and Python artifacts."""
    import shutil

    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[CLEAN] Session started at {now_str()}\n")
    try:
        color_log(session, "Cleaning build, cache, and Python artifacts...", "yellow")
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
        color_log(session, "Cleaned build/cache artifacts.", "green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[CLEAN] Cleaned build/cache artifacts.\n")
    except Exception as e:
        color_error(session, f"[CLEAN][ERROR] {e}", "red")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[CLEAN][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[CLEAN] Session ended at {now_str()}\n")


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def dev(session):
    """Start a Python REPL with all dev dependencies installed."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[DEV] Session started at {now_str()}\n")
    try:
        color_log(session, "Starting Python REPL with dev dependencies...", "cyan")
        session.run("poetry", "install", "--with", "dev", external=True)
        session.run("poetry", "run", "python", external=True)
        color_log(session, "Python REPL started.", "green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[DEV] Python REPL started.\n")
    except Exception as e:
        color_error(session, f"[DEV][ERROR] {e}", "red")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DEV][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DEV] Session ended at {now_str()}\n")
