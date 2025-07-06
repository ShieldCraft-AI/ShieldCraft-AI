import shutil
import os
import subprocess
import sys
import hashlib


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def npm_preflight(project_dir, npm_bin, force=False):
    marker = os.path.join(project_dir, ".nox-npm-installed")
    pkg_json = os.path.join(project_dir, "package.json")
    lock_json = os.path.join(project_dir, "package-lock.json")
    node_modules = os.path.join(project_dir, "node_modules")
    pkg_hash = file_hash(pkg_json) if os.path.exists(pkg_json) else ""
    lock_hash = file_hash(lock_json) if os.path.exists(lock_json) else ""
    need_npm = True
    if os.path.exists(marker) and not force:
        try:
            with open(marker) as f:
                marker_hash = f.read().strip().split("|")
                if (
                    len(marker_hash) == 2
                    and marker_hash[0] == pkg_hash
                    and marker_hash[1] == lock_hash
                    and os.path.exists(node_modules)
                ):
                    need_npm = False
        except Exception:
            need_npm = True
    if need_npm:
        print(f"[npm-preflight] Running npm install in {project_dir} ...")
        subprocess.check_call([npm_bin, "install"], cwd=project_dir)
        with open(marker, "w") as f:
            f.write(f"{pkg_hash}|{lock_hash}")
    else:
        print(f"[npm-preflight] npm install not needed in {project_dir} (cache valid)")


def main():
    # Robust Windows/Unix check for npm, npm.cmd, npm.bat
    npm_bin = shutil.which("npm") or shutil.which("npm.cmd") or shutil.which("npm.bat")
    if not npm_bin:
        print(
            "\033[1;31m╔════════════════════════════════════════════════════════════╗\033[0m",
            file=sys.stderr,
        )
        print(
            "\033[1;31m║  🟥 [npm-preflight] ERROR: npm is not installed or not in PATH.\033[0m",
            file=sys.stderr,
        )
        print(
            "\033[1;31m║  Please install Node.js and npm from https://nodejs.org/   \033[0m",
            file=sys.stderr,
        )
        print(
            "\033[1;31m╚════════════════════════════════════════════════════════════╝\033[0m",
            file=sys.stderr,
        )
        sys.exit(1)
    # Add all npm-based subprojects here
    npm_projects = ["docs-site", "ui"]  # future react app
    force = "--force" in sys.argv
    for proj in npm_projects:
        if os.path.exists(os.path.join(proj, "package.json")):
            npm_preflight(proj, npm_bin, force=force)
    print("[npm-preflight] All npm preflight checks complete.")


if __name__ == "__main__":
    main()
