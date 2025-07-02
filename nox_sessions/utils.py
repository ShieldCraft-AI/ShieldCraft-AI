import os
import hashlib
import functools
import traceback
import sys


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


def _should_poetry_install(dev=False, force=False, skip=False):

    marker = ".nox-poetry-installed-dev" if dev else ".nox-poetry-installed"
    lock_hash = file_hash("poetry.lock") if os.path.exists("poetry.lock") else ""
    py_hash = file_hash("pyproject.toml") if os.path.exists("pyproject.toml") else ""
    if skip:
        return False, marker, lock_hash, py_hash
    if not os.path.exists(marker):
        print(
            "\033[91mERROR: Poetry environment not bootstrapped. Run 'nox -s bootstrap' first.\033[0m",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        with open(marker) as f:
            marker_hash = f.read().strip().split("|")
            if (
                len(marker_hash) == 2
                and marker_hash[0] == lock_hash
                and marker_hash[1] == py_hash
            ):
                return False, marker, lock_hash, py_hash
    except Exception:
        pass
    print(
        "\033[91mERROR: Poetry environment out of date. Run 'nox -s bootstrap' to update.\033[0m",
        file=sys.stderr,
    )
    sys.exit(1)


def _should_npm_install(force=False):
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
