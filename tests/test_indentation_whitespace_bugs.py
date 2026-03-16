#!/usr/bin/env python3
"""
Bug Condition Exploration Test: Indentation and Whitespace Rendering Bugs

**Property 1: Bug Condition** - Indentation and Whitespace Issues
**CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
**DO NOT attempt to fix the test or the code when it fails.**

**Validates: Requirements 1.26, 1.27, 1.28, 2.26, 2.27, 2.28**

Tests concrete failing cases from Andrea's review feedback:
- Indented paragraphs don't render as code blocks or blockquotes (Req 1.26, 2.26)
- Definition list-style content renders properly (Req 1.27, 2.27)
- Text starting with ": " converts to proper Markdown (Req 1.28, 2.28)
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


def find_definition_list_colon_lines(content):
    """
    Find lines starting with ':   ' (colon followed by 3+ spaces) that are
    RST definition list artifacts. In Markdown, these render as literal text
    with visible colons instead of proper definition lists.

    RST definition lists use the pattern:
        term
            definition text

    The converter produced:
        term

        :   definition text

    which is not valid Markdown and renders the colon literally.

    Returns list of (line_text, line_number) tuples.
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

        # Pattern: line starts with ':' followed by 3+ spaces
        # This is RST definition list syntax that doesn't render in Markdown
        if re.match(r'^:\s{3,}', line):
            results.append((line.strip(), i + 1))

    return results


def find_definition_list_colon_dash(content):
    """
    Find definition list-style content with ': - text' patterns.

    In RST, definition lists can contain sub-lists:
        term
            - item 1
            - item 2

    The converter produced:
        :   - item 1
            - item 2

    This renders as malformed text with visible ': -' in Markdown.

    Returns list of (line_text, line_number) tuples.
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

        # Pattern: ':   - text' — definition list with sub-list items
        if re.match(r'^:\s{3,}-\s', line):
            results.append((line.strip(), i + 1))

    return results


def find_indented_definition_terms(content):
    """
    Find RST definition list term/definition pairs where the term is on
    one line and the definition starts with ':   ' on a subsequent line.

    Pattern in converted files:
        Literal

        :   `'SRS_NAME'` (optional)

        Expression

        :   expression text

    These are RST definition lists that have no standard Markdown equivalent.
    The ':   ' prefix renders as literal text.

    Returns list of (term, definition_preview, line_number) tuples.
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

        # Look for ':   ' definition line preceded by a blank line and a term
        if re.match(r'^:\s{3,}', line) and i >= 2:
            prev_line = lines[i - 1].strip()
            term_line = lines[i - 2].strip() if i >= 2 else ""
            # The term is a non-empty line, followed by blank, followed by ':   '
            if prev_line == "" and term_line != "" and not term_line.startswith("#"):
                definition_preview = line.strip()[:80]
                results.append((term_line, definition_preview, i + 1))

    return results


# ---------------------------------------------------------------------------
# Requirement 1.26 / 2.26: Indented paragraphs must NOT render as code blocks
# or blockquotes
# ---------------------------------------------------------------------------

# Pages where indented paragraphs are incorrectly rendered as code blocks
# (4+ spaces of indentation triggers code block in Markdown)
INDENTED_PARAGRAPH_PAGES = [
    "doc/en/user/data/app-schema/cql-functions.md",
    "doc/en/user/data/app-schema/polymorphism.md",
    "doc/en/user/data/app-schema/joining.md",
    "doc/en/user/data/app-schema/property-interpolation.md",
    "doc/en/user/data/app-schema/secondary-namespaces.md",
    "doc/en/user/data/app-schema/configuration.md",
]


