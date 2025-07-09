import nox
from nox_sessions.utils import nox_session_guard
from nox_sessions.utils_encoding import force_utf8

force_utf8()


@nox.session()
@nox_session_guard
def yaml_format(session):
    """Auto-format only changed YAML files with prettier."""
    from nox_sessions.utils_color import matrix_log
    import subprocess

    matrix_log(session, "[YAML_FORMAT] Checking for changed YAML files", color="green")
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f for f in result.stdout.splitlines() if f.endswith((".yml", ".yaml"))]
        if not files:
            matrix_log(
                session, "[YAML_FORMAT] No changed YAML files to format.", color="green"
            )
            return
        matrix_log(
            session,
            f"[YAML_FORMAT] Formatting {len(files)} YAML file(s)",
            color="green",
        )
        session.run("npx", "prettier", "--write", *files, external=True)
        matrix_log(
            session, "[YAML_FORMAT] Prettier formatting complete.", color="green"
        )
    except Exception as e:
        matrix_log(session, f"[YAML_FORMAT][ERROR] {e}", color="red")
        raise


@nox.session()
@nox_session_guard
def yaml_lint(session):
    """Lint only changed YAML files with yamllint."""
    from nox_sessions.utils_color import matrix_log
    import subprocess

    matrix_log(session, "[YAML_LINT] Checking for changed YAML files", color="green")
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f for f in result.stdout.splitlines() if f.endswith((".yml", ".yaml"))]
        if not files:
            matrix_log(
                session, "[YAML_LINT] No changed YAML files to lint.", color="green"
            )
            return
        matrix_log(
            session, f"[YAML_LINT] Linting {len(files)} YAML file(s)", color="green"
        )
        session.run("yamllint", *files, external=True)
        matrix_log(session, "[YAML_LINT] yamllint complete.", color="green")
    except Exception as e:
        matrix_log(session, f"[YAML_LINT][ERROR] {e}", color="red")
        raise
