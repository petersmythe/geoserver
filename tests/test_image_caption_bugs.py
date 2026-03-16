#!/usr/bin/env python3
"""
Bug Condition Exploration Test: Image and Caption Rendering Bugs

**Property 1: Bug Condition** - Image and Caption Issues
**CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
**DO NOT attempt to fix the test or the code when it fails.**

Validates: Requirements 1.17, 1.18, 2.17, 2.18

Tests concrete failing cases from Andrea's review feedback:
- Image captions appear below images, not beside them (Req 1.17, 2.17)
- Images don't have blockquote wrapping (Req 1.18, 2.18)
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


def find_blockquote_wrapped_images(content):
    """
    Find images that are incorrectly wrapped in blockquote syntax.

    In the RST source, these images were indented (e.g. inside a list step
    or a directive). The converter turned the indentation into Markdown
    blockquote prefix "> ", producing lines like:
        > ![](path/to/image.png)

    This causes the image to render inside a styled blockquote box instead
    of as a normal inline image.

    Returns list of (image_ref, line_number) tuples.
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

        # Pattern: blockquote-prefixed image
        # e.g. "> ![](images/foo.png)" or ">     ![image](path.png)"
        m = re.match(r'^>\s*!\[([^\]]*)\]\(([^)]+)\)', line)
        if m:
            image_ref = m.group(2)
            results.append((image_ref, i + 1))

    return results


def find_blockquote_captions(content):
    """
    Find image captions that are inside blockquotes alongside their images.

    The pattern is:
        > ![](image.png)
        > *Caption text*

    In the original RST, the caption was part of a ``.. figure::`` directive
    and rendered below the image. The converter placed both the image and
    the caption inside a blockquote, causing the caption to appear as
    blockquoted italic text beside/below the image rather than as a proper
    figure caption.

    Returns list of (caption_text, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False
    prev_was_bq_image = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            prev_was_bq_image = False
            continue
        if in_fence:
            prev_was_bq_image = False
            continue

        is_bq_image = bool(re.match(r'^>\s*!\[', line))

        # Caption line: "> *Some caption text*"
        m = re.match(r'^>\s*\*(.+)\*\s*$', line)
        if m and prev_was_bq_image:
            results.append((m.group(1), i + 1))

        prev_was_bq_image = is_bq_image

    return results


def find_images_in_raw_markdown_blocks(content):
    """
    Find images trapped inside ``` raw_markdown code blocks.

    The converter sometimes wrapped image+caption combinations in
    fenced code blocks with a ``raw_markdown`` info string. These
    render as literal code text instead of actual images.

    Returns list of (image_ref, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_raw_block = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```\s*raw_markdown', line):
            in_raw_block = True
            continue
        if in_raw_block and re.match(r'^\s*```\s*$', line):
            in_raw_block = False
            continue
        if in_raw_block:
            m = re.match(r'^\s*!\[([^\]]*)\]\(([^)]+)\)', line)
            if m:
                results.append((m.group(2), i + 1))

    return results


