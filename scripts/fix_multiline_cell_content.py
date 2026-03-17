#!/usr/bin/env python3
"""Fix multi-line cell content that splits across multiple table rows.

Bug condition: The RST-to-Markdown converter split multi-line cell content
into separate continuation rows. Each continuation row has an empty first
cell and content in subsequent cells that belongs to the parent row above.

This script handles continuation rows containing:
- Plain text paragraphs (descriptions, notes)
- Images (![...](...)  syntax)
- Admonition fragments (:::: note, ::: title, etc.)
- Blockquoted content (> text)
- Captions/emphasis (*text*)
- Any other non-list content

Note: List-item continuation rows (- text) and definition list syntax
(:   text) are handled by fix_lists_in_table_cells.py and are skipped here.

Detection heuristics for true continuation rows vs data rows with empty
first cells:
- Preceded by an empty row (all cells empty) → always a continuation
- NOT preceded by empty row but content in only one non-first column
  → likely a continuation (additional examples for same parameter)
- NOT preceded by empty row with content in multiple columns
  → likely an independent data row, skip

Preservation: Only targets pipe-table continuation rows (first cell empty)
that were NOT already handled by the list fix script. Correctly formatted
tables, grid tables (+---+), and tables without continuation rows are
left untouched.

Requirements: 1.21, 2.21, 3.3
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
SEPARATOR_RE = re.compile(r"^\|[-| :]+\|$")
_HAS_DASH = re.compile(r"-")
GRID_BORDER_RE = re.compile(r"^\+[-=]+\+")


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def _split_cells(line: str) -> list[str]:
    """Split a pipe-table row into cell contents (excluding outer pipes).

    Handles backtick-escaped pipes and link syntax with pipes inside.
    """
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]

    cells = []
    current = []
    in_backtick = False
    in_link = False
    i = 0
    while i < len(stripped):
        ch = stripped[i]
        if ch == '`':
            in_backtick = not in_backtick
            current.append(ch)
        elif ch == '[' and not in_backtick:
            in_link = True
            current.append(ch)
        elif ch == ')' and in_link and not in_backtick:
            in_link = False
            current.append(ch)
        elif ch == '|' and not in_backtick and not in_link:
            cells.append(''.join(current))
            current = []
        else:
            current.append(ch)
        i += 1
    cells.append(''.join(current))
    return cells


def _is_pipe_table_row(line: str) -> bool:
    """Check if a line is a pipe-table row (starts and ends with |)."""
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and not GRID_BORDER_RE.match(s)


def _is_separator_row(line: str) -> bool:
    """Check if a line is a Markdown table separator row (|---|---|)."""
    s = line.strip()
    return bool(SEPARATOR_RE.match(s)) and bool(_HAS_DASH.search(s))


def _is_empty_row(cells: list[str]) -> bool:
    """Check if all cells are empty or whitespace-only."""
    return all(not c.strip() for c in cells)


def _has_list_item(text: str) -> bool:
    """Check if text contains a list item marker (- text)."""
    return bool(re.match(r'\s*-\s+\S', text))


def _has_deflist_prefix(text: str) -> bool:
    """Check if text has definition list prefix ':   text'."""
    return bool(re.match(r'\s*:\s{2,}\S', text))


def _is_list_or_deflist_continuation(cells: list[str]) -> bool:
    """Check if any non-empty cell has list/deflist content (handled elsewhere)."""
    for c in cells:
        s = c.strip()
        if not s:
            continue
        if _has_list_item(c) or _has_deflist_prefix(c):
            return True
    return False


def _is_admonition_fragment(text: str) -> bool:
    """Check if text is part of an admonition block (:::: note, ::: title, etc.)."""
    s = text.strip()
    return bool(re.match(r'^:{2,}\s*\w*$', s)) or bool(re.match(r'^:{2,}$', s))


def _count_nonempty_cells(cells: list[str], skip_first: bool = True) -> int:
    """Count non-empty cells, optionally skipping the first cell."""
    start = 1 if skip_first else 0
    return sum(1 for c in cells[start:] if c.strip())


def _rebuild_row(cells: list[str]) -> str:
    """Rebuild a pipe-table row from cells."""
    return "| " + " | ".join(cells) + " |"


def fix_multiline_cells(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Merge non-list continuation rows back into their parent rows.

    Targets continuation rows (first cell empty) that contain plain text,
    images, admonition fragments, blockquoted content, or other non-list
    content. List-item and definition-list continuation rows are skipped
    (handled by fix_lists_in_table_cells.py).

    A continuation row is identified by:
    1. First cell is empty
    2. At least one other cell has content
    3. Either preceded by an empty row (strong signal) OR has content in
       only one non-first column (weak signal for additional examples)
    4. NOT a list/deflist row (handled by other script)

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

        # Skip non-table rows
        if not _is_pipe_table_row(line):
            result.append(line)
            i += 1
            continue

        # Skip separator rows
        if _is_separator_row(line):
            result.append(line)
            i += 1
            continue

        # We have a data row. Look ahead for continuation rows.
        parent_cells = _split_cells(line)

        # Collect continuation rows
        continuations = []
        j = i + 1
        while j < n:
            next_line = lines[j]
            if not _is_pipe_table_row(next_line) or _is_separator_row(next_line):
                break

            next_cells = _split_cells(next_line)

            # Pad to same length
            while len(next_cells) < len(parent_cells):
                next_cells.append("")
            while len(parent_cells) < len(next_cells):
                parent_cells.append("")

            # Must have empty first cell to be a continuation
            if next_cells[0].strip():
                break

            if _is_empty_row(next_cells):
                continuations.append(("empty", j, next_cells))
                j += 1
                continue

            if _is_list_or_deflist_continuation(next_cells):
                # Stop: list continuations are handled by the other script.
                break

            # Determine if this is a true continuation or independent data row.
            # Check if preceded by an empty row (strong signal).
            preceded_by_empty = False
            if continuations and continuations[-1][0] == "empty":
                preceded_by_empty = True

            # Count non-empty non-first cells
            nonempty_count = _count_nonempty_cells(next_cells, skip_first=True)

            if preceded_by_empty:
                # Strong signal: empty row before this → it's a continuation
                continuations.append(("content", j, next_cells))
            elif nonempty_count <= 1:
                # Weak signal: only one column has content → likely continuation
                # (e.g., additional examples in a single column)
                continuations.append(("content", j, next_cells))
            else:
                # Multiple columns with content, no empty row before →
                # likely an independent data row (e.g., war.md table)
                break

            j += 1

        # Only proceed if there's at least one content continuation
        real_continuations = [c for c in continuations if c[0] == "content"]
        if not real_continuations:
            result.append(line)
            i += 1
            continue

        # Trim trailing empty rows
        while continuations and continuations[-1][0] == "empty":
            continuations.pop()
            j -= 1

        # Merge continuation rows into parent row
        merged_cells = [c.strip() for c in parent_cells]

        for cont_type, _cont_line, cont_cells in continuations:
            if cont_type == "empty":
                # Empty rows between content rows are just separators, skip
                continue
            for col_idx in range(len(cont_cells)):
                cell_text = cont_cells[col_idx].strip()
                if not cell_text:
                    continue

                # Clean admonition fragments — discard markers, keep content
                if _is_admonition_fragment(cell_text):
                    continue
                # Skip bare admonition type words following ::: title
                if cell_text.lower() in ('note', 'warning', 'caution', 'tip',
                                         'important', 'danger', 'info', 'todo'):
                    # Only skip if it looks like an admonition label
                    # (check if previous content in same column was an
                    # admonition fragment)
                    prev_was_admonition = False
                    for prev_cont in reversed(continuations):
                        if prev_cont[0] == "empty":
                            continue
                        prev_cell = prev_cont[2][col_idx].strip() if col_idx < len(prev_cont[2]) else ""
                        if _is_admonition_fragment(prev_cell):
                            prev_was_admonition = True
                        break
                    if prev_was_admonition:
                        continue

                if merged_cells[col_idx]:
                    merged_cells[col_idx] += "<br>" + cell_text
                else:
                    merged_cells[col_idx] = cell_text

        # Build the merged row
        merged_line = _rebuild_row(merged_cells)
        result.append(merged_line)

        changes.append({
            "line": i + 1,
            "merged": len(continuations),
            "text": merged_line.strip()[:120],
        })

        i = j
        continue

    return result, changes


def remove_duplicate_table_rows(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Remove consecutive duplicate table rows (conversion artifacts).

    When the RST converter splits multi-line content, it sometimes
    produces exact duplicate rows. This pass removes the duplicates.

    Returns (new_lines, list_of_changes).
    """
    result: list[str] = []
    changes: list[dict] = []
    n = len(lines)
    in_fence = False
    prev_table_row = None

    for i in range(n):
        line = lines[i]

        if FENCE_RE.match(line):
            in_fence = not in_fence
            result.append(line)
            prev_table_row = None
            continue
        if in_fence:
            result.append(line)
            prev_table_row = None
            continue

        stripped = line.strip()
        if _is_pipe_table_row(line) and not _is_separator_row(line):
            if prev_table_row is not None and stripped == prev_table_row:
                # Duplicate row — skip it
                changes.append({
                    "line": i + 1,
                    "merged": 0,
                    "text": f"removed duplicate: {stripped[:100]}",
                })
                continue
            prev_table_row = stripped
        else:
            prev_table_row = None

        result.append(line)

    return result, changes


def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Apply multi-line cell content fix to a single file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    # Pass 1: merge continuation rows
    new_lines, changes = fix_multiline_cells(lines)

    # Pass 2: remove duplicate table rows
    new_lines, dup_changes = remove_duplicate_table_rows(new_lines)
    changes.extend(dup_changes)

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
        print("No multi-line cell content issues found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    verb = "Would fix" if dry_run else "Fixed"

    print(
        f"{verb} {total} multi-line cell content issue(s) "
        f"across {len(all_results)} file(s):\n"
    )

    for r in all_results:
        for c in r["changes"]:
            print(
                f"  {r['file']}:{c['line']} "
                f"[merged {c['merged']} row(s)] "
                f"{c['text']}"
            )

    print(f"\nSummary: {verb} {total} issue(s) across {len(all_results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
