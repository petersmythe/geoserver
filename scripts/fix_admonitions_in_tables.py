#!/usr/bin/env python3
"""
Fix admonitions that appear immediately after table rows, breaking the
visual association between table and surrounding content.

Inserts a separator paragraph between the table and the admonition to
ensure the table structure is visually complete before the admonition.

Requirements: 1.16, 2.16
Preservation: Tables without admonitions remain unchanged.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"


def fix_admonitions_after_tables(filepath):
    """
    Insert a separator between tables and immediately following admonitions.

    Returns (new_content, changes_count) or (None, 0) if no changes.
    """
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []
    changes = 0
    in_fence = False
    prev_was_table_row = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track code fences
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            prev_was_table_row = False
            new_lines.append(line)
            i += 1
            continue

        if in_fence:
            prev_was_table_row = False
            new_lines.append(line)
            i += 1
            continue

        is_table_row = bool(re.match(r'^\|.*\|', line))

        if not is_table_row and prev_was_table_row:
            # We just left a table. Check if an admonition follows.
            if line.strip() == "":
                # Look ahead for admonition within next few lines
                adm_line_idx = None
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].strip() != "":
                        if re.match(r'^!!!\s+\w+', lines[j]):
                            adm_line_idx = j
                        break

                if adm_line_idx is not None:
                    # Insert separator: blank line, then a comment, then blank
                    new_lines.append("")  # blank after table
                    new_lines.append("<!-- admonition follows -->")
                    new_lines.append("")
                    # Skip the blank lines between table and admonition
                    i = adm_line_idx
                    changes += 1
                    continue
            else:
                # Admonition directly after table (no blank line)
                if re.match(r'^!!!\s+\w+', line):
                    new_lines.append("")
                    new_lines.append("<!-- admonition follows -->")
                    new_lines.append("")
                    # Don't skip — let the admonition line be added normally
                    changes += 1
                    # Fall through to append the line

        prev_was_table_row = is_table_row
        new_lines.append(line)
        i += 1

    if changes == 0:
        return None, 0

    return "\n".join(new_lines), changes


def main():
    total_changes = 0
    files_changed = 0

    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        new_content, changes = fix_admonitions_after_tables(md_file)
        if new_content is not None:
            md_file.write_text(new_content, encoding="utf-8")
            rel = md_file.relative_to(ROOT)
            print(f"  Fixed {changes} table-admonition break(s) in {rel}")
            total_changes += changes
            files_changed += 1

    print(f"\nDone: {total_changes} table-admonition break(s) fixed in {files_changed} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
