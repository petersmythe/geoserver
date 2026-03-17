#!/usr/bin/env python3
"""Fix complex table alignment issues: RST grid tables and mixed grid/pipe syntax.

Bug condition: The RST-to-Markdown converter left RST grid table syntax
(+---+---+ borders) and mixed grid/pipe table syntax in Markdown files.
These don't render in MkDocs and need conversion to standard pipe tables.

Patterns detected and fixed:

1. **Pure RST grid tables** (+---+---+ borders with | content rows):
   +------+------+
   | Head | Head |
   +------+------+
   | data | data |
   +------+------+
   → Converted to standard Markdown pipe tables.

2. **Mixed grid/pipe tables** (pipe rows with +---+ internal separators):
   | Sym  | Attr    | Supported |
   |      +--------+-----------+
   |      | Radius  | yes       |
   → Remove +---+ separator rows, keep data rows as standard pipe table.

3. **Single-image grid tables** (grid table wrapping just an image):
   +---------------------------------------------+
   | ![alt](path){.align-middle}                 |
   +---------------------------------------------+
   → Unwrap to plain image syntax.

4. **Grid tables with multi-line cells** (content + empty continuation rows):
   | PROP_NAME                    | x | x | x |
   |                              |   |   |   |
   | [link text](url)             |   |   |   |
   → Merge continuation rows into parent using <br>.

Preservation: Only targets grid table syntax and mixed grid/pipe patterns.
Standard pipe tables are left untouched.

Requirements: 1.22, 2.22, 3.3
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
# Grid table border: +----+----+ or +=====+=====+ (also single-column +----+)
GRID_BORDER_RE = re.compile(r"^\+[-=]+(\+[-=]+)*\+\s*$")
# Mixed separator: starts with | then has +---+ patterns
MIXED_SEP_RE = re.compile(r"^\|[^+]*\+[-]+(\+[-]+)*\+\s*$")
# Standard pipe table row
PIPE_ROW_RE = re.compile(r"^\|.*\|\s*$")
# Standard separator row |---|---|
PIPE_SEP_RE = re.compile(r"^\|[-| :]+\|\s*$")
_HAS_DASH = re.compile(r"-")


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def _split_grid_cells(line: str) -> list[str]:
    """Split a grid table content row (|...|) into cell contents.

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


def _is_single_image_grid(block_lines: list[str]) -> tuple[bool, str]:
    """Check if a grid table block is just wrapping a single image.

    Returns (is_single_image, image_line).
    """
    content_lines = [
        l for l in block_lines if not GRID_BORDER_RE.match(l.strip())
    ]
    if len(content_lines) != 1:
        return False, ""
    cells = _split_grid_cells(content_lines[0])
    if len(cells) != 1:
        return False, ""
    cell = cells[0].strip()
    if re.match(r"!\[.*\]\(.*\)", cell):
        return True, cell
    return False, ""


def _compute_col_widths_from_border(border_line: str) -> list[int]:
    """Extract column widths from a grid border line like +----+------+."""
    # Remove leading/trailing +
    inner = border_line.strip()[1:-1]
    segments = inner.split("+")
    return [len(s) for s in segments]


def _build_pipe_row(cells: list[str], col_widths: list[int]) -> str:
    """Build a pipe table row from cells, padding to column widths."""
    parts = []
    for i, cell in enumerate(cells):
        content = cell.strip()
        width = col_widths[i] if i < len(col_widths) else max(len(content), 3)
        parts.append(f" {content.ljust(width)} ")
    return "|" + "|".join(parts) + "|"


def _build_separator(col_widths: list[int]) -> str:
    """Build a pipe table separator row from column widths."""
    parts = []
    for w in col_widths:
        parts.append("-" * (w + 2))
    return "|" + "|".join(parts) + "|"



def _detect_indent(line: str) -> str:
    """Return the leading whitespace of a line."""
    return line[: len(line) - len(line.lstrip())]


def _convert_grid_table(block_lines: list[str]) -> list[str]:
    """Convert a pure RST grid table block to a Markdown pipe table.

    Handles multi-line cells by merging continuation rows with <br>.
    Preserves leading indentation from the original block.
    """
    # Detect indentation from first line
    indent = _detect_indent(block_lines[0])

    # Check for single-image grid table first
    is_img, img_line = _is_single_image_grid(block_lines)
    if is_img:
        return [indent + img_line, ""]

    # Find column widths from first border line
    first_border = block_lines[0].strip()
    col_widths = _compute_col_widths_from_border(first_border)
    num_cols = len(col_widths)

    # Separate borders and content rows
    content_rows = []
    border_indices = []
    for idx, line in enumerate(block_lines):
        s = line.strip()
        if GRID_BORDER_RE.match(s):
            border_indices.append(idx)
        else:
            content_rows.append((idx, line))

    if not content_rows:
        return block_lines

    # Group content rows between borders into logical rows.
    # Each group of consecutive content rows between two borders = one logical row.
    logical_rows = []
    current_group = []
    for idx, line in content_rows:
        # Check if there's a border between this and the previous content row
        if current_group:
            prev_idx = current_group[-1][0]
            has_border_between = any(
                prev_idx < bi < idx for bi in border_indices
            )
            if has_border_between:
                logical_rows.append(current_group)
                current_group = []
        current_group.append((idx, line))
    if current_group:
        logical_rows.append(current_group)

    # Convert each logical row: merge multi-line cells with <br>
    merged_rows = []
    for group in logical_rows:
        # Parse all content lines in this group
        all_cells = []
        for _, line in group:
            cells = _split_grid_cells(line)
            # Pad to num_cols
            while len(cells) < num_cols:
                cells.append("")
            all_cells.append([c.strip() for c in cells[:num_cols]])

        # Merge: for each column, join non-empty values with <br>
        merged = []
        for col in range(num_cols):
            parts = [row[col] for row in all_cells if row[col]]
            merged.append("<br>".join(parts))
        merged_rows.append(merged)

    if not merged_rows:
        return block_lines

    # Use content-based widths but cap at a reasonable maximum
    # to avoid extremely wide lines. Markdown renderers handle overflow.
    MAX_COL_WIDTH = 80
    effective_widths = []
    for col in range(num_cols):
        max_w = max(
            (len(row[col]) for row in merged_rows if col < len(row)),
            default=3,
        )
        effective_widths.append(max(min(max_w, MAX_COL_WIDTH), 3))

    # Build output: header row, separator, data rows
    out = []
    # First logical row is the header
    out.append(indent + _build_pipe_row(merged_rows[0], effective_widths))
    out.append(indent + _build_separator(effective_widths))
    for row in merged_rows[1:]:
        out.append(indent + _build_pipe_row(row, effective_widths))

    return out


