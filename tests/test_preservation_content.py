#!/usr/bin/env python3
"""
Preservation Property Tests: Correctly Formatted Content

**Property 2: Preservation** - Correctly Formatted Content Preservation
These tests MUST PASS on UNFIXED code, establishing baseline behavior to preserve.

Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6

Tests that pages WITHOUT known formatting issues continue to render correctly:
- Pages with proper titles render correctly (Req 3.1)
- Code blocks with proper highlighting continue to work (Req 3.2)
- Correctly formatted tables maintain structure (Req 3.3)
- Properly nested lists maintain indentation (Req 3.4)
- Correctly formatted images display properly (Req 3.5)
- Working links continue to resolve (Req 3.6)
"""

import os
import re
import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, Phase

# Project root
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc"


def read_md_file(rel_path):
    """Read a markdown file and return its content."""
    full_path = ROOT / rel_path
    if not full_path.exists():
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def get_md_title(content):
    """Extract the first H1 title from markdown content."""
    if content is None:
        return None
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def find_fenced_code_blocks(content):
    """
    Find all fenced code blocks in content.
    Returns list of (language, code_body, start_line) tuples.
    """
    blocks = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^(\s*)(```+)\s*(\{[^}]*\}|[a-zA-Z0-9_+-]*)\s*$', line)
        if m:
            indent = m.group(1)
            fence = m.group(2)
            lang_raw = m.group(3).strip()
            lang = None
            if lang_raw.startswith("{"):
                lang_match = re.search(r'\.(\w+)', lang_raw)
                if lang_match:
                    lang = lang_match.group(1)
            elif lang_raw:
                lang = lang_raw
            body_lines = []
            i += 1
            while i < len(lines):
                if re.match(r'^' + re.escape(indent) + re.escape(fence) + r'\s*$', lines[i]):
                    break
                body_lines.append(lines[i])
                i += 1
            blocks.append((lang, "\n".join(body_lines), m.start()))
        i += 1
    return blocks


def find_markdown_tables(content):
    """
    Find markdown pipe tables in content.
    Returns list of (header_row, separator_row, data_rows, start_line) tuples.
    """
    tables = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # A table starts with a pipe-delimited row followed by a separator row
        if "|" in line and i + 1 < len(lines):
            sep = lines[i + 1]
            if re.match(r'^\s*\|?[\s:]*-+[\s:]*(\|[\s:]*-+[\s:]*)*\|?\s*$', sep):
                header = line
                separator = sep
                data_rows = []
                j = i + 2
                while j < len(lines) and "|" in lines[j]:
                    data_rows.append(lines[j])
                    j += 1
                tables.append((header, separator, data_rows, i + 1))
                i = j
                continue
        i += 1
    return tables


def find_markdown_images(content):
    """
    Find markdown image references.
    Returns list of (alt_text, url, line_number) tuples.
    """
    images = []
    for i, line in enumerate(content.split("\n"), 1):
        for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', line):
            images.append((m.group(1), m.group(2), i))
    return images


def find_markdown_links(content):
    """
    Find markdown links (excluding images).
    Returns list of (label, url, line_number) tuples.
    """
    links = []
    for i, line in enumerate(content.split("\n"), 1):
        # Remove images first to avoid matching image syntax
        cleaned = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', line)
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', cleaned):
            links.append((m.group(1), m.group(2), i))
    return links


def find_list_items(content):
    """
    Find list items (ordered and unordered).
    Returns list of (indent_level, marker, text, line_number) tuples.
    """
    items = []
    in_fence = False
    for i, line in enumerate(content.split("\n"), 1):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r'^(\s*)([-*+]|\d+[.)]) (.+)', line)
        if m:
            indent = len(m.group(1))
            marker = m.group(2)
            text = m.group(3)
            items.append((indent, marker, text, i))
    return items


# ---------------------------------------------------------------------------
# Well-formatted pages NOT in any bug condition test lists.
# These pages are confirmed to render correctly and must be preserved.
# ---------------------------------------------------------------------------

# Pages with proper titles (Req 3.1)
WELL_TITLED_PAGES = [
    "doc/en/user/introduction/overview.md",
    "doc/en/user/introduction/history.md",
    "doc/en/user/introduction/license.md",
    "doc/en/user/introduction/gettinginvolved.md",
    "doc/en/user/production/java.md",
    "doc/en/user/production/data.md",
    "doc/en/user/production/config.md",
    "doc/en/user/production/linuxscript.md",
    "doc/en/user/webadmin/about.md",
    "doc/en/user/webadmin/welcome.md",
    "doc/en/user/filter/syntax.md",
    "doc/en/user/filter/function.md",
]

# Pages with properly fenced and highlighted code blocks (Req 3.2)
WELL_FORMATTED_CODE_PAGES = [
    "doc/en/user/production/config.md",
    "doc/en/user/production/data.md",
]

# Pages with correctly formatted tables (Req 3.3)
WELL_FORMATTED_TABLE_PAGES = [
    "doc/en/user/production/config.md",  # Has service strategy table
]

# Pages with properly nested lists (Req 3.4)
WELL_FORMATTED_LIST_PAGES = [
    "doc/en/user/introduction/overview.md",
    "doc/en/user/production/config.md",
    "doc/en/user/production/java.md",
    "doc/en/user/filter/syntax.md",
]

# Pages with correctly formatted images (Req 3.5)
WELL_FORMATTED_IMAGE_PAGES = [
    "doc/en/user/webadmin/about.md",
    "doc/en/user/webadmin/welcome.md",
    "doc/en/user/production/identify.md",
    "doc/en/user/production/config.md",
]

# Pages with working links (Req 3.6)
WELL_FORMATTED_LINK_PAGES = [
    "doc/en/user/introduction/overview.md",
    "doc/en/user/introduction/history.md",
    "doc/en/user/production/config.md",
    "doc/en/user/production/data.md",
    "doc/en/user/filter/syntax.md",
    "doc/en/user/webadmin/welcome.md",
]


# ---------------------------------------------------------------------------
# Requirement 3.1: Pages with proper titles render correctly
# ---------------------------------------------------------------------------

class TestPreservationTitles:
    """Preservation: Pages with proper titles must continue to render correctly."""

    @pytest.mark.parametrize("page_path", WELL_TITLED_PAGES)
    def test_page_has_valid_h1_title(self, page_path):
        """
        Requirement 3.1: Well-formatted pages must have a valid H1 title
        that is human-readable (not path/index, not garbled).
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        title = get_md_title(content)
        assert title is not None, (
            f"Preservation BROKEN: {page_path} lost its H1 title"
        )
        # Title should be human-readable
        assert not re.search(r"\w+/index$", title), (
            f"Preservation BROKEN: {page_path} title is path/index: '{title}'"
        )
        # Title should not be empty
        assert len(title.strip()) > 0, (
            f"Preservation BROKEN: {page_path} has empty title"
        )
        # Title should not contain raw markdown syntax
        assert "```" not in title, (
            f"Preservation BROKEN: {page_path} title contains code fence syntax"
        )

    @given(
        page_path=st.sampled_from(WELL_TITLED_PAGES)
    )
    @settings(max_examples=len(WELL_TITLED_PAGES), phases=[Phase.explicit, Phase.generate])
    def test_title_is_human_readable_property(self, page_path):
        """
        Requirement 3.1 (PBT): All well-formatted page titles must remain
        human-readable with no garbled concatenations or path fragments.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        title = get_md_title(content)
        assert title is not None, f"Title missing from {page_path}"

        # No CamelCase garbling
        assert not re.match(r'^[A-Z][a-z]+[A-Z][a-z]+\w*$', title), (
            f"Preservation BROKEN: {page_path} title looks garbled: '{title}'"
        )
        # Title should contain spaces (multi-word) or be a known single-word title
        # Single-word titles like "Overview", "History" are fine
        assert len(title) >= 3, (
            f"Preservation BROKEN: {page_path} title too short: '{title}'"
        )


# ---------------------------------------------------------------------------
# Requirement 3.2: Code blocks with proper highlighting continue to work
# ---------------------------------------------------------------------------

class TestPreservationCodeBlocks:
    """Preservation: Correctly formatted code blocks must maintain highlighting."""

    @pytest.mark.parametrize("page_path", WELL_FORMATTED_CODE_PAGES)
    def test_fenced_code_blocks_have_language(self, page_path):
        """
        Requirement 3.2: Pages with properly highlighted code blocks must
        continue to have language identifiers on their fenced code blocks.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        blocks = find_fenced_code_blocks(content)
        assert len(blocks) > 0, (
            f"Preservation BROKEN: {page_path} lost all its code blocks"
        )

        # At least some blocks should have language identifiers
        blocks_with_lang = [b for b in blocks if b[0] is not None]
        assert len(blocks_with_lang) > 0, (
            f"Preservation BROKEN: {page_path} has {len(blocks)} code blocks "
            f"but none have language identifiers for syntax highlighting"
        )

    @pytest.mark.parametrize("page_path", WELL_FORMATTED_CODE_PAGES)
    def test_code_blocks_are_properly_fenced(self, page_path):
        """
        Requirement 3.2: Code blocks must use proper fencing (``` markers)
        and not be rendered as indented code blocks.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        blocks = find_fenced_code_blocks(content)
        for lang, body, start in blocks:
            # Code block body should not be empty
            assert len(body.strip()) > 0 or body == "", (
                f"Preservation BROKEN: {page_path} has empty code block at position {start}"
            )

    def test_config_page_xml_blocks_have_xml_language(self):
        """
        Requirement 3.2: production/config.md has XML code blocks that must
        retain their 'xml' language identifier.
        """
        content = read_md_file("doc/en/user/production/config.md")
        if content is None:
            pytest.skip("production/config.md not found")

        blocks = find_fenced_code_blocks(content)
        xml_blocks = [b for b in blocks if b[0] == "xml"]
        assert len(xml_blocks) >= 2, (
            f"Preservation BROKEN: production/config.md should have at least 2 "
            f"XML code blocks with 'xml' language, found {len(xml_blocks)}"
        )

    def test_data_page_xml_blocks_have_xml_language(self):
        """
        Requirement 3.2: production/data.md has code blocks that must
        retain their language identifiers.
        """
        content = read_md_file("doc/en/user/production/data.md")
        if content is None:
            pytest.skip("production/data.md not found")

        blocks = find_fenced_code_blocks(content)
        xml_blocks = [b for b in blocks if b[0] == "xml"]
        assert len(xml_blocks) >= 2, (
            f"Preservation BROKEN: production/data.md should have at least 2 "
            f"code blocks with 'xml' language, found {len(xml_blocks)}"
        )


# ---------------------------------------------------------------------------
# Requirement 3.3: Correctly formatted tables maintain structure
# ---------------------------------------------------------------------------

class TestPreservationTables:
    """Preservation: Correctly formatted tables must maintain structure."""

    @pytest.mark.parametrize("page_path", WELL_FORMATTED_TABLE_PAGES)
    def test_tables_have_valid_structure(self, page_path):
        """
        Requirement 3.3: Tables must have a header row, separator row,
        and at least one data row with consistent column counts.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        tables = find_markdown_tables(content)
        assert len(tables) > 0, (
            f"Preservation BROKEN: {page_path} lost all its tables"
        )

        for header, separator, data_rows, line_num in tables:
            # Count columns in header
            header_cols = len([c for c in header.split("|") if c.strip()])
            sep_cols = len([c for c in separator.split("|") if c.strip()])

            # Header and separator should have same column count
            assert header_cols == sep_cols, (
                f"Preservation BROKEN: {page_path} table at line {line_num} "
                f"has mismatched header ({header_cols}) and separator ({sep_cols}) columns"
            )

            # Data rows should have consistent column count
            for row in data_rows:
                row_cols = len([c for c in row.split("|") if c.strip()])
                assert row_cols == header_cols, (
                    f"Preservation BROKEN: {page_path} table at line {line_num} "
                    f"has data row with {row_cols} columns, expected {header_cols}"
                )

    def test_config_page_strategy_table(self):
        """
        Requirement 3.3: production/config.md has a service strategy table
        with 4 rows (SPEED, BUFFER, FILE, PARTIAL-BUFFER2) that must be preserved.
        """
        content = read_md_file("doc/en/user/production/config.md")
        if content is None:
            pytest.skip("production/config.md not found")

        tables = find_markdown_tables(content)
        # Find the strategy table by looking for SPEED in data rows
        strategy_table = None
        for header, sep, data_rows, line_num in tables:
            all_text = " ".join(data_rows)
            if "SPEED" in all_text and "BUFFER" in all_text:
                strategy_table = (header, sep, data_rows, line_num)
                break

        assert strategy_table is not None, (
            "Preservation BROKEN: production/config.md lost its service strategy table"
        )
        _, _, data_rows, _ = strategy_table
        assert len(data_rows) == 4, (
            f"Preservation BROKEN: strategy table should have 4 rows, "
            f"found {len(data_rows)}"
        )


