#!/usr/bin/env python3
"""Fix blockquote-wrapped images from RST-to-Markdown conversion.

Bug condition: Images incorrectly wrapped in blockquote syntax (> ![...](path))
when they should be standalone images. This happens because the RST converter
wrapped indented images in blockquote markers.

Two sub-patterns are fixed:

Pattern A – Standalone blockquote image (no caption):
    > ![](path/to/image.png)
  Becomes:
    ![](path/to/image.png)

Pattern B – Blockquote image + caption only (no other text):
    > ![](path/to/image.png)
    >
    > *Caption text*
  Becomes:
    ![](path/to/image.png)

    *Caption text*

  Also handles the pre-fix-caption variant (no blank > line):
    > ![](path/to/image.png)
    > *Caption text*
  Becomes:
    ![](path/to/image.png)

    *Caption text*

Preservation: Images inside blockquotes that also contain regular text
paragraphs are NOT modified — those are legitimate blockquote contexts.

Requirements: 1.18, 2.18, 3.5
"""

import re
import sys
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r'^\s*```')
BQ_IMAGE_RE = re.compile(r'^(\s*)>\s*!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?\s*$')
BQ_BLANK_RE = re.compile(r'^(\s*)>\s*$')
BQ_CAPTION_RE = re.compile(r'^(\s*)>\s*\*(.+)\*\s*$')
BQ_TEXT_RE = re.compile(r'^(\s*)>\s*\S')


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def is_blockquote_line(line):
    """Check if a line is a blockquote continuation (starts with >)."""
    return bool(re.match(r'^\s*>', line))


def get_blockquote_block(lines, start_idx):
    """Given a blockquote image at start_idx, find the full blockquote block.

    Returns (block_lines, end_idx) where block_lines are the consecutive
    blockquote lines and end_idx is the index after the last blockquote line.
    """
    block = []
    i = start_idx
    while i < len(lines) and is_blockquote_line(lines[i]):
        block.append(lines[i])
        i += 1
    return block, i


def block_is_image_only(block):
    """Check if a blockquote block contains ONLY an image and optionally a caption.

    Returns (True, image_line_idx, caption_line_idx_or_None) if the block
    is just image (+ optional blank > lines + optional caption).
    Returns (False, None, None) otherwise.
    """
    # Filter out blank blockquote lines (just ">")
    content_lines = []
    for idx, line in enumerate(block):
        stripped = re.sub(r'^\s*>\s?', '', line).strip()
        if stripped:
            content_lines.append((idx, stripped, line))

    if not content_lines:
        return False, None, None

    # First content line must be an image
    first_idx, first_text, first_raw = content_lines[0]
    if not re.match(r'^!\[', first_text):
        return False, None, None

    if len(content_lines) == 1:
        # Just an image, no caption
        return True, first_idx, None

    if len(content_lines) == 2:
        # Image + one more line — check if it's a caption (*text*)
        second_idx, second_text, second_raw = content_lines[1]
        if re.match(r'^\*(.+)\*$', second_text):
            return True, first_idx, second_idx
        # Not a caption — this is a text blockquote with an image
        return False, None, None

    # More than 2 content lines — this is a legitimate blockquote
    return False, None, None


def check_context_is_legitimate_blockquote(lines, block_start, block_end):
    """Check if the blockquote block is part of a larger blockquote context.

    Look at lines immediately before block_start to see if there's blockquote
    text leading into this image. If so, the image is part of a legitimate
    blockquote and should be preserved.

    Also look at lines after block_end for the same reason.
    """
    # Check lines before the block
    i = block_start - 1
    while i >= 0:
        line = lines[i].strip()
        if not line:
            # Blank non-blockquote line — end of blockquote context
            break
        if is_blockquote_line(lines[i]):
            content = re.sub(r'^\s*>\s?', '', lines[i]).strip()
            if not content:
                # Blank blockquote line (just ">") — keep looking back
                i -= 1
                continue
            if not re.match(r'^!\[', content) and not re.match(r'^\*(.+)\*$', content):
                # Found actual text in the blockquote — legitimate context
                return True
            # It's another image or caption — keep looking back
            i -= 1
            continue
        # Non-blockquote, non-blank line — end of search
        break

    # Check lines after the block
    i = block_end
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            break
        if is_blockquote_line(lines[i]):
            content = re.sub(r'^\s*>\s?', '', lines[i]).strip()
            if not content:
                i += 1
                continue
            if not re.match(r'^!\[', content) and not re.match(r'^\*(.+)\*$', content):
                return True
            i += 1
            continue
        break

    return False


