import nox
import os
from datetime import datetime
from nox_sessions.utils import nox_session_guard
from .bootstrap import PYTHON_VERSIONS, _should_poetry_install

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox.session
@nox_session_guard
def bump_version(session):
    """Bump the project version. Usage: nox -s bump_version -- <new_version>"""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[RELEASE_BUMP] Session started at {datetime.now()}\n")
    try:
        session.install("poetry")
        if not session.posargs:
            session.error(
                "No version specified. Usage: nox -s bump_version -- <new_version>"
            )
        new_version = session.posargs[0]
        session.run("poetry", "version", new_version, external=True)
        session.run("git", "add", "pyproject.toml", external=True)
        session.run(
            "git",
            "commit",
            "-m",
            f"chore: bump version to {new_version}",
            external=True,
        )
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[RELEASE_BUMP] Version bumped to {new_version}.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[RELEASE_BUMP][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[RELEASE_BUMP] Session ended at {datetime.now()}\n")


@nox.session
@nox_session_guard
def release(session):
    """Automate version bump, changelog, and git tagging."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[RELEASE] Session started at {datetime.now()}\n")
    try:
        session.install("poetry")
        session.run("poetry", "version", "patch", external=True)
        session.run("git", "add", "pyproject.toml", external=True)
        session.run(
            "git", "commit", "-m", "chore: bump version [nox release]", external=True
        )
        session.run("git", "tag", "v$(poetry version -s)", external=True)
        session.run("git", "push", "--follow-tags", external=True)
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[RELEASE] Version bumped, tagged, and pushed.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[RELEASE][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[RELEASE] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def checklist(session):
    """Update checklist progress bar."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[CHECKLIST] Session started at {datetime.now()}\n")
    try:
        session.install("poetry")
        skip = "--skip-poetry-install" in session.posargs
        _should_poetry_install(dev=False, skip=skip)
        session.run(
            "poetry", "run", "python", ".github/scripts/update_checklist_progress.py"
        )
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[CHECKLIST] Checklist progress updated.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[CHECKLIST][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[CHECKLIST] Session ended at {datetime.now()}\n")
