import re
from pathlib import Path

# Path to new docs directory
SITE_DIR = Path(__file__).parent.parent / "docs-site" / "docs" / "site"

STYLE_ATTR_REGEX = re.compile(r'\s*style="[^"]*"')


# Remove all style="..." attributes from HTML tags in Markdown files
def clean_style_attributes(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    cleaned = STYLE_ATTR_REGEX.sub("", content)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"Cleaned style attributes: {md_path}")


if __name__ == "__main__":
    for md_file in SITE_DIR.rglob("*.md"):
        clean_style_attributes(md_file)
    print("All style attributes removed from Markdown files.")