def strip_blockquote_prefix(line):
    """Remove the blockquote '> ' prefix from a line, preserving other indentation."""
    # Match "> " or ">" at the start (with optional leading whitespace)
    return re.sub(r'^(\s*)>\s?', r'\1', line)


def fix_blockquote_images(lines):
    """Remove blockquote wrapping from standalone images.

    Returns (new_lines, list_of_changes).
    """
    result = []
    changes = []
    i = 0
    n = len(lines)
    in_fence = False

    while i < n:
        line = lines[i]

        # Track fenced code blocks
        if FENCE_RE.match(line):
            in_fence = not in_fence
            result.append(line)
            i += 1
            continue

        if in_fence:
            result.append(line)
            i += 1
            continue

        # Check for blockquote image
        bq_img = BQ_IMAGE_RE.match(line)
        if not bq_img:
            result.append(line)
            i += 1
            continue

        # Found a blockquote image — analyze the full blockquote block
        block, block_end = get_blockquote_block(lines, i)
        is_img_only, img_idx, caption_idx = block_is_image_only(block)

        if not is_img_only:
            # Image is part of a larger blockquote — preserve
            for bl in block:
                result.append(bl)
            i = block_end
            continue

        # Check if this block is preceded by blockquote text (legitimate context)
        if check_context_is_legitimate_blockquote(lines, i, block_end):
            for bl in block:
                result.append(bl)
            i = block_end
            continue

        # This is a standalone blockquote image — remove the > prefix
        image_line = strip_blockquote_prefix(block[img_idx])
        result.append(image_line)

        if caption_idx is not None:
            # Add blank line between image and caption
            result.append('')
            caption_line = strip_blockquote_prefix(block[caption_idx])
            result.append(caption_line)
            changes.append({
                'line': i + 1,
                'type': 'blockquote_image_with_caption',
                'image': bq_img.group(3),
            })
        else:
            changes.append({
                'line': i + 1,
                'type': 'blockquote_image_standalone',
                'image': bq_img.group(3),
            })

        i = block_end
        continue

    return result, changes


def fix_file(filepath, dry_run=False):
    """Apply blockquote image fix to a single file.

    Returns a dict with change details, or empty dict if no changes.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    new_lines, changes = fix_blockquote_images(lines)

    if not changes:
        return {}

    if not dry_run:
        filepath.write_text("\n".join(new_lines), encoding="utf-8")

    return {"file": rel, "changes": changes}


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN -- no files will be modified ===\n")

    all_results = []
    for md_file in iter_md_files():
        result = fix_file(md_file, dry_run=dry_run)
        if result:
            all_results.append(result)

    if not all_results:
        print("No blockquote-wrapped image issues found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    standalone = sum(1 for r in all_results for c in r["changes"] if c["type"] == "blockquote_image_standalone")
    with_caption = sum(1 for r in all_results for c in r["changes"] if c["type"] == "blockquote_image_with_caption")
    verb = "Would fix" if dry_run else "Fixed"

    print(f"{verb} {total} blockquote-wrapped image(s) in {len(all_results)} file(s):")
    print(f"  - Standalone blockquote images: {standalone}")
    print(f"  - Blockquote images with captions: {with_caption}")
    print()

    for r in all_results:
        for c in r["changes"]:
            print(f"  {r['file']}:{c['line']}  [{c['type']}]  {c['image'][:80]}")

    print(f"\nSummary: {verb} {total} blockquote-wrapped images across {len(all_results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
