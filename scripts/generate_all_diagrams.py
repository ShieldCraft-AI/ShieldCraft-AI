import os
import subprocess
import sys

print("Using Python:", sys.executable)


def is_diagram_script(filename):
    return filename.endswith("_diagram.py")


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    diagrams_dir = os.path.join(repo_root, "docs-site", "src", "diagrams")
    scripts = [f for f in os.listdir(diagrams_dir) if is_diagram_script(f)]
    if not scripts:
        print("No diagram scripts found.")
        return
    scripts = sorted(scripts)
    print("Select a diagram to generate:")
    for idx, script in enumerate(scripts, 1):
        default_marker = " (default)" if "system_context_diagram.py" in script else ""
        print(f"  {idx}. {script}{default_marker}")
    default_idx = (
        next((i for i, s in enumerate(scripts) if "system_context_diagram.py" in s), 0)
        + 1
    )
    try:
        choice = input(f"Enter number [default {default_idx}]: ").strip()
        if not choice:
            choice = default_idx
        else:
            choice = int(choice)
        if not (1 <= int(choice) <= len(scripts)):
            print("Invalid selection.")
            return
    except Exception:
        print("Invalid input.")
        return
    script = scripts[int(choice) - 1]
    script_path = os.path.join(diagrams_dir, script)
    print(f"Generating diagram: {script}")
    result = subprocess.run(
        [sys.executable, script_path], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error generating {script}:")
        print(result.stderr)
    else:
        print(f"Successfully generated {script}")


if __name__ == "__main__":
    main()
