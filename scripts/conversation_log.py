"""
Append-only conversation logger for the ShieldCraft-AI repo.

This script records messages (role, timestamp, content) in a JSONL file under
`logs/conversation_history.jsonl`. It snapshots a local copilot-instructions file
if present and optionally runs a `git commit` to keep the log in repo history.

Usage examples:
  # Append a single message
  python scripts/conversation_log.py --role user --message "What's the plan?"

  # Read assistant reply from stdin (useful when piping)
  echo "Assistant reply text" | python scripts/conversation_log.py --role assistant --from-stdin

  # Append and git-commit the change (requires git repo and configured user)
  python scripts/conversation_log.py --role assistant --message "..." --git-commit

The script looks for common copilot-instructions paths and records a sha256
snapshot if found so we have a trace of the instruction file used during the
conversation.
"""

from __future__ import annotations
import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime
import sys
import subprocess

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "conversation_history.jsonl"

COPILOT_CANDIDATES = [
    Path(".github") / "instructions" / "copilot-instructions.md",
    Path(".github") / "copilot-instructions",
    Path(".copilot_instructions"),
    Path("copilot-instructions"),
]


def read_copilot_snapshot() -> dict | None:
    for p in COPILOT_CANDIDATES:
        if p.exists():
            txt = p.read_text(encoding="utf-8")
            h = hashlib.sha256(txt.encode("utf-8")).hexdigest()
            return {"path": str(p), "sha256": h, "snippet": txt[:2048]}
    return None


def append_entry(entry: dict):
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def maybe_git_commit(msg: str):
    try:
        subprocess.run(["git", "add", str(LOG_FILE)], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
    except Exception:
        # non-fatal: do not raise if git isn't configured or commit fails
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", choices=["user", "assistant", "system"], required=True)
    ap.add_argument("--message", help="Message text")
    ap.add_argument("--from-stdin", action="store_true", help="Read message from stdin")
    ap.add_argument("--meta", help="Optional JSON metadata")
    ap.add_argument(
        "--git-commit", action="store_true", help="Run a git commit after append"
    )
    args = ap.parse_args()

    if args.from_stdin:
        msg = sys.stdin.read().rstrip("\n")
    else:
        msg = args.message or ""
    if not msg:
        print("No message provided (use --message or --from-stdin).", file=sys.stderr)
        sys.exit(2)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "role": args.role,
        "message": msg,
        "meta": None,
    }
    if args.meta:
        try:
            entry["meta"] = json.loads(args.meta)
        except Exception:
            entry["meta"] = {"raw_meta": args.meta}

    copilot_snapshot = read_copilot_snapshot()
    if copilot_snapshot:
        entry["copilot_instructions_snapshot"] = copilot_snapshot

    append_entry(entry)

    if args.git_commit:
        commit_msg = (
            f"chore(log): append conversation entry ({args.role}) {entry['timestamp']}"
        )
        maybe_git_commit(commit_msg)

    print(f"Appended entry to {LOG_FILE}")


if __name__ == "__main__":
    main()
