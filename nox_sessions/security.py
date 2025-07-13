import nox
import os
from nox_sessions.utils import now_str
from nox_sessions.utils import nox_session_guard
from .bootstrap import PYTHON_VERSIONS
from nox_sessions.utils_encoding import force_utf8

force_utf8()

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox.session()
@nox_session_guard
def security(session):
    from nox_sessions.utils_poetry import ensure_poetry_installed

    ensure_poetry_installed()
    from nox_sessions.utils_color import color_log, color_error


@nox.session()
def audit_secrets(session):
    """Run audit script to check for plaintext secrets in config files."""
    session.run("poetry", "install", "--with", "dev", external=True)
    from nox_sessions.utils_color import color_log, color_error

    color_log(session, "[AUDIT] Running secrets audit...", style="cyan")
    config_files = ["config/dev.yml", "config/prod.yml", "config/staging.yml"]
    for config_file in config_files:
        try:
            session.run(
                "poetry",
                "run",
                "python",
                "scripts/audit_secrets.py",
                config_file,
                external=True,
            )
        except Exception as e:
            color_error(session, f"[AUDIT][ERROR] {config_file}: {e}")
            raise
    color_log(session, "[AUDIT] Secrets audit complete.", style="green")


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def safety(session):
    from nox_sessions.utils_color import color_log, color_error
    import os
    import subprocess

    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[SAFETY] Session started at {now_str()}\n")
    color_log(session, f"[SAFETY] Session started at {now_str()}", style="cyan")
    try:
        session.env["PYTHONIOENCODING"] = "UTF-8"
        session.env["PYTHONUTF8"] = "1"
        # Check Poetry version
        poetry_version_out = session.run(
            "poetry", "--version", silent=True, external=True
        )
        import re

        match = re.search(
            r"Poetry \(version ([0-9]+)\.([0-9]+)\.([0-9]+)\)", poetry_version_out
        )
        if not match:
            color_error(
                session, "[SAFETY][ERROR] Could not determine Poetry version. Aborting."
            )
            raise RuntimeError("Could not determine Poetry version")
        major, minor, patch = map(int, match.groups())
        if (major, minor) < (1, 2):
            color_error(
                session,
                f"[SAFETY][ERROR] Poetry >=1.2.0 required for 'poetry export', found {major}.{minor}.{patch}. Please upgrade Poetry in your environment.",
            )
            raise RuntimeError("Poetry version too old for export")
        # Export requirements
        session.run(
            "poetry",
            "export",
            "-f",
            "requirements.txt",
            "--output",
            "requirements.txt",
            "--without-hashes",
            external=True,
        )
        # Run safety check
        result = subprocess.run(
            [
                "poetry",
                "run",
                "safety",
                "check",
                "--file=requirements.txt",
                "--full-report",
            ],
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )
        print(result.stdout)
        if result.returncode != 0:
            color_error(
                session,
                f"[SAFETY][ERROR] safety check failed with exit code {result.returncode}",
            )
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write(
                    f"[SAFETY][ERROR] safety check failed with exit code {result.returncode}\n"
                )
            raise RuntimeError("Safety check failed")
        color_log(session, "[SAFETY] safety scan complete.", style="green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[SAFETY] safety scan complete.\n")
    except Exception as e:
        color_error(session, f"[SAFETY][ERROR] {e}")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[SAFETY][ERROR] {e}\n")
        raise
    finally:
        color_log(session, f"[SAFETY] Session ended at {now_str()}", style="cyan")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[SAFETY] Session ended at {now_str()}\n")
