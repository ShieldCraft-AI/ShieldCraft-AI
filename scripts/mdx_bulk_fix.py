import re
import shutil
import logging
import html
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def fix_self_closing_tags(html):
    # HTML5 void elements that must be self-closing in MDX
    void_tags = [
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"
    ]
    # Use BeautifulSoup for all void/self-closing tags
    soup = BeautifulSoup(html, "html.parser")
    for tag_name in void_tags + ["progress"]:
        for tag in soup.find_all(tag_name):
            if not tag.contents or (len(tag.contents) == 1 and str(tag.contents[0]).strip() == ""):
                tag.attrs = dict(tag.attrs)
                tag.string = None
                tag.replace_with(BeautifulSoup(f"<{tag_name}{' '.join([f'{k}="{v}"' for k,v in tag.attrs.items()])}/>", "html.parser"))
            else:
                if tag_name == "progress" and not str(tag).endswith("</progress>"):
                    logging.warning("Auto-closing <progress> tag with content for MDX compatibility.")
                    tag.append(BeautifulSoup("</progress>", "html.parser"))
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
    # Convert Markdown admonition blocks to Docusaurus Admonition syntax
    blocks = []
    admonition_type = None
    for child in section_tag.children:
        if getattr(child, 'name', None) in ["ul", "ol"]:
            blocks.append("")
            blocks.append(convert_list(child))
            blocks.append("")
        elif getattr(child, 'name', None) in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            blocks.append("")
            blocks.append(convert_heading(child))
            blocks.append("")
        elif getattr(child, 'name', None) == "p":
            txt = child.get_text(strip=True)
            # Detect admonition type from first paragraph
            m = re.match(r'^(Note|Warning|Tip|Info|Danger|Caution|Important):', txt, re.I)
            if m:
                admonition_type = m.group(1).lower()
                txt = re.sub(r'^(Note|Warning|Tip|Info|Danger|Caution|Important):', '', txt, flags=re.I).strip()
            blocks.append(txt)
        elif getattr(child, 'name', None) == "div":
            blocks.append(child.get_text(strip=True))
        elif isinstance(child, str):
            if child.strip():
                blocks.append(child.strip())
        else:
            blocks.append(convert_block(child))
    text = "\n\n".join([b for b in blocks if b.strip() or b == ""])
    text = re.sub(r'(\n\n)+', '\n\n', text).strip()
    if admonition_type:
        return f'<Admonition type="{admonition_type}">\n{text}\n</Admonition>'
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
    # Validate code block language
    lang = ""
    if pre_tag.has_attr("class"):
        for c in pre_tag["class"]:
            if c.startswith("language-"):
                lang = c.replace("language-", "")
    if "mermaid" in code_text or lang == "mermaid":
        return f"```mermaid\n{code_text}\n```"
    elif lang:
        return f"```{lang}\n{code_text}\n```"
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
    # Centralize all assets in docs-site/docs/converted/assets
    if not src or src.startswith('http'):
        return src
    assets_dir = Path('docs-site/docs/converted/assets')
    assets_dir.mkdir(parents=True, exist_ok=True)
    src_file = (src_path.parent / src).resolve()
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
    if html is None or not isinstance(html, str) or not html.strip():
        logging.error(f"Input HTML for {src_path} is None or empty.")
        return ""
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
    markdown = re.sub(r'<progress([^>]*)>(?!.*?</progress>)', lambda m: f'<progress{m.group(1).rstrip()} />', markdown)
    markdown = re.sub(r'(<progress[^>]*/>)\s*/+', r'\1', markdown)
    markdown = re.sub(r'<progress([^>]*)\s*/+\s*>', lambda m: f'<progress{m.group(1).rstrip()} />', markdown)
    if re.search(r'<progress([^>]*)>(?!.*?</progress>)', markdown):
        logging.warning("Unclosed <progress> tag detected after conversion. Please check the source file.")
    return markdown

def load_tree(tree_path):
    """Parse tree.txt and return a set of all files and a mapping of base names to converted names."""
    files = set()
    converted_map = defaultdict(str)
    with open(tree_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.endswith('/'):
                continue
            files.add(line)
            # If .md file, map to .converted.md
            if line.endswith('.md'):
                base = line.rsplit('.md', 1)[0]
                converted_map[line] = base + '.converted.md'
    return files, converted_map

import os
def rewrite_links(markdown, src_path, tree_files, converted_map):
    """Rewrite internal links to point to converted files and correct relative paths, including anchors and query params. Insert warnings for broken links."""
    broken_links = []
    def link_replacer(match):
        text, url = match.group(1), match.group(2)
        if url.startswith('http'):
            return match.group(0)
        base_url, anchor = re.match(r'([^#?]+)([#?].*)?', url).groups() if re.match(r'([^#?]+)([#?].*)?', url) else (url, '')
        if not base_url.endswith('.md'):
            return match.group(0)
        for tree_file in tree_files:
            if tree_file.endswith(base_url):
                new_url = converted_map.get(tree_file, tree_file)
                src_converted_dir = src_path.parent / 'converted'
                target_converted_path = Path('docs-site/docs/converted') / Path(tree_file).parent / Path(new_url).name
                try:
                    rel_path = os.path.relpath(str(target_converted_path), str(src_converted_dir))
                except Exception as e:
                    logging.warning(f"Could not compute relative path for link: {url} in {src_path}: {e}")
                    rel_path = new_url
                return f'[{text}]({rel_path}{anchor or ""})'
        logging.warning(f"Unresolved link: {url} in {src_path}")
        broken_links.append(url)
        return f'{match.group(0)} <!-- BROKEN LINK -->'
    markdown = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_replacer, markdown)
    # Insert summary of broken links at the end
    if broken_links:
        markdown += f"\n\n<!-- Broken links detected: {', '.join(broken_links)} -->"
    return markdown