def find_unfigured_captions(content):
    """
    Find image captions that are plain italic text on the line after an
    image, without any figure/caption markup.

    The pattern is (inside a list item or at top level):
        ![](image.png)
        *Caption text*

    In proper Markdown with MkDocs, images with captions should use an
    HTML <figure> element or the attr_list / md_in_html extension so
    the caption is semantically associated with the image. Plain italic
    text on the next line renders as a separate paragraph, not as a
    figure caption.

    Returns list of (caption_text, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False
    prev_was_image = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            prev_was_image = False
            continue
        if in_fence:
            prev_was_image = False
            continue

        is_image = bool(re.match(r'^\s*!\[', line))

        # Caption line: "    *Some caption text*" (indented italic)
        m = re.match(r'^\s+\*([A-Z].*)\*\s*$', line)
        if m and prev_was_image:
            results.append((m.group(1), i + 1))

        prev_was_bq_image = False
        prev_was_image = is_image

    return results


# ---------------------------------------------------------------------------
# Requirement 1.18 / 2.18: Images must not have blockquote wrapping
# ---------------------------------------------------------------------------

# Pages where images are incorrectly wrapped in blockquote syntax
BLOCKQUOTE_IMAGE_PAGES = [
    "doc/en/user/tutorials/imagemosaic_footprint/imagemosaic_footprint.md",
    "doc/en/user/security/tutorials/activedirectory/index.md",
    "doc/en/user/security/tutorials/ldap/index.md",
    "doc/en/user/security/tutorials/cert/index.md",
    "doc/en/user/security/tutorials/j2ee/index.md",
    "doc/en/user/security/tutorials/httpheaderproxy/index.md",
    "doc/en/user/extensions/wps-download/index.md",
    "doc/en/user/extensions/wps-download/rawDownload.md",
    "doc/en/user/extensions/metadata/uiconfiguration.md",
    "doc/en/user/extensions/monitoring/overview.md",
    "doc/en/user/extensions/monitoring/installation.md",
    "doc/en/user/extensions/importer/configuring.md",
    "doc/en/user/extensions/kml/quickstart.md",
    "doc/en/user/extensions/kml/tutorials/kmlplacemark/index.md",
    "doc/en/user/extensions/cas/index.md",
    "doc/en/user/gettingstarted/postgis-quickstart/index.md",
    "doc/en/user/gettingstarted/image-quickstart/index.md",
    "doc/en/user/gettingstarted/geopkg-quickstart/index.md",
    "doc/en/user/gettingstarted/group-quickstart/index.md",
    "doc/en/user/data/webadmin/layers.md",
    "doc/en/user/configuration/virtual-services.md",
    "doc/en/user/styling/workshop/css/polygon.md",
    "doc/en/user/styling/workshop/mbstyle/polygon.md",
]


# Pages where blockquote images also have captions in blockquotes
BLOCKQUOTE_CAPTION_PAGES = [
    "doc/en/user/extensions/monitoring/overview.md",
    "doc/en/user/extensions/monitoring/installation.md",
    "doc/en/user/extensions/importer/configuring.md",
    "doc/en/user/extensions/kml/quickstart.md",
    "doc/en/user/extensions/kml/tutorials/kmlplacemark/index.md",
    "doc/en/user/extensions/metadata/uiconfiguration.md",
    "doc/en/user/gettingstarted/postgis-quickstart/index.md",
    "doc/en/user/gettingstarted/image-quickstart/index.md",
    "doc/en/user/gettingstarted/geopkg-quickstart/index.md",
    "doc/en/user/gettingstarted/group-quickstart/index.md",
    "doc/en/user/data/webadmin/layers.md",
    "doc/en/user/configuration/virtual-services.md",
]


class TestBlockquoteWrappedImages:
    """Test that images are not incorrectly wrapped in blockquote syntax."""

    def test_imagemosaic_footprint_no_blockquote_images(self):
        """
        Requirement 1.18: imagemosaic_footprint.md has multiple images
        wrapped in blockquote syntax (> ![](img/...)).

        These images were indented in the original RST (inside list items
        or directives) and the converter turned the indentation into
        blockquote prefixes. They should render as normal images.
        """
        content = read_md_file(
            "doc/en/user/tutorials/imagemosaic_footprint/imagemosaic_footprint.md"
        )
        assert content is not None, "imagemosaic_footprint.md not found"

        bq_images = find_blockquote_wrapped_images(content)

        assert len(bq_images) == 0, (
            f"Bug 1.18 confirmed: imagemosaic_footprint.md has "
            f"{len(bq_images)} image(s) wrapped in blockquote syntax:\n"
            + "\n".join(
                f"  - Line {line}: '> ![...]({img})'"
                for img, line in bq_images
            )
            + "\n  Images should render without blockquote wrapping"
        )

    def test_kml_quickstart_no_blockquote_images(self):
        """
        Requirement 1.18: kml/quickstart.md has images wrapped in
        blockquote syntax with captions also in blockquotes.

        The Google Earth screenshots should be normal images, not
        rendered inside blockquote boxes.
        """
        content = read_md_file("doc/en/user/extensions/kml/quickstart.md")
        assert content is not None, "kml/quickstart.md not found"

        bq_images = find_blockquote_wrapped_images(content)

        assert len(bq_images) == 0, (
            f"Bug 1.18 confirmed: kml/quickstart.md has "
            f"{len(bq_images)} image(s) wrapped in blockquote syntax:\n"
            + "\n".join(
                f"  - Line {line}: '> ![...]({img})'"
                for img, line in bq_images
            )
        )

    def test_metadata_uiconfiguration_no_blockquote_images(self):
        """
        Requirement 1.18: metadata/uiconfiguration.md has many field type
        screenshots wrapped in blockquote syntax. Each field type example
        (TEXT, TEXTAREA, UUID, NUMBER, etc.) has its image in a blockquote.
        """
        content = read_md_file(
            "doc/en/user/extensions/metadata/uiconfiguration.md"
        )
        assert content is not None, "metadata/uiconfiguration.md not found"

        bq_images = find_blockquote_wrapped_images(content)

        assert len(bq_images) == 0, (
            f"Bug 1.18 confirmed: metadata/uiconfiguration.md has "
            f"{len(bq_images)} image(s) wrapped in blockquote syntax:\n"
            + "\n".join(
                f"  - Line {line}: '> ![...]({img})'"
                for img, line in bq_images
            )
        )

    def test_security_tutorials_no_blockquote_images(self):
        """
        Requirement 1.18: Security tutorial pages (LDAP, ActiveDirectory,
        cert, J2EE) have login/configuration screenshots wrapped in
        blockquote syntax.
        """
        security_pages = [
            "doc/en/user/security/tutorials/ldap/index.md",
            "doc/en/user/security/tutorials/activedirectory/index.md",
            "doc/en/user/security/tutorials/cert/index.md",
            "doc/en/user/security/tutorials/j2ee/index.md",
        ]
        all_issues = []
        for page_path in security_pages:
            content = read_md_file(page_path)
            if content is None:
                continue
            bq_images = find_blockquote_wrapped_images(content)
            for img, line in bq_images:
                all_issues.append((page_path, img, line))

        assert len(all_issues) == 0, (
            f"Bug 1.18 confirmed: Security tutorials have "
            f"{len(all_issues)} image(s) wrapped in blockquote syntax:\n"
            + "\n".join(
                f"  - {path} line {line}: '> ![...]({img})'"
                for path, img, line in all_issues
            )
        )

    @given(page_path=st.sampled_from(BLOCKQUOTE_IMAGE_PAGES))
    @settings(
        max_examples=len(BLOCKQUOTE_IMAGE_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_blockquote_wrapped_images(self, page_path):
        """
        Requirement 1.18 (PBT): No page should have images wrapped in
        blockquote syntax. Images should render without blockquote styling.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        bq_images = find_blockquote_wrapped_images(content)

        assert len(bq_images) == 0, (
            f"Bug 1.18: {page_path} has {len(bq_images)} image(s) "
            f"wrapped in blockquote syntax:\n"
            + "\n".join(
                f"  - Line {line}: '> ![...]({img})'"
                for img, line in bq_images
            )
        )


