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


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    from nox_sessions.utils_color import matrix_log

    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[TESTS] Session started at {now_str()}\n")
    matrix_log(session, f"[TESTS] Session started at {now_str()}", color="green")
    try:
        # Node.js preflight: ensure npm/node deps are ready for infra tests (if needed)
        import shutil
        import sys

        node_bin = shutil.which("node")
        pre_npm = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "scripts", "pre_npm.py"
        )
        if node_bin and os.path.isfile(pre_npm):
            session.log("[TESTS] Running Node.js/npm preflight...")
            session.run(sys.executable, pre_npm, external=True)
            matrix_log(session, "[TESTS] Node.js/npm preflight complete.", color="cyan")
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write("[TESTS] Node.js/npm preflight complete.\n")
        # Always install all main and test dependencies unless user opts out
        if "--skip-poetry-install" not in session.posargs:
            session.run(
                "poetry",
                "install",
                "--no-interaction",
                "--with",
                "test",
            )
            matrix_log(session, "[TESTS] poetry install complete.", color="cyan")
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write("[TESTS] poetry install complete.\n")
        # By default, run pytest in parallel using pytest-xdist (-n auto), unless user disables with --no-xdist
        user_args = [
            a for a in session.posargs if a not in ("--force", "--skip-poetry-install")
        ]
        pytest_args = ["--color=yes", "--cov=src"]
        if not any(a.startswith("-n") or a == "--no-xdist" for a in user_args):
            pytest_args += ["-n", "auto"]
        pytest_args += user_args
        session.run(
            "poetry",
            "run",
            "pytest",
            *pytest_args,
        )
        matrix_log(session, "[TESTS] pytest run complete.", color="green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[TESTS] pytest run complete.\n")
    except Exception as e:
        matrix_log(session, f"[TESTS][ERROR] {e}", color="red")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[TESTS][ERROR] {e}\n")
        raise
    finally:
        matrix_log(session, f"[TESTS] Session ended at {now_str()}", color="green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[TESTS] Session ended at {now_str()}\n")


# Legacy orchestration and fast test sessions (test_fast, check, ci, all) have been removed.
# Use `tests` for all test runs, and `commit_flow` for full workflow orchestration.
