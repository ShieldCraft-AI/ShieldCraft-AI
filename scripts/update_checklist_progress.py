"""
Auto-update the progress bar in docs/checklist.md and README.md based on 🟩 and 🟥 items.
Run this script after a successful push (e.g., as a post-push hook or in CI).
"""

import re
import sys
from pathlib import Path
from typing import Iterable, Optional


def find_repo_root(start: Path) -> Path:
    """Walk upward from start until a directory containing a repo marker is found.

    Markers (in priority order): .git, pyproject.toml, README.md
    Falls back to provided start if nothing else is found before filesystem root.
    """
    markers = {".git", "pyproject.toml"}
    current = start
    while True:
        if any((current / m).exists() for m in markers):
            return current
        # Heuristic: if README.md AND docs-site exist, assume root
        if (current / "README.md").exists() and (current / "docs-site").exists():
            return current
        if current.parent == current:
            # Reached filesystem root
            return start
        current = current.parent


def resolve_paths(root_override: Optional[str] = None):
    script_dir = Path(__file__).resolve().parent
    if root_override:
        root = Path(root_override).expanduser().resolve()
    else:
        # Original logic overshot by going 3 levels up (.. / .. / ..) which landed outside the repo
        # We now discover repo root robustly.
        root = find_repo_root(script_dir)
    checklist = root / "docs-site" / "docs" / "github" / "checklist.md"
    readme = root / "README.md"
    mdx = root / "docs-site" / "docs" / "site" / "checklist.mdx"
    return root, checklist, readme, mdx


# Allow optional CLI arg: python update_checklist_progress.py [repo_root]
REPO_ROOT, CHECKLIST_PATH, README_PATH, MDX_PATH = resolve_paths(
    sys.argv[1] if len(sys.argv) > 1 else None
)

PROGRESS_BAR_PATTERN = re.compile(
    r'(<progress[^>]+id="shieldcraft-progress"[^>]+value=")\d+("[^>]+max=")\d+("[^>]*>)',
    re.MULTILINE,
)
PROGRESS_LABEL_PATTERN = re.compile(
    r'(<div id="progress-label">)\d+% Complete(</div>)', re.MULTILINE
)
PROGRESSBAR_MDX_PATTERN = re.compile(
    r"(<ProgressBar\s+value=\{)\d+(\}\s+label=)",
    re.MULTILINE,
)


if not CHECKLIST_PATH.exists():
    print(
        f"[update_checklist_progress] ERROR: Checklist file not found: {CHECKLIST_PATH}\n"
        f"  Resolved repo root: {REPO_ROOT}\n"
        f"  (Pass an explicit repo root path as first argument if auto-detection failed.)"
    )
    sys.exit(1)
if not README_PATH.exists():
    print(f"[update_checklist_progress] ERROR: README file not found: {README_PATH}")
    sys.exit(1)
if not MDX_PATH.exists():
    print(
        f"[update_checklist_progress] WARNING: MDX file not found (optional): {MDX_PATH}"
    )

with CHECKLIST_PATH.open("r", encoding="utf-8") as f:
    checklist_content = f.read()

# If explicit counted scope markers exist, restrict counting to that region
scope_match = re.search(
    r"<!-- COUNTED_SCOPE_BEGIN -->(.*)<!-- COUNTED_SCOPE_END -->",
    checklist_content,
    re.DOTALL,
)
count_region = scope_match.group(1) if scope_match else checklist_content

# Count status icons (only in counted scope region)
COMPLETED_ICONS: Iterable[str] = ("🟩", "✅")
REMAINING_ICONS: Iterable[str] = ("🟥", "🕒")


def count_icons(text: str, icons: Iterable[str]) -> int:
    return sum(text.count(icon) for icon in icons)


num_done = count_icons(count_region, COMPLETED_ICONS)
num_todo = count_icons(count_region, REMAINING_ICONS)
num_total = num_done + num_todo
percent = int(round((num_done / num_total) * 100)) if num_total > 0 else 0

# Update <progress> value and label in checklist
content_new = PROGRESS_BAR_PATTERN.sub(
    rf"\g<1>{percent}\g<2>100\g<3>", checklist_content
)
content_new = PROGRESS_LABEL_PATTERN.sub(rf"\g<1>{percent}% Complete\g<2>", content_new)

if content_new != checklist_content:
    with CHECKLIST_PATH.open("w", encoding="utf-8") as f:
        f.write(content_new)
    print(
        f"[update_checklist_progress] Progress bar updated in checklist.md: {percent}% complete."
    )
else:
    print(
        f"[update_checklist_progress] Progress bar already up-to-date in checklist.md: {percent}%."
    )

# Update <progress> value and label in README
with README_PATH.open("r", encoding="utf-8") as f:
    readme_content = f.read()

readme_new = PROGRESS_BAR_PATTERN.sub(rf"\g<1>{percent}\g<2>100\g<3>", readme_content)
readme_new = PROGRESS_LABEL_PATTERN.sub(rf"\g<1>{percent}% Complete\g<2>", readme_new)

if readme_new != readme_content:
    with README_PATH.open("w", encoding="utf-8") as f:
        f.write(readme_new)
    print(
        f"[update_checklist_progress] Progress bar updated in README.md: {percent}% complete."
    )
else:
    print(
        f"[update_checklist_progress] Progress bar already up-to-date in README.md: {percent}%."
    )

# Update percentage in checklist.mdx
if MDX_PATH.exists():
    with MDX_PATH.open("r", encoding="utf-8") as f:
        mdx_content = f.read()
    # Update custom ProgressBar component value and any stray '% Complete' strings
    mdx_new = PROGRESSBAR_MDX_PATTERN.sub(rf"\g<1>{percent}\g<2>", mdx_content)
    mdx_new = re.sub(r"\d+% Complete", f"{percent}% Complete", mdx_new)
    if mdx_new != mdx_content:
        with MDX_PATH.open("w", encoding="utf-8") as f:
            f.write(mdx_new)
        print(
            f"[update_checklist_progress] Progress percentage updated in checklist.mdx: {percent}% complete."
        )
    else:
        print(
            f"[update_checklist_progress] Progress percentage already up-to-date in checklist.mdx: {percent}%."
        )
