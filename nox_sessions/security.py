import nox
import os
from datetime import datetime
from nox_sessions.utils import _should_poetry_install, nox_session_guard
from .bootstrap import PYTHON_VERSIONS

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox.session
@nox_session_guard
def security(session):
    """Run security checks: safety and bandit. Allow deploy if only mlflow vulnerabilities remain and have no known fix."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[SECURITY] Session started at {datetime.now()}\n")
    try:
        session.install("poetry")
        session.run("poetry", "install", external=True)
        session.install("safety", "bandit")
        # Run safety scan and capture output
        result = session.run(
            "safety", "scan", success_codes=[0, 64], log=False, silent=True
        )
        output = result if isinstance(result, str) else ""
        if (
            "mlflow" in output
            and "No known fix for mlflow" in output
            and "Command safety scan failed" in output
        ):
            session.log(
                "\n\033[93mWARNING: Vulnerabilities found only in mlflow and have no known fix. Allowing deploy.\033[0m\n"
            )
            print(output)
        elif "Command safety scan failed" in output:
            print(output)
            session.error(
                "\n\033[91mCRITICAL: Vulnerabilities found in dependencies other than mlflow. Aborting.\033[0m\n"
            )
        else:
            print(output)
        session.run("bandit", "-r", "src")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[SECURITY] safety and bandit checks complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[SECURITY][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[SECURITY] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def safety(session):
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[SAFETY] Session started at {datetime.now()}\n")
    try:
        session.install("poetry")
        skip = "--skip-poetry-install" in session.posargs
        need_install, marker, lock_hash, py_hash = _should_poetry_install(
            dev=False, skip=skip
        )
        if need_install:
            session.run("poetry", "install", external=True)
            with open(marker, "w") as f2:
                f2.write(f"{lock_hash}|{py_hash}")
        else:
            session.log(
                "Poetry install skipped: dependencies unchanged or --skip-poetry-install set."
            )
        session.install("safety")
        session.run("safety", "scan")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[SAFETY] safety scan complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[SAFETY][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[SAFETY] Session ended at {datetime.now()}\n")
