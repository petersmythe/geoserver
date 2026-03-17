#!/usr/bin/env python3
"""
Fix nested list indentation issues (Task 14.2).

Addresses two categories of indentation problems:

1. **Blockquoted list items** – The RST-to-Markdown converter wrapped list items
   in blockquote syntax (``> - item``) instead of using proper Markdown
   indentation.  This script detects contiguous blockquote blocks that contain
   list items and converts them to properly indented lists.

2. **Odd-space indentation** – Some nested list items use 3, 5, or 7 spaces
   instead of the standard 4-space multiples expected by MkDocs.  These are
   normalised to the nearest valid indentation level.

Requirements: 1.9, 2.9, 3.4
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
LIST_MARKER_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s")
BQ_LINE_RE = re.compile(r"^(\s*)(>)+(.*)$")
BQ_LIST_RE = re.compile(r"^(\s*)(>)\s*([-*]|\d+\.)\s")
ADMONITION_RE = re.compile(r"^\s*(!{3}|:{3,})\s+\w+")


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def _is_fence(line: str) -> bool:
    return bool(FENCE_RE.match(line.strip()))


# ---------------------------------------------------------------------------
# Part 1: Fix blockquoted list blocks
# ---------------------------------------------------------------------------

def _find_parent_indent(lines: list[str], block_start: int) -> int:
    """Determine the indentation level the blockquoted block should have.

    Looks backwards from *block_start* to find the nearest parent list item
    or paragraph.  Returns the number of spaces the unquoted content should
    be indented at.

    Rules:
      - If preceded by a numbered list item (``1.  text``), content should be
        indented to align with the text after the marker (typically +4).
      - If preceded by a bullet list item (``- text``), indent +2.
      - If preceded by a heading or paragraph (not a list), indent 0 (the
        blockquote was a top-level list that just happened to be quoted).
    """
    for j in range(block_start - 1, max(0, block_start - 15), -1):
        line = lines[j]
        stripped = line.strip()
        if not stripped:
            continue
        # Skip blockquote continuation lines that belong to the same block
        if stripped.startswith(">"):
            continue

        # Check for numbered list item: "  1.  text"
        m = re.match(r"^(\s*)(\d+\.)\s+", line)
        if m:
            parent_indent = len(m.group(1))
            marker_width = len(m.group(2)) + 1  # "1." + at least 1 space
            # Align with text after marker (standard: 4 spaces from parent)
            return parent_indent + 4

        # Check for bullet list item: "  - text"
        m = re.match(r"^(\s*)([-*])\s+", line)
        if m:
            parent_indent = len(m.group(1))
            return parent_indent + 2

        # Not a list item – the blockquoted list is a standalone list
        return 0

    return 0


def _unquote_block(lines: list[str], start: int, end: int, base_indent: int) -> list[str]:
    """Convert a range of blockquoted lines to properly indented lines.

    Handles:
      - ``> text``        → ``{indent}text``
      - ``> > text``      → ``{indent}    text``  (nested blockquote → extra indent)
      - ``>``             → ``{indent}`` (blank continuation)
      - Preserves code fences inside the block
    """
    result = []
    indent_str = " " * base_indent

    for i in range(start, end):
        line = lines[i]

        # Match blockquote prefix(es)
        m = re.match(r"^(\s*)(>(?:\s*>)*)\s?(.*)", line)
        if not m:
            # Not a blockquote line (shouldn't happen in a block, but be safe)
            result.append(line)
            continue

        leading_ws = m.group(1)
        bq_markers = m.group(2)
        content = m.group(3)

        # Count nesting depth (number of '>' characters)
        depth = bq_markers.count(">")

        if depth == 1:
            # Single blockquote → just use base indent
            if content:
                result.append(indent_str + content)
            else:
                result.append("")
        else:
            # Nested blockquote (depth >= 2) → add extra indentation
            extra = "    " * (depth - 1)
            if content:
                result.append(indent_str + extra + content)
            else:
                result.append("")

    return result


def fix_blockquoted_lists(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Fix all blockquoted list blocks in a file's lines.

    Returns (new_lines, changes) where changes is a list of dicts describing
    each fix applied.
    """
    new_lines = []
    changes = []
    i = 0
    n = len(lines)

    # Track whether we're inside a code fence (to skip those)
    in_fence = False
    fence_indent = 0

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Track code fences
        fm = FENCE_RE.match(line)
        if fm and not in_fence:
            in_fence = True
            fence_indent = len(fm.group(1))
            new_lines.append(line)
            i += 1
            continue
        if in_fence:
            # Check for closing fence
            if fm:
                close_indent = len(fm.group(1))
                if close_indent <= fence_indent:
                    in_fence = False
            new_lines.append(line)
            i += 1
            continue

        # Check if this line starts a blockquote block containing list items
        if not re.match(r"^\s*>", line):
            new_lines.append(line)
            i += 1
            continue

        # Found a blockquote line – scan ahead to find the full block
        block_start = i
        block_has_list = False
        j = i

        # Collect the full contiguous blockquote block
        # A block continues as long as lines start with ">" or are blank
        # (blank lines between blockquote lines are part of the block)
        while j < n:
            l = lines[j]
            ls = l.strip()

            if re.match(r"^\s*>", l):
                if BQ_LIST_RE.match(l):
                    block_has_list = True
                j += 1
            elif ls == "" and j + 1 < n and re.match(r"^\s*>", lines[j + 1]):
                # Blank line between blockquote lines – part of the block
                j += 1
            else:
                break

        block_end = j

        if not block_has_list:
            # This blockquote block doesn't contain list items – leave it alone
            for k in range(block_start, block_end):
                new_lines.append(lines[k])
            i = block_end
            continue

        # Determine the base indentation for the unquoted content
        base_indent = _find_parent_indent(lines, block_start)

        # Unquote the block
        fixed = _unquote_block(lines, block_start, block_end, base_indent)
        new_lines.extend(fixed)

        changes.append({
            "start_line": block_start + 1,
            "end_line": block_end,
            "base_indent": base_indent,
            "lines_fixed": block_end - block_start,
        })

        i = block_end

    return new_lines, changes


