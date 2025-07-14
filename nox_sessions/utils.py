"""
Utility functions for Nox sessions, including logging, file hashing, and session decorators.
"""

import os
import hashlib
import functools
import traceback
import sys
from datetime import datetime
from nox_sessions.utils_encoding import force_utf8

force_utf8()

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_debug_log(message, log_file=None):
    """
    Centralized log writer for commit_nox_debug.log and other debug logs.
    Ensures UTF-8 encoding and timestamping.
    """
    if log_file is None:
        log_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
        )
    timestamp = now_str()
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def validate_poetry_marker(
    marker_file=None, lock_file="poetry.lock", pyproject_file="pyproject.toml"
):
    """
    Validate the .nox-poetry-installed marker file against current poetry.lock and pyproject.toml hashes.
    Adds debug logging for troubleshooting environment drift.
    Returns True if valid, False otherwise.
    """
    debug_log_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
    )
    if marker_file is None:
        marker_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), ".nox-poetry-installed"
        )
    cwd = os.getcwd()
    write_debug_log(f"[MARKER VALIDATION] cwd: {cwd}", debug_log_file)
    print(f"[MARKER VALIDATION] cwd: {cwd}")
    # Check existence and permissions
    marker_exists = os.path.exists(marker_file)
    lock_exists = os.path.exists(lock_file)
    py_exists = os.path.exists(pyproject_file)
    write_debug_log(f"[MARKER VALIDATION] marker_file: {marker_file} exists={marker_exists}", debug_log_file)
    write_debug_log(f"[MARKER VALIDATION] lock_file: {lock_file} exists={lock_exists}", debug_log_file)
    write_debug_log(f"[MARKER VALIDATION] pyproject_file: {pyproject_file} exists={py_exists}", debug_log_file)
    # Debug: Print/log file contents
    def safe_read(path):
        try:
            with open(path, "rb") as f:
                content = f.read()
                return content.hex()[:128] + "..." if len(content) > 128 else content.decode(errors="replace")
        except Exception as e:
            return f"[ERROR reading {path}: {e}]"
    if marker_exists:
        marker_content = safe_read(marker_file)
        write_debug_log(f"[MARKER VALIDATION] marker_file content: {marker_content}", debug_log_file)
        print(f"[MARKER VALIDATION] marker_file content: {marker_content}")
    if lock_exists:
        lock_content = safe_read(lock_file)
        write_debug_log(f"[MARKER VALIDATION] lock_file content: {lock_content}", debug_log_file)
        print(f"[MARKER VALIDATION] lock_file content: {lock_content}")
    if py_exists:
        py_content = safe_read(pyproject_file)
        write_debug_log(f"[MARKER VALIDATION] pyproject_file content: {py_content}", debug_log_file)
        print(f"[MARKER VALIDATION] pyproject_file content: {py_content}")
    lock_hash = file_hash(lock_file) if lock_exists else ""
    py_hash = file_hash(pyproject_file) if py_exists else ""
    expected = f"{lock_hash}|{py_hash}"
    actual = None
    try:
        with open(marker_file, "r", encoding="utf-8") as f:
            actual = f.read()
        # Strip whitespace and newlines for robust comparison
        actual = actual.strip()
    except Exception as e:
        msg = f"[MARKER VALIDATION] Could not read marker file: {e}"
        write_debug_log(msg, debug_log_file)
        print(msg)
        return False
    write_debug_log(f"[MARKER VALIDATION] lock_hash: {lock_hash}", debug_log_file)
    write_debug_log(f"[MARKER VALIDATION] lock_hash (repr): {repr(lock_hash)}", debug_log_file)
    write_debug_log(f"[MARKER VALIDATION] py_hash: {py_hash}", debug_log_file)
    write_debug_log(f"[MARKER VALIDATION] py_hash (repr): {repr(py_hash)}", debug_log_file)
    write_debug_log(f"[MARKER VALIDATION] expected: {expected}", debug_log_file)
    write_debug_log(f"[MARKER VALIDATION] expected (repr): {repr(expected)}", debug_log_file)
    write_debug_log(f"[MARKER VALIDATION] actual: {actual}", debug_log_file)
    write_debug_log(f"[MARKER VALIDATION] actual (repr): {repr(actual)}", debug_log_file)
    print(f"[MARKER VALIDATION] expected: {expected}")
    print(f"[MARKER VALIDATION] actual: {actual}")
    if actual == expected:
        write_debug_log("[MARKER VALIDATION] Marker file is valid.", debug_log_file)
        print("[MARKER VALIDATION] Marker file is valid.")
        return True
    else:
        write_debug_log("[MARKER VALIDATION] Marker file is INVALID.", debug_log_file)
        print("[MARKER VALIDATION] Marker file is INVALID.")
        return False

def nox_session_guard(func):
    """Decorator to catch and log all exceptions in Nox sessions, printing tracebacks and exiting with error."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            print(
                "\033[91m[NOX SESSION ERROR]\033[0m Exception in session '{}':".format(
                    func.__name__
                ),
                file=sys.stderr,
            )
            traceback.print_exc()
            # Optionally, re-raise to let Nox handle exit code
            raise
    return wrapper

def _should_npm_install(force=False):
    # Deprecated: All npm install logic should be handled in a centralized preflight script, not in session files.
    # This function is retained for backward compatibility but should not be used in new code.
    marker = os.path.join("docs-site", ".nox-npm-installed")
    pkg_hash = (
        file_hash(os.path.join("docs-site", "package.json"))
        if os.path.exists(os.path.join("docs-site", "package.json"))
        else ""
    )
    lock_hash = (
        file_hash(os.path.join("docs-site", "package-lock.json"))
        if os.path.exists(os.path.join("docs-site", "package-lock.json"))
        else ""
    )
    need_npm = True
    if os.path.exists(marker) and not force:
        try:
            with open(marker) as f:
                marker_hash = f.read().strip().split("|")
                if (
                    len(marker_hash) == 2
                    and marker_hash[0] == pkg_hash
                    and marker_hash[1] == lock_hash
                    and os.path.exists(os.path.join("docs-site", "node_modules"))
                ):
                    need_npm = False
        except Exception:
            need_npm = True
    return need_npm, marker, pkg_hash, lock_hash
