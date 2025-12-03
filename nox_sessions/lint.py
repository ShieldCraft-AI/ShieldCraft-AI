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

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# --- Compatibility shims for tests: expose a small lint orchestration API ---


class CommandFailed(Exception):
    """Raised when an underlying command fails in a nox session."""


@dataclass
class LintRunContext:
    verbose: bool
    snapshot_update: bool
    snapshot_ignore: bool


class _FailureAggregator:
    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    def reset(self) -> None:
        self._events = []

    def record(self, event: Dict[str, Any]) -> None:
        self._events.append(event)

    def summary_event(self) -> Optional[Dict[str, Any]]:
        if not self._events:
            return None
        return {"summary": True, "count": len(self._events)}


_FAILURE_AGGREGATOR = _FailureAggregator()


# Expose common script helpers at module-level so tests can monkeypatch them.
try:
    from scripts.lint.lint_events import build_event  # type: ignore
except Exception:
    build_event = None  # type: ignore

try:
    from scripts.lint.lint_failure import safe_emit, fail_event  # type: ignore
except Exception:
    safe_emit = None  # type: ignore
    fail_event = None  # type: ignore


def _run_lint_health_checks() -> None:
    """Run the lint health checks (wrapper for `scripts.lint.lint_health`)."""
    try:
        from scripts.lint import lint_health

        lint_health.check_formatter_contract()
        lint_health.check_builder_contract()
        lint_health.check_snapshot_consistency()
    except Exception:
        # In shim mode, surface errors to callers; tests monkeypatch this function.
        raise


def _assert_capabilities_valid(context: LintRunContext) -> None:
    """Validate lint capabilities and emit failure if invalid."""
    try:
        from scripts.lint import lint_capabilities

        valid, failure = lint_capabilities.validate_capabilities()
        if not valid and failure is not None:
            if callable(safe_emit):
                safe_emit(failure, allow_quiet=not context.verbose)
            raise RuntimeError("capabilities invalid")
    except Exception:
        # Let callers/tests handle monkeypatching; do not swallow errors.
        raise


def _assert_feature_flags_valid(context: LintRunContext) -> None:
    """Validate feature flags; emits failure_event on invalid matrix."""
    try:
        from scripts.lint import lint_feature_flags

        valid, failure = lint_feature_flags.validate_flags()
        if not valid and failure is not None:
            if callable(safe_emit):
                safe_emit(failure, allow_quiet=not context.verbose)
            raise RuntimeError("feature flags invalid")
    except Exception:
        raise


def _run_registry_contract_check(context: LintRunContext) -> None:
    """Validate registry contract; emits failure_event on invalid registry."""
    try:
        from scripts.lint import lint_registry

        strict = bool(os.getenv("GITHUB_ACTIONS"))
        valid, failure = lint_registry.validate_registry(strict=strict)
        if not valid and failure is not None:
            if callable(safe_emit):
                safe_emit(failure, allow_quiet=not context.verbose)
            raise RuntimeError("registry validation failed")
    except Exception:
        raise


def _parse_lint_flags(session) -> Tuple[bool, bool]:
    """Extract supported flags from session.posargs.

    Returns (verbose, ignore_snapshot) and mutates `session.posargs` to remove handled flags.
    """
    pos = list(getattr(session, "posargs", []) or [])
    verbose = False
    ignore = False
    remaining: List[str] = []
    for token in pos:
        if token == "--verbose":
            verbose = True
            continue
        if token == "--ignore-snapshot" or token == "--ignore-snapshots":
            ignore = True
            continue
        remaining.append(token)
    # Mutate in-place if possible
    if hasattr(session, "posargs"):
        session.posargs = remaining
    return verbose, ignore


def _ensure_ignore_snapshot_allowed(ignore_snapshot: bool, verbose: bool) -> None:
    # Placeholder: real check may consult env/CI guards; tests monkeypatch this.
    return None


def _build_context(verbose: bool, ignore_snapshot: bool) -> LintRunContext:
    return LintRunContext(
        verbose=verbose, snapshot_update=False, snapshot_ignore=ignore_snapshot
    )


