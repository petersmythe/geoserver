#!/usr/bin/env python3
"""
Bug Condition Exploration Test: Admonition Block Rendering Bugs

**Property 1: Bug Condition** - Admonition and Note Issues
**CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
**DO NOT attempt to fix the test or the code when it fails.**

Validates: Requirements 1.14, 1.15, 1.16, 2.14, 2.15, 2.16

Tests concrete failing cases from Andrea's review feedback:
- RST note/warning blocks render as styled admonitions, not blockquotes (Req 1.14, 2.14)
- Admonition blocks don't show visible syntax markers like "!!! warning" (Req 1.15, 2.15)
- Admonitions in tables don't break table structure (Req 1.16, 2.16)
"""

import re
import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, Phase

# Project root
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en" / "user"


def read_md_file(rel_path):
    """Read a markdown file and return its content."""
    full_path = ROOT / rel_path
    if not full_path.exists():
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def find_blockquoted_admonitions(content):
    """
    Find RST-style admonition blocks that were converted to blockquotes
    instead of proper MkDocs admonition syntax.

    These appear as blockquoted content with :::: note/warning markers
    and ::: title sub-markers — raw pandoc fenced-div syntax that renders
    as visible markup instead of styled admonition boxes.

    Returns list of (admonition_type, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Pattern: blockquoted fenced-div admonition syntax
        # e.g. "> :::: warning" or ">     :::: warning"
        m = re.match(r'^>\s*:{3,4}\s+(\w+)', line)
        if m:
            results.append((m.group(1), i + 1))

    return results


def find_admonitions_with_blank_line(content):
    """
    Find MkDocs admonitions that have a blank line between the !!! marker
    and the indented content. While MkDocs Material may tolerate this in
    some cases, it's a conversion artifact from RST that can cause rendering
    issues — the blank line can cause the content to be treated as a
    separate paragraph rather than admonition body.

    Returns list of (admonition_type, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Match !!! type (with optional title)
        m = re.match(r'^(\s*)!!!\s+(\w+)', line)
        if m:
            indent = m.group(1)
            adm_type = m.group(2)
            # Check if next line is blank and line after is indented content
            if i + 1 < len(lines) and lines[i + 1].strip() == "":
                if i + 2 < len(lines) and re.match(
                    r'^' + re.escape(indent) + r'    \S', lines[i + 2]
                ):
                    results.append((adm_type, i + 1))

    return results


def find_admonitions_breaking_tables(content):
    """
    Find admonitions that appear immediately after a table row, breaking
    the table structure. In Markdown, a table must be a contiguous block
    of | rows. An !!! admonition right after the last table row (with no
    blank line, or even with one) that was meant to be part of the table
    context breaks the visual flow and may have been inside a table cell
    in the original RST.

    Returns list of (admonition_type, table_context, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False
    prev_was_table_row = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            prev_was_table_row = False
            continue
        if in_fence:
            prev_was_table_row = False
            continue

        is_table_row = bool(re.match(r'^\|.*\|', line))

        # Check if this is an admonition right after a table
        if not is_table_row and prev_was_table_row:
            # Allow one blank line between table and admonition
            if line.strip() == "":
                # Check next non-blank line
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].strip() != "":
                        m = re.match(r'^!!!\s+(\w+)', lines[j])
                        if m:
                            # Get the last table row for context
                            table_row = lines[i - 1].strip()[:80]
                            results.append((m.group(1), table_row, j + 1))
                        break
            else:
                m = re.match(r'^!!!\s+(\w+)', line)
                if m:
                    table_row = lines[i - 1].strip()[:80]
                    results.append((m.group(1), table_row, i + 1))

        prev_was_table_row = is_table_row

    return results


def find_visible_admonition_syntax_in_blockquotes(content):
    """
    Find admonition syntax that is visible as raw markup inside blockquotes.
    This happens when the converter wraps RST admonitions in blockquote
    syntax, making the ::: / :::: fenced-div markers visible to readers.

    Returns list of (syntax_fragment, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Visible fenced-div syntax in blockquotes
        if re.match(r'^>\s*:{3,4}\s*$', line):
            results.append((line.strip(), i + 1))
        elif re.match(r'^>\s*:{3,4}\s+\w+', line):
            results.append((line.strip(), i + 1))
        # Visible ::: title markers
        elif re.match(r'^>\s*:::\s+title\s*$', line):
            results.append((line.strip(), i + 1))

    return results


# ---------------------------------------------------------------------------
# Requirement 1.14 / 2.14: RST note/warning blocks must render as styled
# admonitions, not blockquotes
# ---------------------------------------------------------------------------

# Pages where RST admonitions were converted to blockquotes with visible
# fenced-div syntax (:::: note, ::: title, etc.)
BLOCKQUOTED_ADMONITION_PAGES = [
    "doc/en/user/gettingstarted/preflight-quickstart/index.md",
    "doc/en/user/security/tutorials/httpheaderproxy/index.md",
    "doc/en/user/community/wps-longitudinal-profile/index.md",
    "doc/en/user/community/wps-openai/index.md",
    "doc/en/user/community/remote-wps/install_python.md",
    "doc/en/user/community/graticules/index.md",
    "doc/en/user/community/gwc-azure-blob/index.md",
    "doc/en/user/community/geopkg/installing.md",
    "doc/en/user/community/gwc-gcs-blob/index.md",
    "doc/en/user/community/colormap/index.md",
]


class TestAdmonitionsAsBlockquotes:
    """Test that RST admonitions render as styled admonition boxes, not blockquotes."""

    def test_preflight_quickstart_note_not_blockquoted(self):
        """
        Requirement 1.14: preflight-quickstart/index.md has a note block
        rendered as a blockquote with visible :::: note / ::: title syntax.

        The "What is the keystore password" note should be a styled admonition
        box, not a blockquote with raw fenced-div markers.
        """
        content = read_md_file(
            "doc/en/user/gettingstarted/preflight-quickstart/index.md"
        )
        assert content is not None, "preflight-quickstart/index.md not found"

        bq_admonitions = find_blockquoted_admonitions(content)

        assert len(bq_admonitions) == 0, (
            f"Bug 1.14 confirmed: preflight-quickstart/index.md has "
            f"{len(bq_admonitions)} admonition(s) rendered as blockquotes "
            f"with visible fenced-div syntax:\n"
            + "\n".join(
                f"  - Line {line}: ':::: {atype}' in blockquote"
                for atype, line in bq_admonitions
            )
            + "\n  Should be: '!!! note' with indented content (MkDocs admonition)"
        )

    def test_httpheaderproxy_warning_not_blockquoted(self):
        """
        Requirement 1.14: httpheaderproxy/index.md has a warning block
        rendered as a blockquote with visible :::: warning / ::: title syntax.

        The security warning about header attribute names should be a styled
        warning admonition, not a blockquote.
        """
        content = read_md_file(
            "doc/en/user/security/tutorials/httpheaderproxy/index.md"
        )
        assert content is not None, "httpheaderproxy/index.md not found"

        bq_admonitions = find_blockquoted_admonitions(content)

        assert len(bq_admonitions) == 0, (
            f"Bug 1.14 confirmed: httpheaderproxy/index.md has "
            f"{len(bq_admonitions)} admonition(s) rendered as blockquotes:\n"
            + "\n".join(
                f"  - Line {line}: ':::: {atype}' in blockquote"
                for atype, line in bq_admonitions
            )
        )

    @given(
        page_path=st.sampled_from(BLOCKQUOTED_ADMONITION_PAGES)
    )
    @settings(
        max_examples=len(BLOCKQUOTED_ADMONITION_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_blockquoted_admonitions(self, page_path):
        """
        Requirement 1.14 (PBT): No page should have RST admonitions
        rendered as blockquotes with visible fenced-div syntax.
        All admonitions should use MkDocs !!! syntax.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        bq_admonitions = find_blockquoted_admonitions(content)

        assert len(bq_admonitions) == 0, (
            f"Bug 1.14: {page_path} has {len(bq_admonitions)} admonition(s) "
            f"rendered as blockquotes instead of MkDocs admonitions:\n"
            + "\n".join(
                f"  - Line {line}: ':::: {atype}'"
                for atype, line in bq_admonitions
            )
        )


# ---------------------------------------------------------------------------
# Requirement 1.15 / 2.15: Admonition blocks must not show visible syntax
# markers like "!!! warning" or fenced-div markers
# ---------------------------------------------------------------------------

# Pages where admonitions have blank lines between !!! marker and content,
# which is a conversion artifact that can cause rendering issues
BLANK_LINE_ADMONITION_PAGES = [
    "doc/en/user/services/wfs/axis_order.md",
    "doc/en/user/services/wfs/vendor.md",
    "doc/en/user/services/wfs/reference.md",
    "doc/en/user/services/wfs/outputformats.md",
    "doc/en/user/services/wfs/basics.md",
    "doc/en/user/tutorials/wmsreflector.md",
    "doc/en/user/tutorials/tomcat-jndi/tomcat-jndi.md",
    "doc/en/user/tutorials/staticfiles.md",
    "doc/en/user/tutorials/imagemosaic_timeseries/imagemosaic_timeseries.md",
    "doc/en/user/tutorials/georss/georss.md",
    "doc/en/user/tutorials/GetFeatureInfo/html.md",
    "doc/en/user/tutorials/imagemosaic_footprint/imagemosaic_footprint.md",
]

# Pages where visible fenced-div syntax appears in blockquotes
VISIBLE_SYNTAX_PAGES = [
    "doc/en/user/gettingstarted/preflight-quickstart/index.md",
    "doc/en/user/security/tutorials/httpheaderproxy/index.md",
    "doc/en/user/community/wps-longitudinal-profile/index.md",
    "doc/en/user/community/wps-openai/index.md",
    "doc/en/user/community/remote-wps/install_python.md",
    "doc/en/user/community/graticules/index.md",
    "doc/en/user/community/gwc-azure-blob/index.md",
    "doc/en/user/community/geopkg/installing.md",
    "doc/en/user/community/gwc-gcs-blob/index.md",
    "doc/en/user/community/colormap/index.md",
]


class TestVisibleAdmonitionSyntax:
    """Test that admonition blocks don't show visible syntax markers."""

    def test_axis_order_admonitions_no_blank_line(self):
        """
        Requirement 1.15: wfs/axis_order.md has admonitions with a blank
        line between the !!! marker and the indented content. This is a
        conversion artifact from RST that can cause the admonition content
        to render incorrectly.

        Andrea specifically called out this page for admonition issues.
        """
        content = read_md_file("doc/en/user/services/wfs/axis_order.md")
        assert content is not None, "wfs/axis_order.md not found"

        blank_line_admonitions = find_admonitions_with_blank_line(content)

        assert len(blank_line_admonitions) == 0, (
            f"Bug 1.15 confirmed: wfs/axis_order.md has "
            f"{len(blank_line_admonitions)} admonition(s) with blank line "
            f"between !!! marker and content:\n"
            + "\n".join(
                f"  - Line {line}: '!!! {atype}' followed by blank line"
                for atype, line in blank_line_admonitions
            )
            + "\n  Content should immediately follow the !!! marker (no blank line)"
        )

    def test_preflight_quickstart_no_visible_fenced_div_syntax(self):
        """
        Requirement 1.15: preflight-quickstart/index.md has visible
        fenced-div syntax markers (:::: note, ::: title, ::::) inside
        blockquotes. These raw markers should not be visible to readers.
        """
        content = read_md_file(
            "doc/en/user/gettingstarted/preflight-quickstart/index.md"
        )
        assert content is not None, "preflight-quickstart/index.md not found"

        visible_syntax = find_visible_admonition_syntax_in_blockquotes(content)

        assert len(visible_syntax) == 0, (
            f"Bug 1.15 confirmed: preflight-quickstart/index.md has "
            f"{len(visible_syntax)} visible fenced-div syntax marker(s):\n"
            + "\n".join(
                f"  - Line {line}: '{syntax}'"
                for syntax, line in visible_syntax
            )
            + "\n  These raw markers should not be visible to readers"
        )

    def test_tomcat_jndi_admonitions_no_blank_line(self):
        """
        Requirement 1.15: tomcat-jndi.md has multiple admonitions with
        blank lines between !!! marker and content.
        """
        content = read_md_file(
            "doc/en/user/tutorials/tomcat-jndi/tomcat-jndi.md"
        )
        assert content is not None, "tomcat-jndi.md not found"

        blank_line_admonitions = find_admonitions_with_blank_line(content)

        assert len(blank_line_admonitions) == 0, (
            f"Bug 1.15 confirmed: tomcat-jndi.md has "
            f"{len(blank_line_admonitions)} admonition(s) with blank line "
            f"after !!! marker:\n"
            + "\n".join(
                f"  - Line {line}: '!!! {atype}'"
                for atype, line in blank_line_admonitions
            )
        )

    @given(
        page_path=st.sampled_from(BLANK_LINE_ADMONITION_PAGES)
    )
    @settings(
        max_examples=len(BLANK_LINE_ADMONITION_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_admonitions_no_blank_line_after_marker(self, page_path):
        """
        Requirement 1.15 (PBT): Admonitions should not have a blank line
        between the !!! marker and the indented content. Content should
        immediately follow the marker.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        blank_line_admonitions = find_admonitions_with_blank_line(content)

        assert len(blank_line_admonitions) == 0, (
            f"Bug 1.15: {page_path} has {len(blank_line_admonitions)} "
            f"admonition(s) with blank line after !!! marker:\n"
            + "\n".join(
                f"  - Line {line}: '!!! {atype}'"
                for atype, line in blank_line_admonitions
            )
        )

    @given(
        page_path=st.sampled_from(VISIBLE_SYNTAX_PAGES)
    )
    @settings(
        max_examples=len(VISIBLE_SYNTAX_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_visible_fenced_div_syntax(self, page_path):
        """
        Requirement 1.15 (PBT): No page should have visible fenced-div
        syntax markers (::::, :::, ::: title) in blockquotes. These are
        raw pandoc conversion artifacts.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        visible_syntax = find_visible_admonition_syntax_in_blockquotes(content)

        assert len(visible_syntax) == 0, (
            f"Bug 1.15: {page_path} has {len(visible_syntax)} visible "
            f"fenced-div syntax marker(s):\n"
            + "\n".join(
                f"  - Line {line}: '{syntax}'"
                for syntax, line in visible_syntax
            )
        )


# ---------------------------------------------------------------------------
# Requirement 1.16 / 2.16: Admonitions in tables must not break table
# structure
# ---------------------------------------------------------------------------

# Pages where admonitions appear immediately after table rows, breaking
# the table context (these were likely inside table cells in the original RST)
ADMONITION_TABLE_PAGES = [
    "doc/en/user/tutorials/imagemosaic_timeseries/imagemosaic_timeseries.md",
    "doc/en/user/styling/ysld/reference/scalezoom.md",
    "doc/en/user/styling/ysld/reference/filters.md",
    "doc/en/user/styling/ysld/reference/featurestyles.md",
    "doc/en/user/styling/ysld/reference/symbolizers/include/fill.md",
    "doc/en/user/styling/sld/reference/rules.md",
    "doc/en/user/styling/sld/reference/labeling.md",
    "doc/en/user/styling/css/filters.md",
    "doc/en/user/services/wms/time.md",
    "doc/en/user/services/wms/nonstandardautonamespace.md",
    "doc/en/user/services/wcs/reference.md",
    "doc/en/user/security/layer.md",
    "doc/en/user/rest/api/services.md",
    "doc/en/user/rest/api/accesscontrol.md",
]


class TestAdmonitionsInTables:
    """Test that admonitions in tables don't break table structure."""

    def test_imagemosaic_timeseries_table_not_broken_by_admonition(self):
        """
        Requirement 1.16: imagemosaic_timeseries.md has admonitions that
        appear immediately after table rows. In the original RST, these
        notes were likely part of the table context or immediately following
        it. The conversion placed !!! note/warning right after the last
        table row, breaking the visual association.

        Counterexample: The datastore.properties table is followed by
        '!!! note' about DBMS parameters, and the indexer.properties table
        is followed by '!!! warning' about TimeAttribute.
        """
        content = read_md_file(
            "doc/en/user/tutorials/imagemosaic_timeseries/imagemosaic_timeseries.md"
        )
        assert content is not None, "imagemosaic_timeseries.md not found"

        table_admonitions = find_admonitions_breaking_tables(content)

        assert len(table_admonitions) == 0, (
            f"Bug 1.16 confirmed: imagemosaic_timeseries.md has "
            f"{len(table_admonitions)} admonition(s) breaking table context:\n"
            + "\n".join(
                f"  - Line {line}: '!!! {atype}' after table row: {ctx}"
                for atype, ctx, line in table_admonitions
            )
            + "\n  Admonitions should be integrated into or clearly "
            "separated from table content"
        )

    def test_scalezoom_table_not_broken_by_admonition(self):
        """
        Requirement 1.16: scalezoom.md has !!! note admonitions immediately
        after attribute tables. The notes about scale expressions should be
        part of the table description, not breaking the table flow.
        """
        content = read_md_file(
            "doc/en/user/styling/ysld/reference/scalezoom.md"
        )
        assert content is not None, "scalezoom.md not found"

        table_admonitions = find_admonitions_breaking_tables(content)

        assert len(table_admonitions) == 0, (
            f"Bug 1.16 confirmed: scalezoom.md has "
            f"{len(table_admonitions)} admonition(s) breaking table context:\n"
            + "\n".join(
                f"  - Line {line}: '!!! {atype}' after: {ctx}"
                for atype, ctx, line in table_admonitions
            )
        )

    def test_wms_time_table_not_broken_by_admonition(self):
        """
        Requirement 1.16: services/wms/time.md has !!! note admonitions
        immediately after time format example tables.
        """
        content = read_md_file("doc/en/user/services/wms/time.md")
        assert content is not None, "wms/time.md not found"

        table_admonitions = find_admonitions_breaking_tables(content)

        assert len(table_admonitions) == 0, (
            f"Bug 1.16 confirmed: wms/time.md has "
            f"{len(table_admonitions)} admonition(s) breaking table context:\n"
            + "\n".join(
                f"  - Line {line}: '!!! {atype}' after: {ctx}"
                for atype, ctx, line in table_admonitions
            )
        )

    def test_security_layer_table_not_broken_by_admonition(self):
        """
        Requirement 1.16: security/layer.md has !!! note admonitions
        immediately after access control rule tables.
        """
        content = read_md_file("doc/en/user/security/layer.md")
        assert content is not None, "security/layer.md not found"

        table_admonitions = find_admonitions_breaking_tables(content)

        assert len(table_admonitions) == 0, (
            f"Bug 1.16 confirmed: security/layer.md has "
            f"{len(table_admonitions)} admonition(s) breaking table context:\n"
            + "\n".join(
                f"  - Line {line}: '!!! {atype}' after: {ctx}"
                for atype, ctx, line in table_admonitions
            )
        )

    @given(
        page_path=st.sampled_from(ADMONITION_TABLE_PAGES)
    )
    @settings(
        max_examples=len(ADMONITION_TABLE_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_admonitions_breaking_tables(self, page_path):
        """
        Requirement 1.16 (PBT): Admonitions should not appear immediately
        after table rows, breaking the table context. Content that was
        part of a table in RST should remain associated with the table.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        table_admonitions = find_admonitions_breaking_tables(content)

        assert len(table_admonitions) == 0, (
            f"Bug 1.16: {page_path} has {len(table_admonitions)} "
            f"admonition(s) breaking table structure:\n"
            + "\n".join(
                f"  - Line {line}: '!!! {atype}' after: {ctx}"
                for atype, ctx, line in table_admonitions
            )
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all admonition requirements
# ---------------------------------------------------------------------------

ALL_ADMONITION_ISSUE_PAGES = list(set(
    BLOCKQUOTED_ADMONITION_PAGES +
    BLANK_LINE_ADMONITION_PAGES +
    VISIBLE_SYNTAX_PAGES +
    ADMONITION_TABLE_PAGES
))


class TestAdmonitionProperty:
    """Property-based tests across all admonition and note requirements."""

    @given(
        page_path=st.sampled_from(ALL_ADMONITION_ISSUE_PAGES)
    )
    @settings(
        max_examples=min(len(ALL_ADMONITION_ISSUE_PAGES), 30),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_admonition_issues(self, page_path):
        """
        Combined property (Req 1.14, 1.15, 1.16): Pages should not have
        any admonition rendering issues including blockquoted admonitions,
        visible syntax markers, blank lines after !!! markers, or
        admonitions breaking table structure.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []

        # Check for blockquoted admonitions (Req 1.14)
        bq_admonitions = find_blockquoted_admonitions(content)
        for atype, line in bq_admonitions:
            issues.append(
                f"Blockquoted admonition ':::: {atype}' at line {line} (Req 1.14)"
            )

        # Check for visible fenced-div syntax (Req 1.15)
        visible_syntax = find_visible_admonition_syntax_in_blockquotes(content)
        for syntax, line in visible_syntax:
            issues.append(
                f"Visible syntax '{syntax}' at line {line} (Req 1.15)"
            )

        # Check for blank lines after !!! markers (Req 1.15)
        blank_line_admonitions = find_admonitions_with_blank_line(content)
        for atype, line in blank_line_admonitions:
            issues.append(
                f"Blank line after '!!! {atype}' at line {line} (Req 1.15)"
            )

        # Check for admonitions breaking tables (Req 1.16)
        table_admonitions = find_admonitions_breaking_tables(content)
        for atype, ctx, line in table_admonitions:
            issues.append(
                f"Admonition '!!! {atype}' breaks table at line {line} (Req 1.16)"
            )

        assert len(issues) == 0, (
            f"Admonition issues in {page_path}:\n"
            + "\n".join(f"  - {issue}" for issue in issues)
        )
