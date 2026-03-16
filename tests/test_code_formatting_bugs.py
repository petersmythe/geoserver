#!/usr/bin/env python3
"""
Bug Condition Exploration Test: Code Formatting and Syntax Highlighting Bugs

**Property 1: Bug Condition** - Code Formatting Issues
**CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
**DO NOT attempt to fix the test or the code when it fails.**

Validates: Requirements 1.5, 1.6, 1.7, 1.8, 2.5, 2.6, 2.7, 2.8

Tests concrete failing cases from Andrea's review feedback:
- Code blocks have consistent syntax highlighting (Req 1.5, 2.5)
- Inline code in nested lists renders with backticks (Req 1.6, 2.6)
- YAML/JSON blocks have syntax highlighting (Req 1.7, 2.7)
- Code sections maintain code block formatting (Req 1.8, 2.8)
"""

import os
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


def find_fenced_code_blocks(content):
    """
    Find all fenced code blocks in content.
    Returns list of (language, code_body, start_line) tuples.
    Language is None if no language identifier is specified.
    """
    blocks = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match opening fence: ``` or ```lang or ``` {.lang ...}
        m = re.match(r'^(\s*)(```+)\s*(\{[^}]*\}|[a-zA-Z0-9_+-]*)\s*$', line)
        if m:
            indent = m.group(1)
            fence = m.group(2)
            lang_raw = m.group(3).strip()
            # Parse language from pandoc-style {.lang ...} or plain lang
            lang = None
            if lang_raw.startswith("{"):
                lang_match = re.search(r'\.(\w+)', lang_raw)
                if lang_match:
                    lang = lang_match.group(1)
            elif lang_raw:
                lang = lang_raw
            # Collect body until closing fence
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


def find_indented_code_blocks(content):
    """
    Find indented code blocks (4+ spaces or tab) that are NOT inside fenced
    code blocks or MkDocs admonition blocks. These are Markdown's implicit
    code blocks that render without syntax highlighting.
    Returns list of (code_text, line_number) tuples.
    """
    lines = content.split("\n")
    blocks = []
    in_fence = False
    admonition_indent = -1  # indent level of current admonition, -1 = none
    current_block = []
    block_start = None

    for i, line in enumerate(lines):
        # Track fenced code blocks
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Track admonition blocks (content indented under !!! type)
        if re.match(r'^(\s*)!!!\s+\w+', line):
            admonition_indent = len(re.match(r'^(\s*)', line).group(1))
            continue
        if admonition_indent >= 0:
            # Admonition content is indented 4 spaces beyond the !!! marker
            expected_indent = admonition_indent + 4
            if line.strip() == "" or line.startswith(" " * expected_indent):
                continue
            else:
                admonition_indent = -1

        # Detect indented code (4+ spaces, not blank)
        # Also catch 6+ space indented blocks inside list items
        if re.match(r'^    \S', line) or re.match(r'^      \S', line):
            if not current_block:
                block_start = i + 1
            current_block.append(line)
        else:
            if current_block:
                blocks.append(("\n".join(current_block), block_start))
                current_block = []
                block_start = None

    if current_block:
        blocks.append(("\n".join(current_block), block_start))

    return blocks


def looks_like_code(text):
    """
    Heuristic: does this indented text block look like it should be
    a fenced code block? Checks for common code patterns.
    """
    code_indicators = [
        r'^\s*<\w+',           # XML/HTML tags
        r'^\s*\{',             # JSON/YAML opening brace
        r'^\s*curl\s',         # curl commands
        r'^\s*\$\s',           # shell prompts
        r'^\s*import\s',       # Python imports
        r'^\s*def\s',          # Python functions
        r'^\s*class\s',        # Class definitions
        r'^\s*<\?xml',         # XML declaration
        r'^\s*[A-Z]\w+=',      # Property assignments like Levels=0.4
        r'^\s*SPI=',           # SPI property
        r'^\s*host=',          # Connection properties
        r'^\s*port=',          # Connection properties
        r'^\s*regex=',         # Regex properties
        r'^\s*<context-param', # XML context params
        r'^\s*-D\w+',         # Java system properties
        r'^\s*export\s+\w+=',  # Shell exports
        r'http://localhost',   # URL examples
        r'^\s*<param-',        # XML param elements
    ]
    for pattern in code_indicators:
        if re.search(pattern, text, re.MULTILINE):
            return True
    return False



