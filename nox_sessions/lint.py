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


from nox_sessions.utils_color import matrix_log


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def lint(session):
    """Lint code with ruff and black (no auto-fix)."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[LINT] Session started at {now_str()}\n")
    matrix_log(session, f"[LINT] Session started at {now_str()}", color="green")
    try:
        # Ensure lint dependencies are installed
        session.run("poetry", "install", "--with", "lint", external=True)
        # Run ruff check (no auto-fix)
        matrix_log(session, "[LINT] Running ruff check...", color="green")
        ruff_result = session.run(
            "poetry",
            "run",
            "ruff",
            "check",
            ".",
            success_codes=[0, 1],
            silent=True,
            external=True,
        )
        matrix_log(session, "[LINT] Running black check...", color="green")
        # Run black check, auto-fix if needed, then re-check
        black_result = session.run(
            "poetry",
            "run",
            "black",
            "--check",
            ".",
            success_codes=[0, 1],
            silent=True,
            external=True,
        )
        if black_result == 1:
            matrix_log(
                session,
                "[LINT] Black found formatting issues, auto-formatting...",
                color="yellow",
            )
            session.run("poetry", "run", "black", ".", external=True)
            # Re-run ruff and black check after auto-format
            ruff_result2 = session.run(
                "poetry",
                "run",
                "ruff",
                "check",
                ".",
                success_codes=[0, 1],
                silent=True,
                external=True,
            )
            black_result2 = session.run(
                "poetry",
                "run",
                "black",
                "--check",
                ".",
                success_codes=[0, 1],
                silent=True,
                external=True,
            )
            if black_result2 != 0:
                matrix_log(
                    session,
                    "[LINT][ERROR] Black could not auto-fix all issues.",
                    color="red",
                )
                raise RuntimeError("Black could not auto-fix all issues.")
            if ruff_result2 == 1:
                matrix_log(
                    session,
                    "[LINT] Ruff still found lint issues after auto-format.",
                    color="yellow",
                )
        if ruff_result == 0 and black_result == 0:
            matrix_log(session, "[LINT] ruff and black checks complete.", color="green")
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write("[LINT] ruff and black checks complete.\n")
        elif black_result == 1:
            matrix_log(
                session,
                "[LINT] Black auto-format applied. Please review changes.",
                color="yellow",
            )
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write("[LINT] Black auto-format applied. Please review changes.\n")
        elif ruff_result == 1:
            matrix_log(
                session,
                "[LINT] Ruff found lint issues. Please review.",
                color="yellow",
            )
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write("[LINT] Ruff found lint issues. Please review.\n")
    except Exception as e:
        matrix_log(session, f"[LINT][ERROR] {e}", color="red")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[LINT][ERROR] {e}\n")
        raise
    finally:
        matrix_log(session, f"[LINT] Session ended at {now_str()}", color="green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[LINT] Session ended at {now_str()}\n")


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def format(session):
    """Auto-format code with black and ruff. Never fail the build on fixable linting issues."""

    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[FORMAT] Session started at {now_str()}\n")
    matrix_log(session, f"[FORMAT] Session started at {now_str()}", color="green")
    try:
        matrix_log(session, "[FORMAT] Running ruff --fix...", color="green")
        session.run(
            "poetry",
            "run",
            "ruff",
            "check",
            ".",
            "--fix",
            success_codes=[0, 1],
            silent=True,
            external=True,
        )
        matrix_log(session, "[FORMAT] Running black...", color="green")
        session.run(
            "poetry",
            "run",
            "black",
            ".",
            success_codes=[0, 1],
            silent=True,
            external=True,
        )
        # After auto-fix, check if any unfixable issues remain
        ruff_check = session.run(
            "poetry",
            "run",
            "ruff",
            "check",
            ".",
            success_codes=[0, 1],
            silent=True,
            external=True,
        )
        black_check = session.run(
            "poetry",
            "run",
            "black",
            "--check",
            ".",
            success_codes=[0, 1],
            silent=True,
            external=True,
        )
        if black_check != 0:
            matrix_log(
                session,
                "[FORMAT][ERROR] Black could not auto-fix all issues. Failing build.",
                color="red",
            )
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write("[FORMAT][ERROR] Black could not auto-fix all issues. Failing build.\n")
            raise RuntimeError("Black could not auto-fix all issues. Please fix formatting errors.")
        if ruff_check == 1:
            matrix_log(
                session,
                "[FORMAT][ERROR] Ruff found remaining lint issues after auto-fix. Failing build.",
                color="red",
            )
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write(
                    "[FORMAT][ERROR] Ruff found remaining lint issues after auto-fix. Failing build.\n"
                )
            raise RuntimeError("Ruff found remaining lint issues after auto-fix. Please fix lint errors.")
        matrix_log(session, "[FORMAT] ruff --fix and black complete.", color="green")
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[FORMAT] ruff --fix and black complete.\n")
    except Exception as e:
        matrix_log(session, f"[FORMAT][ERROR] {e}", color="red")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[FORMAT][ERROR] {e}\n")
        # Do not raise, just log the error and continue
    finally:
        matrix_log(
            session,
            f"[FORMAT] Session ended at {now_str()}",
            color="green",
        )
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[FORMAT] Session ended at {now_str()}\n")


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def typecheck(session):
    """Typecheck code with mypy."""

    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[TYPECHECK] Session started at {now_str()}\n")
    matrix_log(
        session,
        f"[TYPECHECK] Session started at {now_str()}",
        color="green",
    )
    try:
        session.run("poetry", "install", "--with", "typecheck", external=True)
        session.run("poetry", "run", "mypy", "src", external=True)
        matrix_log(session, "[TYPECHECK] mypy run complete.", color="green")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write("[TYPECHECK] mypy run complete.\n")
    except Exception as e:
        matrix_log(session, f"[TYPECHECK][ERROR] {e}", color="red")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[TYPECHECK][ERROR] {e}\n")
        raise
    finally:
        matrix_log(
            session,
            f"[TYPECHECK] Session ended at {now_str()}",
            color="green",
        )
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[TYPECHECK] Session ended at {now_str()}\n")


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def precommit(session):

    with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[PRECOMMIT] Session started at {now_str()}\n")
    matrix_log(
        session,
        f"[PRECOMMIT] Session started at {now_str()}",
        color="green",
    )
    try:
        # Run pre-commit, and if files are modified (exit code 1), run again for auto-fix. Only fail if second run fails.
        result = session.run(
            "poetry",
            "run",
            "pre-commit",
            "run",
            "--all-files",
            external=True,
            success_codes=[0, 1],
            silent=True,
        )
        matrix_log(
            session,
            f"[PRECOMMIT] pre-commit first run exit code: {result}",
            color="yellow",
        )
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[PRECOMMIT] pre-commit first run exit code: {result}\n")
        if result == 1:
            matrix_log(
                session,
                "[PRECOMMIT] Files were modified by hooks, running pre-commit again...",
                color="yellow",
            )
            result2 = session.run(
                "poetry",
                "run",
                "pre-commit",
                "run",
                "--all-files",
                external=True,
                success_codes=[0, 1],
                silent=True,
            )
            matrix_log(
                session,
                f"[PRECOMMIT] pre-commit second run exit code: {result2}",
                color="yellow",
            )
            with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[PRECOMMIT] pre-commit second run exit code: {result2}\n")
            if result2 != 0:
                raise RuntimeError("pre-commit failed after auto-fix attempt.")
        matrix_log(session, "[PRECOMMIT] pre-commit run complete.", color="green")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write("[PRECOMMIT] pre-commit run complete.\n")
    except Exception as e:
        matrix_log(session, f"[PRECOMMIT][ERROR] {e}", color="red")
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[PRECOMMIT][ERROR] {e}\n")
        raise
    finally:
        matrix_log(
            session,
            f"[PRECOMMIT] Session ended at {now_str()}",
            color="green",
        )
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[PRECOMMIT] Session ended at {now_str()}\n")
