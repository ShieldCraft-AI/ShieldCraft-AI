import nox
import os
from datetime import datetime
from nox_sessions.utils import _should_npm_install, nox_session_guard

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox.session
@nox_session_guard
def docs(session):
    """Build Docusaurus documentation."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[DOCS] Session started at {datetime.now()}\n")
    force = session.posargs and "--force" in session.posargs
    need_npm, marker, pkg_hash, lock_hash = _should_npm_install(force=force)
    prev_cwd = os.getcwd()
    try:
        if need_npm:
            os.chdir("docs-site")
            session.run("npm", "install", external=True)
            with open(marker, "w") as f2:
                f2.write(f"{pkg_hash}|{lock_hash}")
            os.chdir(prev_cwd)
        os.chdir("docs-site")
        session.run("npm", "run", "build", external=True)
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[DOCS] npm build complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DOCS][ERROR] {e}\n")
        raise
    finally:
        os.chdir(prev_cwd)
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DOCS] Session ended at {datetime.now()}\n")


@nox.session
@nox_session_guard
def docs_dev(session):
    """Run Docusaurus dev server with live reload."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[DOCS_DEV] Session started at {datetime.now()}\n")
    force = session.posargs and "--force" in session.posargs
    need_npm, marker, pkg_hash, lock_hash = _should_npm_install(force=force)
    prev_cwd = os.getcwd()
    try:
        if need_npm:
            os.chdir("docs-site")
            session.run("npm", "install", external=True)
            with open(marker, "w") as f2:
                f2.write(f"{pkg_hash}|{lock_hash}")
            os.chdir(prev_cwd)
        os.chdir("docs-site")
        session.run("npm", "run", "start", external=True)
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[DOCS_DEV] npm start complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DOCS_DEV][ERROR] {e}\n")
        raise
    finally:
        os.chdir(prev_cwd)
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DOCS_DEV] Session ended at {datetime.now()}\n")


@nox.session
@nox_session_guard
def docs_lint(session):
    """Lint Markdown docs with markdownlint-cli2."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[DOCS_LINT] Session started at {datetime.now()}\n")
    force = session.posargs and "--force" in session.posargs
    need_npm, marker, pkg_hash, lock_hash = _should_npm_install(force=force)
    prev_cwd = os.getcwd()
    try:
        if need_npm:
            os.chdir("docs-site")
            session.run("npm", "install", external=True)
            os.makedirs(os.path.dirname(marker), exist_ok=True)
            with open(marker, "w") as f2:
                f2.write(f"{pkg_hash}|{lock_hash}")
            os.chdir(prev_cwd)
        os.chdir("docs-site")
        session.run("npx", "markdownlint-cli2", "docs/**/*.md", external=True)
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[DOCS_LINT] markdownlint run complete.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DOCS_LINT][ERROR] {e}\n")
        raise
    finally:
        os.chdir(prev_cwd)
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DOCS_LINT] Session ended at {datetime.now()}\n")
