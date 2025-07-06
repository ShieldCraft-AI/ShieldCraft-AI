import nox
import os
from nox_sessions.utils import nox_session_guard


@nox.session
@nox_session_guard
def docker_build(session):
    """Build all Docker images (main, api, ingestion) using the repo Dockerfiles."""
    # Debug log removed
    try:
        # Ensure Docker is in PATH (robust for Windows, GitBash, Poetry venvs)
        import shutil

        docker_dirs = [
            r"C:\\Program Files\\Docker\\Docker\\resources\\bin",
            r"C:\\Program Files\\Docker\\resources\\bin",
            r"C:\\Program Files\\Docker",
        ]
        for d in docker_dirs:
            if os.path.exists(d) and d not in os.environ["PATH"]:
                os.environ["PATH"] += os.pathsep + d
        docker_path = shutil.which("docker")
        # Debug logs removed
        if not docker_path:
            session.error(
                "\n\033[91mERROR: Docker is not installed or not found in PATH. Please install Docker and ensure it is available in your PATH.\033[0m\n"
            )
        dockerfiles = [
            ("Dockerfile", "shieldcraft-main:dev"),
            ("Dockerfile.api", "shieldcraft-api:dev"),
            ("Dockerfile.ingestion", "shieldcraft-ingestion:dev"),
        ]
        for dockerfile, tag in dockerfiles:
            session.log(f"🟦 Building Docker image {tag} from {dockerfile}")
            build_args = ["build", "-f", dockerfile, "-t", tag, "."]
            env = dict(os.environ)
            env["DOCKER_BUILDKIT"] = "1"
            if session.posargs and "--ci" in session.posargs:
                build_args.extend(
                    [
                        "--build-arg",
                        "BUILDKIT_INLINE_CACHE=1",
                        "--cache-from",
                        f"type=registry,ref={tag}",
                    ]
                )
            try:
                session.run("docker", *build_args, external=True, env=env)
            except Exception as e:
                session.error(
                    f"\n\033[91mERROR: Failed to build Docker image {tag} from {dockerfile}: {e}\033[0m\n"
                )
        # Debug log removed
    except Exception:
        raise


@nox.session
@nox_session_guard
def docker_scan(session):
    """Scan all Docker images for vulnerabilities using Trivy and Grype.
    Usage: nox -s docker_scan -- [--tag <tag>]
    """
    import shutil
    import subprocess

    docker_path = shutil.which("docker")
    if not docker_path:
        session.error(
            "\n\033[91mERROR: Docker is not installed or not found in PATH. Please install Docker and ensure it is available in your PATH.\033[0m\n"
        )

    # Parse --tag argument (default: dev)
    tag = "dev"
    if session.posargs:
        for i, arg in enumerate(session.posargs):
            if arg == "--tag" and i + 1 < len(session.posargs):
                tag = session.posargs[i + 1]
    images = [
        f"shieldcraft-api:{tag}",
        f"shieldcraft-ingestion:{tag}",
        f"shieldcraft-main:{tag}",
    ]

    # Helper: check if image exists locally
    def image_exists(image_name):
        try:
            subprocess.run(
                [docker_path, "image", "inspect", image_name],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    session.run("docker", "pull", "aquasec/trivy:latest", external=True)
    for image in images:
        if not image_exists(image):
            session.log(f"Skipping scan: image {image} does not exist locally.")
            continue
        try:
            session.run(
                "docker",
                "run",
                "--rm",
                "aquasec/trivy:latest",
                "image",
                "--severity",
                "CRITICAL,HIGH",
                image,
                external=True,
            )
        except Exception as e:
            session.error(
                f"\n\033[91mERROR: Trivy scan failed for image {image}: {e}\033[0m\n"
            )
    session.run("docker", "pull", "anchore/grype:latest", external=True)
    for image in images:
        if not image_exists(image):
            session.log(f"Skipping scan: image {image} does not exist locally.")
            continue
        try:
            session.run(
                "docker",
                "run",
                "--rm",
                "anchore/grype:latest",
                image,
                external=True,
            )
        except Exception as e:
            session.error(
                f"\n\033[91mERROR: Grype scan failed for image {image}: {e}\033[0m\n"
            )
    import sys

    session.log(f"sys.executable: {sys.executable}")
    session.log(f"os.environ['PATH']: {os.environ.get('PATH')}")
