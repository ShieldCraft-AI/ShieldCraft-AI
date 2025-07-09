# Utility for consistent timestamp formatting (YYYY-MM-DD HH:MM:SS)
from datetime import datetime


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


import os
import hashlib
import functools
import traceback
import sys
from nox_sessions.utils_encoding import force_utf8

force_utf8()


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


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
