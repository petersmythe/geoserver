#!/usr/bin/env python3
"""Fix images in list items that were trapped inside code fences during RST-to-Markdown conversion.

Bug condition: The RST-to-Markdown converter wrapped image references (with optional captions)
inside ``` raw_markdown ``` code fences, causing them to render as code blocks instead of images.

Fix: Remove the code fence markers, leaving the image content properly indented so it renders
as an image within the list item (or at the top level).

Preservation: Only targets fences with info string "raw_markdown" whose body contains image
references. Other code fences are left untouched.

Requirements: 1.10, 2.10, 3.4, 3.5
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^(\s*)(`{3,})(.*)")
IMG_RE = re.compile(r"!\[.*?\]\(.*?\)")


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def fix_raw_markdown_image_fences(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Remove raw_markdown code fences that wrap image references.

    Returns (new_lines, list_of_changes).
    """
    result = []
    changes = []
    i = 0
    n = len(lines)

    while i < n:
        m = FENCE_RE.match(lines[i])
        if m and m.group(3).strip() == "raw_markdown":
            fence_indent = m.group(1)
            fence_ticks = m.group(2)
            fence_start = i

            # Collect body lines until closing fence
            body = []
            j = i + 1
            while j < n:
                cm = FENCE_RE.match(lines[j])
                if cm and cm.group(3).strip() == "" and len(cm.group(2)) >= len(fence_ticks):
                    break
                body.append(lines[j])
                j += 1

            # Check if body contains at least one image reference
            body_text = "\n".join(body)
            if IMG_RE.search(body_text):
                # Remove fence markers, keep body lines as-is
                result.extend(body)
                changes.append({
                    "start_line": fence_start + 1,
                    "end_line": j + 1,
                    "body_lines": len(body),
                    "preview": body[0].strip()[:80] if body else "",
                })
                i = j + 1  # skip past closing fence
            else:
                # Not an image fence — keep as-is
                result.append(lines[i])
                i += 1
        else:
            result.append(lines[i])
            i += 1

    return result, changes


def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Apply image-in-code-fence fix to a single file.

    Returns a dict with change details, or empty dict if no changes.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    new_lines, changes = fix_raw_markdown_image_fences(lines)

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
        print("No images trapped in code fences found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    verb = "Would remove" if dry_run else "Removed"

    print(f"{verb} {total} raw_markdown code fence(s) wrapping images "
          f"in {len(all_results)} file(s):\n")

    for r in all_results:
        for c in r["changes"]:
            print(f"  {r['file']}:{c['start_line']}-{c['end_line']} "
                  f"({c['body_lines']} body lines) {c['preview']}")

    print(f"\nSummary: {verb} {total} code fences across {len(all_results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