# ---------------------------------------------------------------------------
# Requirement 1.17 / 2.17: Image captions must appear below images using
# proper figure markup, not as italic text beside them
# ---------------------------------------------------------------------------

# Pages where captions are plain italic text after images (not in a figure)
# These render as separate paragraphs, not as semantically associated captions
UNFIGURED_CAPTION_PAGES = [
    "doc/en/user/installation/win_installer.md",
    "doc/en/user/installation/win_binary.md",
    "doc/en/user/installation/war.md",
    "doc/en/user/installation/linux.md",
    "doc/en/user/installation/docker.md",
    "doc/en/user/styling/workshop/design/symbology.md",
    "doc/en/user/styling/workshop/ysld/ysld.md",
    "doc/en/user/styling/workshop/css/css.md",
    "doc/en/user/styling/workshop/mbstyle/mbstyle.md",
    "doc/en/user/styling/ysld/reference/symbolizers/index.md",
    "doc/en/user/styling/ysld/reference/scalezoom.md",
    "doc/en/user/services/wfs/axis_order.md",
]

# Pages where images are trapped inside ``` raw_markdown code blocks
RAW_MARKDOWN_IMAGE_PAGES = [
    "doc/en/user/styling/qgis/index.md",
    "doc/en/user/data/raster/imagemosaic/tutorial.md",
]


