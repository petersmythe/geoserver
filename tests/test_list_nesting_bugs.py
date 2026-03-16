#!/usr/bin/env python3
"""
Bug Condition Exploration Test: List and Nesting Structure Bugs

**Property 1: Bug Condition** - List and Nesting Issues
**CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
**DO NOT attempt to fix the test or the code when it fails.**

Validates: Requirements 1.9, 1.10, 1.11, 1.12, 1.13, 2.9, 2.10, 2.11, 2.12, 2.13

Tests concrete failing cases from Andrea's review feedback:
- Nested list items maintain proper indentation (Req 1.9, 2.9)
- Images in list items render as images, not code blocks (Req 1.10, 2.10)
- Indented content in lists doesn't render as blockquotes (Req 1.11, 2.11)
- Numbered lists maintain structure (Req 1.12, 2.12)
- List items retain all content (Req 1.13, 2.13)
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


def find_images_as_code_blocks(content):
    """
    Find images that are wrapped in code fences (``` raw_markdown or similar)
    instead of being rendered as actual images. This is a conversion artifact
    where images inside list items got wrapped in code blocks.
    Returns list of (image_ref, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_code_fence = False
    fence_start = None
    fence_body = []

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line) and not in_code_fence:
            in_code_fence = True
            fence_start = i + 1
            fence_body = []
            continue
        if re.match(r'^\s*```', line) and in_code_fence:
            # Check if the code block contained image references
            body_text = "\n".join(fence_body)
            img_matches = re.findall(r'!\[.*?\]\(.*?\)', body_text)
            for img in img_matches:
                results.append((img, fence_start))
            in_code_fence = False
            fence_body = []
            continue
        if in_code_fence:
            fence_body.append(line)

    return results


def find_blockquoted_list_items(content):
    """
    Find list items where content is incorrectly wrapped in blockquote
    syntax (> - item or > * item). This happens when the converter
    misinterprets indented RST list content as blockquotes.
    Returns list of (line_text, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False
    in_admonition = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Track admonition blocks — content inside !!! note etc. is valid
        if re.match(r'^\s*!!!\s+\w+', line):
            in_admonition = True
            continue
        if in_admonition:
            if line.strip() == "" or re.match(r'^\s{4,}', line):
                continue
            else:
                in_admonition = False

        # Blockquoted list items: > - item or > * item or > 1. item
        # Also catch indented blockquoted lists:    > - item
        if re.match(r'^\s*>\s*[-*]\s', line) or re.match(r'^\s*>\s*\d+\.\s', line):
            results.append((line.strip(), i + 1))

    return results


def find_definition_list_numbered_items(content):
    """
    Find numbered list items that are prefixed with definition list syntax
    (":   1. item") which causes them to render as a single block instead
    of a proper numbered list.
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

        # Definition list prefix before numbered items: ":   1." or ": 1."
        if re.match(r'^:\s+\d+\.\s', line):
            results.append((line.strip(), i + 1))

    return results


def find_empty_list_items(content):
    """
    Find list items that appear to have lost their content, showing as
    empty bullets or with only whitespace after the marker.
    Also detects the pattern where a bullet is followed by a blank line
    and then definition-list style content (": - text").
    Returns list of (context, line_number) tuples.
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

        # Empty list item: "- " followed by nothing or just whitespace
        # But with content on the next line that should have been part of it
        if re.match(r'^-\s*$', line) or re.match(r'^\*\s*$', line):
            # Check if next non-blank line has content that looks like
            # it should have been part of this list item
            for j in range(i + 1, min(i + 4, len(lines))):
                next_line = lines[j].strip()
                if next_line and not re.match(r'^[-*]\s', next_line):
                    results.append((f"Empty bullet at line {i+1}, "
                                    f"followed by: {next_line[:60]}",
                                    i + 1))
                    break

        # Also detect "- \n\n  **text**:" pattern where the bullet lost
        # its inline content and it ended up on the next line
        if re.match(r'^-\s+$', line):
            results.append((f"Trailing whitespace bullet: '{line}'", i + 1))

    return results



# ---------------------------------------------------------------------------
# Requirement 1.10 / 2.10: Images in list items must render as images,
# not code blocks
# ---------------------------------------------------------------------------

# Pages Andrea specifically called out for images in lists rendered as code
IMAGES_IN_LISTS_PAGES = [
    "doc/en/user/data/raster/imagemosaic/tutorial.md",
    "doc/en/user/styling/qgis/index.md",
]


class TestImagesInListItems:
    """Test that images in list items render as images, not code blocks."""

    def test_imagemosaic_tutorial_images_not_in_code_blocks(self):
        """
        Requirement 1.10: imagemosaic/tutorial.md has images inside list items
        wrapped in ``` raw_markdown code fences instead of rendering as images.

        Counterexample from Andrea: "nested image reference rendered as code,
        multiple instances in this page"
        """
        content = read_md_file(
            "doc/en/user/data/raster/imagemosaic/tutorial.md"
        )
        assert content is not None, "imagemosaic/tutorial.md not found"

        images_in_code = find_images_as_code_blocks(content)

        assert len(images_in_code) == 0, (
            f"Bug 1.10 confirmed: imagemosaic/tutorial.md has "
            f"{len(images_in_code)} image(s) wrapped in code fences "
            f"instead of rendering as actual images:\n"
            + "\n".join(
                f"  - Line {line}: {img[:80]}"
                for img, line in images_in_code[:10]
            )
        )

    def test_qgis_styling_images_not_in_code_blocks(self):
        """
        Requirement 1.10: styling/qgis/index.md has images inside numbered
        list items wrapped in ``` raw_markdown code fences.

        Andrea reported this page for "Code bits in nested list rendered
        verbatim" which includes images rendered as code.
        """
        content = read_md_file("doc/en/user/styling/qgis/index.md")
        assert content is not None, "styling/qgis/index.md not found"

        images_in_code = find_images_as_code_blocks(content)

        assert len(images_in_code) == 0, (
            f"Bug 1.10 confirmed: styling/qgis/index.md has "
            f"{len(images_in_code)} image(s) wrapped in code fences:\n"
            + "\n".join(
                f"  - Line {line}: {img[:80]}"
                for img, line in images_in_code[:10]
            )
        )

    @given(
        page_path=st.sampled_from(IMAGES_IN_LISTS_PAGES)
    )
    @settings(
        max_examples=len(IMAGES_IN_LISTS_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_images_inside_code_fences(self, page_path):
        """
        Requirement 1.10 (PBT): No page should have image references
        (![...](...)  ) wrapped inside code fence blocks.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        images_in_code = find_images_as_code_blocks(content)

        assert len(images_in_code) == 0, (
            f"Bug 1.10: {page_path} has {len(images_in_code)} image(s) "
            f"inside code fences instead of rendering as images."
        )


# ---------------------------------------------------------------------------
# Requirement 1.11 / 2.11: Indented content in lists must not render as
# blockquotes
# ---------------------------------------------------------------------------

# Pages Andrea called out for "Indented portion of a list item rendered as
# quoted text, quoted lists, and other stuff that should not have been quoted"
BLOCKQUOTED_LIST_PAGES = [
    "doc/en/user/tutorials/imagepyramid/imagepyramid.md",
    "doc/en/user/tutorials/imagemosaic_footprint/imagemosaic_footprint.md",
    "doc/en/user/tutorials/freemarker.md",
    "doc/en/user/data/raster/imagemosaic/tutorial.md",
    "doc/en/user/gettingstarted/geopkg-quickstart/index.md",
    "doc/en/user/gettingstarted/image-quickstart/index.md",
    "doc/en/user/gettingstarted/group-quickstart/index.md",
    "doc/en/user/data/database/postgis.md",
    "doc/en/user/data/database/sqlview.md",
    "doc/en/user/data/database/primarykey.md",
    "doc/en/user/styling/sld/cookbook/lines.md",
    "doc/en/user/styling/sld/reference/filters.md",
    "doc/en/user/configuration/virtual-services.md",
    "doc/en/user/extensions/controlflow/index.md",
]


class TestBlockquotedListContent:
    """Test that indented list content doesn't render as blockquotes."""

    def test_imagepyramid_lists_not_blockquoted(self):
        """
        Requirement 1.11: imagepyramid.md has list items where the content
        is wrapped in blockquote syntax (> - item) instead of being normal
        indented list items.

        The gdal_retile parameter list should be a normal nested list,
        not blockquoted.
        """
        content = read_md_file(
            "doc/en/user/tutorials/imagepyramid/imagepyramid.md"
        )
        assert content is not None, "imagepyramid.md not found"

        bq_items = find_blockquoted_list_items(content)

        assert len(bq_items) == 0, (
            f"Bug 1.11 confirmed: imagepyramid.md has {len(bq_items)} "
            f"list item(s) incorrectly wrapped in blockquote syntax:\n"
            + "\n".join(
                f"  - Line {line}: {text[:80]}"
                for text, line in bq_items[:10]
            )
        )

    def test_imagemosaic_footprint_lists_not_blockquoted(self):
        """
        Requirement 1.11: imagemosaic_footprint.md has list items wrapped
        in blockquote syntax. The footprint behaviour list (None, Transparent,
        Cut) and granule list should be normal lists.
        """
        content = read_md_file(
            "doc/en/user/tutorials/imagemosaic_footprint/imagemosaic_footprint.md"
        )
        assert content is not None, "imagemosaic_footprint.md not found"

        bq_items = find_blockquoted_list_items(content)

        assert len(bq_items) == 0, (
            f"Bug 1.11 confirmed: imagemosaic_footprint.md has "
            f"{len(bq_items)} list item(s) in blockquote syntax:\n"
            + "\n".join(
                f"  - Line {line}: {text[:80]}"
                for text, line in bq_items[:10]
            )
        )

    def test_freemarker_lists_not_blockquoted(self):
        """
        Requirement 1.11: freemarker.md has environment variable lists
        and request property lists wrapped in blockquote syntax.
        """
        content = read_md_file("doc/en/user/tutorials/freemarker.md")
        assert content is not None, "freemarker.md not found"

        bq_items = find_blockquoted_list_items(content)

        assert len(bq_items) == 0, (
            f"Bug 1.11 confirmed: freemarker.md has {len(bq_items)} "
            f"list item(s) in blockquote syntax:\n"
            + "\n".join(
                f"  - Line {line}: {text[:80]}"
                for text, line in bq_items[:10]
            )
        )

    def test_imagemosaic_tutorial_lists_not_blockquoted(self):
        """
        Requirement 1.11: imagemosaic/tutorial.md has list items in the
        "Create a new store" section wrapped in blockquote syntax
        (> - The absolute path...).
        """
        content = read_md_file(
            "doc/en/user/data/raster/imagemosaic/tutorial.md"
        )
        assert content is not None, "imagemosaic/tutorial.md not found"

        bq_items = find_blockquoted_list_items(content)

        assert len(bq_items) == 0, (
            f"Bug 1.11 confirmed: imagemosaic/tutorial.md has "
            f"{len(bq_items)} list item(s) in blockquote syntax:\n"
            + "\n".join(
                f"  - Line {line}: {text[:80]}"
                for text, line in bq_items[:10]
            )
        )

    @given(
        page_path=st.sampled_from(BLOCKQUOTED_LIST_PAGES)
    )
    @settings(
        max_examples=len(BLOCKQUOTED_LIST_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_blockquoted_list_items(self, page_path):
        """
        Requirement 1.11 (PBT): List items should not be wrapped in
        blockquote syntax (> - item). Indented list content should
        render as normal indented text, not blockquotes.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        bq_items = find_blockquoted_list_items(content)

        assert len(bq_items) == 0, (
            f"Bug 1.11: {page_path} has {len(bq_items)} list item(s) "
            f"incorrectly wrapped in blockquote syntax:\n"
            + "\n".join(
                f"  - Line {line}: {text[:80]}"
                for text, line in bq_items[:10]
            )
        )


# ---------------------------------------------------------------------------
# Requirement 1.9 / 2.9: Nested list items must maintain proper indentation
# ---------------------------------------------------------------------------

# Pages Andrea called out for list nesting formatting issues
LIST_NESTING_PAGES = [
    "doc/en/user/installation/upgrade.md",
    "doc/en/user/data/raster/imagemosaic/tutorial.md",
    "doc/en/user/data/app-schema/complex-features.md",
    "doc/en/user/data/app-schema/mapping-file.md",
    "doc/en/user/data/app-schema/cql-functions.md",
    "doc/en/user/data/app-schema/property-interpolation.md",
    "doc/en/user/data/app-schema/feature-chaining.md",
    "doc/en/user/data/app-schema/polymorphism.md",
    "doc/en/user/data/app-schema/wfs-2.0-support.md",
    "doc/en/user/data/app-schema/tutorial.md",
]


class TestNestedListIndentation:
    """Test that nested list items maintain proper indentation."""

    def test_imagemosaic_tutorial_nested_list_indentation(self):
        """
        Requirement 1.9: imagemosaic/tutorial.md has nested list items
        where the indentation is broken. The "Create a new store" section
        has sub-items that should be indented under their parent items
        but instead use blockquote syntax or code fences.

        Andrea reported: "multiple instances in this page"
        """
        content = read_md_file(
            "doc/en/user/data/raster/imagemosaic/tutorial.md"
        )
        assert content is not None, "imagemosaic/tutorial.md not found"

        # Check for the specific pattern: numbered list items with
        # sub-content wrapped in blockquotes or code fences
        issues = []

        # Pattern 1: blockquoted sub-items under numbered list
        bq_items = find_blockquoted_list_items(content)
        if bq_items:
            issues.extend(
                f"Blockquoted sub-item at line {line}: {text[:60]}"
                for text, line in bq_items
            )

        # Pattern 2: images in code fences under list items
        img_code = find_images_as_code_blocks(content)
        if img_code:
            issues.extend(
                f"Image in code fence at line {line}: {img[:60]}"
                for img, line in img_code
            )

        assert len(issues) == 0, (
            f"Bug 1.9 confirmed: imagemosaic/tutorial.md has "
            f"{len(issues)} nesting issue(s):\n"
            + "\n".join(f"  - {issue}" for issue in issues[:15])
        )

    @given(
        page_path=st.sampled_from(LIST_NESTING_PAGES)
    )
    @settings(
        max_examples=len(LIST_NESTING_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_nested_lists_have_proper_structure(self, page_path):
        """
        Requirement 1.9 (PBT): Nested list items should maintain proper
        indentation. Sub-items should not be wrapped in blockquotes or
        code fences.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []

        bq_items = find_blockquoted_list_items(content)
        if bq_items:
            issues.extend(
                f"Blockquoted list at line {line}"
                for _, line in bq_items
            )

        img_code = find_images_as_code_blocks(content)
        if img_code:
            issues.extend(
                f"Image in code fence at line {line}"
                for _, line in img_code
            )

        assert len(issues) == 0, (
            f"Bug 1.9: {page_path} has {len(issues)} nesting issue(s):\n"
            + "\n".join(f"  - {issue}" for issue in issues[:10])
        )



# ---------------------------------------------------------------------------
# Requirement 1.12 / 2.12: Numbered lists must maintain structure
# ---------------------------------------------------------------------------

# Pages Andrea called out for numbered lists turned into solid text blocks
FLATTENED_LIST_PAGES = [
    "doc/en/user/extensions/dxf/index.md",
]


class TestNumberedListStructure:
    """Test that numbered lists maintain their structure."""

    def test_dxf_format_options_is_proper_list(self):
        """
        Requirement 1.12: dxf/index.md has a numbered list of format_options
        that is prefixed with definition list syntax (":   1. version...")
        causing it to render as a solid block of text instead of a proper
        numbered list.

        Andrea reported: "numbered list turned into a solid block of text"
        """
        content = read_md_file("doc/en/user/extensions/dxf/index.md")
        assert content is not None, "dxf/index.md not found"

        deflist_items = find_definition_list_numbered_items(content)

        assert len(deflist_items) == 0, (
            f"Bug 1.12 confirmed: dxf/index.md has {len(deflist_items)} "
            f"numbered list item(s) with definition list prefix "
            f"(':   1.') causing them to render as a solid text block:\n"
            + "\n".join(
                f"  - Line {line}: {text[:80]}"
                for text, line in deflist_items[:10]
            )
        )

    def test_no_definition_list_prefix_on_numbered_items(self):
        """
        Requirement 1.12 (broader): Scan known pages for numbered list
        items that have been prefixed with definition list syntax,
        which flattens them into text blocks.
        """
        # Scan a broader set of pages for this pattern
        pages_to_check = [
            "doc/en/user/extensions/dxf/index.md",
            "doc/en/user/extensions/netcdf-out/index.md",
            "doc/en/user/data/app-schema/cql-functions.md",
        ]

        all_issues = []
        for page_path in pages_to_check:
            content = read_md_file(page_path)
            if content is None:
                continue
            deflist_items = find_definition_list_numbered_items(content)
            for text, line in deflist_items:
                all_issues.append((page_path, line, text))

        assert len(all_issues) == 0, (
            f"Bug 1.12: {len(all_issues)} numbered list item(s) with "
            f"definition list prefix across pages:\n"
            + "\n".join(
                f"  - {path} line {line}: {text[:70]}"
                for path, line, text in all_issues[:10]
            )
        )


# ---------------------------------------------------------------------------
# Requirement 1.13 / 2.13: List items must retain all content
# ---------------------------------------------------------------------------

# Pages Andrea called out for lost list content
LOST_CONTENT_PAGES = [
    "doc/en/user/data/app-schema/cql-functions.md",
]


class TestListContentRetention:
    """Test that list items retain all their content."""

    def test_cql_functions_categorize_list_content(self):
        """
        Requirement 1.13: cql-functions.md has list items in the Categorize
        section where content is lost. Andrea reported: "some more funky
        business with list items right after this issue."

        The "preceding/succeeding" parameter description has an empty bullet
        followed by definition-list style content that should be inline.
        """
        content = read_md_file(
            "doc/en/user/data/app-schema/cql-functions.md"
        )
        assert content is not None, "cql-functions.md not found"

        # Look for the specific pattern: "- \n\n  **preceding/succeeding**:"
        # or empty bullet followed by definition-list content
        empty_items = find_empty_list_items(content)

        # Also check for the ":   -" pattern (definition list inside list)
        lines = content.split("\n")
        deflist_in_list = []
        in_fence = False
        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            # Definition list syntax that should be a sub-list
            if re.match(r'^\s+:\s+-\s', line):
                deflist_in_list.append((line.strip(), i + 1))

        issues = empty_items + [
            (f"Definition list in list: {text}", line)
            for text, line in deflist_in_list
        ]

        assert len(issues) == 0, (
            f"Bug 1.13 confirmed: cql-functions.md has {len(issues)} "
            f"list item(s) with lost or malformed content:\n"
            + "\n".join(
                f"  - Line {line}: {text[:80]}"
                for text, line in issues[:10]
            )
        )

    def test_cql_functions_empty_bullet_before_definition(self):
        """
        Requirement 1.13: cql-functions.md has a specific pattern where
        a bullet point is empty (just "- ") followed by bold text and
        definition-list content on the next line. The content should be
        inline with the bullet.
        """
        content = read_md_file(
            "doc/en/user/data/app-schema/cql-functions.md"
        )
        assert content is not None, "cql-functions.md not found"

        # Find the specific "- \n\n  **preceding/succeeding**:" pattern
        # This is a bullet that lost its content
        pattern = re.compile(
            r'^-\s*\n\s*\n\s+\*\*\w+',
            re.MULTILINE
        )
        matches = pattern.findall(content)

        assert len(matches) == 0, (
            f"Bug 1.13 confirmed: cql-functions.md has {len(matches)} "
            f"empty bullet(s) followed by content that should be inline "
            f"with the bullet marker."
        )

    @given(
        page_path=st.sampled_from(LOST_CONTENT_PAGES)
    )
    @settings(
        max_examples=len(LOST_CONTENT_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_list_items_have_content(self, page_path):
        """
        Requirement 1.13 (PBT): List items should not be empty bullets.
        All list items should retain their content.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        empty_items = find_empty_list_items(content)

        assert len(empty_items) == 0, (
            f"Bug 1.13: {page_path} has {len(empty_items)} empty or "
            f"content-lost list item(s):\n"
            + "\n".join(
                f"  - Line {line}: {text[:80]}"
                for text, line in empty_items[:10]
            )
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all list/nesting requirements
# ---------------------------------------------------------------------------

ALL_LIST_ISSUE_PAGES = list(set(
    IMAGES_IN_LISTS_PAGES +
    BLOCKQUOTED_LIST_PAGES +
    LIST_NESTING_PAGES +
    FLATTENED_LIST_PAGES +
    LOST_CONTENT_PAGES
))


class TestListNestingProperty:
    """Property-based tests across all list and nesting requirements."""

    @given(
        page_path=st.sampled_from(ALL_LIST_ISSUE_PAGES)
    )
    @settings(
        max_examples=min(len(ALL_LIST_ISSUE_PAGES), 25),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_list_nesting_issues(self, page_path):
        """
        Combined property (Req 1.9, 1.10, 1.11, 1.12, 1.13): Pages should
        not have any list/nesting structural issues including blockquoted
        lists, images in code fences, definition-list prefixed numbered
        items, or empty list items.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []

        # Check for images in code fences (Req 1.10)
        img_code = find_images_as_code_blocks(content)
        for img, line in img_code:
            issues.append(
                f"Image in code fence at line {line} (Req 1.10)"
            )

        # Check for blockquoted list items (Req 1.11)
        bq_items = find_blockquoted_list_items(content)
        for text, line in bq_items:
            issues.append(
                f"Blockquoted list item at line {line} (Req 1.11)"
            )

        # Check for definition-list numbered items (Req 1.12)
        deflist_items = find_definition_list_numbered_items(content)
        for text, line in deflist_items:
            issues.append(
                f"Definition-list numbered item at line {line} (Req 1.12)"
            )

        # Check for empty list items (Req 1.13)
        empty_items = find_empty_list_items(content)
        for text, line in empty_items:
            issues.append(
                f"Empty/lost content list item at line {line} (Req 1.13)"
            )

        assert len(issues) == 0, (
            f"List/nesting issues in {page_path}:\n"
            + "\n".join(f"  - {issue}" for issue in issues)
        )