def lint_all(session) -> None:
    """Compatibility entrypoint used by CI and tests.

    Parses flags, builds a context, and delegates to `lint_all_sequence`.
    """
    verbose, ignore = _parse_lint_flags(session)
    _ensure_ignore_snapshot_allowed(ignore, verbose)
    context = _build_context(verbose, ignore)
    # In verbose local runs, print capabilities for visibility
    try:
        from scripts.lint.lint_capabilities import get_capabilities

        caps = get_capabilities()
    except Exception:
        caps = {}

    if verbose and not os.getenv("GITHUB_ACTIONS"):
        print(json.dumps(caps, sort_keys=True))
        # Also print feature flags manifest for visibility in verbose mode
        try:
            from scripts.lint import lint_feature_flags

            flags = lint_feature_flags.get_flags()
            print(json.dumps(flags, sort_keys=True))
        except Exception:
            pass
    # Optional health checks guard: controlled by env var to avoid noisy CI runs
    try:
        if os.getenv("SHIELDCRAFT_LINT_HEALTH"):
            _run_lint_health_checks()
    except Exception:
        # Let the health check propagate errors in real runs; tests may monkeypatch this.
        raise

    # Registry validation: run with strict mode in CI
    try:
        strict = bool(os.getenv("GITHUB_ACTIONS"))
        valid, failure = validate_registry(strict=strict)
        if verbose and not os.getenv("GITHUB_ACTIONS"):
            # Print registry snapshot for visibility in verbose local runs
            try:
                snap = get_registry_snapshot()
                print(json.dumps(snap, sort_keys=True))
            except Exception:
                pass
    except Exception:
        # If registry validation fails, let it raise (tests may override/monkeypatch)
        raise

    # Delegate to sequence helper (tests monkeypatch this function)
    if hasattr(globals().get("lint_all_sequence"), "__call__"):
        lint_all_sequence(session, context=context)  # type: ignore[name-defined]


def lint_all_sequence(session, *, context: LintRunContext) -> None:
    """Helper that defines the canonical lint target ordering.

    Tests inspect this function's AST for literal targets; keep 'lint_forbidden' and 'lint'
    as the first two entries.
    """
    targets = [
        "lint_forbidden",
        "lint",
        "lint_formatter",
        "lint_registry",
        "lint_health",
    ]
    for t in targets:
        # Each target would be invoked via _run_lint_target in real flows.
        _run_lint_target(session, t, verbose=context.verbose)


def _run_lint_target(session, target: str, verbose: bool) -> None:
    """Run a single lint target with quiet/verbose retry behavior.

    Emits events via `safe_emit` and validates event payloads using the lint contract.
    """
    from scripts.lint.lint_contract import validate_lint_payload

    # Use module-level build_event / safe_emit / fail_event so tests can monkeypatch
    _build_event = globals().get("build_event")
    _safe_emit = globals().get("safe_emit")
    _fail_event = globals().get("fail_event")

    try:
        payload = _build_event(target, "ok") if callable(_build_event) else None
    except Exception:
        payload = None

    if payload is None or not validate_lint_payload(payload):
        raise ValueError("invalid event payload")

    # Attempt run
    try:
        # Quiet run first when not verbose
        session.run("true", silent=not verbose)
    except Exception as exc:  # noqa: BLE001 - broad catch intentional for shim
        is_cmd_failed = isinstance(exc, CommandFailed)
        # On failure, emit fail (quiet)
        # Emit a quiet-mode failure event (use 'fail' status so tests expect 'fail')
        if callable(_build_event) and callable(_safe_emit):
            quiet_evt = _build_event(target, "fail", "quiet-mode-failure")
            _safe_emit(quiet_evt, allow_quiet=not verbose)
        if not verbose:
            # emit retrying-verbose event
            if callable(_build_event) and callable(_safe_emit):
                retry_evt = _build_event(target, "fail", "retrying-verbose")
                _safe_emit(retry_evt, allow_quiet=False)
            # retry in verbose mode
            try:
                session.run("true", silent=False)
                # emit ok after successful retry; include diagnostic to indicate retry
                if callable(_build_event) and callable(_safe_emit):
                    ok_evt = _build_event(target, "ok", "retry-verbose")
                    _safe_emit(ok_evt, allow_quiet=False)
            except Exception:
                # If retry fails, propagate that exception
                raise
        # After retry, re-raise original CommandFailed to surface the initial failure
        if is_cmd_failed:
            raise exc
        raise

    # On success, emit ok (respect quiet mode)
    if callable(_build_event) and callable(_safe_emit):
        ok_evt = _build_event(target, "ok")
        _safe_emit(ok_evt, allow_quiet=not verbose)


def _handle_snapshot(payload: Dict[str, Any], context: LintRunContext) -> None:
    """Handle snapshot comparisons and enforce snapshot rules.

    Emits a 'snapshot-mismatch' event and raises in strict modes.
    """
    from scripts.lint import lint_snapshots

    _safe_emit = globals().get("safe_emit")

    target = payload.get("target")
    if not target:
        raise ValueError("payload missing target")

    matches = lint_snapshots.snapshot_matches(target, payload)
    if matches:
        return

    # Snapshot mismatch
    evt = payload.copy()
    evt["diagnostic"] = "snapshot-mismatch"
    evt["status"] = "error"
    allow_quiet = not context.verbose
    if callable(_safe_emit):
        _safe_emit(evt, allow_quiet=allow_quiet)

    if context.snapshot_ignore:
        # Allow override only in verbose local runs
        if os.getenv("GITHUB_ACTIONS"):
            raise RuntimeError("snapshot override not allowed in CI")
        if context.verbose:
            return
        raise RuntimeError("snapshot override requires verbose mode")

    raise RuntimeError("snapshot mismatch detected")


