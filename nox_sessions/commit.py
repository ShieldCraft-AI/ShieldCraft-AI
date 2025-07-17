"""
Commit Flow Nox Session
"""

import nox
import concurrent.futures
import os
from nox_sessions.utils import nox_session_guard
from nox_sessions.utils_encoding import force_utf8
from nox_sessions.utils import now_str, validate_poetry_marker, write_debug_log

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


def log_debug(msg):
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[commit_flow] {now_str()} {msg}\n")


@nox.session(name="commit_flow")
@nox_session_guard
def commit_flow(session):
    # Session registry to track completed sessions and avoid duplicate work
    session_registry = {}

    def run_once(session_name, notify=True, parallel=False):
        if session_registry.get(session_name):
            matrix_log(
                session,
                f"[REGISTRY] Skipping already completed session: {session_name}",
                color="yellow",
            )
            return True
        try:
            if notify:
                if parallel:
                    matrix_log(
                        session,
                        f"▶ {session_name.upper()} running (parallel)...",
                        color="green",
                    )
                else:
                    matrix_log(
                        session, f"▶ {session_name.upper()} running...", color="green"
                    )
                log_debug(f"Notifying session: {session_name}")
                session.notify(session_name)
                matrix_log(
                    session, f"✅ {session_name.upper()} complete.", color="green"
                )
            session_registry[session_name] = True
            return True
        except Exception as e:
            matrix_log(session, f"❌ {session_name.upper()} failed: {e}", color="red")
            log_debug(f"Session {session_name} failed: {e}")
            session_registry[session_name] = False
            return False

    # Validate poetry marker before running any orchestration
    marker_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), ".nox-poetry-installed"
    )
    if not validate_poetry_marker(marker_file):
        write_debug_log(
            "[pre_nox] Poetry environment not bootstrapped or out of date. Run 'nox -s bootstrap' first."
        )
        matrix_log(
            session,
            "🟥 Nox commit_flow session failed. No commit performed.",
            color="red",
        )
        log_debug("[ERROR] Nox commit_flow session failed. No commit performed.")
        return
    nox.options.reuse_existing_virtualenv = True
    session.run("python", "scripts/clear_and_run_notebooks.py", external=True)
    matrix_log(session, "🟩 commit_flow session started.", color="green")
    log_debug(f"Session started. posargs={session.posargs}")

    # Session orchestration
    # 1. Bootstrap (serial, only if not already run)
    run_once("bootstrap")

    # 2. Code quality sessions in parallel
    code_quality_sessions = ["lint", "format", "typecheck", "precommit"]
    matrix_log(
        session,
        f"Running Code quality sessions: {', '.join(code_quality_sessions)}",
        color="green",
    )
    log_debug(f"Running Code quality sessions: {code_quality_sessions}")
    failed = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(code_quality_sessions)
    ) as executor:
        future_to_session = {
            executor.submit(run_once, s, parallel=True): s
            for s in code_quality_sessions
        }
        for future in concurrent.futures.as_completed(future_to_session):
            s = future_to_session[future]
            ok = future.result()
            if not ok:
                failed.append(s)
    if failed:
        for s in failed:
            matrix_log(session, f"❌ {s.upper()} failed.", color="red")
            log_debug(f"[FAIL] Session {s} failed.")
        raise RuntimeError(f"Critical Code quality session(s) failed: {failed}")

    # 3. Tests and notebooks sessions in parallel
    test_and_notebook_sessions = ["tests", "notebooks"]
    matrix_log(
        session,
        f"Running Test and notebook sessions: {', '.join(test_and_notebook_sessions)}",
        color="green",
    )
    log_debug(f"Running Test and notebook sessions: {test_and_notebook_sessions}")
    failed = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(test_and_notebook_sessions)
    ) as executor:
        future_to_session = {
            executor.submit(run_once, s, parallel=True): s
            for s in test_and_notebook_sessions
        }
        for future in concurrent.futures.as_completed(future_to_session):
            s = future_to_session[future]
            ok = future.result()
            if not ok:
                failed.append(s)
    if failed:
        for s in failed:
            matrix_log(session, f"❌ {s.upper()} failed.", color="red")
            log_debug(f"[FAIL] Session {s} failed.")
        raise RuntimeError(f"Critical Test and notebook session(s) failed: {failed}")

    # 4. Security session (serial)
    matrix_log(session, "Running Security session: security", color="green")
    log_debug("Running Security session: security")
    if not run_once("security"):
        raise RuntimeError("Critical Security session failed.")

    # 5. Docs and docker build sessions in parallel
    docs_and_docker_sessions = ["docs", "docker_build"]
    matrix_log(
        session,
        f"Running Docs and docker build sessions: {', '.join(docs_and_docker_sessions)}",
        color="green",
    )
    log_debug(f"Running Docs and docker build sessions: {docs_and_docker_sessions}")
    failed = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(docs_and_docker_sessions)
    ) as executor:
        future_to_session = {
            executor.submit(run_once, s, parallel=True): s
            for s in docs_and_docker_sessions
        }
        for future in concurrent.futures.as_completed(future_to_session):
            s = future_to_session[future]
            ok = future.result()
            if not ok:
                failed.append(s)
    if failed:
        for s in failed:
            matrix_log(session, f"❌ {s.upper()} failed.", color="red")
            log_debug(f"[FAIL] Session {s} failed.")
        raise RuntimeError(
            f"Critical Docs and docker build session(s) failed: {failed}"
        )

    matrix_log(session, "🟩 commit_flow session finished.", color="green")
    log_debug("Session finished.")
