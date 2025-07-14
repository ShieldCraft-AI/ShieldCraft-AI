
import re
import shutil
import logging
from bs4 import BeautifulSoup
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def fix_self_closing_tags(html):
    # HTML5 void elements that must be self-closing in MDX
    void_tags = [
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"
    ]
    # Self-close all void tags (except progress)
    pattern = r'<({})([^>/]*)(?<!/)>'.format("|".join(void_tags))
    html = re.sub(pattern, r'<\1\2 />', html)

    # Use BeautifulSoup to robustly handle <progress> tags
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("progress"):
        if not tag.contents or (len(tag.contents) == 1 and str(tag.contents[0]).strip() == ""):
            # Empty <progress> -> self-close
            tag.attrs = dict(tag.attrs)  # ensure attrs is a dict
            tag.string = None
            tag.insert_after(BeautifulSoup("", "html.parser"))
            tag.replace_with(BeautifulSoup(str(tag).replace("<progress", "<progress").replace("></progress>", " />"), "html.parser"))
        else:
            # Has content, ensure properly closed
            if not str(tag).endswith("</progress>"):
                logging.warning("Auto-closing <progress> tag with content for MDX compatibility.")
                tag.append(BeautifulSoup("</progress>", "html.parser"))
    # Return soup as string
    return str(soup)
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

def convert_inline(tag, asset_copier=None, src_path=None, out_dir=None):
    if tag.name == "a":
        href = tag.get("href", "")
        text = tag.get_text(strip=True)
        return f"[{text}]({href})"
    elif tag.name == "img":
        src = tag.get("src", "")
        alt = tag.get("alt", "")
        # Copy asset if needed
        if asset_copier and src:
            new_src = asset_copier(src, src_path, out_dir)
        else:
            new_src = src
        return f"![{alt}]({new_src})"
    elif tag.name == "code":
        return f"`{tag.get_text(strip=True)}`"
    elif tag.name == "span":
        return tag.get_text(strip=True)
    return tag.get_text(strip=True)

def convert_heading(tag):
    level = int(tag.name[1]) if tag.name[0] == "h" and tag.name[1].isdigit() else 1
    return f"{'#' * level} {tag.get_text(strip=True)}"


# Recursive block-level processor
def convert_block(tag, unhandled_tags=None, indent_level=0, asset_copier=None, src_path=None, out_dir=None):
    if unhandled_tags is None:
        unhandled_tags = set()
    if isinstance(tag, str):
        return tag.strip()
    if tag.name == "section":
        section_text = tag.get_text(" ", strip=True)
        if any(k in section_text for k in ["Best Practice", "Guidance", "Insight", "Auditability"]):
            admonition = convert_admonition(tag)
            return admonition
        else:
            blocks = []
            for child in tag.children:
                block = convert_block(child, unhandled_tags, indent_level, asset_copier, src_path, out_dir)
                if block:
                    blocks.append(block)
            return "\n\n".join(blocks)
    elif tag.name == "table":
        return html_table_to_markdown(tag)
    elif tag.name in ["ul", "ol"]:
        items = []
        bullet = "*" if tag.name == "ul" else "1."
        for li in tag.find_all("li", recursive=False):
            content = convert_block(li, unhandled_tags, indent_level + 1, asset_copier, src_path, out_dir)
            prefix = "  " * indent_level + bullet
            items.append(f"{prefix} {content}")
        return "\n".join(items)
    elif tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        return convert_heading(tag)
    elif tag.name == "pre":
        return convert_code_block(tag)
    elif tag.name == "div" or tag.name == "p":
        content = " ".join([convert_block(child, unhandled_tags, indent_level, asset_copier, src_path, out_dir) for child in tag.children if not isinstance(child, str) or child.strip()])
        return content.strip()
    elif tag.name in ["a", "img", "code", "span"]:
        return convert_inline(tag, asset_copier, src_path, out_dir)
    elif tag.name is None:
        return str(tag).strip()
    else:
        unhandled_tags.add(tag.name)
        return tag.get_text(strip=True)

def asset_copier(src, src_path, out_dir):
    # Copy asset to out_dir/assets, return new relative path
    if not src or src.startswith('http'):
        return src
    src_file = (src_path.parent / src).resolve()
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    dest_file = assets_dir / src_file.name
    try:
        if src_file.exists():
            shutil.copy2(src_file, dest_file)
            logging.info(f"Copied asset: {src_file} -> {dest_file}")
            return f"./assets/{src_file.name}"
        else:
            logging.warning(f"Asset not found: {src_file}")
            return src
    except Exception as e:
        logging.error(f"Error copying asset {src_file}: {e}")
        return src

