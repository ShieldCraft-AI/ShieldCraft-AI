import nox
import os
from nox_sessions.utils import now_str, nox_session_guard, write_debug_log
from .bootstrap import PYTHON_VERSIONS
from nox_sessions.utils_encoding import force_utf8

force_utf8()

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def notebooks(session):
    """Validate and lint/format all Jupyter notebooks (nbval, nbqa, ruff, black)."""
    from nox_sessions.utils_color import color_log, color_error

    write_debug_log("[NOTEBOOKS] Session started", DEBUG_LOG_FILE)
    color_log(session, f"[NOTEBOOKS] Session started at {now_str()}", style="cyan")
    try:
        # Install all required tools
        session.install("nbval")
        session.install("pytest")
        session.install("nbqa")
        session.install("ruff")
        session.install("black")

        # 1. Validate notebooks with nbval/pytest
        color_log(
            session, "[NOTEBOOKS] Running nbval/pytest validation...", style="cyan"
        )
        session.run("pytest", "--nbval", "--disable-warnings", "notebooks/")
        color_log(session, "[NOTEBOOKS] nbval run complete.", style="green")

        # 2. Lint notebooks with nbqa ruff
        color_log(session, "[NOTEBOOKS] Running nbqa ruff...", style="cyan")
        session.run("nbqa", "ruff", "notebooks/")
        color_log(session, "[NOTEBOOKS] nbqa ruff complete.", style="green")

        # 3. Format notebooks with nbqa black
        color_log(session, "[NOTEBOOKS] Running nbqa black...", style="cyan")
        session.run("nbqa", "black", "notebooks/")
        color_log(session, "[NOTEBOOKS] nbqa black complete.", style="green")

        write_debug_log(
            "[NOTEBOOKS] nbval, nbqa ruff, and nbqa black complete.", DEBUG_LOG_FILE
        )
    except Exception as e:
        color_error(session, f"[NOTEBOOKS][ERROR] {e}")
        write_debug_log(f"[NOTEBOOKS][ERROR] {e}", DEBUG_LOG_FILE)
        raise
    finally:
        color_log(session, f"[NOTEBOOKS] Session ended at {now_str()}", style="cyan")
        write_debug_log("[NOTEBOOKS] Session ended", DEBUG_LOG_FILE)


# notebook_lint is now merged into notebooks session for DRYness and maintainability.
# The notebooks session now runs both validation and lint/format by default.