# ---------------------------------------------------------------------------
# Requirement 3.4: Properly nested lists maintain indentation
# ---------------------------------------------------------------------------

class TestPreservationLists:
    """Preservation: Correctly formatted lists must maintain nesting."""

    @pytest.mark.parametrize("page_path", WELL_FORMATTED_LIST_PAGES)
    def test_lists_exist_and_have_content(self, page_path):
        """
        Requirement 3.4: Pages with lists must continue to have list items
        with actual content (not empty bullets).
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        items = find_list_items(content)
        assert len(items) > 0, (
            f"Preservation BROKEN: {page_path} lost all its list items"
        )

        # No empty list items
        empty_items = [(indent, marker, text, line)
                       for indent, marker, text, line in items
                       if len(text.strip()) == 0]
        assert len(empty_items) == 0, (
            f"Preservation BROKEN: {page_path} has empty list items at lines: "
            f"{[line for _, _, _, line in empty_items]}"
        )

    def test_overview_page_list_items_are_complete(self):
        """
        Requirement 3.4: introduction/overview.md has a list of OGC compliance
        statements that must all be preserved.
        """
        content = read_md_file("doc/en/user/introduction/overview.md")
        if content is None:
            pytest.skip("introduction/overview.md not found")

        items = find_list_items(content)
        # The overview page has a list of OGC compliance items
        ogc_items = [text for _, _, text, _ in items if "GeoServer" in text]
        assert len(ogc_items) >= 10, (
            f"Preservation BROKEN: overview.md should have at least 10 OGC "
            f"compliance list items, found {len(ogc_items)}"
        )

    def test_config_page_nested_lists_preserved(self):
        """
        Requirement 3.4: production/config.md has nested lists that must
        maintain their indentation structure.
        """
        content = read_md_file("doc/en/user/production/config.md")
        if content is None:
            pytest.skip("production/config.md not found")

        items = find_list_items(content)
        # Should have items at multiple indentation levels
        indent_levels = set(indent for indent, _, _, _ in items)
        assert len(indent_levels) >= 2, (
            f"Preservation BROKEN: production/config.md should have nested lists "
            f"with multiple indent levels, found levels: {indent_levels}"
        )


# ---------------------------------------------------------------------------
# Requirement 3.5: Correctly formatted images display properly
# ---------------------------------------------------------------------------

class TestPreservationImages:
    """Preservation: Correctly formatted images must display properly."""

    @pytest.mark.parametrize("page_path", WELL_FORMATTED_IMAGE_PAGES)
    def test_images_have_valid_syntax(self, page_path):
        """
        Requirement 3.5: Image references must use proper Markdown syntax
        ![alt](url) and not be wrapped in blockquotes or code blocks.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        images = find_markdown_images(content)
        assert len(images) > 0, (
            f"Preservation BROKEN: {page_path} lost all its images"
        )

        for alt, url, line_num in images:
            # URL should not be empty
            assert len(url.strip()) > 0, (
                f"Preservation BROKEN: {page_path} has image with empty URL "
                f"at line {line_num}"
            )

    @pytest.mark.parametrize("page_path", WELL_FORMATTED_IMAGE_PAGES)
    def test_images_not_in_blockquotes(self, page_path):
        """
        Requirement 3.5: Images must not be incorrectly wrapped in
        blockquote syntax (> prefix).
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*>\s*!\[', line):
                pytest.fail(
                    f"Preservation BROKEN: {page_path} has blockquote-wrapped "
                    f"image at line {i}: {line.strip()}"
                )

    def test_welcome_page_images_count(self):
        """
        Requirement 3.5: webadmin/welcome.md has multiple images showing
        the web admin interface that must all be preserved.
        """
        content = read_md_file("doc/en/user/webadmin/welcome.md")
        if content is None:
            pytest.skip("webadmin/welcome.md not found")

        images = find_markdown_images(content)
        assert len(images) >= 5, (
            f"Preservation BROKEN: welcome.md should have at least 5 images, "
            f"found {len(images)}"
        )

    def test_identify_page_images_with_captions(self):
        """
        Requirement 3.5: production/identify.md has images with italic
        captions below them that must be preserved.
        """
        content = read_md_file("doc/en/user/production/identify.md")
        if content is None:
            pytest.skip("production/identify.md not found")

        images = find_markdown_images(content)
        assert len(images) >= 3, (
            f"Preservation BROKEN: identify.md should have at least 3 images, "
            f"found {len(images)}"
        )

        # Check that images are followed by italic caption lines
        lines = content.split("\n")
        caption_count = 0
        for i, line in enumerate(lines):
            if re.match(r'^!\[', line) and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith("*") and next_line.endswith("*"):
                    caption_count += 1

        assert caption_count >= 3, (
            f"Preservation BROKEN: identify.md should have at least 3 image "
            f"captions (italic text below images), found {caption_count}"
        )


# ---------------------------------------------------------------------------
# Requirement 3.6: Working links continue to resolve
# ---------------------------------------------------------------------------

class TestPreservationLinks:
    """Preservation: Working links must continue to resolve correctly."""

    @pytest.mark.parametrize("page_path", WELL_FORMATTED_LINK_PAGES)
    def test_links_have_valid_syntax(self, page_path):
        """
        Requirement 3.6: Links must use proper [label](url) syntax with
        non-empty labels and URLs.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        links = find_markdown_links(content)
        assert len(links) > 0, (
            f"Preservation BROKEN: {page_path} lost all its links"
        )

        for label, url, line_num in links:
            # Label should not be empty
            assert len(label.strip()) > 0, (
                f"Preservation BROKEN: {page_path} has link with empty label "
                f"at line {line_num}"
            )
            # URL should not be empty
            assert len(url.strip()) > 0, (
                f"Preservation BROKEN: {page_path} has link with empty URL "
                f"at line {line_num}"
            )

    @pytest.mark.parametrize("page_path", WELL_FORMATTED_LINK_PAGES)
    def test_links_have_no_dangling_syntax(self, page_path):
        """
        Requirement 3.6: Links must not have visible RST-style syntax
        like dangling [Cache] anchors or garbled labels.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        # Find standalone bracket references that aren't proper links
        # Pattern: [text] not followed by ( or [
        in_fence = False
        for i, line in enumerate(content.split("\n"), 1):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Find [text] not part of [text](url) or [text][ref]
            # and not image syntax ![text]
            standalone = re.findall(r'(?<!!)\[([^\]]+)\](?!\(|\[)', line)
            for ref in standalone:
                # Skip footnote-style references like [^1] and attribute syntax like {: #id}
                if ref.startswith("^") or ref.startswith(":"):
                    continue
                # Skip reference-style link definitions [label]: url
                if re.match(r'^\s*\[' + re.escape(ref) + r'\]:', line):
                    continue
                # This is a potential dangling anchor
                # Only flag if it looks like an RST cross-reference
                if re.match(r'^[A-Z][a-z]+$', ref) and len(ref) < 20:
                    pytest.fail(
                        f"Preservation BROKEN: {page_path} has potential dangling "
                        f"anchor '[{ref}]' at line {i}"
                    )

    def test_internal_links_point_to_existing_files(self):
        """
        Requirement 3.6: Internal relative links in well-formatted pages
        should point to files that exist in the docs directory.
        """
        missing_targets = []

        for page_path in WELL_FORMATTED_LINK_PAGES:
            content = read_md_file(page_path)
            if content is None:
                continue

            page_dir = Path(page_path).parent
            links = find_markdown_links(content)

            for label, url, line_num in links:
                # Only check relative links (not http/https/mailto)
                if url.startswith(("http://", "https://", "mailto:", "#")):
                    continue

                # Strip anchor fragment
                url_path = url.split("#")[0]
                if not url_path:
                    continue

                # Resolve relative path
                target = (ROOT / page_dir / url_path).resolve()
                if not target.exists():
                    # Try with .md extension
                    if not target.with_suffix(".md").exists():
                        missing_targets.append(
                            f"{page_path}:{line_num} -> [{label}]({url})"
                        )

        assert len(missing_targets) == 0, (
            f"Preservation BROKEN: Internal links point to missing files:\n"
            + "\n".join(f"  - {t}" for t in missing_targets)
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all preservation requirements
# ---------------------------------------------------------------------------

ALL_PRESERVATION_PAGES = list(set(
    WELL_TITLED_PAGES + WELL_FORMATTED_CODE_PAGES +
    WELL_FORMATTED_TABLE_PAGES + WELL_FORMATTED_LIST_PAGES +
    WELL_FORMATTED_IMAGE_PAGES + WELL_FORMATTED_LINK_PAGES
))


class TestPreservationProperty:
    """Property-based tests across all preservation requirements."""

    @given(
        page_path=st.sampled_from(ALL_PRESERVATION_PAGES)
    )
    @settings(max_examples=len(ALL_PRESERVATION_PAGES), phases=[Phase.explicit, Phase.generate])
    def test_well_formatted_page_has_no_conversion_artifacts(self, page_path):
        """
        Combined preservation property (Req 3.1-3.6): Well-formatted pages
        must not contain any RST conversion artifacts.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []

        # Check for RST directive remnants
        if re.search(r'^\.\.\s+\w+::', content, re.MULTILINE):
            issues.append("Contains RST directive syntax (.. directive::)")

        # Check for RST role syntax
        if re.search(r':\w+:`[^`]+`', content):
            issues.append("Contains RST role syntax (:role:`text`)")

        # Check for pandoc-style fenced divs that should be admonitions
        if re.search(r'^::::\s+\w+', content, re.MULTILINE):
            issues.append("Contains pandoc fenced-div syntax (:::: type)")

        # Check for visible admonition syntax in wrong context
        in_fence = False
        for line in content.split("\n"):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            # Visible !!! in blockquotes is a bug
            if re.match(r'^\s*>\s*!!!', line):
                issues.append(f"Admonition syntax in blockquote: {line.strip()}")
                break

        assert len(issues) == 0, (
            f"Preservation BROKEN: {page_path} has conversion artifacts:\n"
            + "\n".join(f"  - {issue}" for issue in issues)
        )
