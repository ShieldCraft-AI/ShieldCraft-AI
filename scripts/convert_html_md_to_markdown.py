"""
Script: convert_html_md_to_markdown.py
Purpose: Batch convert HTML-heavy MD/MDX files to pure Markdown for Docusaurus compatibility.
Tested on: aws_stack_architecture.md

Usage:
  poetry run python scripts/convert_html_md_to_markdown.py <input_file> <output_file>

Dependencies:
  poetry add beautifulsoup4 markdownify
"""

from pathlib import Path
import sys
from bs4 import BeautifulSoup
import markdownify


def convert_html_md_to_markdown(input_path: str, output_path: str):
    # Read file
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove code fences (preserve Mermaid, code blocks)
    # We'll process HTML outside code blocks only
    lines = content.splitlines()
    in_code = False
    processed_lines = []
    code_block = []
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            processed_lines.append(line)
            continue
        if in_code:
            processed_lines.append(line)
        else:
            code_block.append(line)
    # Join non-code lines for HTML processing
    html_text = "\n".join(code_block)
    # Use BeautifulSoup to parse and remove unwanted tags/styles
    soup = BeautifulSoup(html_text, "html.parser")
    # Remove all style attributes and tags
    for tag in soup.find_all(True):
        if tag.has_attr("style"):
            del tag["style"]
    # Convert HTML to Markdown
    markdown_text = markdownify.markdownify(str(soup), heading_style="ATX")
    # Merge code blocks back in
    final_lines = []
    code_idx = 0
    for line in processed_lines:
        if line.strip().startswith("```"):
            final_lines.append(line)
        elif line.strip() == "":
            final_lines.append("")
        else:
            # Use converted markdown for non-code lines
            if code_idx == 0:
                final_lines.extend(markdown_text.splitlines())
                code_idx = 1
    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))
    print(f"Converted {input_path} to Markdown at {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: poetry run python scripts/convert_html_md_to_markdown.py <input_file> <output_file>"
        )
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_html_md_to_markdown(input_file, output_file)