# ---------------------------------------------------------------------------
# Requirement 1.5 / 2.5: Code blocks must have consistent syntax highlighting
# ---------------------------------------------------------------------------

# Pages Andrea specifically called out for code formatting issues
CODE_FORMATTING_PAGES = [
    "doc/en/user/extensions/importer/rest_examples.md",
    "doc/en/user/security/webadmin/csrf.md",
    "doc/en/user/security/webadmin/filebrowse.md",
    "doc/en/user/configuration/logging.md",
    "doc/en/user/data/database/postgis.md",
    "doc/en/user/data/database/oracle.md",
    "doc/en/user/data/database/sqlview.md",
    "doc/en/user/rest/layers.md",
    "doc/en/user/rest/stores.md",
]


class TestCodeBlockSyntaxHighlighting:
    """Test that code blocks have consistent syntax highlighting."""

    def test_rest_layers_json_response_is_fenced(self):
        """
        Requirement 1.5: rest/layers.md has a JSON response rendered as an
        indented code block (4-space indent) instead of a fenced code block
        with language identifier.

        Counterexample from Andrea: REST pages have code without highlighting.
        """
        content = read_md_file("doc/en/user/rest/layers.md")
        assert content is not None, "rest/layers.md not found"

        # The JSON response for "List all layers" is indented, not fenced
        # Look for the indented JSON block that starts with {
        indented_blocks = find_indented_code_blocks(content)
        json_indented = [
            (text, line) for text, line in indented_blocks
            if '"layers"' in text or '"layer"' in text
        ]

        assert len(json_indented) == 0, (
            f"Bug 1.5 confirmed: rest/layers.md has JSON response as indented "
            f"code block (no syntax highlighting) at line(s) "
            f"{[line for _, line in json_indented]}. "
            f"Should be a fenced code block with ```json."
        )

    def test_csrf_page_code_is_fenced(self):
        """
        Requirement 1.5/1.8: security/webadmin/csrf.md has XML and shell
        code rendered as indented blocks instead of fenced code blocks.

        Andrea reported: "most of the code is actually hidden in the rendering"
        """
        content = read_md_file("doc/en/user/security/webadmin/csrf.md")
        assert content is not None, "csrf.md not found"

        indented_blocks = find_indented_code_blocks(content)
        code_like_blocks = [
            (text, line) for text, line in indented_blocks
            if looks_like_code(text)
        ]

        assert len(code_like_blocks) == 0, (
            f"Bug 1.5/1.8 confirmed: csrf.md has {len(code_like_blocks)} "
            f"code section(s) as indented blocks instead of fenced code blocks. "
            f"Lines: {[line for _, line in code_like_blocks]}. "
            f"These render without syntax highlighting and may be hidden."
        )

    def test_imagemosaic_config_properties_are_fenced(self):
        """
        Requirement 1.5/1.8: imagemosaic/configuration.md has property file
        examples as indented code blocks instead of fenced code blocks.
        """
        content = read_md_file("doc/en/user/data/raster/imagemosaic/configuration.md")
        assert content is not None, "imagemosaic/configuration.md not found"

        indented_blocks = find_indented_code_blocks(content)
        property_blocks = [
            (text, line) for text, line in indented_blocks
            if re.search(r'\w+=\S', text)
        ]

        assert len(property_blocks) == 0, (
            f"Bug 1.5/1.8 confirmed: imagemosaic/configuration.md has "
            f"{len(property_blocks)} property file example(s) as indented "
            f"code blocks at line(s) {[line for _, line in property_blocks]}. "
            f"Should be fenced code blocks with ```properties."
        )

    @given(
        page_path=st.sampled_from(CODE_FORMATTING_PAGES)
    )
    @settings(max_examples=len(CODE_FORMATTING_PAGES), phases=[Phase.explicit, Phase.generate])
    def test_pages_have_no_indented_code_blocks(self, page_path):
        """
        Requirement 1.5 (PBT): Pages known to have code formatting issues
        should not have code-like content in indented blocks (which lack
        syntax highlighting).
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        indented_blocks = find_indented_code_blocks(content)
        code_like_blocks = [
            (text, line) for text, line in indented_blocks
            if looks_like_code(text)
        ]

        assert len(code_like_blocks) == 0, (
            f"Bug 1.5: {page_path} has {len(code_like_blocks)} code-like "
            f"indented block(s) without syntax highlighting at line(s) "
            f"{[line for _, line in code_like_blocks]}."
        )



# ---------------------------------------------------------------------------
# Requirement 1.6 / 2.6: Inline code in nested lists must use backticks
# ---------------------------------------------------------------------------

# Pages Andrea called out for "Code bits in nested list rendered verbatim"
INLINE_CODE_LIST_PAGES = [
    "doc/en/user/data/raster/imagemosaic/tutorial.md",
    "doc/en/user/styling/qgis/index.md",
]


class TestInlineCodeInNestedLists:
    """Test that inline code references in nested lists use backtick formatting."""

    def test_imagemosaic_tutorial_inline_code_has_backticks(self):
        """
        Requirement 1.6: imagemosaic/tutorial.md has inline code references
        in nested lists rendered as verbatim text without backtick formatting.

        Counterexample from Andrea: "multi-crs-mosaic" section has code
        references like file names and property names without backticks.
        """
        content = read_md_file("doc/en/user/data/raster/imagemosaic/tutorial.md")
        assert content is not None, "imagemosaic/tutorial.md not found"

        # Look for common code-like terms in list items that lack backticks
        # These are technical terms that should be inline code
        code_terms = [
            r'\.properties\b',
            r'\.shp\b',
            r'\.tif\b',
            r'\.xml\b',
            r'\.prj\b',
            r'EPSG:\d+',
            r'CRS\b',
        ]

        lines = content.split("\n")
        issues = []
        in_fence = False

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Only check list items (lines starting with - or * or digits.)
            if not re.match(r'^\s*[-*]\s|^\s*\d+\.\s', line):
                continue

            for term_pattern in code_terms:
                # Find the term NOT inside backticks
                # Strategy: find all occurrences, check if they're inside backticks
                for m in re.finditer(term_pattern, line):
                    start = m.start()
                    # Check if this occurrence is inside backticks
                    before = line[:start]
                    after = line[start:]
                    # Count backticks before - if odd, we're inside inline code
                    backtick_count = before.count('`')
                    if backtick_count % 2 == 0:
                        # Not inside backticks - this is a bare code reference
                        issues.append((i + 1, m.group(), line.strip()[:80]))

        assert len(issues) == 0, (
            f"Bug 1.6 confirmed: imagemosaic/tutorial.md has {len(issues)} "
            f"inline code reference(s) in list items without backtick formatting:\n"
            + "\n".join(
                f"  - Line {line}: '{term}' in: {ctx}"
                for line, term, ctx in issues[:10]
            )
        )

    def test_qgis_styling_inline_code_has_backticks(self):
        """
        Requirement 1.6: styling/qgis.md has inline code references in
        nested lists rendered as verbatim text without backtick formatting.

        Andrea reported: "multiple instances" in exporting-raster-symbology section.
        """
        content = read_md_file("doc/en/user/styling/qgis/index.md")
        assert content is not None, "styling/qgis/index.md not found"

        code_terms = [
            r'\.sld\b',
            r'\.qml\b',
            r'\.xml\b',
            r'ColorMap\b',
            r'RasterSymbolizer\b',
            r'SLD\b',
        ]

        lines = content.split("\n")
        issues = []
        in_fence = False

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            if not re.match(r'^\s*[-*]\s|^\s*\d+\.\s', line):
                continue

            for term_pattern in code_terms:
                for m in re.finditer(term_pattern, line):
                    start = m.start()
                    before = line[:start]
                    if before.count('`') % 2 == 0:
                        issues.append((i + 1, m.group(), line.strip()[:80]))

        assert len(issues) == 0, (
            f"Bug 1.6 confirmed: styling/qgis.md has {len(issues)} "
            f"inline code reference(s) in list items without backtick formatting:\n"
            + "\n".join(
                f"  - Line {line}: '{term}' in: {ctx}"
                for line, term, ctx in issues[:10]
            )
        )

    @given(
        page_path=st.sampled_from(INLINE_CODE_LIST_PAGES)
    )
    @settings(max_examples=len(INLINE_CODE_LIST_PAGES), phases=[Phase.explicit, Phase.generate])
    def test_nested_list_code_refs_use_backticks(self, page_path):
        """
        Requirement 1.6 (PBT): Inline code references in nested list items
        must use backtick formatting, not appear as verbatim text.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        # Look for file extensions and class names in list items without backticks
        code_patterns = [
            r'\.\w{2,4}\b',  # File extensions like .properties, .shp
        ]

        lines = content.split("\n")
        issues = []
        in_fence = False

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Only nested list items (indented list markers)
            if not re.match(r'^\s{2,}\s*[-*]\s|^\s{2,}\s*\d+\.\s', line):
                continue

            for pattern in code_patterns:
                for m in re.finditer(pattern, line):
                    # Skip if inside backticks, markdown links, or image refs
                    start = m.start()
                    before = line[:start]
                    if before.count('`') % 2 == 0 and '](http' not in before[max(0,start-50):start]:
                        term = m.group()
                        # Only flag known code-like extensions
                        if term in ('.properties', '.shp', '.tif', '.xml', '.prj',
                                    '.sld', '.qml', '.json', '.yaml', '.yml'):
                            issues.append((i + 1, term))

        assert len(issues) == 0, (
            f"Bug 1.6: {page_path} has {len(issues)} bare code reference(s) "
            f"in nested list items:\n"
            + "\n".join(f"  - Line {line}: '{term}'" for line, term in issues[:10])
        )



