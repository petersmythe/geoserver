#!/usr/bin/env python3
"""
Detection script for table structure and content issues.

Scans all Markdown files under doc/en/ for five categories of table bugs:
  1. Lists in table cells splitting across multiple cells — Req 1.19
  2. Notes/admonitions in cells breaking table structure — Req 1.20
  3. Multi-line cell content splitting into multiple cells — Req 1.21
  4. Complex tables with misaligned cells (grid table remnants, mixed syntax) — Req 1.22
  5. Tables with empty rows/cells that had content — Req 1.23

Usage:
    python scripts/detect_table_issues.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def read_lines(filepath):
    """Read file and return list of lines."""
    try:
        return filepath.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []


def _is_separator_row(line):
    """Check if a line is a Markdown table separator row (|---|---|)."""
    stripped = line.strip()
    return bool(re.match(r'^\|[-| :]+\|$', stripped)) and '-' in stripped


# -----------------------------------------------------------------------
# Check 1: Lists in table cells splitting across cells  (Req 1.19)
# -----------------------------------------------------------------------

def check_lists_splitting_cells():
    """Find tables where list items in cells split across multiple rows.

    Detects continuation rows with empty leading columns followed by
    list-item content (- text), indicating a list that should have been
    kept inside a single cell.
    """
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Pattern: continuation row where first column(s) are empty
            # but a later column has a list item (- text)
            # e.g. "|  |  | - some item |"
            m = re.match(r'^\|\s{2,}\|\s*\|\s*-\s+\S', line)
            if m:
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "text": line.strip()[:120],
                    "issue": "List item split into continuation row (3+ col)",
                })
                continue

            # 2-column variant: "|  | - some item"
            m = re.match(r'^\|\s{2,}\|\s*-\s+\S', line)
            if m:
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "text": line.strip()[:120],
                    "issue": "List item split into continuation row (2 col)",
                })
                continue

            # Definition list syntax in table cells: "| :   text"
            if re.match(r'^\|', line) and re.search(r'\|\s*:\s{2,}\S', line):
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "text": line.strip()[:120],
                    "issue": "Definition list syntax ':   text' in table cell",
                })

    return issues


# -----------------------------------------------------------------------
# Check 2: Notes/admonitions breaking table structure  (Req 1.20)
# -----------------------------------------------------------------------

def check_admonitions_breaking_tables():
    """Find admonitions immediately after table rows that break table context."""
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False
        prev_was_table_row = False

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                prev_was_table_row = False
                continue
            if in_fence:
                prev_was_table_row = False
                continue

            is_table_row = bool(re.match(r'^\|.*\|', line))

            if not is_table_row and prev_was_table_row:
                # Check if an admonition follows (with or without blank line)
                if line.strip() == "":
                    for j in range(i + 1, min(i + 3, len(lines))):
                        if lines[j].strip() != "":
                            am = re.match(r'^!!!\s+(\w+)', lines[j])
                            if am:
                                issues.append({
                                    "file": rel,
                                    "line": j + 1,
                                    "type": am.group(1),
                                    "table_context": lines[i - 1].strip()[:80],
                                    "issue": "Admonition after table row (blank line gap)",
                                })
                            break
                else:
                    am = re.match(r'^!!!\s+(\w+)', line)
                    if am:
                        issues.append({
                            "file": rel,
                            "line": i + 1,
                            "type": am.group(1),
                            "table_context": lines[i - 1].strip()[:80],
                            "issue": "Admonition immediately after table row",
                        })

            prev_was_table_row = is_table_row

    return issues


# -----------------------------------------------------------------------
# Check 3: Multi-line cell content splitting into multiple cells (Req 1.21)
# -----------------------------------------------------------------------

def check_multiline_cell_splitting():
    """Find tables with duplicate rows or continuation rows indicating
    multi-line cell content that was incorrectly split."""
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False
        prev_table_row = None

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                prev_table_row = None
                continue
            if in_fence:
                prev_table_row = None
                continue

            if re.match(r'^\|', line):
                stripped = line.strip()
                # Skip separator rows
                if _is_separator_row(line):
                    continue

                # Duplicate row detection: same content row appears twice
                if prev_table_row and stripped == prev_table_row:
                    issues.append({
                        "file": rel,
                        "line": i + 1,
                        "text": stripped[:120],
                        "issue": "Duplicate table row (content split artifact)",
                    })

                # Continuation row: first cell empty, others have content
                # e.g. "|  | some continued text |"
                cells = [c.strip() for c in line.split("|")]
                # split("|") gives ['', cell1, cell2, ..., '']
                content_cells = cells[1:-1] if len(cells) > 2 else []
                if (len(content_cells) >= 2
                        and content_cells[0] == ""
                        and any(c for c in content_cells[1:])):
                    # Make sure it's not a separator row
                    if not _is_separator_row(line):
                        issues.append({
                            "file": rel,
                            "line": i + 1,
                            "text": stripped[:120],
                            "issue": "Continuation row with empty first cell",
                        })

                prev_table_row = stripped
            else:
                prev_table_row = None

    return issues


# -----------------------------------------------------------------------
# Check 4: Complex tables with misaligned cells  (Req 1.22)
# -----------------------------------------------------------------------

def check_complex_table_issues():
    """Find RST grid table remnants and mixed grid/pipe table syntax."""
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Grid table border row: +----+----+
            if re.match(r'^\+[-]+\+[-]+\+', line):
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "text": line.strip()[:120],
                    "issue": "RST grid table border (+---+---+)",
                })
                continue

            # Mixed grid/pipe: pipe row containing +---+ separators
            if re.match(r'^\|.*\+[-]+\+', line):
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "text": line.strip()[:120],
                    "issue": "Mixed grid/pipe table syntax",
                })

    return issues


# -----------------------------------------------------------------------
# Check 5: Empty rows/cells that had content  (Req 1.23)
# -----------------------------------------------------------------------

def check_empty_table_cells():
    """Find tables with empty description cells or effectively empty rows."""
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False
        is_in_table = False
        has_header = False

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                is_in_table = False
                has_header = False
                continue
            if in_fence:
                continue

            if re.match(r'^\|', line):
                if not is_in_table:
                    is_in_table = True
                    has_header = False
                    continue
                if _is_separator_row(line):
                    has_header = True
                    continue
                if has_header:
                    # Check for rows where first cell has content but
                    # all remaining cells are empty
                    cells = line.split("|")
                    content_cells = [c.strip() for c in cells[1:-1]]
                    if len(content_cells) >= 3:
                        non_empty = [c for c in content_cells if c.strip()]
                        if len(non_empty) == 1 and content_cells[0].strip():
                            issues.append({
                                "file": rel,
                                "line": i + 1,
                                "param": content_cells[0].strip()[:60],
                                "issue": "Row with content in first cell but empty remaining cells",
                            })

                    # Check for effectively empty rows (all cells empty or
                    # contain only artifact chars like bare ":")
                    if content_cells and all(
                        c in ("", ":") for c in content_cells
                    ):
                        issues.append({
                            "file": rel,
                            "line": i + 1,
                            "text": line.strip()[:80],
                            "issue": "Effectively empty row (whitespace or ':' artifacts only)",
                        })
            else:
                is_in_table = False
                has_header = False

    return issues


# -----------------------------------------------------------------------
# Report
# -----------------------------------------------------------------------

def print_report(title, issues, fields):
    """Print a formatted section of the report."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")
    if not issues:
        print("  [OK] No issues found.")
        return 0
    print(f"  Found {len(issues)} issue(s):\n")
    for idx, issue in enumerate(issues, 1):
        print(f"  [{idx}]")
        for field in fields:
            if field in issue and issue[field]:
                print(f"      {field}: {issue[field]}")
        print()
    return len(issues)


