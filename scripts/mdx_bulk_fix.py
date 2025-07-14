
import re
from bs4 import BeautifulSoup
from pathlib import Path

def html_table_to_markdown(table_tag):
    # Process table with header and body
    md_rows = []
    header = table_tag.find("thead")
    if header:
        header_cols = [th.get_text(strip=True) for th in header.find_all("th")]
        md_rows.append("| " + " | ".join(header_cols) + " |")
        md_rows.append("| " + " | ".join(["---"] * len(header_cols)) + " |")
    body = table_tag.find("tbody") or table_tag
    for row in body.find_all("tr"):
        cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
        if cols:
            md_rows.append("| " + " | ".join(cols) + " |")
    return "\n".join(md_rows)

def convert_admonition(section_tag):
    text = section_tag.get_text("\n", strip=True)
    if "Best Practice" in text or "Guidance" in text:
        return f":::tip\n{text}\n:::"  # Docusaurus tip
    elif "Insight" in text or "Auditability" in text:
        return f":::info\n{text}\n:::"  # Docusaurus info
    return text

def convert_list(list_tag):
    items = []
    for li in list_tag.find_all("li", recursive=False):
        items.append(f"* {li.get_text(strip=True)}")
    return "\n".join(items)

def convert_code_block(pre_tag):
    code_text = pre_tag.get_text()
    if "mermaid" in code_text:
        return f"```mermaid\n{code_text}\n```"
    return f"```\n{code_text}\n```"

def convert_inline(tag):
    if tag.name == "a":
        href = tag.get("href", "")
        text = tag.get_text(strip=True)
        return f"[{text}]({href})"
    elif tag.name == "img":
        src = tag.get("src", "")
        alt = tag.get("alt", "")
        return f"![{alt}]({src})"
    elif tag.name == "code":
        return f"`{tag.get_text(strip=True)}`"
    elif tag.name == "span":
        return tag.get_text(strip=True)
    return tag.get_text(strip=True)

def convert_heading(tag):
    level = int(tag.name[1]) if tag.name[0] == "h" and tag.name[1].isdigit() else 1
    return f"{'#' * level} {tag.get_text(strip=True)}"

def convert_node(node, unhandled_tags):
    if isinstance(node, str):
        return node.strip()
    if node.name == "section":
        return convert_admonition(node)
    elif node.name == "table":
        return html_table_to_markdown(node)
    elif node.name in ["ul", "ol"]:
        return convert_list(node)
    elif node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        return convert_heading(node)
    elif node.name == "pre":
        return convert_code_block(node)
    elif node.name == "div":
        # Treat as paragraph if not just style
        return node.get_text(" ", strip=True)
    elif node.name in ["a", "img", "code", "span"]:
        return convert_inline(node)
    elif node.name is None:
        return str(node).strip()
    else:
        unhandled_tags.add(node.name)
        return node.get_text(strip=True)

def convert_html_to_markdown(html):
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body or soup
    markdown_blocks = []
    unhandled_tags = set()
    for child in body.children:
        md = convert_node(child, unhandled_tags)
        if md:
            markdown_blocks.append(md)
    markdown = "\n\n".join([block for block in markdown_blocks if block.strip()])
    if unhandled_tags:
        markdown += f"\n\n<!-- Unhandled tags: {', '.join(sorted(unhandled_tags))} -->"
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    return markdown

def process_file(path, dry_run=False):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()
    updated = convert_html_to_markdown(original)
    if original != updated:
        if not dry_run:
            out_path = path.with_name(path.name.replace('.md', '.converted.md'))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"Converted file written to: {out_path}")

if __name__ == "__main__":
    test_file = Path("docs-site/docs/aws_stack_architecture.md")
    process_file(test_file, dry_run=False)
