#!/usr/bin/env python3
"""Fix numbered lists that were flattened by the RST-to-Markdown converter.

Bug condition: The converter prepended a definition-list prefix (":   ") to
numbered list items, causing them to render as a solid text block instead of
a proper numbered list.

Pattern detected:
    :   1.  First item
        2.  Second item
        3.  Third item

Fix: Remove the definition-list prefix (":   ") from the first item and
un-indent continuation items so they form a proper Markdown numbered list.
When the block appears inside a parent list item, the resulting sub-list is
indented to align with the parent's content.

Preservation: Only targets lines matching the ":   <number>." pattern.
Correctly formatted numbered lists are left untouched.

Requirements: 1.12, 2.12, 3.4
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
# First item of a definition-list-prefixed numbered list:  ":   1.  text"
# Captures: (leading_ws)(colon + spaces)(number. )(text)
DEFLIST_FIRST_RE = re.compile(r"^(\s*):([ \t]+)(\d+\.\s+)(.*)")
# Continuation numbered items at the same indent as items 2..N
NUMBERED_ITEM_RE = re.compile(r"^(\s*)(\d+\.\s+)(.*)")
# Parent list item (bullet or numbered) — used to detect sub-list context
PARENT_LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+")


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def _find_parent_list_indent(lines: list[str], idx: int) -> int | None:
    """Walk backwards from *idx* to find the nearest parent list item.

    Returns the content-indent of that parent (i.e. where sub-list items
    should start), or None if no parent list item is found.
    """
    for j in range(idx - 1, -1, -1):
        stripped = lines[j].strip()
        if stripped == "":
            continue
        m = PARENT_LIST_RE.match(lines[j])
        if m:
            marker_indent = len(m.group(1))
            marker = m.group(2)
            # Content starts after "- " (2) or "1. " (4)
            if marker in ("-", "*"):
                return marker_indent + 2
            else:
                return marker_indent + 4
        # If we hit a non-blank, non-list line, stop searching
        break
    return None


def fix_flattened_numbered_lists(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Remove definition-list prefix from numbered list blocks.

    Scans for blocks that start with ":   1.  text" followed by continuation
    items "    2.  text", "    3.  text", etc.  Strips the colon prefix and
    adjusts indentation so items form a proper Markdown numbered list.

    Returns (new_lines, list_of_changes).
    """
    result: list[str] = []
    changes: list[dict] = []
    n = len(lines)
    i = 0
    in_fence = False

    while i < n:
        line = lines[i]

        # Track code fences
        if FENCE_RE.match(line):
            in_fence = not in_fence
            result.append(line)
            i += 1
            continue
        if in_fence:
            result.append(line)
            i += 1
            continue

        # Detect definition-list-prefixed numbered item
        m = DEFLIST_FIRST_RE.match(line)
        if not m:
            result.append(line)
            i += 1
            continue

        leading_ws = m.group(1)       # whitespace before ":"
        colon_gap = m.group(2)        # spaces between ":" and number
        first_num = m.group(3)        # e.g. "1.  "
        first_text = m.group(4)       # rest of line

        # Calculate the original indent of continuation items.
        # In the source, items 2..N are indented to align with item 1's
        # number, i.e. len(leading_ws) + 1 (colon) + len(colon_gap).
        orig_continuation_indent = len(leading_ws) + 1 + len(colon_gap)

        # Determine target indent for the fixed list.
        # If inside a parent list item, indent to align with parent content.
        parent_indent = _find_parent_list_indent(result, len(result))
        if parent_indent is not None:
            target_indent = parent_indent
        else:
            # Top-level: use the leading whitespace before the colon
            target_indent = len(leading_ws)

        target_prefix = " " * target_indent

        # Emit fixed first item
        result.append(f"{target_prefix}{first_num}{first_text}")
        block_start = i + 1  # 1-based
        block_lines = 1
        i += 1

        # Collect continuation items and their content lines.
        # A continuation line is either:
        #   - a numbered item at orig_continuation_indent
        #   - content indented deeper than orig_continuation_indent
        #   - a blank line followed by more continuation content
        while i < n:
            cline = lines[i]
            stripped = cline.strip()

            # Blank line — could be between items or before content;
            # peek ahead to see if the block continues.
            if stripped == "":
                peek = i + 1
                while peek < n and lines[peek].strip() == "":
                    peek += 1
                if peek < n:
                    peek_line = lines[peek]
                    peek_indent = len(peek_line) - len(peek_line.lstrip())
                    # Continue if next content is a numbered item or
                    # indented content belonging to this list block
                    peek_m = NUMBERED_ITEM_RE.match(peek_line)
                    is_continuation_item = (
                        peek_m and len(peek_m.group(1)) == orig_continuation_indent
                    )
                    is_deep_content = peek_indent > orig_continuation_indent
                    if is_continuation_item or is_deep_content:
                        result.append("")
                        i += 1
                        block_lines += 1
                        continue
                # Not a continuation — stop
                break

            # Check for a numbered item at the continuation indent
            nm = NUMBERED_ITEM_RE.match(cline)
            if nm and len(nm.group(1)) == orig_continuation_indent:
                num_marker = nm.group(2)
                item_text = nm.group(3)
                result.append(f"{target_prefix}{num_marker}{item_text}")
                block_lines += 1
                i += 1
                continue

            # Check for continuation content indented deeper than the
            # continuation items (e.g. images, paragraphs under an item)
            line_indent = len(cline) - len(cline.lstrip())
            if line_indent > orig_continuation_indent:
                extra = line_indent - orig_continuation_indent
                result.append(" " * (target_indent + extra) + cline.lstrip())
                block_lines += 1
                i += 1
                continue

            # Anything else ends the block
            break

        changes.append({
            "start_line": block_start,
            "lines_fixed": block_lines,
            "target_indent": target_indent,
            "preview": f"{first_num}{first_text}"[:80],
        })

    return result, changes


def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Apply flattened-numbered-list fix to a single file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    new_lines, changes = fix_flattened_numbered_lists(lines)

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
        print("No flattened numbered lists found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    verb = "Would fix" if dry_run else "Fixed"

    print(
        f"{verb} {total} flattened numbered list(s) "
        f"across {len(all_results)} file(s):\n"
    )

    for r in all_results:
        for c in r["changes"]:
            print(
                f"  {r['file']}:{c['start_line']} "
                f"({c['lines_fixed']} lines, indent={c['target_indent']}) "
                f"{c['preview']}"
            )

    print(f"\nSummary: {verb} {total} flattened list(s) across {len(all_results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
