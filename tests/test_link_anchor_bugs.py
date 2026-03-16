#!/usr/bin/env python3
"""
Bug Condition Exploration Test: Link and Anchor Resolution Bugs

**Property 1: Bug Condition** - Link and Anchor Resolution Bugs
**CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
**DO NOT attempt to fix the test or the code when it fails.**

**Validates: Requirements 1.24, 1.25, 2.24, 2.25**

Tests concrete failing cases from Andrea's review feedback:
- Internal links resolve correctly without visible syntax (Req 1.24, 2.24)
- Include statements work or are replaced with content (Req 1.25, 2.25)
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


def find_dot_notation_anchors(content):
    """
    Find links using RST-style dot-separated anchor references like
    (#app-schema.complex-features) that were not converted to proper
    Markdown relative links.

    In RST, cross-references use :ref:`app-schema.complex-features`.
    The converter turned these into Markdown links with dot-notation
    anchors (#app-schema.complex-features) that don't resolve in MkDocs
    because MkDocs uses dash-separated heading IDs, not dot-separated.

    Returns list of (link_text, anchor, line_number) tuples.
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

        # Pattern: [link text](#word.word...) - dot-separated anchor
        for m in re.finditer(
            r'\[([^\]]+)\]\(#([a-z][\w-]*\.[a-z][\w.-]*)\)', line
        ):
            link_text = m.group(1)
            anchor = m.group(2)
            results.append((link_text, anchor, i + 1))

    return results


def find_garbled_link_labels(content):
    """
    Find link labels that are garbled concatenations of section prefix
    and page name, like "[DataApp SchemaComplex Features]" or
    "[ServicesWfsAxis Order]".

    These are conversion artifacts where the RST navigation hierarchy
    label was concatenated with the page title to form the link text.
    The correct label should be just the page title (e.g. "Complex
    Features", "Axis Order").

    Returns list of (label, target, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False

    # Known garbled prefixes from the conversion
    garbled_prefixes = [
        "DataApp Schema", "DataCascaded", "DataDatabase",
        "ServicesWfs", "ServicesWms", "ServicesWps",
        "StylingSldTipstricks", "ExtensionsPrinting",
    ]

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
            label = m.group(1)
            target = m.group(2)
            for prefix in garbled_prefixes:
                if label.startswith(prefix):
                    results.append((label, target, i + 1))
                    break

    return results


def find_raw_include_statements(content):
    """
    Find include statements wrapped in {%raw%} tags that render as
    literal template syntax instead of including actual content.

    The RST ``.. include::`` directive was converted to Jinja2-style
    ``{% include "file" %}`` wrapped in ``{%raw%}...{%endraw%}`` to
    prevent MkDocs from processing them. This means the include
    directive is displayed as literal text in a code block instead of
    being replaced with the actual file content.

    Returns list of (include_path, line_number) tuples.
    """
    results = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        # Pattern: {%raw%}{% include "path" %}{%endraw%}
        # or {%raw%}{% include-markdown "path" %}{%endraw%}
        m = re.search(
            r'\{%\s*raw\s*%\}\s*\{%\s*include(?:-markdown)?\s+'
            r'["\']?([^"\'%}]+)["\']?\s*%\}',
            line
        )
        if m:
            include_path = m.group(1).strip()
            results.append((include_path, i + 1))

    return results


def find_unclosed_raw_includes(content):
    """
    Find include statements wrapped in {%raw%} but missing the closing
    {%endraw%} tag. These are malformed and will cause rendering issues.

    Returns list of (include_path, line_number) tuples.
    """
    results = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        # Has {%raw%}{% include but no {%endraw%} on the same line
        if re.search(r'\{%\s*raw\s*%\}\s*\{%\s*include', line):
            if not re.search(r'\{%\s*endraw\s*%\}', line):
                m = re.search(
                    r'\{%\s*raw\s*%\}\s*\{%\s*include(?:-markdown)?\s+'
                    r'["\']?([^"\'%}]+)["\']?',
                    line
                )
                if m:
                    results.append((m.group(1).strip(), i + 1))

    return results


# ---------------------------------------------------------------------------
# Requirement 1.24 / 2.24: Internal links must resolve correctly without
# visible syntax artifacts
# ---------------------------------------------------------------------------

# Pages with RST-style dot-notation anchor references
DOT_ANCHOR_PAGES = [
    "doc/en/user/data/app-schema/cql-functions.md",
    "doc/en/user/data/app-schema/wms-support.md",
    "doc/en/user/data/app-schema/wfs-2.0-support.md",
    "doc/en/user/data/app-schema/mapping-file.md",
    "doc/en/user/data/app-schema/polymorphism.md",
    "doc/en/user/data/app-schema/tutorial.md",
    "doc/en/user/data/app-schema/supported-gml-versions.md",
    "doc/en/user/tutorials/freemarker.md",
    "doc/en/user/services/wms/reference.md",
    "doc/en/user/services/wfs/reference.md",
]

# Pages with garbled concatenated link labels
GARBLED_LABEL_PAGES = [
    "doc/en/user/data/app-schema/index.md",
    "doc/en/user/data/index.md",
    "doc/en/user/data/cascaded/index.md",
    "doc/en/user/data/database/index.md",
    "doc/en/user/services/wfs/index.md",
    "doc/en/user/services/wms/index.md",
    "doc/en/user/services/wps/index.md",
    "doc/en/user/styling/sld/tipstricks/index.md",
    "doc/en/user/extensions/printing/index.md",
]

# ---------------------------------------------------------------------------
# Requirement 1.25 / 2.25: Include statements must work or be replaced
# with actual content
# ---------------------------------------------------------------------------

# Pages with {%raw%}{% include %} statements that render as literal text
RAW_INCLUDE_PAGES = [
    "doc/en/user/tutorials/imagemosaic_timeseries/imagemosaic_timeseries.md",
    "doc/en/user/tutorials/imagemosaic_timeseries/imagemosaic_time-elevationseries.md",
    "doc/en/user/styling/ysld/reference/symbolizers/line.md",
    "doc/en/user/styling/ysld/reference/symbolizers/polygon.md",
    "doc/en/user/styling/ysld/reference/symbolizers/point.md",
    "doc/en/user/styling/ysld/reference/symbolizers/text.md",
    "doc/en/user/styling/ysld/reference/symbolizers/raster.md",
    "doc/en/user/styling/ysld/reference/symbolizers/index.md",
    "doc/en/user/styling/workshop/ysld/ysld.md",
    "doc/en/user/styling/workshop/mbstyle/mbstyle.md",
    "doc/en/user/styling/workshop/mbstyle/polygon.md",
    "doc/en/user/styling/ysld/cookbook/polygons.md",
]


class TestDotNotationAnchors:
    """Test that RST-style dot-notation anchors are converted to proper links."""

    def test_app_schema_cql_functions_dot_anchors(self):
        """
        Requirement 1.24: cql-functions.md uses RST-style dot-notation
        anchors like (#app-schema.mapping-file) and
        (#app-schema.property-interpolation) that don't resolve in MkDocs.

        These should be converted to relative links like
        (mapping-file.md) or proper heading anchors.
        """
        content = read_md_file(
            "doc/en/user/data/app-schema/cql-functions.md"
        )
        assert content is not None, "cql-functions.md not found"

        dot_anchors = find_dot_notation_anchors(content)

        assert len(dot_anchors) == 0, (
            f"Bug 1.24 confirmed: cql-functions.md has "
            f"{len(dot_anchors)} RST-style dot-notation anchor(s) "
            f"that don't resolve in MkDocs:\n"
            + "\n".join(
                f"  - Line {line}: [{text}](#{anchor})"
                for text, anchor, line in dot_anchors
            )
            + "\n  Dot-notation anchors should be converted to relative "
            "Markdown links (e.g. mapping-file.md)"
        )

    def test_app_schema_wms_support_dot_anchors(self):
        """
        Requirement 1.24: wms-support.md has multiple RST-style
        dot-notation anchors including (#app-schema.joining),
        (#app-schema.configuration), (#app-schema.filtering-nested),
        and (#app-schema.feature-chaining-by-reference).

        None of these resolve in MkDocs.
        """
        content = read_md_file(
            "doc/en/user/data/app-schema/wms-support.md"
        )
        assert content is not None, "wms-support.md not found"

        dot_anchors = find_dot_notation_anchors(content)

        assert len(dot_anchors) == 0, (
            f"Bug 1.24 confirmed: wms-support.md has "
            f"{len(dot_anchors)} dot-notation anchor(s):\n"
            + "\n".join(
                f"  - Line {line}: [{text}](#{anchor})"
                for text, anchor, line in dot_anchors
            )
            + "\n  These RST cross-references should be proper "
            "Markdown relative links"
        )

    def test_freemarker_cross_page_dot_anchor(self):
        """
        Requirement 1.24: freemarker.md references
        (#app-schema.complex-features) which is a cross-page RST
        reference that should link to the actual complex-features.md
        page, not an anchor on the current page.
        """
        content = read_md_file("doc/en/user/tutorials/freemarker.md")
        assert content is not None, "freemarker.md not found"

        dot_anchors = find_dot_notation_anchors(content)

        assert len(dot_anchors) == 0, (
            f"Bug 1.24 confirmed: freemarker.md has "
            f"{len(dot_anchors)} cross-page dot-notation anchor(s):\n"
            + "\n".join(
                f"  - Line {line}: [{text}](#{anchor})"
                for text, anchor, line in dot_anchors
            )
            + "\n  Cross-page references should use relative paths "
            "(e.g. ../data/app-schema/complex-features.md)"
        )

    @given(page_path=st.sampled_from(DOT_ANCHOR_PAGES))
    @settings(
        max_examples=len(DOT_ANCHOR_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_dot_notation_anchors(self, page_path):
        """
        Requirement 1.24 (PBT): No page should have RST-style
        dot-notation anchor references that don't resolve in MkDocs.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        dot_anchors = find_dot_notation_anchors(content)

        assert len(dot_anchors) == 0, (
            f"Bug 1.24: {page_path} has {len(dot_anchors)} "
            f"dot-notation anchor(s):\n"
            + "\n".join(
                f"  - Line {line}: [{text}](#{anchor})"
                for text, anchor, line in dot_anchors
            )
        )


class TestGarbledLinkLabels:
    """Test that link labels are clean, not garbled concatenations."""

    def test_app_schema_index_garbled_labels(self):
        """
        Requirement 1.24: data/app-schema/index.md has 15+ links with
        garbled labels like "[DataApp SchemaComplex Features]",
        "[DataApp SchemaMapping File]", etc.

        The converter concatenated the navigation hierarchy prefix
        "DataApp Schema" with the page title. The correct labels should
        be just the page titles (e.g. "Complex Features", "Mapping File").
        """
        content = read_md_file("doc/en/user/data/app-schema/index.md")
        assert content is not None, "app-schema/index.md not found"

        garbled = find_garbled_link_labels(content)

        assert len(garbled) == 0, (
            f"Bug 1.24 confirmed: app-schema/index.md has "
            f"{len(garbled)} garbled link label(s):\n"
            + "\n".join(
                f"  - Line {line}: [{label}]({target})"
                for label, target, line in garbled
            )
            + "\n  Labels should be clean page titles without "
            "section prefix concatenation"
        )

    def test_data_index_garbled_labels(self):
        """
        Requirement 1.24: data/index.md has "[DataApp SchemaIndex]"
        as a link label for the app-schema section. This should be
        a clean label like "Application Schemas".
        """
        content = read_md_file("doc/en/user/data/index.md")
        assert content is not None, "data/index.md not found"

        garbled = find_garbled_link_labels(content)

        assert len(garbled) == 0, (
            f"Bug 1.24 confirmed: data/index.md has "
            f"{len(garbled)} garbled link label(s):\n"
            + "\n".join(
                f"  - Line {line}: [{label}]({target})"
                for label, target, line in garbled
            )
        )

    def test_services_index_pages_garbled_labels(self):
        """
        Requirement 1.24: Service index pages (wfs, wms, wps) have
        garbled labels like "[ServicesWfsAxis Order]" and
        "[ServicesWmsGet Legend GraphicIndex]".
        """
        service_pages = [
            "doc/en/user/services/wfs/index.md",
            "doc/en/user/services/wms/index.md",
            "doc/en/user/services/wps/index.md",
        ]
        all_issues = []
        for page_path in service_pages:
            content = read_md_file(page_path)
            if content is None:
                continue
            garbled = find_garbled_link_labels(content)
            for label, target, line in garbled:
                all_issues.append((page_path, label, target, line))

        assert len(all_issues) == 0, (
            f"Bug 1.24 confirmed: Service index pages have "
            f"{len(all_issues)} garbled link label(s):\n"
            + "\n".join(
                f"  - {path} line {line}: [{label}]({target})"
                for path, label, target, line in all_issues
            )
        )

    @given(page_path=st.sampled_from(GARBLED_LABEL_PAGES))
    @settings(
        max_examples=len(GARBLED_LABEL_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_garbled_link_labels(self, page_path):
        """
        Requirement 1.24 (PBT): No page should have garbled
        concatenated link labels from the conversion.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        garbled = find_garbled_link_labels(content)

        assert len(garbled) == 0, (
            f"Bug 1.24: {page_path} has {len(garbled)} "
            f"garbled link label(s):\n"
            + "\n".join(
                f"  - Line {line}: [{label}]({target})"
                for label, target, line in garbled
            )
        )


class TestIncludeStatements:
    """Test that include statements work or are replaced with content."""

    def test_imagemosaic_timeseries_raw_includes(self):
        """
        Requirement 1.25: imagemosaic_timeseries.md has multiple include
        statements wrapped in {%raw%} tags inside code blocks. These
        render as literal template syntax like:
            {%raw%}{% include "./src/datastore.properties" %}{%endraw%}
        instead of showing the actual file content.

        Some are also missing the closing {%endraw%} tag, making them
        doubly malformed.
        """
        content = read_md_file(
            "doc/en/user/tutorials/imagemosaic_timeseries/"
            "imagemosaic_timeseries.md"
        )
        assert content is not None, "imagemosaic_timeseries.md not found"

        raw_includes = find_raw_include_statements(content)
        unclosed = find_unclosed_raw_includes(content)
        all_issues = raw_includes + [
            (path, line) for path, line in unclosed
            if (path, line) not in raw_includes
        ]

        assert len(all_issues) == 0, (
            f"Bug 1.25 confirmed: imagemosaic_timeseries.md has "
            f"{len(all_issues)} include statement(s) rendered as "
            f"literal template syntax:\n"
            + "\n".join(
                f"  - Line {line}: include '{path}'"
                for path, line in all_issues
            )
            + "\n  Include statements should be replaced with actual "
            "file content or use a working MkDocs include mechanism"
        )

    def test_ysld_symbolizer_pages_raw_include_markdown(self):
        """
        Requirement 1.25: YSLD symbolizer reference pages (line.md,
        polygon.md, point.md, text.md, raster.md) use
        {%raw%}{% include-markdown "./include/..." %}{%endraw%}
        to include shared property tables.

        The {%raw%} wrapper prevents MkDocs from processing the
        include-markdown directive, so the literal template syntax
        is displayed instead of the included table content.
        """
        symbolizer_pages = [
            "doc/en/user/styling/ysld/reference/symbolizers/line.md",
            "doc/en/user/styling/ysld/reference/symbolizers/polygon.md",
            "doc/en/user/styling/ysld/reference/symbolizers/point.md",
            "doc/en/user/styling/ysld/reference/symbolizers/text.md",
            "doc/en/user/styling/ysld/reference/symbolizers/raster.md",
        ]
        all_issues = []
        for page_path in symbolizer_pages:
            content = read_md_file(page_path)
            if content is None:
                continue
            raw_includes = find_raw_include_statements(content)
            for inc_path, line in raw_includes:
                all_issues.append((page_path, inc_path, line))

        assert len(all_issues) == 0, (
            f"Bug 1.25 confirmed: YSLD symbolizer pages have "
            f"{len(all_issues)} include-markdown statement(s) "
            f"rendered as literal syntax:\n"
            + "\n".join(
                f"  - {path} line {line}: include-markdown '{inc}'"
                for path, inc, line in all_issues
            )
            + "\n  Include-markdown directives should not be wrapped "
            "in {%raw%} tags"
        )

    def test_workshop_pages_raw_includes(self):
        """
        Requirement 1.25: Workshop pages (ysld.md, mbstyle.md) use
        {%raw%}{% include "file" %}{%endraw%} inside code blocks to
        show example SLD/YSLD/JSON files. The include is neutralized
        by {%raw%} so the literal syntax is shown instead of file content.
        """
        workshop_pages = [
            "doc/en/user/styling/workshop/ysld/ysld.md",
            "doc/en/user/styling/workshop/mbstyle/mbstyle.md",
            "doc/en/user/styling/workshop/mbstyle/polygon.md",
        ]
        all_issues = []
        for page_path in workshop_pages:
            content = read_md_file(page_path)
            if content is None:
                continue
            raw_includes = find_raw_include_statements(content)
            for inc_path, line in raw_includes:
                all_issues.append((page_path, inc_path, line))

        assert len(all_issues) == 0, (
            f"Bug 1.25 confirmed: Workshop pages have "
            f"{len(all_issues)} include statement(s) rendered as "
            f"literal template syntax:\n"
            + "\n".join(
                f"  - {path} line {line}: include '{inc}'"
                for path, inc, line in all_issues
            )
        )

    def test_unclosed_raw_include_tags(self):
        """
        Requirement 1.25: Some include statements have {%raw%} but are
        missing the closing {%endraw%} tag. This is doubly broken -
        the include doesn't work AND the raw tag leaks into subsequent
        content.
        """
        content = read_md_file(
            "doc/en/user/tutorials/imagemosaic_timeseries/"
            "imagemosaic_timeseries.md"
        )
        assert content is not None, "imagemosaic_timeseries.md not found"

        unclosed = find_unclosed_raw_includes(content)

        assert len(unclosed) == 0, (
            f"Bug 1.25 confirmed: imagemosaic_timeseries.md has "
            f"{len(unclosed)} include statement(s) with unclosed "
            f"{{%raw%}} tags:\n"
            + "\n".join(
                f"  - Line {line}: include '{path}' (missing "
                "{%endraw%})"
                for path, line in unclosed
            )
            + "\n  Unclosed {%raw%} tags cause the include to fail "
            "AND leak raw mode into subsequent content"
        )

    @given(page_path=st.sampled_from(RAW_INCLUDE_PAGES))
    @settings(
        max_examples=len(RAW_INCLUDE_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_raw_include_statements(self, page_path):
        """
        Requirement 1.25 (PBT): No page should have include statements
        wrapped in {%raw%} tags that prevent them from working.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        raw_includes = find_raw_include_statements(content)

        assert len(raw_includes) == 0, (
            f"Bug 1.25: {page_path} has {len(raw_includes)} "
            f"include statement(s) wrapped in {{%raw%}} tags:\n"
            + "\n".join(
                f"  - Line {line}: include '{path}'"
                for path, line in raw_includes
            )
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all link/anchor requirements
# ---------------------------------------------------------------------------

ALL_LINK_ANCHOR_ISSUE_PAGES = list(set(
    DOT_ANCHOR_PAGES +
    GARBLED_LABEL_PAGES +
    RAW_INCLUDE_PAGES
))


class TestLinkAnchorProperty:
    """Property-based tests across all link and anchor requirements."""

    @given(page_path=st.sampled_from(ALL_LINK_ANCHOR_ISSUE_PAGES))
    @settings(
        max_examples=min(len(ALL_LINK_ANCHOR_ISSUE_PAGES), 30),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_link_anchor_issues(self, page_path):
        """
        Combined property (Req 1.24, 1.25): Pages should not have any
        link/anchor resolution issues including dot-notation anchors,
        garbled link labels, or broken include statements.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []

        # Check for dot-notation anchors (Req 1.24)
        dot_anchors = find_dot_notation_anchors(content)
        for text, anchor, line in dot_anchors:
            issues.append(
                f"Dot-notation anchor [{text}](#{anchor}) "
                f"at line {line} (Req 1.24)"
            )

        # Check for garbled link labels (Req 1.24)
        garbled = find_garbled_link_labels(content)
        for label, target, line in garbled:
            issues.append(
                f"Garbled label [{label}]({target}) "
                f"at line {line} (Req 1.24)"
            )

        # Check for raw include statements (Req 1.25)
        raw_includes = find_raw_include_statements(content)
        for inc_path, line in raw_includes:
            issues.append(
                f"Raw include '{inc_path}' at line {line} (Req 1.25)"
            )

        assert len(issues) == 0, (
            f"Link/anchor issues in {page_path}:\n"
            + "\n".join(f"  - {issue}" for issue in issues)
        )
