import nox
import os
from nox_sessions.utils import nox_session_guard

DEBUG_LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "commit_nox_debug.log")


def log_debug(msg):
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[commit_flow] {msg}\n")


@nox.session(name="commit_flow")
@nox_session_guard
def commit_flow(session):
    """Unified developer workflow for commit: runs all checks, version bump, checklist update, and final all-session. Does NOT perform git add/commit/push (user must do these manually)."""
    log_debug(f"Session started. posargs={session.posargs}")
    # Support --fast flag to skip slow/strict checks
    fast_mode = False
    if session.posargs and "--fast" in session.posargs:
        fast_mode = True
        log_debug("FAST mode enabled: skipping slow/strict checks.")

    log_debug("Notifying bootstrap session.")
    session.notify("bootstrap")

    # Define main sessions, and slow/strict sessions to skip in fast mode
    main_sessions = [
        "check",
        "format_check",
        "docs_lint",
        "meta",
        "docker_build",
        "docker_scan",
        "notebooks",
        "notebook_lint",
        "security",
    ]

    for s in main_sessions:
        log_debug(f"Notifying session: {s}")
        session.notify(s)
    if not fast_mode:
        log_debug("Notifying 'all' session.")
        session.notify("all")
    log_debug("Session finished.")