def autocorrect_mdx_compatibility(markdown, path):
    corrections = []
    # Auto-correct unclosed <progress> tags
    if re.search(r'<progress([^>]*)>(?!.*?</progress>)', markdown):
        markdown = re.sub(r'<progress([^>]*)>(?!.*?</progress>)', lambda m: f'<progress{m.group(1).rstrip()} />', markdown)
        corrections.append("Auto-corrected unclosed <progress> tag.")
    # Auto-correct unclosed <img> tags
    if re.search(r'<img([^>]*)>(?!.*?/>)', markdown):
        markdown = re.sub(r'<img([^>]*)>(?!.*?/>)', lambda m: f'<img{m.group(1).rstrip()} />', markdown)
        corrections.append("Auto-corrected unclosed <img> tag.")
    # Auto-correct unclosed <br> tags
    if re.search(r'<br([^>]*)>(?!.*?/>)', markdown):
        markdown = re.sub(r'<br([^>]*)>(?!.*?/>)', lambda m: f'<br{m.group(1).rstrip()} />', markdown)
        corrections.append("Auto-corrected unclosed <br> tag.")
    # Strictly normalize all self-closing tags to <tag ... /> (no trailing slash or space)
    # This regex matches any tag with one or more slashes before > and replaces with a single space and slash
    markdown = re.sub(r'<([a-zA-Z0-9]+)([^>]*)\s*/+\s*>', lambda m: f'<{m.group(1)}{m.group(2).rstrip()} />', markdown)
    # Remove any accidental trailing slash after />
    markdown = re.sub(r'(<[a-zA-Z0-9]+[^>]*/>)\s*/+', r'\1', markdown)
    # Specifically fix any <progress ... //> or <progress ... / > to <progress ... />
    markdown = re.sub(r'<progress([^>]*)\s*/+\s*>', lambda m: f'<progress{m.group(1).rstrip()} />', markdown)
    corrections.append("Strictly normalized self-closing tag syntax for MDX.")
    # Decode HTML entities
    markdown = html.unescape(markdown)
    corrections.append("Decoded HTML entities.")
    # Log corrections
    if corrections:
        logging.info(f"MDX auto-corrections applied to {path}:")
        for corr in corrections:
            logging.info(f"  - {corr}")
    return markdown

def process_file(path, dry_run=False, tree_files=None, converted_map=None, error_list=None):
    try:
        try:
            with open(path, "r", encoding="utf-8") as f:
                original = f.read()
        except Exception as e:
            logging.error(f"Error reading {path}: {e}")
            if error_list is not None:
                error_list.append((str(path), f"Error reading file: {e}"))
            return
        if original is None or not isinstance(original, str) or not original.strip():
            logging.error(f"File {path} is empty or unreadable.")
            if error_list is not None:
                error_list.append((str(path), "File is empty or unreadable."))
            return
        out_dir = path.parent / "converted"
        out_dir.mkdir(parents=True, exist_ok=True)
        updated = convert_html_to_markdown(original, src_path=path, out_dir=out_dir)
        updated = autocorrect_mdx_compatibility(updated, path)
        if tree_files and converted_map:
            updated = rewrite_links(updated, path, tree_files, converted_map)
        if original != updated:
            if not dry_run:
                out_path = out_dir / path.name.replace('.md', '.converted.md')
                try:
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(updated)
                    logging.info(f"Converted file written to: {out_path}")
                except Exception as e:
                    logging.error(f"Error writing {out_path}: {e}")
                    if error_list is not None:
                        error_list.append((str(path), str(e)))
    except Exception as e:
        logging.error(f"Error processing {path}: {e}")
        if error_list is not None:
            error_list.append((str(path), str(e)))

if __name__ == "__main__":
    docs_root = Path("docs-site/docs")
    tree_path = docs_root / "tree.txt"
    tree_files, converted_map = load_tree(tree_path)
    md_files = [md_file for md_file in docs_root.rglob("*.md") if not md_file.name.endswith(".converted.md")]
    error_list = []
    # Parallel processing for scalability
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file, md_file, False, tree_files, converted_map, error_list): md_file for md_file in md_files}
        for future in as_completed(futures):
            pass
    # Summary report
    if error_list:
        logging.error("Summary of errors during conversion:")
        for fname, err in error_list:
            logging.error(f"  {fname}: {err}")
    else:
        logging.info("All files converted successfully.")