# ---------------------------------------------------------------------------
# Part 2: Normalise odd-space indentation on list items
# ---------------------------------------------------------------------------

def _round_indent(spaces: int) -> int:
    """Round an odd indent to the nearest standard level.

    Standard levels: 0, 2, 4, 6, 8, 10, 12 …  (multiples of 2).
    We prefer 4-space multiples but accept 2-space multiples.
    """
    if spaces <= 0:
        return 0
    # Round to nearest even number
    return ((spaces + 1) // 2) * 2


def fix_odd_indentation(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Normalise list items with odd-number indentation (3, 5, 7 …).

    Only touches lines that are list items (start with a marker after spaces).
    Does NOT touch lines inside code fences.
    """
    new_lines = []
    changes = []
    in_fence = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        fm = FENCE_RE.match(line)
        if fm and not in_fence:
            in_fence = True
            new_lines.append(line)
            continue
        if in_fence:
            if fm:
                in_fence = False
            new_lines.append(line)
            continue

        # Check for list item with odd indentation
        m = LIST_MARKER_RE.match(line)
        if m:
            indent = len(m.group(1))
            if indent > 0 and indent % 2 != 0:
                new_indent = _round_indent(indent)
                new_line = " " * new_indent + line.lstrip()
                new_lines.append(new_line)
                changes.append({
                    "line": i + 1,
                    "old_indent": indent,
                    "new_indent": new_indent,
                    "text": stripped[:80],
                })
                continue

        new_lines.append(line)

    return new_lines, changes


# ---------------------------------------------------------------------------
# File-level processing
# ---------------------------------------------------------------------------

def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Apply all nested-list indentation fixes to a single file.

    Returns a dict with change details, or empty dict if no changes.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    # Pass 1: fix blockquoted list blocks
    lines, bq_changes = fix_blockquoted_lists(lines)

    # Pass 2: normalise odd indentation
    lines, indent_changes = fix_odd_indentation(lines)

    if not bq_changes and not indent_changes:
        return {}

    if not dry_run:
        filepath.write_text("\n".join(lines), encoding="utf-8")

    return {
        "file": rel,
        "blockquote_fixes": bq_changes,
        "indent_fixes": indent_changes,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

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
        print("No nested list indentation issues found. Nothing to fix.")
        return 0

    total_bq = sum(len(r["blockquote_fixes"]) for r in all_results)
    total_indent = sum(len(r["indent_fixes"]) for r in all_results)

    print(f"{'Would fix' if dry_run else 'Fixed'} issues in {len(all_results)} file(s):\n")

    if total_bq:
        print(f"  Blockquoted list blocks converted: {total_bq}")
        for r in all_results:
            for c in r["blockquote_fixes"]:
                print(f"    {r['file']}:{c['start_line']}-{c['end_line']} "
                      f"(indent={c['base_indent']}, {c['lines_fixed']} lines)")
        print()

    if total_indent:
        print(f"  Odd-indentation list items normalised: {total_indent}")
        for r in all_results:
            for c in r["indent_fixes"]:
                print(f"    {r['file']}:{c['line']} "
                      f"({c['old_indent']}sp -> {c['new_indent']}sp) {c['text']}")
        print()

    verb = "Would fix" if dry_run else "Fixed"
    print(f"\nSummary: {verb} {total_bq} blockquote blocks + "
          f"{total_indent} odd-indent items across {len(all_results)} files.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