def main():
    print("Table Structure Issue Detection Report")
    print(f"Docs directory: {DOCS_DIR}\n")

    total = 0

    issues1 = check_lists_splitting_cells()
    total += print_report(
        "Check 1: Lists in Table Cells Splitting Across Rows (Req 1.19)",
        issues1,
        ["file", "line", "text", "issue"],
    )

    issues2 = check_admonitions_breaking_tables()
    total += print_report(
        "Check 2: Admonitions Breaking Table Structure (Req 1.20)",
        issues2,
        ["file", "line", "type", "table_context", "issue"],
    )

    issues3 = check_multiline_cell_splitting()
    total += print_report(
        "Check 3: Multi-line Cell Content Splitting (Req 1.21)",
        issues3,
        ["file", "line", "text", "issue"],
    )

    issues4 = check_complex_table_issues()
    total += print_report(
        "Check 4: Complex Table Structure Issues (Req 1.22)",
        issues4,
        ["file", "line", "text", "issue"],
    )

    issues5 = check_empty_table_cells()
    total += print_report(
        "Check 5: Empty Table Rows/Cells (Req 1.23)",
        issues5,
        ["file", "line", "param", "text", "issue"],
    )

    print(f"\n{'=' * 70}")
    print(f"  SUMMARY: {total} total issue(s) found across all checks.")
    print(f"{'=' * 70}\n")

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
