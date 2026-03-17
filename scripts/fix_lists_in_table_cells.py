#!/usr/bin/env python3
"""Fix lists in table cells that split across multiple rows.

Bug condition: The RST-to-Markdown converter split list items in table cells
into separate continuation rows, breaking the table structure. Each list item
ended up on its own row with empty leading columns.

Patterns detected and fixed:

1. **List item continuation rows (3+ col)**:
   | Parameter | Required | - PostGIS: `...` |
   |           |          | - Oracle: `...`  |
   → Merge list items into parent row using <br> separators.

2. **List item continuation rows (2 col)**:
   | Header    | - HIT: description  |
   |           | - MISS: description |
   → Merge list items into parent row using <br> separators.

3. **Definition list syntax in table cells**:
   |           | :   text |
   → Clean up `:   ` prefix artifacts and merge into parent row.

4. **Empty continuation rows with only `:` artifacts**:
   |           |          |   :   |
   → Remove these artifact-only rows entirely.

Preservation: Only targets continuation rows (rows where leading cells are
empty) that contain list items or definition list artifacts. Correctly
formatted tables are left untouched.

Requirements: 1.19, 2.19, 3.3
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
SEPARATOR_RE = re.compile(r"^\|[-| :]+\|$")
# A true separator must contain at least one dash
_HAS_DASH = re.compile(r"-")
# Grid table border: +----+----+
GRID_BORDER_RE = re.compile(r"^\+[-=]+\+")


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def _split_cells(line: str) -> list[str]:
    """Split a pipe-table row into cell contents (excluding outer pipes).

    Handles backtick-escaped pipes and link syntax with pipes inside.
    Returns list of cell content strings (untrimmed).
    """
    # Remove leading/trailing pipe
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


def _is_continuation_row(cells: list[str]) -> bool:
    """Check if a row is a continuation row (first cell empty, some later cells have content)."""
    if not cells:
        return False
    if cells[0].strip():
        return False
    return any(c.strip() for c in cells[1:])


def _is_empty_or_artifact_row(cells: list[str]) -> bool:
    """Check if all cells are empty or contain only ':' artifacts."""
    for c in cells:
        s = c.strip()
        if s and s != ':':
            return False
    return True


def _has_list_item(text: str) -> bool:
    """Check if text contains a list item marker (- text)."""
    return bool(re.match(r'\s*-\s+\S', text))


def _has_deflist_prefix(text: str) -> bool:
    """Check if text has definition list prefix ':   text'."""
    return bool(re.match(r'\s*:\s{2,}\S', text))


def _clean_cell_content(text: str) -> str:
    """Clean definition list prefix from cell content.

    ':   - TEXT' → '- TEXT'
    ':   and all jobs...' → 'and all jobs...'
    """
    # Remove definition list prefix
    m = re.match(r'^(\s*):\s{2,}(.*)', text)
    if m:
        return m.group(2).strip()
    return text.strip()


def _rebuild_row(cells: list[str], col_widths: list[int]) -> str:
    """Rebuild a pipe-table row from cells, padding to column widths."""
    parts = []
    for i, cell in enumerate(cells):
        width = col_widths[i] if i < len(col_widths) else len(cell)
        parts.append(f" {cell.ljust(width)} ")
    return "|" + "|".join(parts) + "|"


def fix_lists_in_table_cells(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Merge list-item continuation rows back into their parent rows.

    Only acts when continuation rows contain list items (- text) or
    definition list syntax (:   text). Empty/artifact continuation rows
    are only removed when they appear alongside real list continuations.
    Tables with continuation rows that contain other content (images, text)
    are left untouched.

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

        # We have a data row. Look ahead for continuation rows that
        # contain list items or definition list syntax.
        parent_cells = _split_cells(line)

        # Collect ALL continuation rows (first cell empty)
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
            first_cell_empty = not next_cells[0].strip() if next_cells else False
            if not first_cell_empty:
                break

            # Classify the row
            if _is_empty_or_artifact_row(next_cells):
                continuations.append(("artifact", j, next_cells))
            else:
                has_list = any(_has_list_item(c) for c in next_cells)
                has_deflist = any(_has_deflist_prefix(c) for c in next_cells)
                if has_list or has_deflist:
                    continuations.append(("list", j, next_cells))
                else:
                    # Plain text continuation — include it provisionally.
                    # It will only be merged if list items follow.
                    continuations.append(("text", j, next_cells))
            j += 1

        # Only proceed if there's at least one real list/deflist continuation
        real_continuations = [c for c in continuations if c[0] == "list"]
        if not real_continuations:
            # No list items found — leave everything untouched
            result.append(line)
            i += 1
            continue

        # Trim trailing non-list continuations (text/artifact rows after
        # the last list row should not be merged)
        while continuations and continuations[-1][0] != "list":
            continuations.pop()
            j -= 1

        # Merge continuation rows into parent row
        merged_cells = [c.strip() for c in parent_cells]

        for cont_type, cont_line, cont_cells in continuations:
            if cont_type == "artifact":
                continue
            for col_idx in range(len(cont_cells)):
                cell_text = cont_cells[col_idx].strip()
                if not cell_text or cell_text == ':':
                    continue
                cleaned = _clean_cell_content(cont_cells[col_idx])
                if not cleaned:
                    continue
                if merged_cells[col_idx]:
                    merged_cells[col_idx] += "<br>" + cleaned
                else:
                    merged_cells[col_idx] = cleaned

        # Build the merged row
        merged_line = "| " + " | ".join(merged_cells) + " |"
        result.append(merged_line)

        changes.append({
            "line": i + 1,
            "action": f"merged {len(continuations)} continuation row(s)",
            "text": merged_line.strip()[:120],
        })

        i = j
        continue

    return result, changes


def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Apply list-in-table-cell fix to a single file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    new_lines, changes = fix_lists_in_table_cells(lines)

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
        print("No list-in-table-cell issues found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    verb = "Would fix" if dry_run else "Fixed"

    print(
        f"{verb} {total} list-in-table-cell issue(s) "
        f"across {len(all_results)} file(s):\n"
    )

    for r in all_results:
        for c in r["changes"]:
            print(
                f"  {r['file']}:{c['line']} "
                f"[{c['action']}] "
                f"{c['text']}"
            )

    print(f"\nSummary: {verb} {total} issue(s) across {len(all_results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
