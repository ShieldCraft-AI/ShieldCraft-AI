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
    if marker_file is None:
        marker_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), ".nox-poetry-installed"
        )
    marker_exists = os.path.exists(marker_file)
    lock_exists = os.path.exists(lock_file)
    py_exists = os.path.exists(pyproject_file)
    lock_hash = file_hash(lock_file) if lock_exists else ""
    py_hash = file_hash(pyproject_file) if py_exists else ""
    expected = f"{lock_hash}|{py_hash}"
    actual = None
    try:
        with open(marker_file, "r", encoding="utf-8") as f:
            actual = f.read()
        actual = actual.strip()
    except Exception:
        return False
    return actual == expected

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
