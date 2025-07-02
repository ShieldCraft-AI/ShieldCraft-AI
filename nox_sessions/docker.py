import nox
import os
from datetime import datetime
from nox_sessions.utils import nox_session_guard

DEBUG_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "commit_nox_debug.log"
)


@nox.session
@nox_session_guard
def docker_build(session):
    """Build all Docker images (main, api, ingestion) using the repo Dockerfiles."""
    with open(DEBUG_LOG_FILE, "a") as f:
        f.write(f"[DOCKER_BUILD] Session started at {datetime.now()}\n")
    try:
        dockerfiles = [
            ("Dockerfile", "shieldcraft-main:dev"),
            ("Dockerfile.api", "shieldcraft-api:dev"),
            ("Dockerfile.ingestion", "shieldcraft-ingestion:dev"),
        ]
        for dockerfile, tag in dockerfiles:
            session.log(f"🟦 Building Docker image {tag} from {dockerfile}")
            session.run(
                "docker",
                "build",
                "-f",
                dockerfile,
                "-t",
                tag,
                ".",
                external=True,
            )
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write("[DOCKER_BUILD] All docker images built.\n")
    except Exception as e:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DOCKER_BUILD][ERROR] {e}\n")
        raise
    finally:
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[DOCKER_BUILD] Session ended at {datetime.now()}\n")


@nox.session
@nox_session_guard
def docker_scan(session):
    """Scan all Docker images for vulnerabilities using Trivy and Grype."""
    # Trivy
    session.run("docker", "pull", "aquasec/trivy:latest", external=True)
    for image in [
        "shieldcraft-api:dev",
        "shieldcraft-ingestion:dev",
        "shieldcraft-main:dev",
    ]:
        session.run(
            "docker",
            "run",
            "--rm",
            "-v",
            "/var/run/docker.sock:/var/run/docker.sock",
            "aquasec/trivy:latest",
            "image",
            image,
            external=True,
        )
    # Grype
    session.run("docker", "pull", "anchore/grype:latest", external=True)
    for image in [
        "shieldcraft-api:dev",
        "shieldcraft-ingestion:dev",
        "shieldcraft-main:dev",
    ]:
        session.run(
            "docker",
            "run",
            "--rm",
            "-v",
            "/var/run/docker.sock:/var/run/docker.sock",
            "anchore/grype:latest",
            image,
            external=True,
        )
