import nox
import os
from nox_sessions.utils import now_str, nox_session_guard
from nox_sessions.utils_encoding import force_utf8
from nox_sessions.utils_color import matrix_log
from .bootstrap import PYTHON_VERSIONS

force_utf8()

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox_session_guard
@nox.session(name="spotcheck", python=PYTHON_VERSIONS)
def spotcheck(session):
    """Run the retrieval relevance spot-check harness (local-only).

    Pass-through any additional arguments to the script, e.g.:
      nox -s spotcheck -- --threshold 0.5 --pretty
    """
    start = now_str()
    with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[SPOTCHECK] Session started at {start}\n")
    matrix_log(session, f"[SPOTCHECK] Session started at {start}", color="green")
    try:
        args = ["poetry", "run", "python", "scripts/retrieval_spotcheck.py"]
        # Default pretty for visibility if user didn't provide flags
        user_args = list(session.posargs) if session.posargs else ["--pretty"]
        session.run(*args, *user_args, external=True)
        matrix_log(session, "[SPOTCHECK] Harness run complete.", color="green")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write("[SPOTCHECK] Harness run complete.\n")
    except Exception as e:
        matrix_log(session, f"[SPOTCHECK][ERROR] {e}", color="red")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[SPOTCHECK][ERROR] {e}\n")
        raise
    finally:
        end = now_str()
        matrix_log(session, f"[SPOTCHECK] Session ended at {end}", color="green")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[SPOTCHECK] Session ended at {end}\n")
