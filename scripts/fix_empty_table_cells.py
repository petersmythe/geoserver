#!/usr/bin/env python3
"""Fix empty table cells by restoring content from RST sources.

Bug condition: Tables show empty rows/cells that had content in the
original RST documentation. The automated RST-to-Markdown converter
either dropped row content entirely or converted grid-table separator
lines into empty pipe rows.

Two patterns are fixed:

1. **Lost row content** (jwt-headers/configuration.md):
   RST list-table rows with sub-lists were dropped, leaving empty rows.
   Content is restored from the original RST source.

2. **Spurious empty rows from grid tables** (printing/configuration.md):
   RST grid table separator lines (+---+---+) were converted to empty
   pipe rows (|  |  |) instead of being removed.

Preservation: Non-empty cells remain unchanged. Only targets the
specific empty-row patterns detected by detect_table_issues.py Check 5.

Requirements: 1.23, 2.23, 3.3
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def _is_separator_row(line: str) -> bool:
    """Check if a line is a Markdown table separator (|---|---|).

    Must contain at least one dash to distinguish from empty rows.
    """
    stripped = line.strip()
    return bool(re.match(r"^\|[-| :]+\|$", stripped)) and "-" in stripped


def _is_empty_row(line: str) -> bool:
    """Check if a pipe-table row has all empty cells."""
    if not line.strip().startswith("|"):
        return False
    cells = line.split("|")
    content_cells = [c.strip() for c in cells[1:-1]]
    if not content_cells:
        return False
    return all(c in ("", ":") for c in content_cells)


def fix_jwt_headers_tables(filepath: Path) -> list[dict]:
    """Restore lost rows in jwt-headers/configuration.md tables."""
    changes = []
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    new_lines = list(lines)

    # --- Table 1: User Name Options ---
    # The RST had a row for "Format the Header value is in" with a sub-list.
    # In the Markdown, this row was lost, leaving |  |  | between
    # "Request header attribute for User Name" and "JSON path for the User Name".
    restored_row_1 = (
        "| Format the Header value is in | "
        "Format that the user name is in: "
        "Simple String (user name is the header's value), "
        "JSON (header is a JSON string, use JSON path), "
        "or JWT (header is a base64 JWT string, use JSON path). |"
    )

    # --- Table 2: New Role Source Options ---
    # The RST had a row for "Role Source" with a sub-list.
    # In the Markdown, this row was lost, leaving |  |  | between
    # the header separator and "Request Header attribute for Roles".
    restored_row_2 = (
        "| Role Source | "
        "Which Role Source to use: "
        "Header containing JSON String (header contains a JSON claims object) "
        "or Header Containing JWT (header contains a Base64 JWT Access Token). |"
    )

    for i, line in enumerate(lines):
        if not _is_empty_row(line):
            continue

        # Look at surrounding context to identify which table this is
        prev_content = ""
        next_content = ""
        for j in range(i - 1, max(i - 5, -1), -1):
            if lines[j].strip().startswith("|") and not _is_separator_row(lines[j]):
                prev_content = lines[j]
                break
        for j in range(i + 1, min(i + 5, len(lines))):
            if lines[j].strip().startswith("|") and not _is_separator_row(lines[j]):
                next_content = lines[j]
                break

        if "Request header attribute for User Name" in prev_content and \
           "JSON path for the User Name" in next_content:
            new_lines[i] = restored_row_1
            changes.append({
                "line": i + 1,
                "action": "restore_row",
                "text": "Restored 'Format the Header value is in' row",
            })
        elif "JSON path for the User Name" in prev_content:
            # This shouldn't happen but guard against it
            pass
        elif "Config Option" in prev_content and \
             "Request Header attribute for Roles" in next_content:
            new_lines[i] = restored_row_2
            changes.append({
                "line": i + 1,
                "action": "restore_row",
                "text": "Restored 'Role Source' row",
            })

    if changes:
        filepath.write_text("\n".join(new_lines), encoding="utf-8")

    return changes


def fix_printing_empty_rows(filepath: Path) -> list[dict]:
    """Remove spurious empty rows from the pageSizes table.

    The RST grid table had separator lines (+---+---+) between every
    data row. The converter turned these into empty pipe rows instead
    of removing them.
    """
    changes = []
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    new_lines = []
    in_fence = False
    in_target_table = False
    skip_indices = set()

    # First pass: identify the pageSizes table and mark empty rows
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            in_target_table = False
            continue
        if in_fence:
            continue

        if not in_target_table:
            # Detect start of pageSizes table by looking for the header
            if re.match(r"^\|\s*name\s*\|", line):
                in_target_table = True
            continue

        # We're inside the pageSizes table
        if not line.strip().startswith("|"):
            in_target_table = False
            continue

        if _is_separator_row(line):
            continue  # skip separator, it's fine

        if _is_empty_row(line):
            skip_indices.add(i)
            changes.append({
                "line": i + 1,
                "action": "remove_empty_row",
                "text": "Removed spurious empty row from pageSizes table",
            })

    if changes:
        for i, line in enumerate(lines):
            if i not in skip_indices:
                new_lines.append(line)
        filepath.write_text("\n".join(new_lines), encoding="utf-8")

    return changes


def fix_file(filepath: Path, dry_run: bool = False) -> dict | None:
    """Apply empty table cell fixes to a single file."""
    rel = str(filepath.relative_to(ROOT))

    # Only process the two known affected files
    norm = rel.replace("\\", "/")

    if "community/jwt-headers/configuration.md" in norm:
        if dry_run:
            # Read-only check
            text = filepath.read_text(encoding="utf-8")
            lines = text.split("\n")
            empty_count = sum(1 for l in lines if _is_empty_row(l))
            if empty_count == 0:
                return None
            return {
                "file": rel,
                "changes": [{"line": 0, "action": "dry_run",
                              "text": f"Would restore {empty_count} empty row(s)"}],
            }
        changes = fix_jwt_headers_tables(filepath)
        if changes:
            return {"file": rel, "changes": changes}

    elif "extensions/printing/configuration.md" in norm:
        if dry_run:
            text = filepath.read_text(encoding="utf-8")
            lines = text.split("\n")
            # Quick count of empty rows in pageSizes table area
            in_table = False
            empty_count = 0
            for line in lines:
                if re.match(r"^\|\s*name\s*\|", line):
                    in_table = True
                    continue
                if in_table:
                    if not line.strip().startswith("|"):
                        in_table = False
                        continue
                    if _is_empty_row(line):
                        empty_count += 1
            if empty_count == 0:
                return None
            return {
                "file": rel,
                "changes": [{"line": 0, "action": "dry_run",
                              "text": f"Would remove {empty_count} empty row(s)"}],
            }
        changes = fix_printing_empty_rows(filepath)
        if changes:
            return {"file": rel, "changes": changes}

    return None


def main():
    import io
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN -- no files will be modified ===\n")

    targets = [
        DOCS_DIR / "user" / "community" / "jwt-headers" / "configuration.md",
        DOCS_DIR / "user" / "extensions" / "printing" / "configuration.md",
    ]

    all_results = []
    for md_file in targets:
        if not md_file.exists():
            print(f"WARNING: {md_file} not found, skipping.")
            continue
        result = fix_file(md_file, dry_run=dry_run)
        if result:
            all_results.append(result)

    if not all_results:
        print("No empty table cell issues found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    verb = "Would fix" if dry_run else "Fixed"

    print(f"{verb} {total} empty table cell issue(s) across {len(all_results)} file(s):\n")

    for r in all_results:
        for c in r["changes"]:
            print(f"  {r['file']}:{c['line']} [{c['action']}] {c['text']}")

    print(f"\nSummary: {verb} {total} issue(s) across {len(all_results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
