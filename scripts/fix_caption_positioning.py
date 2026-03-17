#!/usr/bin/env python3
"""Fix image caption positioning issues from RST-to-Markdown conversion.

Bug condition: Image captions appear as plain italic text on the line
immediately after the image, with no blank line separating them. This
causes the caption to render inline/beside the image instead of below it.

Fix: Insert a blank line between the image and its caption so Markdown
treats them as separate blocks (image above, caption paragraph below).

Two patterns are handled:

Pattern A – Unfigured captions (indented or top-level):
    ![](path/to/image.png)
    *Caption text*
  Becomes:
    ![](path/to/image.png)

    *Caption text*

Pattern B – Blockquote image+caption pairs:
    > ![](path/to/image.png)
    > *Caption text*
  Becomes:
    > ![](path/to/image.png)
    >
    > *Caption text*

Preservation: Images without captions, images already separated by a
blank line from their caption, and non-caption italic text are unchanged.

Requirements: 1.17, 2.17, 3.5
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

# Regex patterns
IMAGE_RE = re.compile(r'^(\s*)!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?\s*$')
BQ_IMAGE_RE = re.compile(r'^(\s*)>\s*!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?\s*$')
CAPTION_RE = re.compile(r'^(\s*)\*([A-Z].+)\*\s*$')
BQ_CAPTION_RE = re.compile(r'^(\s*)>\s*\*(.+)\*\s*$')
FENCE_RE = re.compile(r'^\s*```')


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def fix_captions(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Insert blank lines between images and their captions.

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

        # Pattern B: blockquote image + blockquote caption (no blank line)
        bq_img = BQ_IMAGE_RE.match(line)
        if bq_img and i + 1 < n:
            next_line = lines[i + 1]
            bq_cap = BQ_CAPTION_RE.match(next_line)
            if bq_cap:
                indent = bq_img.group(1)
                caption = bq_cap.group(2)
                # Add image line, then a blank blockquote line, then caption
                result.append(line)
                result.append(f'{indent}>')
                result.append(next_line)
                changes.append({
                    'line': i + 1,
                    'type': 'blockquote_caption',
                    'caption': caption,
                })
                i += 2
                continue

        # Pattern A: image + italic caption on next line (no blank line)
        img = IMAGE_RE.match(line)
        if img and i + 1 < n:
            next_line = lines[i + 1]
            cap = CAPTION_RE.match(next_line)
            if cap:
                caption = cap.group(2)
                # Add image line, then a blank line, then caption
                result.append(line)
                result.append('')
                result.append(next_line)
                changes.append({
                    'line': i + 1,
                    'type': 'unfigured_caption',
                    'caption': caption,
                })
                i += 2
                continue

        result.append(line)
        i += 1

    return result, changes


def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Apply caption positioning fix to a single file.

    Returns a dict with change details, or empty dict if no changes.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    new_lines, changes = fix_captions(lines)

    if not changes:
        return {}

    if not dry_run:
        filepath.write_text("\n".join(new_lines), encoding="utf-8")

    return {"file": rel, "changes": changes}


def main():
    import io
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
        print("No caption positioning issues found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    bq_count = sum(1 for r in all_results for c in r["changes"] if c["type"] == "blockquote_caption")
    uf_count = sum(1 for r in all_results for c in r["changes"] if c["type"] == "unfigured_caption")
    verb = "Would fix" if dry_run else "Fixed"

    print(f"{verb} {total} caption positioning issue(s) in {len(all_results)} file(s):")
    print(f"  - Blockquote image+caption pairs: {bq_count}")
    print(f"  - Unfigured captions (italic after image): {uf_count}")
    print()

    for r in all_results:
        for c in r["changes"]:
            print(f"  {r['file']}:{c['line']}  [{c['type']}]  \"{c['caption'][:60]}\"")

    print(f"\nSummary: {verb} {total} captions across {len(all_results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
