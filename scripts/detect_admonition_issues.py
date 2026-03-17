#!/usr/bin/env python3
"""
Detection script for admonition and note rendering issues.

Scans all Markdown files under doc/en/ for three categories of admonition bugs:
  1. Fenced-div syntax in blockquotes (:::: note, ::: title) — Req 1.14
  2. Blank lines between !!! marker and content — Req 1.15
  3. Admonitions immediately after table rows, breaking table context — Req 1.16

Usage:
    python scripts/detect_admonition_issues.py
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


# -----------------------------------------------------------------------
# Check 1: Fenced-div admonition syntax in blockquotes  (Req 1.14)
# -----------------------------------------------------------------------

def check_blockquoted_fenced_divs():
    """Find blockquoted fenced-div admonition syntax (:::: note, ::: title)."""
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False

        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Blockquoted fenced-div: "> :::: warning" or "> ::: title"
            m = re.match(r'^>\s*:{3,4}\s+(\w+)', line)
            if m:
                issues.append({
                    "file": rel,
                    "line": i,
                    "type": m.group(1),
                    "text": line.strip()[:100],
                    "issue": "Fenced-div admonition syntax in blockquote",
                })

            # Standalone fenced-div (not in blockquote, not in code fence)
            # e.g. ":::: warning" at start of line
            elif re.match(r'^:{3,4}\s+\w+', line):
                issues.append({
                    "file": rel,
                    "line": i,
                    "type": re.match(r'^:{3,4}\s+(\w+)', line).group(1),
                    "text": line.strip()[:100],
                    "issue": "Standalone fenced-div admonition syntax",
                })

    return issues


# -----------------------------------------------------------------------
# Check 2: Blank line between !!! marker and content  (Req 1.15)
# -----------------------------------------------------------------------

def check_blank_line_after_admonition():
    """Find !!! admonitions with a blank line before the indented content."""
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

            m = re.match(r'^(\s*)!!!\s+(\w+)', line)
            if m:
                indent = m.group(1)
                adm_type = m.group(2)
                # Check: next line blank, line after that is indented content
                if (i + 1 < len(lines) and lines[i + 1].strip() == "" and
                        i + 2 < len(lines) and
                        re.match(r'^' + re.escape(indent) + r'    \S', lines[i + 2])):
                    issues.append({
                        "file": rel,
                        "line": i + 1,
                        "type": adm_type,
                        "text": line.strip()[:100],
                        "issue": "Blank line between !!! marker and content",
                    })

    return issues


# -----------------------------------------------------------------------
# Check 3: Admonitions breaking table structure  (Req 1.16)
# -----------------------------------------------------------------------

def check_admonitions_breaking_tables():
    """Find admonitions immediately after table rows."""
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
                if line.strip() == "":
                    # Check next non-blank line
                    for j in range(i + 1, min(i + 3, len(lines))):
                        if lines[j].strip() != "":
                            am = re.match(r'^!!!\s+(\w+)', lines[j])
                            if am:
                                table_row = lines[i - 1].strip()[:80]
                                issues.append({
                                    "file": rel,
                                    "line": j + 1,
                                    "type": am.group(1),
                                    "table_context": table_row,
                                    "issue": "Admonition immediately after table row",
                                })
                            break
                else:
                    am = re.match(r'^!!!\s+(\w+)', line)
                    if am:
                        table_row = lines[i - 1].strip()[:80]
                        issues.append({
                            "file": rel,
                            "line": i + 1,
                            "type": am.group(1),
                            "table_context": table_row,
                            "issue": "Admonition immediately after table row (no blank line)",
                        })

            prev_was_table_row = is_table_row

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
        print("  ✓ No issues found.")
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
    print("Admonition Issue Detection Report")
    print(f"Docs directory: {DOCS_DIR}\n")

    total = 0

    issues1 = check_blockquoted_fenced_divs()
    total += print_report(
        "Check 1: Fenced-div Admonition Syntax in Blockquotes (Req 1.14)",
        issues1,
        ["file", "line", "type", "text", "issue"],
    )

    issues2 = check_blank_line_after_admonition()
    total += print_report(
        "Check 2: Blank Line After !!! Admonition Marker (Req 1.15)",
        issues2,
        ["file", "line", "type", "text", "issue"],
    )

    issues3 = check_admonitions_breaking_tables()
    total += print_report(
        "Check 3: Admonitions Breaking Table Structure (Req 1.16)",
        issues3,
        ["file", "line", "type", "table_context", "issue"],
    )

    print(f"\n{'=' * 70}")
    print(f"  SUMMARY: {total} total issue(s) found across all checks.")
    print(f"{'=' * 70}\n")

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
