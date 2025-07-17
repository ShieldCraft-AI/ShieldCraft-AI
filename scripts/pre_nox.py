"""
Preflight script for ShieldCraft AI: ensures Poetry environment is bootstrapped before running any Nox session.
Usage:
    python scripts/pre_nox.py -s <session> [-- <nox args>]
    python scripts/pre_nox.py lint
    python scripts/pre_nox.py -s tests -- --cov=src

- Checks .nox-poetry-installed and .nox-poetry-installed-dev markers.
- If missing or out of date, runs 'nox -s bootstrap'.
- Then runs the requested Nox session(s) with all arguments.
"""

import os
import sys
import subprocess
import argparse
import hashlib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = os.path.join(PROJECT_ROOT, ".nox-poetry-installed")
DEV_MARKER = os.path.join(PROJECT_ROOT, ".nox-poetry-installed-dev")
PYPROJECT = os.path.join(PROJECT_ROOT, "pyproject.toml")
LOCKFILE = os.path.join(PROJECT_ROOT, "poetry.lock")


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def marker_valid(marker, pyproject, lockfile):
    if not os.path.exists(marker):
        return False
    lock_hash = file_hash(lockfile) if os.path.exists(lockfile) else ""
    py_hash = file_hash(pyproject) if os.path.exists(pyproject) else ""
    try:
        with open(marker) as f:
            marker_hash = f.read().strip().split("|")
            if len(marker_hash) != 2:
                return False
            if marker_hash[0] == lock_hash and marker_hash[1] == py_hash:
                return True
    except Exception:
        pass
    return False


def ensure_bootstrap():
    # Preflight import check for nox_sessions
    try:
        import importlib.util

        spec = importlib.util.find_spec("nox_sessions")
        if spec is None:
            print(
                "[pre_nox] ERROR: 'nox_sessions' module not importable. Check PYTHONPATH and project structure.",
                file=sys.stderr,
            )
            sys.exit(1)
    except Exception as e:
        print(
            f"[pre_nox] ERROR: Exception during import check for 'nox_sessions': {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    # Check both markers for full dev installs
    if marker_valid(MARKER, PYPROJECT, LOCKFILE) and marker_valid(
        DEV_MARKER, PYPROJECT, LOCKFILE
    ):
        return
    print(
        "[pre_nox] Poetry environment not bootstrapped or out of date. Running 'poetry run nox -s bootstrap'...",
        flush=True,
    )
    result = subprocess.run(
        ["poetry", "run", "nox", "-s", "bootstrap"], cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        print("[pre_nox] Bootstrap failed. Exiting.", file=sys.stderr)
        sys.exit(result.returncode)
    # Re-check after bootstrap
    if not (
        marker_valid(MARKER, PYPROJECT, LOCKFILE)
        and marker_valid(DEV_MARKER, PYPROJECT, LOCKFILE)
    ):
        print(
            "[pre_nox] Poetry environment still not valid after bootstrap. Exiting.",
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="ShieldCraft AI Nox preflight runner")
    parser.add_argument("-s", "--session", help="Nox session to run", nargs="?")
    parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Arguments to pass to Nox"
    )
    parser.add_argument(
        "session_positional",
        nargs="?",
        help="Session as positional arg (for 'python pre_nox.py lint')",
    )
    args = parser.parse_args()

    # Robustly detect --version as the only argument, regardless of how argparse splits it
    argv = sys.argv[1:]
    if argv == ["--", "--version"] or argv == ["--version"]:
        result = subprocess.run(
            ["poetry", "run", "nox", "--version"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()
        if output:
            print(output)
        sys.exit(result.returncode)

    # Robustly support both -s lint and just 'lint' as positional, and also handle
    # the case where the session is the first arg in args.args (e.g. pre_nox.py format)
    session = args.session or args.session_positional
    nox_args = []
    # If no explicit session, but first arg in args.args is not an option, treat as session
    if not session and args.args:
        first_arg = args.args[0]
        if not first_arg.startswith("-"):
            session = first_arg
            args.args = args.args[1:]
    if session:
        nox_args = ["-s", session]
    if args.args:
        # Remove leading '--' if present
        if args.args and args.args[0] == "--":
            nox_args += args.args[1:]
        else:
            nox_args += args.args

    ensure_bootstrap()
    cmd = ["poetry", "run", "nox"] + nox_args
    print(f"[pre_nox] Running: {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
