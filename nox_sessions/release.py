import nox
import os
from datetime import datetime
from nox_sessions.utils import nox_session_guard
from .bootstrap import PYTHON_VERSIONS

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox.session(python=PYTHON_VERSIONS)
@nox_session_guard
def checklist(session):
    """Update checklist progress bar."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[CHECKLIST] Session started at {datetime.now()}\n")
    try:
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
