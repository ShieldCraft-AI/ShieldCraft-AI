import nox
import os
from datetime import datetime
from nox_sessions.utils import nox_session_guard
from .bootstrap import PYTHON_VERSIONS, _should_poetry_install

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def tests(session):
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[TESTS] Session started at {datetime.now()}\n")
    try:
        session.install("poetry")
        skip = "--skip-poetry-install" in session.posargs
        _should_poetry_install(dev=False, skip=skip)  # will error if not bootstrapped
        session.run(
            "poetry",
            "run",
            "pytest",
            "--cov=src",
            *[
                a
                for a in session.posargs
                if a not in ("--force", "--skip-poetry-install")
            ],
        )
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[TESTS] pytest run complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[TESTS][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[TESTS] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def test_fast(session):
    """Run only fast/unit tests (skip slow/integration)."""
    session.install("poetry")
    skip = "--skip-poetry-install" in session.posargs
    _should_poetry_install(dev=False, skip=skip)
    session.run(
        "poetry",
        "run",
        "pytest",
        "-m",
        "not slow",
        "--cov=src",
        *[a for a in session.posargs if a != "--skip-poetry-install"],
    )


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def check(session):
    """Run all checks: lint, typecheck, tests, safety, precommit."""
    session.notify("lint")
    session.notify("typecheck")
    session.notify("tests")
    session.notify("safety")
    session.notify("precommit")


@nox.session
@nox_session_guard
def ci(session):
    """Run all checks required for CI (fast, fail early)."""
    session.notify("check")
    session.notify("docs")
    session.notify("docs_lint")
    session.notify("docker_build")
    session.notify("docker_scan")
    session.notify("meta")
    session.notify("requirements")
    session.notify("security")


@nox.session
@nox_session_guard
def all(session):
    """Run all sessions: check, format, docs, notebooks, docker, scan, meta, clean, etc."""
    session.notify("check")
    session.notify("format")
    session.notify("notebooks")
    session.notify("notebook_lint")
    session.notify("docs")
    session.notify("docs_lint")
    session.notify("docker_build")
    session.notify("docker_scan")
    session.notify("meta")
    session.notify("requirements")
    session.notify("checklist")
    session.notify("security")
    session.notify("clean")
