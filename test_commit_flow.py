from nox_sessions.commit import commit_flow


class DummySession:
    def __init__(self, posargs):
        self.posargs = posargs

    def log(self, msg):
        print(msg)

    def notify(self, session_name):
        print(f"Would run session: {session_name}")


commit_flow(DummySession(["--fast"]))
