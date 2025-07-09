import nox
import os
from nox_sessions.utils import now_str
from nox_sessions.utils import nox_session_guard

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox_session_guard
@nox.session()
def docs(session):
    """Build Docusaurus documentation."""
    from nox_sessions.utils_color import color_log, color_error

    with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[DOCS] Session started at {now_str()}\n")
    color_log(session, f"[DOCS] Session started at {now_str()}", style="cyan")
    prev_cwd = os.getcwd()
    try:
        os.chdir("docs-site")
        # Suppress noisy webpack VFileMessage warnings
        session.run(
            "bash",
            "-c",
            "npm run build 2>&1 | grep -v 'No serializer registered for VFileMessage' | grep -v 'PackFileCacheStrategy' | grep -v 'MDX compilation failed' | grep -v 'end-tag-mismatch'",
            external=True,
        )
        color_log(session, "[DOCS] npm build complete.", style="green")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write("[DOCS] npm build complete.\n")
    except Exception as e:
        color_error(session, f"[DOCS][ERROR] {e}")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[DOCS][ERROR] {e}\n")
        raise
    finally:
        os.chdir(prev_cwd)
        color_log(session, f"[DOCS] Session ended at {now_str()}", style="cyan")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[DOCS] Session ended at {now_str()}\n")


@nox_session_guard
@nox.session()
def docs_dev(session):
    """Run Docusaurus dev server with live reload."""
    from nox_sessions.utils_color import color_log, color_error

    with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[DOCS_DEV] Session started at {now_str()}\n")
    color_log(session, f"[DOCS_DEV] Session started at {now_str()}", style="cyan")
    prev_cwd = os.getcwd()
    try:
        os.chdir("docs-site")
        session.run("npm", "run", "start", external=True)
        color_log(session, "[DOCS_DEV] npm start complete.", style="green")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write("[DOCS_DEV] npm start complete.\n")
    except Exception as e:
        color_error(session, f"[DOCS_DEV][ERROR] {e}")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[DOCS_DEV][ERROR] {e}\n")
        raise
    finally:
        os.chdir(prev_cwd)
        color_log(session, f"[DOCS_DEV] Session ended at {now_str()}", style="cyan")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[DOCS_DEV] Session ended at {now_str()}\n")
