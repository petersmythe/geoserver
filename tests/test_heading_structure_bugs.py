#!/usr/bin/env python3
"""
Bug Condition Exploration Test: Heading and Structure Rendering Bugs

**Property 1: Bug Condition** - Heading and Structure Issues
**CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
**DO NOT attempt to fix the test or the code when it fails.**

**Validates: Requirements 1.29, 1.30, 2.29, 2.30**

Tests concrete failing cases from Andrea's review feedback:
- Low-level subsection headings render with correct hierarchy (Req 1.29, 2.29)
- Quoted specification text formats as blockquotes, not code (Req 1.30, 2.30)
"""

import re
import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, Phase

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en" / "user"


def read_md_file(rel_path):
    full_path = ROOT / rel_path
    if not full_path.exists():
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def find_bold_as_headings(content):
    """Find bold text on its own line that should be proper headings."""
    results = []
    lines = content.split("\n")
    in_fence = False
    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if re.match(r'^\*\*[^*]+\*\*$', stripped) and len(stripped) < 80:
            prev_blank = (i == 0) or (lines[i - 1].strip() == "")
            next_blank = (i == len(lines) - 1) or (lines[i + 1].strip() == "")
            if prev_blank and next_blank:
                results.append((stripped, i + 1))
    return results


def find_indented_prose_as_code(content):
    """Find 4-space indented prose that renders as code blocks."""
    results = []
    lines = content.split("\n")
    in_fence = False
    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not re.match(r'^    [A-Z]', line):
            continue
        text = line.strip()
        if len(text) < 40:
            continue
        if not ('. ' in text or ', ' in text):
            continue
        if re.search(r'[{}()<>=;]', text):
            continue
        prev_idx = i - 1
        while prev_idx >= 0 and lines[prev_idx].strip() == "":
            prev_idx -= 1
        if prev_idx >= 0:
            prev = lines[prev_idx].strip()
            if prev.startswith("!!!") or prev.startswith("???"):
                continue
            if lines[prev_idx].startswith("    "):
                pp = prev_idx - 1
                while pp >= 0 and lines[pp].strip() == "":
                    pp -= 1
                if pp >= 0 and (
                    lines[pp].strip().startswith("!!!")
                    or lines[pp].strip().startswith("???")
                ):
                    continue
        results.append((text[:80], i + 1))
    return results


# ---------------------------------------------------------------------------
# Requirement 1.29 / 2.29: Low-level subsection headings must render with
# correct heading levels in the visual hierarchy
# ---------------------------------------------------------------------------

BOLD_AS_HEADING_PAGES = [
    "doc/en/user/community/pmtiles-store/usage.md",
    "doc/en/user/rest/api/authenticationfilters.md",
    "doc/en/user/extensions/mapml/installation.md",
    "doc/en/user/rest/styles.md",
    "doc/en/user/tutorials/freemarker.md",
    "doc/en/user/rest/api/usergroupservices.md",
    "doc/en/user/rest/authenticationproviders.md",
    "doc/en/user/styling/sld/reference/filters.md",
    "doc/en/user/rest/imagemosaic.md",
    "doc/en/user/rest/security.md",
    "doc/en/user/rest/urlchecks.md",
]


