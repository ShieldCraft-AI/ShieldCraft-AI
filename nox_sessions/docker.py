import nox
from nox_sessions.utils_color import color_log
from nox_sessions.utils_encoding import force_utf8

force_utf8()


@nox.session()
def docker_build(session):
    """Build all Docker images (main, api, ingestion) using the repo Dockerfiles."""
    import shutil

    if not shutil.which("docker"):
        color_log(
            session,
            "Docker not found in PATH. Skipping docker_build session.",
            "yellow",
        )
        session.skip("Docker is not installed or not in PATH.")
    dockerfiles = [
        ("Dockerfile", "shieldcraft-main:dev"),
        ("Dockerfile.api", "shieldcraft-api:dev"),
        ("Dockerfile.ingestion", "shieldcraft-ingestion:dev"),
    ]
    for dockerfile, tag in dockerfiles:
        color_log(session, f"🟦 Building Docker image {tag} from {dockerfile}", "cyan")
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


@nox.session()
def docker_scan(session):
    """Scan all Docker images for vulnerabilities using Trivy and Grype."""
    import shutil

    if not shutil.which("docker"):
        color_log(
            session, "Docker not found in PATH. Skipping docker_scan session.", "yellow"
        )
        session.skip("Docker is not installed or not in PATH.")
    color_log(session, "Pulling Trivy scanner...", "magenta")
    session.run("docker", "pull", "aquasec/trivy:latest", external=True)
    for image in [
        "shieldcraft-api:dev",
        "shieldcraft-ingestion:dev",
        "shieldcraft-main:dev",
    ]:
        color_log(session, f"Scanning {image} with Trivy...", "cyan")
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
    color_log(session, "Pulling Grype scanner...", "magenta")
    session.run("docker", "pull", "anchore/grype:latest", external=True)
    for image in [
        "shieldcraft-api:dev",
        "shieldcraft-ingestion:dev",
        "shieldcraft-main:dev",
    ]:
        color_log(session, f"Scanning {image} with Grype...", "cyan")
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
