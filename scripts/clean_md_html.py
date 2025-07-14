
import re
from pathlib import Path

# Configurable path to docs directory
DOCS_DIR = Path(__file__).parent.parent / 'docs-site' / 'docs'

# Regex to remove all <section ...>...</section> blocks (multi-line, greedy)
SECTION_BLOCK_REGEX = re.compile(r'<section[\s\S]*?</section>', re.IGNORECASE)

def clean_markdown_file(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove all <section ...>...</section> blocks
    cleaned = SECTION_BLOCK_REGEX.sub('', content)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f"Cleaned: {md_path}")

if __name__ == '__main__':
    for md_file in DOCS_DIR.rglob('*.md'):
        if md_file.name.endswith('.converted.md'):
            continue
        clean_markdown_file(md_file)
    print("Markdown cleanup complete.")
