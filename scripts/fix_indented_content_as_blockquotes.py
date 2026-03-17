#!/usr/bin/env python3
"""Fix indented list content that was incorrectly converted to blockquotes.

Bug condition: The RST-to-Markdown converter wrapped continuation content inside
list items (images, text, admonitions, tables) with blockquote markers (> ...),
causing them to render as quoted content instead of normal indented list content.

Fix: Remove the blockquote prefix (>) and indent the content to align with the
parent list item's text, so it renders as continuation content within the list.

Preservation: Only targets blockquote blocks that immediately follow a list item
(bullet or numbered). Standalone blockquotes not preceded by list items are left
untouched.

Requirements: 1.11, 2.11, 3.4
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

# Regex patterns
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+")
BQ_RE = re.compile(r"^(\s*)>\s?(.*)")


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def _content_indent_for_list(line: str) -> int:
    """Calculate the indentation level for continuation content of a list item.

    For bullet lists (- item), content aligns at marker_indent + 2.
    For numbered lists (1. item), content aligns at marker_indent + 4.
    """
    m = LIST_RE.match(line)
    if not m:
        return 4  # fallback
    marker_indent = len(m.group(1))
    marker = m.group(2)
    if marker in ("-", "*"):
        return marker_indent + 2
    else:
        # numbered: "1." -> align with text after "1.  "
        return marker_indent + 4


def fix_blockquoted_list_content(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Remove blockquote markers from continuation content inside list items.

    Scans for blockquote blocks (lines starting with >) that appear as
    continuation content after a list item. Replaces the > prefix with
    proper indentation so the content is part of the list item.

    Returns (new_lines, list_of_changes).
    """
    result: list[str] = []
    changes: list[dict] = []
    n = len(lines)
    i = 0

    in_fence = False

    # Track the most recent list item we've seen
    last_list_line: int | None = None
    last_list_content_indent: int = 4

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # --- Track code fences (skip everything inside) ---
        fm = FENCE_RE.match(line)
        if fm:
            in_fence = not in_fence
            result.append(line)
            i += 1
            last_list_line = None
            continue
        if in_fence:
            result.append(line)
            i += 1
            continue

        # --- Detect list items ---
        lm = LIST_RE.match(line)
        if lm:
            last_list_line = i
            last_list_content_indent = _content_indent_for_list(line)
            result.append(line)
            i += 1
            continue

        # --- Detect blockquote block after a list item ---
        if last_list_line is not None and BQ_RE.match(line):
            # Collect the full contiguous blockquote block
            block_start = i
            block_lines: list[str] = []
            j = i
            while j < n:
                bm = BQ_RE.match(lines[j])
                if bm:
                    block_lines.append(lines[j])
                    j += 1
                elif lines[j].strip() == "" and j + 1 < n and BQ_RE.match(lines[j + 1]):
                    # Blank line between blockquote lines — part of the block
                    block_lines.append(lines[j])
                    j += 1
                else:
                    break
            block_end = j

            # Unquote: replace > prefix with proper indentation
            indent_str = " " * last_list_content_indent
            fixed_lines: list[str] = []
            for bl in block_lines:
                bm = BQ_RE.match(bl)
                if bm:
                    content = bm.group(2)
                    if content:
                        fixed_lines.append(indent_str + content)
                    else:
                        # Empty blockquote continuation line -> blank line
                        fixed_lines.append("")
                else:
                    # Blank line within block (not a > line)
                    fixed_lines.append(bl)

            result.extend(fixed_lines)
            changes.append({
                "start_line": block_start + 1,
                "end_line": block_end,
                "lines_fixed": len(block_lines),
                "indent": last_list_content_indent,
                "preview": block_lines[0].strip()[:80] if block_lines else "",
            })
            i = block_end
            continue

        # --- Non-list, non-blockquote line ---
        if stripped == "":
            # Blank lines don't reset list context (continuation may follow)
            result.append(line)
            i += 1
            continue

        # Any other content resets list context
        last_list_line = None
        result.append(line)
        i += 1

    return result, changes


def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Apply blockquote-to-indent fix to a single file.

    Returns a dict with change details, or empty dict if no changes.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    new_lines, changes = fix_blockquoted_list_content(lines)

    if not changes:
        return {}

    if not dry_run:
        filepath.write_text("\n".join(new_lines), encoding="utf-8")

    return {"file": rel, "changes": changes}


def main():
    import io

    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN -- no files will be modified ===\n")

    all_results = []
    for md_file in iter_md_files():
        result = fix_file(md_file, dry_run=dry_run)
        if result:
            all_results.append(result)

    if not all_results:
        print("No blockquoted list content found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    verb = "Would fix" if dry_run else "Fixed"

    print(
        f"{verb} {total} blockquote block(s) in list items "
        f"across {len(all_results)} file(s):\n"
    )

    for r in all_results:
        for c in r["changes"]:
            print(
                f"  {r['file']}:{c['start_line']}-{c['end_line']} "
                f"({c['lines_fixed']} lines, indent={c['indent']}) "
                f"{c['preview']}"
            )

    print(f"\nSummary: {verb} {total} blockquote blocks across {len(all_results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
