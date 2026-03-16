#!/usr/bin/env python3
"""
Bug Condition Exploration Test: Navigation and Title Rendering Bugs

**Property 1: Bug Condition** - Navigation and Title Issues
**CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
**DO NOT attempt to fix the test or the code when it fails.**

Validates: Requirements 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4

Tests concrete failing cases from Andrea's review feedback:
- Pages with "path/index" titles render with proper human-readable titles (Req 1.2, 2.2)
- Page titles in content match navigation tree entries (Req 1.1, 2.1)
- "Table of contents" is labeled as "Page contents" (Req 1.3, 2.3)
- "Installation" section has clear hierarchy with "Section contents" label (Req 1.4, 2.4)
"""

import os
import re
import yaml
import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, Phase

# Project root
ROOT = Path(__file__).resolve().parent.parent
MKDOCS_YML = ROOT / "mkdocs.yml"
DOCS_DIR = ROOT / "doc"


def load_mkdocs_config():
    """Load and return the mkdocs.yml configuration."""
    with open(MKDOCS_YML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_nav_entries(nav, parent_label=None):
    """
    Recursively extract (nav_label, file_path) pairs from the mkdocs nav structure.

    MkDocs nav entries can be:
      - A string (bare path, label derived from page title)
      - A dict with {label: path} or {label: [children]}
    """
    entries = []
    if isinstance(nav, list):
        for item in nav:
            if isinstance(item, str):
                entries.append((parent_label, item))
            elif isinstance(item, dict):
                for label, value in item.items():
                    if isinstance(value, str):
                        entries.append((label, value))
                    elif isinstance(value, list):
                        entries.extend(extract_nav_entries(value, parent_label=label))
    return entries


def read_md_file(rel_path):
    """Read a markdown file and return its content."""
    full_path = DOCS_DIR / rel_path if not (ROOT / rel_path).exists() else ROOT / rel_path
    if not full_path.exists():
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


def get_link_labels_from_content(content):
    """Extract markdown link labels from content, e.g. [label](url)."""
    if content is None:
        return []
    return re.findall(r"\[([^\]]+)\]\([^)]+\)", content)


# ---------------------------------------------------------------------------
# Requirement 1.2 / 2.2: Pages must NOT have "path/index" as link labels
# ---------------------------------------------------------------------------

# Concrete pages from Andrea's feedback where path/index appears as link text
PATH_INDEX_PAGES = [
    "doc/en/user/services/index.md",  # Shows "wms/index", "wfs/index" etc.
]


class TestPathIndexTitles:
    """Test that pages don't use 'path/index' patterns as link labels or titles."""

    def test_services_index_no_path_index_labels(self):
        """
        Requirement 1.2: services/index.md should NOT have link labels like
        'wms/index', 'wfs/index' etc. They should be human-readable names.

        Counterexample from Andrea: services page shows 'path/index' as title.
        """
        content = read_md_file("doc/en/user/services/index.md")
        assert content is not None, "services/index.md not found"

        labels = get_link_labels_from_content(content)
        path_index_labels = [l for l in labels if re.search(r"\w+/index$", l)]

        assert len(path_index_labels) == 0, (
            f"Bug 1.2 confirmed: services/index.md has path/index link labels: "
            f"{path_index_labels}. Expected human-readable names like "
            f"'Web Map Service (WMS)', 'Web Feature Service (WFS)', etc."
        )

    @given(
        page_path=st.sampled_from([
            "doc/en/user/services/index.md",
            "doc/en/user/data/index.md",
            "doc/en/user/styling/index.md",
            "doc/en/user/index.md",
            "doc/en/user/gettingstarted/index.md",
        ])
    )
    @settings(max_examples=5, phases=[Phase.explicit, Phase.generate])
    def test_index_pages_no_path_index_link_labels(self, page_path):
        """
        Requirement 1.2 (PBT): No index page should use 'path/index' as link text.
        Human-readable labels are required.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        labels = get_link_labels_from_content(content)
        path_index_labels = [l for l in labels if re.search(r"\w+/index$", l)]

        assert len(path_index_labels) == 0, (
            f"Bug 1.2: {page_path} has path/index link labels: {path_index_labels}"
        )


# ---------------------------------------------------------------------------
# Requirement 1.1 / 2.1: Page title in content must match navigation tree entry
# ---------------------------------------------------------------------------

# Concrete mismatches from Andrea's feedback
KNOWN_TITLE_NAV_MISMATCHES = {
    # nav_label -> file_path (relative to doc/)
    # Andrea reported: "Data settings" in page but "webadmin" in nav tree
    "en/user/data/webadmin/index.md": {
        "nav_parent": "Webadmin",
        "page_title": "Data settings",
    },
}


class TestTitleNavMismatch:
    """Test that page titles match their navigation tree entries."""

    def test_data_webadmin_title_matches_nav(self):
        """
        Requirement 1.1: data/webadmin/index.md page title 'Data settings'
        should match its nav entry. Andrea reported the nav shows 'webadmin'
        while the page shows 'Data settings'.
        """
        config = load_mkdocs_config()
        nav_entries = extract_nav_entries(config.get("nav", []))

        # Find the nav label for data/webadmin/index.md
        nav_label = None
        for label, path in nav_entries:
            if path == "en/user/data/webadmin/index.md":
                nav_label = label
                break

        content = read_md_file("doc/en/user/data/webadmin/index.md")
        page_title = get_md_title(content)

        assert nav_label is not None, "data/webadmin/index.md not found in nav"
        assert page_title is not None, "No H1 title in data/webadmin/index.md"

        # The nav label should meaningfully match the page title
        # "Webadmin" (nav) vs "Data settings" (page) is a mismatch
        assert nav_label.lower().strip() == page_title.lower().strip() or \
               page_title.lower() in nav_label.lower() or \
               nav_label.lower() in page_title.lower(), (
            f"Bug 1.1 confirmed: Nav label '{nav_label}' does not match "
            f"page title '{page_title}' for data/webadmin/index.md"
        )

    def test_garbled_link_labels_in_index_pages(self):
        """
        Requirement 1.1: Link labels in index pages should be clean
        human-readable text, not garbled concatenations like
        'DataApp SchemaIndex' or 'InstallationWin Binary'.
        """
        garbled_pattern = re.compile(
            r"[A-Z][a-z]+[A-Z][a-z]+"  # CamelCase-like concatenation without space
        )

        # Also check for known garbled prefix patterns with spaces
        prefix_garbled_pattern = re.compile(
            r"^(?:Data|Installation|Services|Styling)[A-Z]\w+"  # e.g. DataApp, InstallationWin, ServicesWfs
        )

        issues = []
        pages_to_check = [
            "doc/en/user/data/index.md",
            "doc/en/user/installation/index.md",
            "doc/en/user/services/wfs/index.md",
        ]

        for page_path in pages_to_check:
            content = read_md_file(page_path)
            if content is None:
                continue
            labels = get_link_labels_from_content(content)
            for label in labels:
                # Check CamelCase without space
                if " " not in label and garbled_pattern.search(label):
                    issues.append((page_path, label))
                # Check prefix concatenation (with or without space after)
                elif prefix_garbled_pattern.match(label):
                    issues.append((page_path, label))

        assert len(issues) == 0, (
            f"Bug 1.1 confirmed: Garbled link labels found:\n"
            + "\n".join(f"  - {path}: '{label}'" for path, label in issues)
        )

    def test_nav_labels_match_page_titles_for_sections(self):
        """
        Requirement 1.1 (PBT): Navigation section labels should match or
        closely relate to the page titles, not be bare directory names
        like 'Webadmin', 'Wms', 'Sld', 'Gettingstarted'.
        """
        config = load_mkdocs_config()
        nav_entries = extract_nav_entries(config.get("nav", []))

        mismatches = []
        for nav_label, nav_path in nav_entries:
            if nav_label is None or not nav_path.endswith("index.md"):
                continue

            content = read_md_file(f"doc/{nav_path}")
            page_title = get_md_title(content)
            if page_title is None:
                continue

            # Check if nav label is a bare directory name (single capitalized word)
            is_bare_dirname = (
                re.match(r"^[A-Z][a-z]+$", nav_label)
                and len(nav_label) < 15
            )
            title_is_more_descriptive = len(page_title) > len(nav_label) + 5

            if is_bare_dirname and title_is_more_descriptive:
                mismatches.append(
                    f"Nav '{nav_label}' vs page title '{page_title}' ({nav_path})"
                )

        assert len(mismatches) == 0, (
            f"Bug 1.1: Nav labels are bare directory names instead of descriptive titles:\n"
            + "\n".join(f"  - {m}" for m in mismatches)
        )


# ---------------------------------------------------------------------------
# Requirement 1.3 / 2.3: TOC should be labeled "Page contents" not "Table of contents"
# ---------------------------------------------------------------------------

class TestTocLabeling:
    """Test that TOC is labeled 'Page contents' not 'Table of contents'."""

    def test_sphinx_layout_no_table_of_contents_label(self):
        """
        Requirement 1.3: The old Sphinx layout.html templates should not
        use 'Table Of Contents' label. Andrea reported this causes confusion.
        """
        layout_files = [
            "doc/themes/geoserver/layout.html",
            "doc/en/themes/geoserver/layout.html",
        ]

        issues = []
        for layout_path in layout_files:
            full_path = ROOT / layout_path
            if full_path.exists():
                content = full_path.read_text(encoding="utf-8")
                if "Table Of Contents" in content or "Table of Contents" in content:
                    issues.append(layout_path)

        assert len(issues) == 0, (
            f"Bug 1.3 confirmed: 'Table Of Contents' label found in layout templates: "
            f"{issues}. Should be 'Page contents' per Andrea's feedback."
        )

    def test_mkdocs_theme_toc_label_is_page_contents(self):
        """
        Requirement 1.3: The MkDocs Material theme should display 'Page Contents'
        for the right-sidebar TOC, not 'Table of contents'.

        The CSS override exists but the underlying template label may still
        show 'Table of contents' in some contexts.
        """
        extra_css = ROOT / "doc/themes/geoserver/stylesheets/extra.css"
        assert extra_css.exists(), "extra.css not found"

        content = extra_css.read_text(encoding="utf-8")

        # Verify the CSS override is present
        assert 'content: "Page Contents"' in content, (
            "Bug 1.3: extra.css does not contain 'Page Contents' CSS override"
        )

        # But also check that old Sphinx templates don't conflict
        layout = ROOT / "doc/themes/geoserver/layout.html"
        if layout.exists():
            layout_content = layout.read_text(encoding="utf-8")
            assert "Table Of Contents" not in layout_content, (
                "Bug 1.3: layout.html still contains 'Table Of Contents' which "
                "may conflict with the CSS 'Page Contents' override"
            )


# ---------------------------------------------------------------------------
# Requirement 1.4 / 2.4: Installation section hierarchy with "Section contents"
# ---------------------------------------------------------------------------

class TestInstallationHierarchy:
    """Test that Installation section has clear hierarchy."""

    def test_installation_index_has_section_contents_label(self):
        """
        Requirement 1.4: Installation section should have a 'Section contents'
        label for clear hierarchy. Andrea reported the hierarchy is unclear
        due to inconsistent indentation and bolding.
        """
        content = read_md_file("doc/en/user/installation/index.md")
        assert content is not None, "installation/index.md not found"

        # Check for "Section contents" label
        has_section_contents = (
            "Section contents" in content
            or "section contents" in content.lower()
        )

        assert has_section_contents, (
            "Bug 1.4 confirmed: installation/index.md lacks a 'Section contents' "
            "label. Andrea reported the hierarchy is unclear — 'Installation' is bold "
            "but less indented than subtitles, making importance unclear."
        )

    def test_installation_links_have_clean_labels(self):
        """
        Requirement 1.4: Installation page links should have clean labels,
        not concatenated names like 'InstallationWin Binary'.
        """
        content = read_md_file("doc/en/user/installation/index.md")
        assert content is not None

        labels = get_link_labels_from_content(content)
        bad_labels = [
            l for l in labels
            if l.startswith("Installation") and len(l) > len("Installation") + 1
            and not l.startswith("Installation ")  # Allow "Installation guide" etc.
        ]

        assert len(bad_labels) == 0, (
            f"Bug 1.4 confirmed: installation/index.md has concatenated link labels: "
            f"{bad_labels}. Expected clean labels like 'Windows Binary', 'Windows Installer'."
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all navigation/title requirements
# ---------------------------------------------------------------------------

class TestNavigationTitleProperty:
    """Property-based tests across navigation and title requirements."""

    @given(
        section_index=st.sampled_from([
            "doc/en/user/services/index.md",
            "doc/en/user/data/index.md",
            "doc/en/user/installation/index.md",
            "doc/en/user/styling/index.md",
            "doc/en/user/gettingstarted/index.md",
            "doc/en/user/webadmin/index.md",
            "doc/en/user/index.md",
        ])
    )
    @settings(max_examples=7, phases=[Phase.explicit, Phase.generate])
    def test_section_index_links_are_human_readable(self, section_index):
        """
        Combined property (Req 1.1, 1.2): All link labels in section index
        pages must be human-readable — no path/index patterns, no garbled
        concatenations, no bare directory names.
        """
        content = read_md_file(section_index)
        if content is None:
            pytest.skip(f"{section_index} not found")

        labels = get_link_labels_from_content(content)
        issues = []

        for label in labels:
            # Check for path/index pattern
            if re.search(r"\w+/index$", label):
                issues.append(f"path/index pattern: '{label}'")

            # Check for garbled concatenation (CamelCase without spaces)
            if re.match(r"^[A-Z][a-z]+[A-Z][a-z]+\w*$", label) and " " not in label:
                issues.append(f"garbled concatenation: '{label}'")

            # Check for prefix concatenation like "InstallationWin"
            if re.match(r"^[A-Z][a-z]+[A-Z][A-Z]", label):
                issues.append(f"prefix concatenation: '{label}'")

            # Check for "ServicesWfs" style
            if re.match(r"^Services[A-Z]", label) or re.match(r"^Data[A-Z]", label):
                issues.append(f"section prefix concatenation: '{label}'")

        assert len(issues) == 0, (
            f"Bugs 1.1/1.2 in {section_index}:\n"
            + "\n".join(f"  - {issue}" for issue in issues)
        )
