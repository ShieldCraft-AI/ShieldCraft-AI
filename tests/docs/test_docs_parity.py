from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOC_DIR = PROJECT_ROOT / "docs-site" / "docs" / "guard-suite"
GUARD_SUITE_PAGE = PROJECT_ROOT / "docs-site" / "src" / "pages" / "guard-suite.tsx"
_DOC_SUFFIXES = (".md", ".mdx")


def _load_frontmatter_slug(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise AssertionError(f"{path} is missing required frontmatter")
    closing = text.find("\n---", 3)
    if closing == -1:
        raise AssertionError(f"{path} frontmatter is not terminated with ---")
    block = text[3:closing].strip().splitlines()
    data: dict[str, str] = {}
    for line in block:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    slug = data.get("slug")
    if not slug:
        raise AssertionError(f"{path} must declare a slug in frontmatter")
    return slug


def _guard_suite_doc_links() -> list[str]:
    text = GUARD_SUITE_PAGE.read_text(encoding="utf-8")
    links = re.findall(r"href:\s*'(/guard-suite/[^']+)'", text)
    return sorted(set(links))


def _doc_files() -> list[Path]:
    return sorted(
        path
        for path in DOC_DIR.glob("*")
        if path.suffix in _DOC_SUFFIXES and path.is_file()
    )


@pytest.mark.skipif(not DOC_DIR.exists(), reason="GuardSuite doc directory is missing")
def test_guard_suite_links_have_matching_docs():
    links = _guard_suite_doc_links()
    assert links, "GuardSuite landing page must link to documentation entries"
    for link in links:
        slug = link[len("/guard-suite/") :].rstrip("/")
        slug = slug or "index"
        candidates = [DOC_DIR / f"{slug}{suffix}" for suffix in _DOC_SUFFIXES]
        match = next(
            (candidate for candidate in candidates if candidate.exists()), None
        )
        assert match is not None, f"No document found for route {link}"
        doc_slug = _load_frontmatter_slug(match)
        assert (
            doc_slug == link
        ), f"Document {match} declares slug {doc_slug} but guard-suite route expects {link}"


@pytest.mark.skipif(not DOC_DIR.exists(), reason="GuardSuite doc directory is missing")
def test_guard_suite_docs_are_linked_from_landing_page():
    links = set(_guard_suite_doc_links())
    assert links, "GuardSuite landing page must advertise documentation routes"
    for doc in _doc_files():
        doc_slug = _load_frontmatter_slug(doc)
        assert (
            doc_slug in links
        ), f"GuardSuite doc {doc} (slug {doc_slug}) is not linked from docs-site/src/pages/guard-suite.tsx"
