import nox
from nox_sessions.utils import nox_session_guard


@nox.session
@nox_session_guard
def yaml_format(session):
    """Auto-format YAML files with prettier."""
    session.run("npx", "prettier", "--write", "**/*.yml", external=True)
    session.run("npx", "prettier", "--write", "**/*.yaml", external=True)


@nox.session
@nox_session_guard
def yaml_lint(session):
    """Lint YAML files with yamllint."""
    session.run("yamllint", ".", external=True)
