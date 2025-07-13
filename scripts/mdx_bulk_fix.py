import re
import sys
from pathlib import Path
import difflib

# Patterns for common MDX/HTML issues
VOID_TAGS = ["br", "hr", "img", "input", "meta", "link"]
CLOSING_SLASH_PATTERN = re.compile(r"</([a-zA-Z0-9]+?)/>")


# Fixes for void tags (e.g., <br> to <br />)
def fix_void_tags(text):
    for tag in VOID_TAGS:
        text = re.sub(rf"<{tag}(?![\w/])>", f"<{tag} />", text)
    return text


def fix_closing_slash(text):
    return CLOSING_SLASH_PATTERN.sub(lambda m: f"</{m.group(1)}>", text)


def process_file(path, dry_run=False):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()
    updated = fix_void_tags(original)
    updated = fix_closing_slash(updated)
    if original != updated:
        print(f"\n--- {path} ---")
        for line in difflib.unified_diff(
            original.splitlines(),
            updated.splitlines(),
            lineterm="",
            fromfile="original",
            tofile="updated",
        ):
            print(line)
        if not dry_run:
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)
    else:
        print(f"No changes needed for {path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Bulk-fix MDX/HTML issues in markdown files."
    )
    parser.add_argument("docs_folder", help="Path to docs folder")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show diffs but do not write changes"
    )
    args = parser.parse_args()
    docs_folder = Path(args.docs_folder)
    for md_file in docs_folder.rglob("*.md"):
        process_file(md_file, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
