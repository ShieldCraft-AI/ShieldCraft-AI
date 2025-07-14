import re
from bs4 import BeautifulSoup
import difflib
from pathlib import Path

def html_table_to_markdown(table_tag):
    rows = table_tag.find_all("tr")
    md_rows = []
    header_found = False
    for i, row in enumerate(rows):
        cols = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
        line = "| " + " | ".join(cols) + " |"
        md_rows.append(line)
        if not header_found and row.find("th"):
            md_rows.append("| " + " | ".join(["---"] * len(cols)) + " |")
            header_found = True
    return "\n".join(md_rows)

def convert_html_to_markdown(html):
    soup = BeautifulSoup(html, "html.parser")
    output_lines = []
    unhandled_tags = set()
    for elem in soup.recursiveChildGenerator():
        if elem.name == "section":
            # Convert section to admonition if it contains best practices, insights, etc.
            section_text = elem.get_text(strip=True)
            if "Best Practice" in section_text or "Guidance" in section_text:
                output_lines.append(f":::tip\n{section_text}\n:::")
            elif "Insight" in section_text or "Auditability" in section_text:
                output_lines.append(f":::info\n{section_text}\n:::")
            else:
                output_lines.append(section_text)
        elif elem.name == "div":
            # Ignore divs with only style, treat as paragraph
            output_lines.append(elem.get_text(strip=True))
        elif elem.name == "span":
            # Strip span tags, keep text
            output_lines.append(elem.get_text(strip=True))
        elif elem.name == "h1":
            output_lines.append(f"# {elem.get_text(strip=True)}")
        elif elem.name == "h2":
            output_lines.append(f"## {elem.get_text(strip=True)}")
        elif elem.name == "h3":
            output_lines.append(f"### {elem.get_text(strip=True)}")
        elif elem.name == "a":
            href = elem.get("href", "")
            text = elem.get_text(strip=True)
            output_lines.append(f"[{text}]({href})")
        elif elem.name == "img":
            src = elem.get("src", "")
            alt = elem.get("alt", "")
            output_lines.append(f"![{alt}]({src})")
        elif elem.name == "table":
            output_lines.append(html_table_to_markdown(elem))
        elif elem.name == "ul":
            for li in elem.find_all("li"):
                output_lines.append(f"* {li.get_text(strip=True)}")
        elif elem.name == "pre":
            # Detect mermaid or code block
            code_text = elem.get_text()
            if "mermaid" in code_text:
                output_lines.append(f"```mermaid\n{code_text}\n```")
            else:
                output_lines.append(f"```\n{code_text}\n```")
        elif elem.name == "code":
            output_lines.append(f"`{elem.get_text(strip=True)}`")
        elif elem.name is None:
            text = str(elem).strip()
            if text:
                output_lines.append(text)
        else:
            # Log unhandled tags for auditability
            if elem.name:
                unhandled_tags.add(elem.name)
    markdown = "\n".join([line for line in output_lines if line.strip()])
    if unhandled_tags:
        markdown += f"\n\n<!-- Unhandled tags: {', '.join(sorted(unhandled_tags))} -->"
    # Clean excessive blank lines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    return markdown

def process_file(path, dry_run=False):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()
    updated = convert_html_to_markdown(original)
    if original != updated:
        if dry_run:
            print(f"\n--- {path} ---")
            for line in difflib.unified_diff(
                original.splitlines(),
                updated.splitlines(),
                lineterm="",
                fromfile="original",
                tofile="updated",
            ):
                print(line)
        else:
            out_path = path.parent / (path.stem + ".converted.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"Converted file written to: {out_path}")
    else:
        print(f"No changes needed for {path}")

if __name__ == "__main__":
    test_file = Path("docs-site/docs/aws_stack_architecture.md")
    process_file(test_file, dry_run=True)
