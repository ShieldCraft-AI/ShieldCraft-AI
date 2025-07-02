import os
import shutil
import glob
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def rm(path):
    if os.path.isdir(path):
        print(f"Removing directory: {path}")
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.isfile(path):
        print(f"Removing file: {path}")
        os.remove(path)


def glob_rm(pattern):
    for path in glob.glob(pattern, recursive=True):
        rm(path)


def main():
    os.chdir(PROJECT_ROOT)
    print("=== Shieldcraft-AI: Full Environment Reset ===")
    # Remove all artifacts
    patterns = [
        ".venv",
        ".nox",
        ".tox",
        "dist",
        "build",
        ".pytest_cache",
        ".mypy_cache",
        ".coverage",
        ".eggs",
        "*.egg-info",
        "__pycache__",
        ".DS_Store",
        "*.pyo",
        "*.pyc",
        "*.log",
        "*.tmp",
        "*.bak",
        "*.swp",
        "*.orig",
        "*.old",
        ".cache",
        ".nox_version_tmp",
        ".envrc",
        ".editorconfig",
        ".vscode",
        ".idea",
        ".ipynb_checkpoints",
        "node_modules",
        "docs-site/node_modules",
        "docs-site/.nox-npm-installed",
        "docs-site/.cache",
        "docs-site/.next",
        "docs-site/.docusaurus",
    ]
    for pat in patterns:
        glob_rm(f"{PROJECT_ROOT}/**/{pat}")

    # Remove marker and lock files
    files = [
        ".nox-poetry-installed",
        ".nox-poetry-installed-dev",
        "poetry.lock",
        "Pipfile.lock",
        "yarn.lock",
        "package-lock.json",
        ".coverage",
    ]
    for f in files:
        glob_rm(f"{PROJECT_ROOT}/**/{f}")

    # Optionally prompt for .env
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_path):
        resp = input("Remove .env file? [y/N]: ").strip().lower()
        if resp == "y":
            rm(env_path)

    print("Clean complete.\nChecking Poetry version...")
    try:
        poetry_ver = subprocess.check_output(["poetry", "--version"], text=True).strip()
        print(f"Poetry version: {poetry_ver}")
    except Exception:
        print("[ERROR] Poetry is not installed or not in PATH.")
        sys.exit(1)

    print("Reinstalling Poetry dependencies...")
    try:
        subprocess.run(["poetry", "install"], check=True)
        print("Poetry install complete.")
    except subprocess.CalledProcessError:
        print(
            "[ERROR] Poetry install failed. Please check your pyproject.toml and poetry installation."
        )
        sys.exit(1)

    print("Bootstrapping Nox environment...")
    try:
        subprocess.run(["poetry", "run", "nox", "-s", "bootstrap"], check=True)
        nox_ver = subprocess.check_output(
            ["poetry", "run", "nox", "--version"], text=True
        ).strip()
        print(f"Nox bootstrap session complete. Nox version: {nox_ver}")
    except subprocess.CalledProcessError:
        print(
            "[ERROR] Nox bootstrap failed. Please check your Nox sessions and pyproject.toml."
        )
        sys.exit(1)

    print("\nEnvironment reset and bootstrapped successfully!")
    print("You can now use the commit script or run other Nox sessions as normal.")
    print("For more info, see CONTRIBUTING.md or README.md.")


if __name__ == "__main__":
    main()