def convert_html_to_markdown(html, src_path=None, out_dir=None):
    html = fix_self_closing_tags(html)
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body or soup
    markdown_blocks = []
    nav_links = []
    nav_seen = set()
    unhandled_tags = set()
    header = None
    intro = None
    for child in body.children:
        if getattr(child, 'name', None) == 'div':
            a_tag = child.find('a')
            if a_tag:
                nav_text = convert_inline(a_tag, asset_copier, src_path, out_dir)
                if nav_text not in nav_seen:
                    nav_links.append(nav_text)
                    nav_seen.add(nav_text)
            if child.get('style', '').find('text-align:center') != -1 or child.get('style', '').find('font-size:1.1em') != -1:
                intro_candidate = child.get_text(" ", strip=True)
                if intro_candidate and not intro:
                    intro = intro_candidate
            continue
        if getattr(child, 'name', None) and child.name.startswith('h') and child.name[1:].isdigit():
            if not header:
                header = convert_heading(child)
            continue
        md = convert_block(child, unhandled_tags, asset_copier=asset_copier, src_path=src_path, out_dir=out_dir)
        if md:
            markdown_blocks.append(md)
    markdown_blocks = [block for block in markdown_blocks if block not in nav_links and (header is None or block != header)]
    nav = "\n".join(nav_links)
    parts = []
    if nav:
        parts.append(nav)
        parts.append("")
    if header:
        parts.append(header)
        parts.append("")
    if intro:
        parts.append(intro)
        parts.append("")
    if markdown_blocks:
        parts.append("\n\n".join([block for block in markdown_blocks if block.strip()]))
    markdown = "\n".join(parts)
    if unhandled_tags:
        markdown += f"\n\n<!-- Unhandled tags: {', '.join(sorted(unhandled_tags))} -->"
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    # Final sweep: ensure all <progress> tags are MDX-compatible
    # 1. Self-close orphan <progress ...> tags not followed by </progress>
    markdown = re.sub(r'<progress([^>]*)>(?!.*?</progress>)', r'<progress\1 />', markdown)
    # 2. For <progress ...>...</progress>, ensure both tags are present (already handled by BeautifulSoup, but double check)
    # 3. Remove any stray <progress> tags inside paragraphs
    # 4. Log a warning if any <progress> tags remain unclosed
    if re.search(r'<progress([^>]*)>(?!.*?</progress>)', markdown):
        logging.warning("Unclosed <progress> tag detected after conversion. Please check the source file.")
    return markdown

def autocorrect_mdx_compatibility(markdown, path):
    corrections = []
    # Auto-correct unclosed <progress> tags
    if re.search(r'<progress([^>]*)>(?!.*?</progress>)', markdown):
        markdown = re.sub(r'<progress([^>]*)>(?!.*?</progress>)', r'<progress\1 />', markdown)
        corrections.append("Auto-corrected unclosed <progress> tag.")
    # Auto-correct unclosed <img> tags
    if re.search(r'<img([^>]*)>(?!.*?/>)', markdown):
        markdown = re.sub(r'<img([^>]*)>(?!.*?/>)', r'<img\1 />', markdown)
        corrections.append("Auto-corrected unclosed <img> tag.")
    # Auto-correct unclosed <br> tags
    if re.search(r'<br([^>]*)>(?!.*?/>)', markdown):
        markdown = re.sub(r'<br([^>]*)>(?!.*?/>)', r'<br\1 />', markdown)
        corrections.append("Auto-corrected unclosed <br> tag.")
    # Final sweep: ensure all self-closing tags use <tag .../> (no space before slash)
    markdown = re.sub(r'<([a-zA-Z0-9]+)([^>]*)\s+/\s*>', r'<\1\2/>', markdown)
    corrections.append("Normalized self-closing tag syntax for MDX.")
    # Log corrections
    if corrections:
        logging.info(f"MDX auto-corrections applied to {path}:")
        for corr in corrections:
            logging.info(f"  - {corr}")
    return markdown

def process_file(path, dry_run=False):
    try:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
        out_dir = path.parent / "converted"
        out_dir.mkdir(parents=True, exist_ok=True)
        updated = convert_html_to_markdown(original, src_path=path, out_dir=out_dir)
        # Auto-correct MDX compatibility before writing
        updated = autocorrect_mdx_compatibility(updated, path)
        if original != updated:
            if not dry_run:
                out_path = out_dir / path.name.replace('.md', '.converted.md')
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(updated)
                logging.info(f"Converted file written to: {out_path}")
    except Exception as e:
        logging.error(f"Error processing {path}: {e}")

if __name__ == "__main__":
    docs_root = Path("docs-site/docs")
    md_files = list(docs_root.rglob("*.md"))
    for md_file in md_files:
        if md_file.name.endswith(".converted.md"):
            continue
        process_file(md_file, dry_run=False)
