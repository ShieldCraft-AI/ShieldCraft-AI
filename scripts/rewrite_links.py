
import re
import os
from pathlib import Path


# Configurable paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DOCS_DIR = PROJECT_ROOT / 'docs-site' / 'docs'
CONVERTED_DIR = DOCS_DIR / 'converted'
TREE_FILE = PROJECT_ROOT / 'tree.txt'

# Load tree.txt for valid files
with open(TREE_FILE, 'r', encoding='utf-8') as f:
    valid_files = set(line.strip() for line in f if line.strip() and not line.strip().endswith('/'))

# Build a mapping from .md to .converted.md
converted_map = {}
for fname in valid_files:
    if fname.endswith('.md') and not fname.endswith('.converted.md'):
        base = fname.rsplit('.md', 1)[0]
        converted_map[fname] = base + '.converted.md'

# Regex to find markdown links (captures anchors and query params)
link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

unresolved_links = []

def split_url(url):
    # Split url into path, anchor, query
    anchor = ''
    query = ''
    path = url
    if '#' in url:
        path, anchor = url.split('#', 1)
        anchor = '#' + anchor
    if '?' in path:
        path, query = path.split('?', 1)
        query = '?' + query
        path = path
    return path, anchor, query

def rewrite_links(md_text, src_path):
    def replacer(match):
        text, url = match.group(1), match.group(2)
        path, anchor, query = split_url(url)
        if path.startswith('http') or not path.endswith('.md'):
            return match.group(0)
        # Resolve link path relative to source file
        link_abs_path = (src_path.parent / path).resolve()
        # Compare to normalized tree.txt entries
        for tree_file in valid_files:
            tree_abs_path = (DOCS_DIR / tree_file).resolve()
            print(f"DEBUG: link_abs_path={link_abs_path}, tree_abs_path={tree_abs_path}")
            if link_abs_path == tree_abs_path:
                new_url = converted_map.get(tree_file, tree_file)
                src_converted_dir = src_path.parent / 'converted'
                target_converted_path = CONVERTED_DIR / Path(tree_file).parent / Path(new_url).name
                rel_path = os.path.relpath(str(target_converted_path), str(src_converted_dir))
                return f'[{text}]({rel_path}{query}{anchor})'
        unresolved_links.append((str(src_path), url))
        return f'{match.group(0)} <!-- BROKEN LINK -->'
    return link_pattern.sub(replacer, md_text)

def process_file(md_path):
    src_path = Path(md_path)
    out_dir = src_path.parent / 'converted'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / src_path.name.replace('.md', '.converted.md')
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    updated = rewrite_links(content, src_path)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(updated)
    print(f'Rewritten links: {md_path} -> {out_path}')

if __name__ == '__main__':
    # Process all .md files except .converted.md
    for md_file in DOCS_DIR.rglob('*.md'):
        if not md_file.name.endswith('.converted.md'):
            process_file(md_file)
    if unresolved_links:
        print('\nSummary of unresolved links:')
        for src, url in unresolved_links:
            print(f'  {src}: {url}')