# ---------------------------------------------------------------------------
# Requirement 1.7 / 2.7: YAML/JSON blocks must have syntax highlighting
# ---------------------------------------------------------------------------

# Pages with YAML/JSON that use pandoc-style {.yaml} or {.json} attributes
# which MkDocs may not render with proper highlighting
PANDOC_STYLE_PAGES = [
    "doc/en/user/styling/ysld/reference/featurestyles.md",
    "doc/en/user/styling/workshop/ysld/raster.md",
    "doc/en/user/styling/workshop/ysld/point.md",
    "doc/en/user/styling/workshop/ysld/polygon.md",
    "doc/en/user/styling/workshop/ysld/linestring.md",
]


class TestYamlJsonHighlighting:
    """Test that YAML/JSON blocks have proper syntax highlighting."""

    def test_ysld_featurestyles_no_pandoc_style_fences(self):
        """
        Requirement 1.7: featurestyles.md uses pandoc-style code fence
        attributes like ``` {.yaml emphasize-lines="15"} which MkDocs
        Material may not render with proper syntax highlighting.

        These should use standard ``` yaml format.
        """
        content = read_md_file(
            "doc/en/user/styling/ysld/reference/featurestyles.md"
        )
        assert content is not None, "featurestyles.md not found"

        pandoc_fences = re.findall(
            r'^```\s*\{\.(\w+)[^}]*\}', content, re.MULTILINE
        )

        assert len(pandoc_fences) == 0, (
            f"Bug 1.7 confirmed: featurestyles.md has {len(pandoc_fences)} "
            f"pandoc-style code fence(s) using {{.lang}} syntax instead of "
            f"standard ```lang. Languages found: {pandoc_fences}. "
            f"MkDocs may not apply syntax highlighting to these blocks."
        )

    def test_rest_layers_json_has_language_identifier(self):
        """
        Requirement 1.7: rest/layers.md has JSON response blocks that are
        indented (4-space) instead of fenced with ```json, so they lack
        syntax highlighting.
        """
        content = read_md_file("doc/en/user/rest/layers.md")
        assert content is not None, "rest/layers.md not found"

        # Find indented blocks that look like JSON
        indented_blocks = find_indented_code_blocks(content)
        json_blocks = [
            (text, line) for text, line in indented_blocks
            if re.search(r'^\s*[\{\[]', text.strip()) or '"' in text[:50]
        ]

        assert len(json_blocks) == 0, (
            f"Bug 1.7 confirmed: rest/layers.md has {len(json_blocks)} JSON "
            f"block(s) as indented code (no highlighting) at line(s) "
            f"{[line for _, line in json_blocks]}. "
            f"Should use ```json fenced code blocks."
        )

    def test_printing_faq_yaml_has_language_identifier(self):
        """
        Requirement 1.7: printing/faq.md has a YAML example that Andrea
        flagged. Check that YAML blocks use proper ```yaml fencing.
        """
        content = read_md_file("doc/en/user/extensions/printing/faq.md")
        assert content is not None, "printing/faq.md not found"

        # Find fenced code blocks and check if YAML-looking ones have lang id
        blocks = find_fenced_code_blocks(content)
        yaml_without_lang = []
        for lang, body, start in blocks:
            # Check if body looks like YAML but has no language identifier
            if lang is None and (
                re.search(r'^\s*\w+:', body, re.MULTILINE) and
                '{' in body  # YAML-like with braces
            ):
                yaml_without_lang.append((body[:60], start))

        # Also check for the known YAML block that uses ``` yaml (with space)
        # which should work, but verify it exists
        fenced_yaml = [b for b in blocks if b[0] == 'yaml']

        # The real issue is the definition-list style content that should be
        # code but isn't fenced at all
        has_definition_list_code = ":   " in content

        assert not has_definition_list_code or len(fenced_yaml) > 0, (
            f"Bug 1.7: printing/faq.md has definition-list style content "
            f"that may contain code examples not properly formatted."
        )

    @given(
        page_path=st.sampled_from(PANDOC_STYLE_PAGES)
    )
    @settings(max_examples=len(PANDOC_STYLE_PAGES), phases=[Phase.explicit, Phase.generate])
    def test_no_pandoc_style_code_fences(self, page_path):
        """
        Requirement 1.7 (PBT): YAML/JSON code blocks should use standard
        ```yaml or ```json syntax, not pandoc-style ``` {.yaml ...} which
        may not render with proper highlighting in MkDocs.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        pandoc_fences = re.findall(
            r'^```\s*\{\.(\w+)[^}]*\}', content, re.MULTILINE
        )

        assert len(pandoc_fences) == 0, (
            f"Bug 1.7: {page_path} has {len(pandoc_fences)} pandoc-style "
            f"code fence(s): {pandoc_fences}. Should use standard ```lang."
        )



# ---------------------------------------------------------------------------
# Requirement 1.8 / 2.8: Code sections must maintain code block formatting
# ---------------------------------------------------------------------------

# Pages Andrea called out for "Misformatted code sections"
MISFORMATTED_CODE_PAGES = [
    "doc/en/user/installation/upgrade.md",
    "doc/en/user/gettingstarted/style-quickstart.md",
    "doc/en/user/gettingstarted/postgis-quickstart.md",
    "doc/en/user/data/database/postgis.md",
    "doc/en/user/data/database/oracle.md",
    "doc/en/user/data/database/sqlview.md",
    "doc/en/user/configuration/logging.md",
    "doc/en/user/security/webadmin/filebrowse.md",
    "doc/en/user/security/webadmin/csrf.md",
    "doc/en/user/security/usergrouprole/usergroupservices.md",
    "doc/en/user/extensions/printing/faq.md",
    "doc/en/user/extensions/csw-iso/mapping.md",
]


class TestCodeSectionFormatting:
    """Test that code sections maintain proper code block formatting."""

    def test_wfs_vendor_indented_code_is_fenced(self):
        """
        Requirement 1.8: services/wfs/vendor.md has code examples rendered
        as indented blocks (plain text) instead of fenced code blocks.

        The page has URL examples and parameter syntax as indented text.
        """
        content = read_md_file("doc/en/user/services/wfs/vendor.md")
        assert content is not None, "wfs/vendor.md not found"

        indented_blocks = find_indented_code_blocks(content)
        code_like = [
            (text, line) for text, line in indented_blocks
            if looks_like_code(text) or 'http://' in text or '=' in text
        ]

        assert len(code_like) == 0, (
            f"Bug 1.8 confirmed: wfs/vendor.md has {len(code_like)} code "
            f"section(s) rendered as indented text (plain paragraphs) at "
            f"line(s) {[line for _, line in code_like]}. "
            f"Should be fenced code blocks."
        )

    def test_virtual_services_indented_urls_are_fenced(self):
        """
        Requirement 1.8: configuration/virtual-services.md has URL examples
        as indented text blocks instead of fenced code blocks.
        """
        content = read_md_file("doc/en/user/configuration/virtual-services.md")
        assert content is not None, "virtual-services.md not found"

        indented_blocks = find_indented_code_blocks(content)
        url_blocks = [
            (text, line) for text, line in indented_blocks
            if 'http://' in text or 'localhost' in text
        ]

        assert len(url_blocks) == 0, (
            f"Bug 1.8 confirmed: virtual-services.md has {len(url_blocks)} "
            f"URL example(s) as indented text at line(s) "
            f"{[line for _, line in url_blocks]}. "
            f"Should be fenced code blocks."
        )

    def test_importer_rest_examples_code_in_blockquotes(self):
        """
        Requirement 1.8: importer/rest_examples.md has code blocks wrapped
        in blockquote syntax (> ``` bash) which is a conversion artifact.

        Andrea reported this page specifically for code formatting issues.
        """
        content = read_md_file(
            "doc/en/user/extensions/importer/rest_examples.md"
        )
        assert content is not None, "rest_examples.md not found"

        # Find code blocks inside blockquotes (> ``` pattern)
        blockquoted_code = re.findall(
            r'^>\s*```', content, re.MULTILINE
        )

        assert len(blockquoted_code) == 0, (
            f"Bug 1.8 confirmed: rest_examples.md has {len(blockquoted_code)} "
            f"code block(s) wrapped in blockquote syntax (> ```). "
            f"Code should not be inside blockquotes."
        )

    @given(
        page_path=st.sampled_from(MISFORMATTED_CODE_PAGES)
    )
    @settings(
        max_examples=len(MISFORMATTED_CODE_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_code_sections_are_properly_fenced(self, page_path):
        """
        Requirement 1.8 (PBT): Pages known to have misformatted code sections
        should have all code content in fenced code blocks, not as indented
        text or plain paragraphs.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        indented_blocks = find_indented_code_blocks(content)
        code_like = [
            (text, line) for text, line in indented_blocks
            if looks_like_code(text)
        ]

        assert len(code_like) == 0, (
            f"Bug 1.8: {page_path} has {len(code_like)} code section(s) "
            f"rendered as indented text (no fencing, no highlighting) at "
            f"line(s) {[line for _, line in code_like]}."
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all code formatting requirements
# ---------------------------------------------------------------------------

# All pages with any code formatting issue from Andrea's feedback
ALL_CODE_ISSUE_PAGES = list(set(
    CODE_FORMATTING_PAGES +
    INLINE_CODE_LIST_PAGES +
    PANDOC_STYLE_PAGES +
    MISFORMATTED_CODE_PAGES
))


class TestCodeFormattingProperty:
    """Property-based tests across all code formatting requirements."""

    @given(
        page_path=st.sampled_from(ALL_CODE_ISSUE_PAGES)
    )
    @settings(
        max_examples=min(len(ALL_CODE_ISSUE_PAGES), 20),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_code_formatting_issues(self, page_path):
        """
        Combined property (Req 1.5, 1.7, 1.8): Pages should not have
        code-like content in indented blocks or pandoc-style fences.
        All code should use standard fenced code blocks with language ids.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []

        # Check for indented code blocks (Req 1.5, 1.8)
        indented_blocks = find_indented_code_blocks(content)
        for text, line in indented_blocks:
            if looks_like_code(text):
                issues.append(
                    f"Indented code block at line {line} (no highlighting)"
                )

        # Check for pandoc-style fences (Req 1.7)
        pandoc_fences = re.findall(
            r'^```\s*\{\.(\w+)[^}]*\}', content, re.MULTILINE
        )
        for lang in pandoc_fences:
            issues.append(
                f"Pandoc-style fence {{.{lang}}} (may lack highlighting)"
            )

        # Check for blockquoted code blocks (Req 1.8)
        bq_code = re.findall(r'^>\s*```', content, re.MULTILINE)
        if bq_code:
            issues.append(
                f"{len(bq_code)} code block(s) inside blockquotes"
            )

        assert len(issues) == 0, (
            f"Code formatting issues in {page_path}:\n"
            + "\n".join(f"  - {issue}" for issue in issues)
        )
