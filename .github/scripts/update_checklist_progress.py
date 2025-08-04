"""
Auto-update the progress bar in docs/checklist.md and README.md based on 🟩 and 🟥 items.
Run this script after a successful push (e.g., as a post-push hook or in CI).
"""

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHECKLIST_PATH = REPO_ROOT / "docs-site" / "docs" / "github" / "checklist.md"
README_PATH = REPO_ROOT / "README.md"
MDX_PATH = REPO_ROOT / "docs-site" / "docs" / "site" / "checklist.mdx"

PROGRESS_BAR_PATTERN = re.compile(
    r'(<progress[^>]+id="shieldcraft-progress"[^>]+value=")\d+("[^>]+max=")\d+("[^>]*>)',
    re.MULTILINE,
)
PROGRESS_LABEL_PATTERN = re.compile(
    r'(<div id="progress-label">)\d+% Complete(</div>)', re.MULTILINE
)


if not CHECKLIST_PATH.exists():
    print(
        f"[update_checklist_progress] ERROR: Checklist file not found: {CHECKLIST_PATH}"
    )
    exit(1)
if not README_PATH.exists():
    print(f"[update_checklist_progress] ERROR: README file not found: {README_PATH}")
    exit(1)
if not MDX_PATH.exists():
    print(f"[update_checklist_progress] WARNING: MDX file not found: {MDX_PATH}")

with CHECKLIST_PATH.open("r", encoding="utf-8") as f:
    checklist_content = f.read()

# Count checkboxes
num_done = len(re.findall(r"🟩", checklist_content))
num_todo = len(re.findall(r"🟥", checklist_content))
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
# Update <progress> value and label in README

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
    # Replace the line with '% Complete' (e.g., '32% Complete')
    mdx_new = re.sub(r"\d+% Complete", f"{percent}% Complete", mdx_content)
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