class TestImageCaptionPositioning:
    """Test that image captions appear below images with proper figure markup."""

    def test_win_installer_captions_are_figures(self):
        """
        Requirement 1.17: win_installer.md has 13 images each followed by
        an italic caption like "*Downloading the Windows installer*".

        These captions are plain italic text on the line after the image,
        not semantically associated with the image via figure markup.
        In the original RST, these were ``.. figure::`` directives with
        proper captions. They should use HTML <figure>/<figcaption> or
        equivalent MkDocs figure syntax.
        """
        content = read_md_file("doc/en/user/installation/win_installer.md")
        assert content is not None, "win_installer.md not found"

        unfigured = find_unfigured_captions(content)

        assert len(unfigured) == 0, (
            f"Bug 1.17 confirmed: win_installer.md has "
            f"{len(unfigured)} caption(s) as plain italic text "
            f"instead of proper figure captions:\n"
            + "\n".join(
                f"  - Line {line}: '*{caption}*'"
                for caption, line in unfigured
            )
            + "\n  Captions should use <figure>/<figcaption> or "
            "MkDocs figure syntax"
        )

    def test_symbology_workshop_captions_are_figures(self):
        """
        Requirement 1.17: styling/workshop/design/symbology.md has many
        Color Brewer screenshots with italic captions that are not
        semantically associated with their images.
        """
        content = read_md_file(
            "doc/en/user/styling/workshop/design/symbology.md"
        )
        assert content is not None, "symbology.md not found"

        unfigured = find_unfigured_captions(content)

        assert len(unfigured) == 0, (
            f"Bug 1.17 confirmed: symbology.md has "
            f"{len(unfigured)} caption(s) as plain italic text:\n"
            + "\n".join(
                f"  - Line {line}: '*{caption}*'"
                for caption, line in unfigured
            )
        )

    def test_blockquote_captions_not_in_blockquotes(self):
        """
        Requirement 1.17: Pages with blockquote-wrapped images also have
        their captions inside blockquotes ("> *Caption text*"). The
        caption should be a proper figure caption, not blockquoted italic.
        """
        all_issues = []
        for page_path in BLOCKQUOTE_CAPTION_PAGES:
            content = read_md_file(page_path)
            if content is None:
                continue
            bq_captions = find_blockquote_captions(content)
            for caption, line in bq_captions:
                all_issues.append((page_path, caption, line))

        assert len(all_issues) == 0, (
            f"Bug 1.17 confirmed: {len(all_issues)} caption(s) are inside "
            f"blockquotes instead of using proper figure markup:\n"
            + "\n".join(
                f"  - {path} line {line}: '> *{caption}*'"
                for path, caption, line in all_issues[:15]
            )
            + (f"\n  ... and {len(all_issues) - 15} more"
               if len(all_issues) > 15 else "")
        )

    def test_imagemosaic_tutorial_images_not_in_code_blocks(self):
        """
        Requirement 1.17: data/raster/imagemosaic/tutorial.md has images
        trapped inside ``` raw_markdown code blocks. These render as
        literal code text instead of actual images with captions.
        """
        content = read_md_file(
            "doc/en/user/data/raster/imagemosaic/tutorial.md"
        )
        assert content is not None, "imagemosaic/tutorial.md not found"

        raw_images = find_images_in_raw_markdown_blocks(content)

        assert len(raw_images) == 0, (
            f"Bug 1.17 confirmed: imagemosaic/tutorial.md has "
            f"{len(raw_images)} image(s) trapped in raw_markdown "
            f"code blocks:\n"
            + "\n".join(
                f"  - Line {line}: '![...]({img})' inside ``` raw_markdown"
                for img, line in raw_images
            )
            + "\n  Images should render as actual images, not code text"
        )

    def test_qgis_images_not_in_code_blocks(self):
        """
        Requirement 1.17: styling/qgis/index.md has 15+ images trapped
        inside ``` raw_markdown code blocks. All QGIS screenshots and
        GeoServer upload/preview images render as literal code.
        """
        content = read_md_file("doc/en/user/styling/qgis/index.md")
        assert content is not None, "qgis/index.md not found"

        raw_images = find_images_in_raw_markdown_blocks(content)

        assert len(raw_images) == 0, (
            f"Bug 1.17 confirmed: qgis/index.md has "
            f"{len(raw_images)} image(s) trapped in raw_markdown "
            f"code blocks:\n"
            + "\n".join(
                f"  - Line {line}: '![...]({img})' inside ``` raw_markdown"
                for img, line in raw_images
            )
        )

    @given(page_path=st.sampled_from(UNFIGURED_CAPTION_PAGES))
    @settings(
        max_examples=len(UNFIGURED_CAPTION_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_unfigured_captions(self, page_path):
        """
        Requirement 1.17 (PBT): Image captions should use proper figure
        markup, not plain italic text on the line after the image.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        unfigured = find_unfigured_captions(content)

        assert len(unfigured) == 0, (
            f"Bug 1.17: {page_path} has {len(unfigured)} caption(s) "
            f"as plain italic text instead of figure captions:\n"
            + "\n".join(
                f"  - Line {line}: '*{caption}*'"
                for caption, line in unfigured
            )
        )

    @given(page_path=st.sampled_from(RAW_MARKDOWN_IMAGE_PAGES))
    @settings(
        max_examples=len(RAW_MARKDOWN_IMAGE_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_images_in_raw_markdown_blocks(self, page_path):
        """
        Requirement 1.17 (PBT): Images should not be trapped inside
        ``` raw_markdown code blocks. They should render as actual images.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        raw_images = find_images_in_raw_markdown_blocks(content)

        assert len(raw_images) == 0, (
            f"Bug 1.17: {page_path} has {len(raw_images)} image(s) "
            f"trapped in raw_markdown code blocks:\n"
            + "\n".join(
                f"  - Line {line}: '![...]({img})'"
                for img, line in raw_images
            )
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all image/caption requirements
# ---------------------------------------------------------------------------

ALL_IMAGE_CAPTION_ISSUE_PAGES = list(set(
    BLOCKQUOTE_IMAGE_PAGES +
    BLOCKQUOTE_CAPTION_PAGES +
    UNFIGURED_CAPTION_PAGES +
    RAW_MARKDOWN_IMAGE_PAGES
))


class TestImageCaptionProperty:
    """Property-based tests across all image and caption requirements."""

    @given(page_path=st.sampled_from(ALL_IMAGE_CAPTION_ISSUE_PAGES))
    @settings(
        max_examples=min(len(ALL_IMAGE_CAPTION_ISSUE_PAGES), 40),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_image_caption_issues(self, page_path):
        """
        Combined property (Req 1.17, 1.18): Pages should not have any
        image/caption rendering issues including blockquote-wrapped images,
        blockquoted captions, unfigured captions, or images trapped in
        raw_markdown code blocks.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []

        # Check for blockquote-wrapped images (Req 1.18)
        bq_images = find_blockquote_wrapped_images(content)
        for img, line in bq_images:
            issues.append(
                f"Blockquote-wrapped image '{img}' at line {line} (Req 1.18)"
            )

        # Check for blockquote captions (Req 1.17)
        bq_captions = find_blockquote_captions(content)
        for caption, line in bq_captions:
            issues.append(
                f"Blockquoted caption '*{caption}*' at line {line} (Req 1.17)"
            )

        # Check for unfigured captions (Req 1.17)
        unfigured = find_unfigured_captions(content)
        for caption, line in unfigured:
            issues.append(
                f"Unfigured caption '*{caption}*' at line {line} (Req 1.17)"
            )

        # Check for images in raw_markdown blocks (Req 1.17)
        raw_images = find_images_in_raw_markdown_blocks(content)
        for img, line in raw_images:
            issues.append(
                f"Image '{img}' in raw_markdown block at line {line} (Req 1.17)"
            )

        assert len(issues) == 0, (
            f"Image/caption issues in {page_path}:\n"
            + "\n".join(f"  - {issue}" for issue in issues)
        )
