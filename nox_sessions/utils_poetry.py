import os
import subprocess
import sys
from pathlib import Path


def ensure_poetry_installed():
    """
    Ensures Poetry is installed and available in the current environment.
    If not, attempts to install it using the official install script.
    Raises RuntimeError if installation fails.
    """
    try:
        subprocess.run(
            ["poetry", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    # Try to install poetry using the official install script
    install_cmd = [
        sys.executable,
        "-c",
        (
            "import urllib.request,os,sys; "
            "url='https://install.python-poetry.org'; "
            "code=urllib.request.urlopen(url).read(); "
            "exec(code)"
        ),
    ]
    try:
        subprocess.run(install_cmd, check=True)
    except Exception as e:
        raise RuntimeError(f"Failed to install Poetry: {e}") from e
    poetry_bin = Path.home() / ".local" / "bin" / "poetry"
    if poetry_bin.exists():
        os.environ["PATH"] = f"{poetry_bin.parent}:{os.environ['PATH']}"
    try:
        subprocess.run(
            ["poetry", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        raise RuntimeError(
            "Poetry installation failed or not found in PATH after install."
        )
