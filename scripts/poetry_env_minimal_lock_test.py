import subprocess
import sys
import os
import shutil

# Step 1: Remove poetry.lock and .venv if they exist
def remove_old_files():
    for fname in ["poetry.lock", ".venv"]:
        if os.path.exists(fname):
            if os.path.isdir(fname):
                shutil.rmtree(fname)
            else:
                os.remove(fname)

# Step 2: Remove Poetry cache/config for a truly clean slate
def remove_poetry_cache_config():
    for dname in [os.path.expanduser("~/.cache/pypoetry"), os.path.expanduser("~/.config/pypoetry")]:
        if os.path.exists(dname):
            shutil.rmtree(dname)

# Step 3: Clear Poetry's cache (redundant, but safe)
def clear_poetry_cache():
    subprocess.run(["poetry", "cache", "clear", "pypi", "--all"], check=True)

# Step 4: Use Python 3.12 for Poetry environment
def set_poetry_env():
    subprocess.run(["poetry", "env", "use", "3.12"], check=True)

# Step 5: Lock and install dependencies
def lock_and_install():
    subprocess.run(["poetry", "lock"], check=True)
    subprocess.run(["poetry", "install"], check=True)

# Step 6: Export requirements and grep for python markers
def export_and_grep_markers():
    subprocess.run(["poetry", "export", "--without-hashes", "-f", "requirements.txt", "-o", "exported_requirements.txt"], check=True)
    print("\nPython version markers in exported requirements:")
    subprocess.run(["grep", "python_version", "exported_requirements.txt"])

# Step 7: Debug info and dependency tree
def debug_info():
    subprocess.run(["poetry", "debug", "info"], check=True)
    subprocess.run(["poetry", "show", "--tree"], check=True)

if __name__ == "__main__":
    print("Cleaning old Poetry files, cache, and config...")
    remove_old_files()
    remove_poetry_cache_config()
    clear_poetry_cache()
    print("Setting Poetry environment to Python 3.12...")
    set_poetry_env()
    print("Locking and installing dependencies...")
    try:
        lock_and_install()
        print("Poetry environment setup complete.")
        export_and_grep_markers()
    except subprocess.CalledProcessError:
        print("Error during lock/install. Showing debug info:")
        debug_info()
        export_and_grep_markers()
