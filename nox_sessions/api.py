import nox


@nox.session(python=False)
def api(session):
    """Run the API tests (assumes virtualenv handled by Poetry in CI).
    This session runs pytest for the API tests only.
    """
    session.run("pytest", "tests/test_api_demo.py", *session.posargs)