class TestIndentedParagraphsAsCodeBlocks:
    """Test that indented paragraphs don't render as code blocks (Req 1.26)."""

    def test_cql_functions_indented_syntax_blocks(self):
        """
        Requirement 1.26: cql-functions.md has syntax examples like
        'Recode(COLUMN_NAME, ...)' indented with 4 spaces, which Markdown
        renders as code blocks. These should use fenced code blocks instead.

        Counterexample: Lines like '    Recode(COLUMN_NAME, key1, value1, ...)'
        render as <pre><code> blocks due to 4-space indentation.
        """
        content = read_md_file("doc/en/user/data/app-schema/cql-functions.md")
        assert content is not None, "cql-functions.md not found"

        lines = content.split("\n")
        in_fence = False
        indented_code_lines = []

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # 4+ spaces of indentation outside a code fence = unintended code block
            # Exclude list continuation (lines after '- ' items) and admonition content
            if re.match(r'^    \S', line):
                # Check if previous non-empty line is a list item or admonition
                prev_idx = i - 1
                while prev_idx >= 0 and lines[prev_idx].strip() == "":
                    prev_idx -= 1
                if prev_idx >= 0:
                    prev = lines[prev_idx].strip()
                    # Skip if it's list continuation or admonition content
                    if prev.startswith("- ") or prev.startswith("!!! "):
                        continue
                indented_code_lines.append((line.rstrip(), i + 1))

        assert len(indented_code_lines) == 0, (
            f"Bug 1.26 confirmed: cql-functions.md has "
            f"{len(indented_code_lines)} line(s) with 4-space indentation "
            f"that render as unintended code blocks:\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in indented_code_lines[:10]
            )
            + ("\n  ... and more" if len(indented_code_lines) > 10 else "")
            + "\n  These should use fenced code blocks (```) instead of "
            "4-space indentation"
        )

    def test_polymorphism_indented_syntax_blocks(self):
        """
        Requirement 1.26: polymorphism.md has syntax examples indented
        with 4 spaces that render as code blocks in Markdown.
        """
        content = read_md_file("doc/en/user/data/app-schema/polymorphism.md")
        assert content is not None, "polymorphism.md not found"

        lines = content.split("\n")
        in_fence = False
        indented_code_lines = []

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            if re.match(r'^    \S', line):
                prev_idx = i - 1
                while prev_idx >= 0 and lines[prev_idx].strip() == "":
                    prev_idx -= 1
                if prev_idx >= 0:
                    prev = lines[prev_idx].strip()
                    if prev.startswith("- ") or prev.startswith("!!! "):
                        continue
                indented_code_lines.append((line.rstrip(), i + 1))

        assert len(indented_code_lines) == 0, (
            f"Bug 1.26 confirmed: polymorphism.md has "
            f"{len(indented_code_lines)} line(s) with 4-space indentation "
            f"that render as unintended code blocks:\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in indented_code_lines[:10]
            )
        )

    @given(page_path=st.sampled_from(INDENTED_PARAGRAPH_PAGES))
    @settings(
        max_examples=len(INDENTED_PARAGRAPH_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_indented_paragraphs_as_code_blocks(self, page_path):
        """
        Requirement 1.26 (PBT): No page should have indented paragraphs
        that unintentionally render as code blocks due to 4-space indentation.

        **Validates: Requirements 1.26, 2.26**
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        lines = content.split("\n")
        in_fence = False
        indented_code_lines = []

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            if re.match(r'^    \S', line):
                prev_idx = i - 1
                while prev_idx >= 0 and lines[prev_idx].strip() == "":
                    prev_idx -= 1
                if prev_idx >= 0:
                    prev = lines[prev_idx].strip()
                    if prev.startswith("- ") or prev.startswith("!!! "):
                        continue
                indented_code_lines.append((line.rstrip(), i + 1))

        assert len(indented_code_lines) == 0, (
            f"Bug 1.26: {page_path} has {len(indented_code_lines)} "
            f"indented line(s) rendering as code blocks:\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in indented_code_lines[:10]
            )
        )


# ---------------------------------------------------------------------------
# Requirement 1.27 / 2.27: Definition list-style content with ': - text'
# must render properly
# ---------------------------------------------------------------------------

# Pages with ': - text' definition list patterns
DEFINITION_LIST_DASH_PAGES = [
    "doc/en/user/tutorials/cloud-foundry/run_cf.md",
    "doc/en/user/security/auth/chain.md",
    "doc/en/user/extensions/printing/protocol.md",
    "doc/en/user/extensions/metadata/uiconfiguration.md",
    "doc/en/user/data/app-schema/cql-functions.md",
]


class TestDefinitionListDashContent:
    """Test that ': - text' definition list content renders properly (Req 1.27)."""

    def test_run_cf_definition_list_dash(self):
        """
        Requirement 1.27: run_cf.md has a definition list with ': - text'
        pattern that renders as malformed text:

            The manifest file allows you to configure:

            :   - Resource limits (memory and cpu)
                - configure the route URL

        The ': - ' prefix renders literally instead of as a proper list.
        """
        content = read_md_file(
            "doc/en/user/tutorials/cloud-foundry/run_cf.md"
        )
        assert content is not None, "run_cf.md not found"

        colon_dash = find_definition_list_colon_dash(content)

        assert len(colon_dash) == 0, (
            f"Bug 1.27 confirmed: run_cf.md has {len(colon_dash)} "
            f"definition list ': - text' pattern(s) that render as "
            f"malformed text:\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in colon_dash
            )
            + "\n  These should be converted to proper Markdown lists"
        )

    def test_auth_chain_definition_list_dash(self):
        """
        Requirement 1.27: chain.md has definition lists with ': - text'
        patterns for matching rules and ANT pattern wildcards:

            Matching rules can be applied to:

            :   - HTTP Method (GET, POST, etc.)
                - one or more ANT patterns...

        The ': - ' renders literally as malformed text.
        """
        content = read_md_file("doc/en/user/security/auth/chain.md")
        assert content is not None, "chain.md not found"

        colon_dash = find_definition_list_colon_dash(content)

        assert len(colon_dash) == 0, (
            f"Bug 1.27 confirmed: chain.md has {len(colon_dash)} "
            f"definition list ': - text' pattern(s):\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in colon_dash
            )
        )

    def test_cql_functions_nested_definition_list_dash(self):
        """
        Requirement 1.27: cql-functions.md has a nested definition list
        with ': - text' inside a list item for the Categorize function's
        preceding/succeeding parameter:

            **preceding/succeeding**:

            :   - optional, succeeding is used by default if not specified.
                - not case sensitive.

        This renders as malformed text with visible ': -'.
        """
        content = read_md_file(
            "doc/en/user/data/app-schema/cql-functions.md"
        )
        assert content is not None, "cql-functions.md not found"

        # Look specifically for the nested ': - ' pattern (indented)
        lines = content.split("\n")
        in_fence = False
        nested_colon_dash = []

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Indented ': - ' pattern (inside list items)
            if re.match(r'^\s+:\s{3,}-\s', line):
                nested_colon_dash.append((line.strip(), i + 1))

        assert len(nested_colon_dash) == 0, (
            f"Bug 1.27 confirmed: cql-functions.md has "
            f"{len(nested_colon_dash)} nested ': - text' pattern(s):\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in nested_colon_dash
            )
        )

    @given(page_path=st.sampled_from(DEFINITION_LIST_DASH_PAGES))
    @settings(
        max_examples=len(DEFINITION_LIST_DASH_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_definition_list_colon_dash(self, page_path):
        """
        Requirement 1.27 (PBT): No page should have ': - text' definition
        list patterns that render as malformed text.

        **Validates: Requirements 1.27, 2.27**
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        colon_dash = find_definition_list_colon_dash(content)

        assert len(colon_dash) == 0, (
            f"Bug 1.27: {page_path} has {len(colon_dash)} "
            f"': - text' pattern(s):\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in colon_dash
            )
        )


# ---------------------------------------------------------------------------
# Requirement 1.28 / 2.28: Text starting with ': ' must convert to proper
# Markdown syntax
# ---------------------------------------------------------------------------

# Pages with ':   text' definition list patterns (colon + spaces)
DEFINITION_LIST_COLON_PAGES = [
    "doc/en/user/data/app-schema/cql-functions.md",
    "doc/en/user/styling/workshop/index.md",
    "doc/en/user/extensions/printing/faq.md",
    "doc/en/user/extensions/netcdf-out/nc4.md",
    "doc/en/user/extensions/mapml/installation.md",
    "doc/en/docguide/style.md",
    "doc/en/docguide/sphinx.md",
]


class TestDefinitionListColonSyntax:
    """Test that ':   text' definition syntax converts to proper Markdown (Req 1.28)."""

    def test_cql_functions_definition_list_terms(self):
        """
        Requirement 1.28: cql-functions.md has RST definition list syntax
        where terms like 'Literal', 'Expression', 'pattern', 'date',
        'timezone' are followed by ':   definition text'.

        Example:
            Literal

            :   `'SRS_NAME'` (optional)

            Expression

            :   expression of SRS name

        The ':   ' prefix renders literally in Markdown instead of as
        a proper definition list or formatted content.
        """
        content = read_md_file(
            "doc/en/user/data/app-schema/cql-functions.md"
        )
        assert content is not None, "cql-functions.md not found"

        term_defs = find_indented_definition_terms(content)

        assert len(term_defs) == 0, (
            f"Bug 1.28 confirmed: cql-functions.md has "
            f"{len(term_defs)} RST definition list term/definition "
            f"pair(s) with ':   ' syntax:\n"
            + "\n".join(
                f"  - Line {ln}: term='{term}', def='{defn}'"
                for term, defn, ln in term_defs[:10]
            )
            + ("\n  ... and more" if len(term_defs) > 10 else "")
            + "\n  These should be converted to proper Markdown "
            "(e.g. bold term + description, or HTML <dl> lists)"
        )

    def test_workshop_index_definition_list(self):
        """
        Requirement 1.28: styling/workshop/index.md uses RST definition
        list syntax for workshop section descriptions:

            [setup/index](setup/index.md)

            :   Workshop materials and setup

        The ':   ' renders literally instead of as a description.
        """
        content = read_md_file("doc/en/user/styling/workshop/index.md")
        assert content is not None, "workshop/index.md not found"

        colon_lines = find_definition_list_colon_lines(content)

        assert len(colon_lines) == 0, (
            f"Bug 1.28 confirmed: workshop/index.md has "
            f"{len(colon_lines)} line(s) with ':   ' definition "
            f"list syntax:\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in colon_lines
            )
        )

    def test_printing_faq_definition_list(self):
        """
        Requirement 1.28: printing/faq.md uses RST definition list syntax
        for FAQ answers:

            **All I get in my PDF is: "ERROR: infinite table loop"...**

            :   Something in your page is too big...

        The ':   ' renders literally instead of as the answer text.
        """
        content = read_md_file("doc/en/user/extensions/printing/faq.md")
        assert content is not None, "printing/faq.md not found"

        colon_lines = find_definition_list_colon_lines(content)

        assert len(colon_lines) == 0, (
            f"Bug 1.28 confirmed: printing/faq.md has "
            f"{len(colon_lines)} line(s) with ':   ' definition "
            f"list syntax:\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in colon_lines
            )
        )

    def test_docguide_style_definition_list(self):
        """
        Requirement 1.28: docguide/style.md uses RST definition list
        syntax for good/bad examples:

            Bad

            :   Super-overlays are a great way to publish...

            Good

            :   Super-overlays allow you to efficiently...

        The ':   ' renders literally instead of as example text.
        """
        content = read_md_file("doc/en/docguide/style.md")
        assert content is not None, "docguide/style.md not found"

        colon_lines = find_definition_list_colon_lines(content)

        assert len(colon_lines) == 0, (
            f"Bug 1.28 confirmed: style.md has {len(colon_lines)} "
            f"line(s) with ':   ' definition list syntax:\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in colon_lines
            )
        )

    @given(page_path=st.sampled_from(DEFINITION_LIST_COLON_PAGES))
    @settings(
        max_examples=len(DEFINITION_LIST_COLON_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_definition_list_colon_syntax(self, page_path):
        """
        Requirement 1.28 (PBT): No page should have ':   text' RST
        definition list syntax that renders as literal text in Markdown.

        **Validates: Requirements 1.28, 2.28**
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        colon_lines = find_definition_list_colon_lines(content)

        assert len(colon_lines) == 0, (
            f"Bug 1.28: {page_path} has {len(colon_lines)} "
            f"':   text' pattern(s):\n"
            + "\n".join(
                f"  - Line {ln}: {text[:80]}"
                for text, ln in colon_lines
            )
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all indentation/whitespace requirements
# ---------------------------------------------------------------------------

ALL_INDENTATION_ISSUE_PAGES = list(set(
    INDENTED_PARAGRAPH_PAGES +
    DEFINITION_LIST_DASH_PAGES +
    DEFINITION_LIST_COLON_PAGES
))


class TestIndentationWhitespaceProperty:
    """Property-based tests across all indentation/whitespace requirements."""

    @given(page_path=st.sampled_from(ALL_INDENTATION_ISSUE_PAGES))
    @settings(
        max_examples=min(len(ALL_INDENTATION_ISSUE_PAGES), 15),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_indentation_whitespace_issues(self, page_path):
        """
        Combined property (Req 1.26, 1.27, 1.28): Pages should not have
        any indentation/whitespace rendering issues including unintended
        code blocks, ': - text' patterns, or ':   text' definition syntax.

        **Validates: Requirements 1.26, 1.27, 1.28, 2.26, 2.27, 2.28**
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []

        # Check for ':   text' definition list syntax (Req 1.28)
        colon_lines = find_definition_list_colon_lines(content)
        for text, ln in colon_lines:
            issues.append(
                f"Definition list ':   ' syntax at line {ln}: "
                f"{text[:60]} (Req 1.28)"
            )

        # Check for ': - text' patterns (Req 1.27)
        colon_dash = find_definition_list_colon_dash(content)
        for text, ln in colon_dash:
            issues.append(
                f"Definition list ': - ' pattern at line {ln}: "
                f"{text[:60]} (Req 1.27)"
            )

        # Check for 4-space indented paragraphs as code blocks (Req 1.26)
        lines = content.split("\n")
        in_fence = False
        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if re.match(r'^    \S', line):
                prev_idx = i - 1
                while prev_idx >= 0 and lines[prev_idx].strip() == "":
                    prev_idx -= 1
                if prev_idx >= 0:
                    prev = lines[prev_idx].strip()
                    if prev.startswith("- ") or prev.startswith("!!! "):
                        continue
                issues.append(
                    f"4-space indented line at line {i + 1}: "
                    f"{line.strip()[:60]} (Req 1.26)"
                )

        assert len(issues) == 0, (
            f"Indentation/whitespace issues in {page_path}:\n"
            + "\n".join(f"  - {issue}" for issue in issues[:15])
            + (f"\n  ... and {len(issues) - 15} more"
               if len(issues) > 15 else "")
        )
