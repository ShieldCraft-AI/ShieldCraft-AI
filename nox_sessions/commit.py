"""
Commit Flow Nox Session
"""

import nox
import concurrent.futures
import os
from nox_sessions.utils import nox_session_guard
from nox_sessions.utils_encoding import force_utf8

force_utf8()

DEBUG_LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "commit_nox_debug.log")


def matrix_log(session, msg, color="green"):
    colors = {
        "green": "\033[1;32m",
        "reset": "\033[0m",
        "bold": "\033[1m",
        "black_bg": "\033[40m",
        "yellow": "\033[1;33m",
        "red": "\033[1;31m",
    }
    c = colors.get(color, colors["green"])
    session.log(f"{colors['black_bg']}{c}{msg}{colors['reset']}")


from nox_sessions.utils import now_str


def log_debug(msg):
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[commit_flow] {now_str()} {msg}\n")


@nox.session(name="commit_flow")
@nox_session_guard
def commit_flow(session):
    # Use shared virtualenv for all sessions
    nox.options.reuse_existing_virtualenv = True
    # Install only notebook dependencies for notebook tasks
    session.run("poetry", "install", "--with", "notebook", external=True)
    # Auto-clear and re-execute all notebooks before running checks
    session.run("python", "scripts/clear_and_run_notebooks.py", external=True)
    from nox_sessions.utils_poetry import ensure_poetry_installed

    ensure_poetry_installed()
    matrix_log(session, "🟩 commit_flow session started.", color="green")
    log_debug(f"Session started. posargs={session.posargs}")

    # Grouped session orchestration for clarity and DRYness
    # Optimized session orchestration: group by dependency and parallelizability
    # 1. Always run bootstrap first (serial, fail fast)
    bootstrap_session = ["bootstrap"]

    # 2. Lint, typecheck, and format can run in parallel (code quality)
    code_quality_sessions = [
        "lint",
        "format",
        "typecheck",
        "precommit",
    ]

    # 3. Security and tests can run in parallel (after code quality)
    test_and_security_sessions = [
        "tests",
        "notebooks",
        "security",
    ]

    # 4. Docs and docker build can run in parallel (after tests)

    def notify_and_log(s):
        matrix_log(session, f"▶ {s.upper()} running...", color="green")
        log_debug(f"Notifying session: {s}")
        try:
            # Install only required dependencies for each session
            if s == "lint":
                session.run("poetry", "install", "--with", "lint", external=True)
            elif s == "typecheck":
                session.run("poetry", "install", "--with", "typecheck", external=True)
            elif s == "tests":
                session.run("poetry", "install", "--with", "test", external=True)
            elif s == "notebooks":
                session.run("poetry", "install", "--with", "notebook", external=True)
            elif s == "security":
                session.run("poetry", "install", "--with", "security", external=True)
            elif s == "dev":
                session.run("poetry", "install", "--with", "dev", external=True)
            elif s == "docs":
                session.run("poetry", "install", "--with", "diagnostics", external=True)
            else:
                session.run("poetry", "install", "--only", "main", external=True)
            session.notify(s)
            matrix_log(session, f"✅ {s.upper()} complete.", color="green")
            return (s, True, None)
        except Exception as e:
            matrix_log(session, f"❌ {s.upper()} failed: {e}", color="red")
            log_debug(f"Session {s} failed: {e}")
            return (s, False, str(e))

    # 1. Bootstrap (serial)
    matrix_log(
        session, f"Running bootstrap session: {bootstrap_session[0]}", color="green"
    )
    log_debug("Running bootstrap session (serial)")
    session.notify(bootstrap_session[0])

    # 2-4. All other session groups in parallel, fail-fast on any error
    session_groups = [
        ("Code quality", code_quality_sessions),
        ("Test and security", test_and_security_sessions),
        ("Docs and docker build", ["docs", "docker_build"]),
    ]
    for group_name, group_sessions in session_groups:
        matrix_log(
            session,
            f"Running {group_name} sessions: {', '.join(group_sessions)}",
            color="green",
        )
        log_debug(f"Running {group_name} sessions: {group_sessions}")
        failed = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(group_sessions)
        ) as executor:
            future_to_session = {
                executor.submit(notify_and_log, s): s for s in group_sessions
            }
            for future in concurrent.futures.as_completed(future_to_session):
                s, ok, err = future.result()
                if not ok:
                    failed.append((s, err))
        if failed:
            for s, err in failed:
                matrix_log(session, f"❌ {s.upper()} failed: {err}", color="red")
                log_debug(f"[FAIL] Session {s} failed: {err}")
            raise RuntimeError(
                f"Critical {group_name} session(s) failed: {[s for s, _ in failed]}"
            )

    matrix_log(session, "🟩 commit_flow session finished.", color="green")
    log_debug("Session finished.")
