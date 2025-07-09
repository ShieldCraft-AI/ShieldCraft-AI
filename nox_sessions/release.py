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
def checklist(session):
    """Update checklist progress bar."""
    from nox_sessions.utils_color import color_log, color_error

    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[CHECKLIST] Session started at {now_str()}\n")
    color_log(session, f"[CHECKLIST] Session started at {now_str()}", style="cyan")
    try:
        session.run(
            "poetry", "run", "python", ".github/scripts/update_checklist_progress.py"
        )
        color_log(session, "[CHECKLIST] Checklist progress updated.", style="green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[CHECKLIST] Checklist progress updated.\n")
    except Exception as e:
        color_error(session, f"[CHECKLIST][ERROR] {e}")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[CHECKLIST][ERROR] {e}\n")
        raise
    finally:
        color_log(session, f"[CHECKLIST] Session ended at {now_str()}", style="cyan")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[CHECKLIST] Session ended at {now_str()}\n")
