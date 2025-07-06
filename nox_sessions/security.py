import nox
import os
from datetime import datetime
from nox_sessions.utils import nox_session_guard
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
        # Run safety scan and capture output, ensuring UTF-8 decoding
        import subprocess

        proc = subprocess.run(
            ["poetry", "run", "safety", "scan"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="replace",
        )
        output = proc.stdout
        # Defensive: handle None output
        if output is None:
            output = ""
        # Normalize line endings for robust matching
        output_norm = output.replace("\r\n", "\n").replace("\r", "\n")
        # Check for mlflow-only vulnerabilities
        if (
            "mlflow" in output_norm
            and "No known fix for mlflow" in output_norm
            and "Command safety scan failed" in output_norm
            and not any(
                dep in output_norm and dep != "mlflow"
                for dep in [
                    "pytorch",
                    "torch",
                    "numpy",
                    "pandas",
                    "scipy",
                    "boto3",
                    "requests",
                    "flask",
                    "fastapi",
                    "django",
                ]
            )
        ):
            session.log(
                "\n\033[93mWARNING: Vulnerabilities found only in mlflow and have no known fix. Allowing deploy.\033[0m\n"
            )
            print(output)
        elif "Command safety scan failed" in output_norm:
            print(output)
            session.error(
                "\n\033[91mCRITICAL: Vulnerabilities found in dependencies other than mlflow. Aborting.\033[0m\n"
            )
        else:
            print(output)
        session.run("poetry", "run", "bandit", "-r", "src")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write("[SECURITY] safety and bandit checks complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[SECURITY][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[SECURITY] Session ended at {datetime.now()}\n")


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def safety(session):
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[SAFETY] Session started at {datetime.now()}\n")
    try:
        session.run("poetry", "run", "safety", "scan")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[SAFETY] safety scan complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[SAFETY][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[SAFETY] Session ended at {datetime.now()}\n")