def _fix_mixed_grid_pipe_table(table_lines: list[str]) -> list[str]:
    """Fix a mixed grid/pipe table by removing +---+ separator rows.

    These tables have standard pipe rows interspersed with mixed separator
    rows like: |      +----+----+
    Simply removing the mixed separators yields a valid pipe table.
    """
    result = []
    for line in table_lines:
        s = line.strip()
        if MIXED_SEP_RE.match(s):
            # Skip mixed separator rows
            continue
        result.append(line)
    return result



def fix_complex_tables(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Fix all complex table alignment issues in a list of lines.

    Handles:
    1. Pure RST grid tables (consecutive +---+ and | rows)
    2. Mixed grid/pipe tables (pipe rows with +---+ separators)

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

        s = line.strip()

        # Case 1: Pure grid table starting with +---+
        if GRID_BORDER_RE.match(s):
            # Collect the entire grid table block.
            # Inside a grid table, we accept: grid borders, ANY pipe row
            # (including empty ones that look like separators), and empty
            # lines if the next line continues the table.
            block = [line]
            j = i + 1
            while j < n:
                next_s = lines[j].strip()
                if GRID_BORDER_RE.match(next_s) or PIPE_ROW_RE.match(next_s):
                    block.append(lines[j])
                    j += 1
                elif not next_s:
                    # Empty line might be inside grid table if next line
                    # continues the table
                    if j + 1 < n and (
                        GRID_BORDER_RE.match(lines[j + 1].strip())
                        or PIPE_ROW_RE.match(lines[j + 1].strip())
                    ):
                        block.append(lines[j])
                        j += 1
                    else:
                        break
                else:
                    break

            # Must end with a grid border to be a valid grid table
            last_border = -1
            for bi in range(len(block) - 1, -1, -1):
                if GRID_BORDER_RE.match(block[bi].strip()):
                    last_border = bi
                    break

            if last_border > 0:
                # Trim block to last border
                trailing = block[last_border + 1 :]
                block = block[: last_border + 1]

                converted = _convert_grid_table(block)
                result.extend(converted)
                if trailing:
                    result.extend(trailing)

                changes.append(
                    {
                        "line": i + 1,
                        "action": f"converted grid table ({len(block)} lines -> {len(converted)} lines)",
                        "text": converted[0].strip()[:120] if converted else "",
                    }
                )
                i = j
                continue
            else:
                # Not a valid grid table, leave as-is
                result.append(line)
                i += 1
                continue

        # Case 2: Mixed grid/pipe table
        # Detect when we're in a pipe table that has mixed separators
        if PIPE_ROW_RE.match(s) and not PIPE_SEP_RE.match(s):
            # Look ahead to see if this table contains mixed separators
            table_block = [line]
            has_mixed = False
            j = i + 1
            while j < n:
                next_s = lines[j].strip()
                if MIXED_SEP_RE.match(next_s):
                    table_block.append(lines[j])
                    has_mixed = True
                    j += 1
                elif PIPE_ROW_RE.match(next_s):
                    table_block.append(lines[j])
                    j += 1
                elif PIPE_SEP_RE.match(next_s) and _HAS_DASH.search(next_s):
                    table_block.append(lines[j])
                    j += 1
                else:
                    break

            if has_mixed:
                fixed = _fix_mixed_grid_pipe_table(table_block)
                result.extend(fixed)
                changes.append(
                    {
                        "line": i + 1,
                        "action": f"removed {len(table_block) - len(fixed)} mixed separator(s)",
                        "text": fixed[0].strip()[:120] if fixed else "",
                    }
                )
                i = j
                continue
            else:
                # Normal pipe table, leave as-is
                result.extend(table_block)
                i = j
                continue

        result.append(line)
        i += 1

    return result, changes


def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Apply complex table alignment fix to a single file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    new_lines, changes = fix_complex_tables(lines)

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
        print("No complex table alignment issues found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    verb = "Would fix" if dry_run else "Fixed"

    print(
        f"{verb} {total} complex table issue(s) "
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
