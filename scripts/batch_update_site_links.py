import os
import re
from pathlib import Path

# Directory containing MDX files to update
SITE_DOCS_DIR = Path(__file__).parent / "docs-site" / "docs" / "site"

# Patterns to update: (regex, replacement)
LINK_PATTERNS = [
    # Relative links to root-level docs
    (r"\]\(\.\./([a-zA-Z0-9_-]+)\)", r"](/\1)"),
    # Relative links to sibling docs
    (r"\]\(\.\/([a-zA-Z0-9_-]+)\)", r"](/site/\1)"),
    # Links to intro, security, data_prep, github, etc.
    (r"\]\((intro|security|data_prep|github|site)\)", r"](/\1)"),
    # Links to nested docs (e.g., security/architecture)
    (r"\]\((security/[a-zA-Z0-9_-]+)\)", r"](/\1)"),
    (r"\]\((data_prep/[a-zA-Z0-9_-]+)\)", r"](/\1)"),
    # Links to assets
    (r"\]\(\.\/_assets/([a-zA-Z0-9_.-]+)\)", r"](/docs/_assets/\1)"),
]


def update_links_in_file(filepath: Path):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    original_content = content
    for pattern, repl in LINK_PATTERNS:
        content = re.sub(pattern, repl, content)
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated links in: {filepath}")
    else:
        print(f"No changes needed: {filepath}")


def batch_update_site_links():
    # Only process MDX files directly in docs-site/docs/site, not in subfolders like docs/github
    for mdx_file in SITE_DOCS_DIR.glob("*.mdx"):
        # Defensive: skip if file is in docs/github (shouldn't happen, but future-proof)
        if "github" in mdx_file.parts:
            continue
        update_links_in_file(mdx_file)


if __name__ == "__main__":
    batch_update_site_links()
