
import re
from bs4 import BeautifulSoup
from pathlib import Path

def html_table_to_markdown(table_tag):
    md_rows = []
    header = table_tag.find("thead")
    if header:
        header_cols = [th.get_text(strip=True) for th in header.find_all("th")]
        md_rows.append("| " + " | ".join(header_cols) + " |")
        md_rows.append("| " + " | ".join(["---"] * len(header_cols)) + " |")
    body = table_tag.find("tbody") or table_tag
    for row in body.find_all("tr", recursive=False):
        cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"], recursive=False)]
        if cols:
            md_rows.append("| " + " | ".join(cols) + " |")
    return "\n".join(md_rows)

def convert_admonition(section_tag):
    # Gather block-level children for proper separation and Markdown rendering
    blocks = []
    for child in section_tag.children:
        if getattr(child, 'name', None) in ["ul", "ol"]:
            # Add blank line before and after lists
            blocks.append("")
            blocks.append(convert_list(child))
            blocks.append("")
        elif getattr(child, 'name', None) in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            # Add blank line before and after headings
            blocks.append("")
            blocks.append(convert_heading(child))
            blocks.append("")
        elif getattr(child, 'name', None) == "p":
            blocks.append(child.get_text(strip=True))
        elif getattr(child, 'name', None) == "div":
            blocks.append(child.get_text(strip=True))
        elif isinstance(child, str):
            if child.strip():
                blocks.append(child.strip())
        else:
            blocks.append(convert_block(child))
    # Remove leading/trailing blank lines and join with double newlines
    text = "\n\n".join([b for b in blocks if b.strip() or b == ""])
    text = re.sub(r'(\n\n)+', '\n\n', text).strip()
    # Do not wrap in Docusaurus admonition blocks
    return text

def convert_list(list_tag):
    items = []
    bullet = "*" if list_tag.name == "ul" else "1."
    for li in list_tag.find_all("li", recursive=False):
        # Recursively process children for nested lists
        content = convert_block(li)
        # If content contains multiple lines, indent subsequent lines
        if "\n" in content:
            lines = content.splitlines()
            item = f"{bullet} {lines[0]}"
            for l in lines[1:]:
                item += f"\n  {l}"
            items.append(item)
        else:
            items.append(f"{bullet} {content}")
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


# Recursive block-level processor
def convert_block(tag, unhandled_tags=None, indent_level=0):
    if unhandled_tags is None:
        unhandled_tags = set()
    if isinstance(tag, str):
        return tag.strip()
    if tag.name == "section":
        # Only wrap in admonition if content matches keywords
        section_text = tag.get_text(" ", strip=True)
        if any(k in section_text for k in ["Best Practice", "Guidance", "Insight", "Auditability"]):
            admonition = convert_admonition(tag)
            return admonition
        else:
            # Not an admonition: process children as regular blocks
            blocks = []
            for child in tag.children:
                block = convert_block(child, unhandled_tags, indent_level)
                if block:
                    blocks.append(block)
            return "\n\n".join(blocks)
    elif tag.name == "table":
        return html_table_to_markdown(tag)
    elif tag.name in ["ul", "ol"]:
        # Indent nested lists
        items = []
        bullet = "*" if tag.name == "ul" else "1."
        for li in tag.find_all("li", recursive=False):
            content = convert_block(li, unhandled_tags, indent_level + 1)
            prefix = "  " * indent_level + bullet
            items.append(f"{prefix} {content}")
        return "\n".join(items)
    elif tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        return convert_heading(tag)
    elif tag.name == "pre":
        return convert_code_block(tag)
    elif tag.name == "div" or tag.name == "p":
        # Paragraph: process children, separate by blank lines
        content = " ".join([convert_block(child, unhandled_tags, indent_level) for child in tag.children if not isinstance(child, str) or child.strip()])
        return content.strip()
    elif tag.name in ["a", "img", "code", "span"]:
        return convert_inline(tag)
    elif tag.name is None:
        return str(tag).strip()
    else:
        unhandled_tags.add(tag.name)
        return tag.get_text(strip=True)

def convert_html_to_markdown(html):
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body or soup
    markdown_blocks = []
    nav_links = []
    nav_seen = set()
    unhandled_tags = set()
    header = None
    intro = None
    # First pass: extract header, navigation, and intro
    for child in body.children:
        if getattr(child, 'name', None) == 'div':
            a_tag = child.find('a')
            if a_tag:
                nav_text = convert_inline(a_tag)
                if nav_text not in nav_seen:
                    nav_links.append(nav_text)
                    nav_seen.add(nav_text)
            # Look for intro text in centered divs
            if child.get('style', '').find('text-align:center') != -1 or child.get('style', '').find('font-size:1.1em') != -1:
                intro_candidate = child.get_text(" ", strip=True)
                if intro_candidate and not intro:
                    intro = intro_candidate
            continue
        if getattr(child, 'name', None) and child.name.startswith('h') and child.name[1:].isdigit():
            if not header:
                header = convert_heading(child)
            continue
        # If not header/nav/intro, process as block
        md = convert_block(child, unhandled_tags)
        if md:
            markdown_blocks.append(md)
    # Remove navigation and header from markdown_blocks if present
    markdown_blocks = [block for block in markdown_blocks if block not in nav_links and (header is None or block != header)]
    # Compose Markdown output
    # Render navigation links as individual lines, followed by blank line
    nav = "\n".join(nav_links)
    parts = []
    if nav:
        parts.append(nav)
        parts.append("")  # blank line after navigation
    if header:
        parts.append(header)
        parts.append("")  # blank line after header
    if intro:
        parts.append(intro)
        parts.append("")  # blank line after intro
    if markdown_blocks:
        parts.append("\n\n".join([block for block in markdown_blocks if block.strip()]))
    markdown = "\n".join(parts)
    if unhandled_tags:
        markdown += f"\n\n<!-- Unhandled tags: {', '.join(sorted(unhandled_tags))} -->"
    # Clean up excessive blank lines
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