class TestBoldTextAsHeadings:
    """Test that bold text on its own line is converted to proper headings (Req 1.29)."""

    def test_pmtiles_usage_bold_headings(self):
        """
        Requirement 1.29: pmtiles-store/usage.md has 22 instances of bold
        text on its own line that should be proper Markdown headings.
        Counterexample: "**Retrieve manifests...**" should be "### Retrieve manifests..."
        """
        content = read_md_file("doc/en/user/community/pmtiles-store/usage.md")
        assert content is not None, "pmtiles-store/usage.md not found"
        bold_headings = find_bold_as_headings(content)
        assert len(bold_headings) == 0, (
            f"Bug 1.29 confirmed: pmtiles-store/usage.md has "
            f"{len(bold_headings)} bold text line(s) that should be "
            f"proper headings:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in bold_headings[:10]
            )
            + "\n  These should use ### or #### heading syntax"
        )

    def test_authenticationfilters_bold_headings(self):
        """
        Requirement 1.29: rest/api/authenticationfilters.md has 19 instances
        of bold text used as subsection headings.
        """
        content = read_md_file("doc/en/user/rest/api/authenticationfilters.md")
        assert content is not None, "authenticationfilters.md not found"
        bold_headings = find_bold_as_headings(content)
        assert len(bold_headings) == 0, (
            f"Bug 1.29 confirmed: authenticationfilters.md has "
            f"{len(bold_headings)} bold text line(s) that should be "
            f"proper headings:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in bold_headings[:10]
            )
        )

    def test_mapml_installation_bold_headings(self):
        """
        Requirement 1.29: extensions/mapml/installation.md has 10 instances
        of bold text used as subsection headings.
        """
        content = read_md_file("doc/en/user/extensions/mapml/installation.md")
        assert content is not None, "mapml/installation.md not found"
        bold_headings = find_bold_as_headings(content)
        assert len(bold_headings) == 0, (
            f"Bug 1.29 confirmed: mapml/installation.md has "
            f"{len(bold_headings)} bold text line(s) that should be "
            f"proper headings:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in bold_headings[:10]
            )
        )

    def test_sld_filters_bold_headings(self):
        """
        Requirement 1.29: styling/sld/reference/filters.md has 7 instances
        of bold text used as subsection headings.
        """
        content = read_md_file("doc/en/user/styling/sld/reference/filters.md")
        assert content is not None, "filters.md not found"
        bold_headings = find_bold_as_headings(content)
        assert len(bold_headings) == 0, (
            f"Bug 1.29 confirmed: filters.md has "
            f"{len(bold_headings)} bold text line(s) that should be "
            f"proper headings:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in bold_headings[:10]
            )
        )

    @given(page_path=st.sampled_from(BOLD_AS_HEADING_PAGES))
    @settings(
        max_examples=len(BOLD_AS_HEADING_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_bold_text_as_headings(self, page_path):
        """
        Requirement 1.29 (PBT): No page should have bold text on its own
        line that should be a proper Markdown heading.
        **Validates: Requirements 1.29, 2.29**
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")
        bold_headings = find_bold_as_headings(content)
        assert len(bold_headings) == 0, (
            f"Bug 1.29: {page_path} has {len(bold_headings)} "
            f"bold text line(s) that should be proper headings:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in bold_headings[:10]
            )
        )


# ---------------------------------------------------------------------------
# Requirement 1.30 / 2.30: Quoted specification text must format as styled
# blockquotes, not code blocks
# ---------------------------------------------------------------------------

INDENTED_PROSE_PAGES = [
    "doc/en/user/configuration/logging.md",
    "doc/en/user/datadirectory/setting.md",
    "doc/en/user/installation/docker.md",
    "doc/en/user/installation/linux.md",
    "doc/en/user/installation/war.md",
    "doc/en/user/installation/win_binary.md",
    "doc/en/user/installation/win_installer.md",
    "doc/en/user/production/container.md",
    "doc/en/user/production/misc.md",
    "doc/en/user/production/troubleshooting.md",
]


class TestQuotedSpecTextAsCode:
    """Test that quoted spec text formats as blockquotes, not code (Req 1.30)."""

    def test_war_installation_indented_prose(self):
        """
        Requirement 1.30: installation/war.md has indented prose text that
        renders as code blocks due to 4-space indentation.
        Counterexample: Prose text indented 4 spaces renders as <pre><code>.
        """
        content = read_md_file("doc/en/user/installation/war.md")
        assert content is not None, "war.md not found"
        prose_as_code = find_indented_prose_as_code(content)
        assert len(prose_as_code) == 0, (
            f"Bug 1.30 confirmed: installation/war.md has "
            f"{len(prose_as_code)} indented prose line(s) that render "
            f"as code blocks:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in prose_as_code[:10]
            )
            + "\n  These should use > blockquote syntax or be unindented"
        )

    def test_logging_config_indented_prose(self):
        """
        Requirement 1.30: configuration/logging.md has indented prose text
        that renders as code blocks.
        """
        content = read_md_file("doc/en/user/configuration/logging.md")
        assert content is not None, "logging.md not found"
        prose_as_code = find_indented_prose_as_code(content)
        assert len(prose_as_code) == 0, (
            f"Bug 1.30 confirmed: logging.md has "
            f"{len(prose_as_code)} indented prose line(s) that render "
            f"as code blocks:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in prose_as_code[:10]
            )
        )

    def test_troubleshooting_indented_prose(self):
        """
        Requirement 1.30: production/troubleshooting.md has indented text
        that renders as code blocks.
        """
        content = read_md_file("doc/en/user/production/troubleshooting.md")
        assert content is not None, "troubleshooting.md not found"
        prose_as_code = find_indented_prose_as_code(content)
        assert len(prose_as_code) == 0, (
            f"Bug 1.30 confirmed: troubleshooting.md has "
            f"{len(prose_as_code)} indented prose line(s) that render "
            f"as code blocks:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in prose_as_code[:10]
            )
        )

    def test_docker_installation_indented_prose(self):
        """
        Requirement 1.30: installation/docker.md has indented prose like
        "If you see the GeoServer Welcome page..." that renders as code.
        """
        content = read_md_file("doc/en/user/installation/docker.md")
        assert content is not None, "docker.md not found"
        prose_as_code = find_indented_prose_as_code(content)
        assert len(prose_as_code) == 0, (
            f"Bug 1.30 confirmed: docker.md has "
            f"{len(prose_as_code)} indented prose line(s) that render "
            f"as code blocks:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in prose_as_code[:10]
            )
        )

    @given(page_path=st.sampled_from(INDENTED_PROSE_PAGES))
    @settings(
        max_examples=len(INDENTED_PROSE_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_indented_prose_as_code(self, page_path):
        """
        Requirement 1.30 (PBT): No page should have indented prose text
        that renders as code blocks instead of blockquotes or normal text.
        **Validates: Requirements 1.30, 2.30**
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")
        prose_as_code = find_indented_prose_as_code(content)
        assert len(prose_as_code) == 0, (
            f"Bug 1.30: {page_path} has {len(prose_as_code)} "
            f"indented prose line(s) rendering as code blocks:\n"
            + "\n".join(
                f"  - Line {ln}: {text}"
                for text, ln in prose_as_code[:10]
            )
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all heading/structure requirements
# ---------------------------------------------------------------------------

ALL_HEADING_STRUCTURE_PAGES = list(set(
    BOLD_AS_HEADING_PAGES + INDENTED_PROSE_PAGES
))


class TestHeadingStructureProperty:
    """Property-based tests across all heading/structure requirements."""

    @given(page_path=st.sampled_from(ALL_HEADING_STRUCTURE_PAGES))
    @settings(
        max_examples=min(len(ALL_HEADING_STRUCTURE_PAGES), 20),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_heading_structure_issues(self, page_path):
        """
        Combined property (Req 1.29, 1.30): Pages should not have any
        heading/structure rendering issues.
        **Validates: Requirements 1.29, 1.30, 2.29, 2.30**
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")
        issues = []
        bold_headings = find_bold_as_headings(content)
        for text, ln in bold_headings:
            issues.append(
                f"Bold-as-heading at line {ln}: {text[:60]} (Req 1.29)"
            )
        prose_as_code = find_indented_prose_as_code(content)
        for text, ln in prose_as_code:
            issues.append(
                f"Indented prose as code at line {ln}: {text[:60]} (Req 1.30)"
            )
        assert len(issues) == 0, (
            f"Heading/structure issues in {page_path}:\n"
            + "\n".join(f"  - {issue}" for issue in issues[:15])
            + (f"\n  ... and {len(issues) - 15} more"
               if len(issues) > 15 else "")
        )
