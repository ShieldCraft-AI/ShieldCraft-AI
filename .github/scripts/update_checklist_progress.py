"""
Auto-update the progress bar in docs/checklist.md based on 🟩 and 🟥 items.
Run this script after a successful push (e.g., as a post-push hook or in CI).
"""

import re
from pathlib import Path

CHECKLIST_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "checklist.md"

PROGRESS_BAR_PATTERN = re.compile(
    r'(<progress[^>]+id="shieldcraft-progress"[^>]+value=")\d+(")([^>]+max=")\d+(")',
    re.MULTILINE,
)
PROGRESS_LABEL_PATTERN = re.compile(
    r'(<div id="progress-label">)\d+% Complete(</div>)', re.MULTILINE
)

with CHECKLIST_PATH.open("r", encoding="utf-8") as f:
    content = f.read()

# Count checkboxes
num_done = len(re.findall(r"🟩", content))
num_todo = len(re.findall(r"🟥", content))
num_total = num_done + num_todo
percent = int(round((num_done / num_total) * 100)) if num_total > 0 else 0

# Update <progress> value and label
content_new = PROGRESS_BAR_PATTERN.sub(rf"\g<1>{percent}\g<2>\g<3>100\g<4>", content)
content_new = PROGRESS_LABEL_PATTERN.sub(rf"\g<1>{percent}% Complete\g<2>", content_new)

if content_new != content:
    with CHECKLIST_PATH.open("w", encoding="utf-8") as f:
        f.write(content_new)
    print(f"[update_checklist_progress] Progress bar updated: {percent}% complete.")
else:
    print(f"[update_checklist_progress] Progress bar already up-to-date: {percent}%.")
