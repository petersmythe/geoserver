#!/usr/bin/env python3
"""
Detection script for heading and structure rendering issues.

Scans all Markdown files under doc/en/ for heading/structure bugs:
  1. Bold text on its own line that should be proper headings       — Req 1.29
  2. Indented prose (4+ spaces) rendering as code blocks            — Req 1.30
  3. Heading hierarchy problems (skipped levels, e.g. # then ###)   — Req 1.29

Usage:
    python scripts/detect_heading_structure_issues.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
FRONTMATTER_RE = re.compile(r"^---\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
# Bold text on its own line: **Some Title**
BOLD_LINE_RE = re.compile(r"^\*\*[^*]+\*\*$")
# 4+ space indented line starting with a capital letter (prose, not code)
INDENTED_PROSE_RE = re.compile(r"^( {4,})[A-Z]")
# Admonition marker
ADMONITION_RE = re.compile(r"^\s*(?:!!!|[?]{3})\s+\w+")
# List item
LIST_ITEM_RE = re.compile(r"^\s*([-*]|\d+\.)\s+")
# Table row
TABLE_ROW_RE = re.compile(r"^\s*\|")
# HTML comment
HTML_COMMENT_RE = re.compile(r"^\s*<!--")


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
# Check 1: Bold text on its own line that should be headings (Req 1.29)
# RST low-level subsection headings sometimes convert to **bold** text
# instead of proper Markdown ### headings.
# -----------------------------------------------------------------------

def check_bold_as_headings():
    """Find bold text on its own line that should be a proper heading."""
    issues = []

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False
        in_frontmatter = False
        frontmatter_count = 0

        for i, line in enumerate(lines):
            # Front-matter handling
            if FRONTMATTER_RE.match(line):
                frontmatter_count += 1
                if frontmatter_count <= 2:
                    in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue

            # Code fence toggle
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            stripped = line.strip()
            if not BOLD_LINE_RE.match(stripped):
                continue
            # Must be short enough to be a heading (not a bold paragraph)
            if len(stripped) > 80:
                continue

            # Check surrounding blank lines (heading-like placement)
            prev_blank = (i == 0) or (lines[i - 1].strip() == "")
            next_blank = (i == len(lines) - 1) or (lines[i + 1].strip() == "")
            if prev_blank and next_blank:
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "text": stripped,
                    "issue": "Bold text on own line — should be a proper heading",
                })

    return issues


# -----------------------------------------------------------------------
# Check 2: Indented prose rendering as code blocks (Req 1.30)
# In Markdown, 4+ spaces of indentation triggers a code block.
# Detect prose text indented 4+ spaces that is NOT inside a code fence,
# NOT a list continuation, NOT admonition content, and NOT a table.
# -----------------------------------------------------------------------

def check_indented_prose_as_code():
    """Find indented prose that Markdown renders as code blocks."""
    issues = []

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False
        in_frontmatter = False
        frontmatter_count = 0
        admonition_indent = -1
        list_context_indent = -1
        blank_count = 0

        for i, line in enumerate(lines):
            # Front-matter handling
            if FRONTMATTER_RE.match(line):
                frontmatter_count += 1
                if frontmatter_count <= 2:
                    in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue

            # Code fence toggle
            if FENCE_RE.match(line):
                in_fence = not in_fence
                admonition_indent = -1
                list_context_indent = -1
                continue
            if in_fence:
                continue

            # Track blank lines
            if line.strip() == "":
                blank_count += 1
                if blank_count >= 2:
                    list_context_indent = -1
                continue
            else:
                blank_count = 0

            # Track admonition context
            if ADMONITION_RE.match(line):
                admonition_indent = len(line) - len(line.lstrip()) + 4
                continue
            if admonition_indent >= 0:
                indent = len(line) - len(line.lstrip())
                if indent >= admonition_indent:
                    continue  # admonition body
                else:
                    admonition_indent = -1

            # Track list context
            if LIST_ITEM_RE.match(line):
                list_context_indent = len(line) - len(line.lstrip())
                continue

            # Skip table rows
            if TABLE_ROW_RE.match(line):
                continue

            # Skip HTML comments
            if HTML_COMMENT_RE.match(line):
                continue

            # Check for indented prose
            m = INDENTED_PROSE_RE.match(line)
            if not m:
                # Reset list context on non-indented, non-list lines
                if not line.startswith(" ") and not line.startswith("\t"):
                    list_context_indent = -1
                continue

            indent = len(m.group(1))
            text = line.strip()

            # Skip if list continuation
            if list_context_indent >= 0 and indent > list_context_indent:
                continue

            # Must look like prose: long enough, has sentence punctuation
            if len(text) < 40:
                continue
            if not (". " in text or ", " in text):
                continue
            # Skip if it looks like code (has code-like characters)
            if re.search(r"[{}()<>=;]", text):
                continue

            issues.append({
                "file": rel,
                "line": i + 1,
                "indent": indent,
                "text": text[:120],
                "issue": "Indented prose (4+ spaces) renders as code block",
            })

            # Reset list context on non-indented lines
            if not line.startswith(" ") and not line.startswith("\t"):
                list_context_indent = -1

    return issues


# -----------------------------------------------------------------------
# Check 3: Heading hierarchy problems (Req 1.29)
# Detect headings that skip levels (e.g., # followed by ### with no ##),
# which indicates the converter may have lost intermediate heading levels.
# -----------------------------------------------------------------------

def check_heading_hierarchy():
    """Find heading hierarchy problems (skipped levels)."""
    issues = []

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False
        in_frontmatter = False
        frontmatter_count = 0
        prev_level = 0

        for i, line in enumerate(lines):
            # Front-matter handling
            if FRONTMATTER_RE.match(line):
                frontmatter_count += 1
                if frontmatter_count <= 2:
                    in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue

            # Code fence toggle
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            m = HEADING_RE.match(line)
            if not m:
                continue

            level = len(m.group(1))
            title = m.group(2).strip()

            # Check for skipped levels (e.g., # then ### without ##)
            if prev_level > 0 and level > prev_level + 1:
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "heading": f"{'#' * level} {title}",
                    "prev_level": prev_level,
                    "curr_level": level,
                    "skipped": level - prev_level - 1,
                    "issue": (
                        f"Heading skips {level - prev_level - 1} level(s): "
                        f"h{prev_level} -> h{level}"
                    ),
                })

            prev_level = level

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
        print("  \u2713 No issues found.")
        return 0
    print(f"  Found {len(issues)} issue(s):\n")
    for idx, issue in enumerate(issues, 1):
        print(f"  [{idx}]")
        for field in fields:
            if field in issue and issue[field] is not None:
                print(f"      {field}: {issue[field]}")
        print()
    return len(issues)


def main():
    import io
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("Heading and Structure Issue Detection Report")
    print(f"Docs directory: {DOCS_DIR}\n")

    total = 0

    issues1 = check_bold_as_headings()
    total += print_report(
        "Check 1: Bold Text as Headings (Req 1.29)",
        issues1,
        ["file", "line", "text", "issue"],
    )

    issues2 = check_indented_prose_as_code()
    total += print_report(
        "Check 2: Indented Prose Rendering as Code Blocks (Req 1.30)",
        issues2,
        ["file", "line", "indent", "text", "issue"],
    )

    issues3 = check_heading_hierarchy()
    total += print_report(
        "Check 3: Heading Hierarchy Problems (Req 1.29)",
        issues3,
        ["file", "line", "heading", "prev_level", "curr_level", "skipped", "issue"],
    )

    # Summary
    all_issues = issues1 + issues2 + issues3
    affected_files = sorted(set(issue["file"] for issue in all_issues))

    print(f"\n{'=' * 70}")
    print(f"  SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total issues found: {total}")
    print(f"  Affected files: {len(affected_files)}")

    print(f"\n  By category:")
    print(f"    Check 1 (bold text as headings):       {len(issues1)}")
    print(f"    Check 2 (indented prose as code):       {len(issues2)}")
    print(f"    Check 3 (heading hierarchy skips):      {len(issues3)}")

    if affected_files:
        print(f"\n  Files with issues:")
        for f in affected_files:
            file_count = sum(1 for issue in all_issues if issue["file"] == f)
            print(f"    - {f} ({file_count} issue(s))")
    print()

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
