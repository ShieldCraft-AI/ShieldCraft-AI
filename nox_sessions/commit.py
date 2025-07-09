import nox
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
    """
    ShieldCraft AI: Single orchestration point for all developer/CI checks.
    This session must be the only entry for running all checks, version bump, checklist update, and final all-session.
    Do NOT call other sessions directly from scripts or CI—always use commit_flow for DRY, idempotent, and production-grade automation.
    """

    matrix_log(session, "🟩 commit_flow session started.", color="green")
    log_debug(f"Session started. posargs={session.posargs}")

    # Grouped session orchestration for clarity and DRYness
    import concurrent.futures

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

    # 2. Code quality sessions (parallel)
    matrix_log(
        session,
        f"Running code quality sessions: {', '.join(code_quality_sessions)}",
        color="green",
    )
    log_debug(f"Running code quality sessions: {code_quality_sessions}")
    failed = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(code_quality_sessions)
    ) as executor:
        future_to_session = {
            executor.submit(notify_and_log, s): s for s in code_quality_sessions
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
            f"Critical code quality session(s) failed: {[s for s, _ in failed]}"
        )

    # 3. Test and security sessions (parallel)
    matrix_log(
        session,
        f"Running test and security sessions: {', '.join(test_and_security_sessions)}",
        color="green",
    )
    log_debug(f"Running test and security sessions: {test_and_security_sessions}")
    failed = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(test_and_security_sessions)
    ) as executor:
        future_to_session = {
            executor.submit(notify_and_log, s): s for s in test_and_security_sessions
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
            f"Critical test/security session(s) failed: {[s for s, _ in failed]}"
        )

    # 4. Docs and docker build sessions (parallel)
    docs_and_docker_sessions = [
        "docs",
        "docker_build",
    ]
    matrix_log(
        session,
        f"Running docs and docker build sessions: {', '.join(docs_and_docker_sessions)}",
        color="green",
    )
    log_debug(f"Running docs and docker build sessions: {docs_and_docker_sessions}")
    failed = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(docs_and_docker_sessions)
    ) as executor:
        future_to_session = {
            executor.submit(notify_and_log, s): s for s in docs_and_docker_sessions
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
            f"Critical docs/docker session(s) failed: {[s for s, _ in failed]}"
        )

    matrix_log(session, "🟩 commit_flow session finished.", color="green")
    log_debug("Session finished.")

    matrix_log(session, "🟩 commit_flow session finished.", color="green")
    log_debug("Session finished.")