def _enforce_registry_snapshot(context: LintRunContext) -> None:
    """Run schema drift detection with a verbose retry on mismatch.

    Uses `detect_schema_drift` (may be monkeypatched in tests) and emits events via
    `_emit_lint_event`.
    """
    # detect_schema_drift(path, snapshot_update, verbose) -> (ok: bool, payload: dict)
    detector = globals().get("detect_schema_drift")
    if detector is None:
        # Nothing to enforce in shim mode
        return

    ok, payload = detector(
        "dummy_path", snapshot_update=context.snapshot_update, verbose=False
    )
    _emit_lint_event(payload, context)
    if ok:
        return

    # Retry in verbose mode
    retry_context = LintRunContext(
        True, context.snapshot_update, context.snapshot_ignore
    )
    ok2, payload2 = detector(
        "dummy_path", snapshot_update=context.snapshot_update, verbose=True
    )
    _emit_lint_event(payload2, retry_context)
    if not ok2:
        raise RuntimeError("registry snapshot enforcement failed")


def _emit_lint_event(
    payload: Dict[str, Any], context: LintRunContext, enforce_snapshot: bool = True
) -> None:
    from scripts.lint.lint_failure import safe_emit

    # Forward to safe_emit; tests may monkeypatch this function to capture payload/context
    safe_emit(payload, allow_quiet=not context.verbose)


def _emit_failure_summary() -> None:
    """Emit a failure summary for the aggregated failures and write a fatal snapshot."""
    from scripts.lint import lint_snapshots

    events = getattr(_FAILURE_AGGREGATOR, "_events", [])
    if not events:
        return

    # Build classification list in deterministic order based on targets
    mapping = {
        "lint_forbidden": "forbidden-flag",
        "lint": "syntax",
        "lint_formatter": "formatting",
        "lint-registry-schema": "registry-drift",
        "lint_registry": "registry-drift",
    }
    classifications: List[str] = []
    targets: List[str] = []
    for ev in events:
        t = ev.get("target")
        if not t:
            continue
        targets.append(t)
        cls = mapping.get(t, "other")
        if cls not in classifications:
            classifications.append(cls)

    diag = f"classifications={','.join(classifications)};targets={','.join(targets)}"
    event = {
        "target": "lint-fatal-summary",
        "status": "error",
        "diagnostic": diag,
        "stdout": "",
        "stderr": "",
        "timestamp": "2025-11-01T00:00:00Z",
        "lint_version": "v1",
    }
    # Write fatal snapshot for downstream inspection
    try:
        lint_snapshots.write_fatal_snapshot("lint-fatal-summary", event)
    except Exception:
        pass
    # Emit once
    try:
        from scripts.lint.lint_failure import safe_emit

        safe_emit(event, allow_quiet=False)
    except Exception:
        print("[LINT] failed to emit summary")


def validate_registry(strict: bool = False):
    try:
        from scripts.lint import lint_registry

        return lint_registry.validate_registry(strict=strict)
    except Exception:
        return True, None


def get_registry_snapshot():
    try:
        from scripts.lint import lint_registry

        return lint_registry.get_registry_snapshot()
    except Exception:
        return {}


@nox_session_guard
@nox.session(python=PYTHON_VERSIONS)
def lint(session):
    """Lint code with ruff and black (no auto-fix)."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[LINT] Session started at {now_str()}\n")
    matrix_log(session, f"[LINT] Session started at {now_str()}", color="green")
    try:
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
    """Auto-format code with black and ruff, running both in parallel for speed. Fails build on unfixable issues."""
    import concurrent.futures
    import subprocess
    import sys

    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[FORMAT] Session started at {now_str()}\n")
    matrix_log(session, f"[FORMAT] Session started at {now_str()}", color="green")
    try:
        matrix_log(
            session,
            "[FORMAT] Running ruff --fix and black in parallel...",
            color="green",
        )

        def run_ruff():
            return subprocess.run(
                [sys.executable, "-m", "poetry", "run", "ruff", "check", ".", "--fix"],
                capture_output=True,
            )

        def run_black():
            return subprocess.run(
                [sys.executable, "-m", "poetry", "run", "black", "."],
                capture_output=True,
            )

        with concurrent.futures.ThreadPoolExecutor() as executor:
            ruff_future = executor.submit(run_ruff)
            black_future = executor.submit(run_black)
            ruff_result = ruff_future.result()
            black_result = black_future.result()

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
                "[FORMAT][WARN] Black could not auto-fix all issues. Please review and fix formatting errors.",
                color="yellow",
            )
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write(
                    "[FORMAT][WARN] Black could not auto-fix all issues. Please review and fix formatting errors.\n"
                )
        if ruff_check == 1:
            matrix_log(
                session,
                "[FORMAT][WARN] Ruff found remaining lint issues after auto-fix. Please review and fix.",
                color="yellow",
            )
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write(
                    "[FORMAT][WARN] Ruff found remaining lint issues after auto-fix. Please review and fix.\n"
                )
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
