#!/usr/bin/env python3
"""
Detection script for indentation and whitespace rendering issues.

Scans all Markdown files under doc/en/ for indentation/whitespace bugs:
  1. Indented paragraphs that render as code blocks (4+ space indent)  — Req 1.26
  2. Definition list-style content (":   text") rendered incorrectly   — Req 1.27
  3. Text starting with ": " that renders as malformed syntax          — Req 1.28

Usage:
    python scripts/detect_indentation_whitespace_issues.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
# Definition list marker: line starts with ":   " (colon + 3 spaces)
DEFLIST_RE = re.compile(r"^: {3}(.*)$")
# Broader colon-space prefix: indented ":   " inside list context
INDENTED_DEFLIST_RE = re.compile(r"^(\s+): {3}(.*)$")
# Lines starting with ": " but not ":   " (2-space variant)
COLON_SPACE_RE = re.compile(r"^: {1,2}\S")
# 4+ space indented line that looks like prose (starts with letter)
INDENTED_PROSE_RE = re.compile(r"^( {4,})[A-Za-z]")
# List item pattern
LIST_ITEM_RE = re.compile(r"^\s*([-*]|\d+\.)\s+")
# Admonition content (indented under !!! marker)
ADMONITION_RE = re.compile(r"^\s*!!!\s+\w+")
# Front-matter delimiter
FRONTMATTER_RE = re.compile(r"^---\s*$")
# HTML comment
HTML_COMMENT_RE = re.compile(r"^\s*<!--")
# Table row
TABLE_ROW_RE = re.compile(r"^\s*\|")


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
# Check 1: Indented paragraphs rendered as code blocks  (Req 1.26)
# In Markdown, 4+ spaces of indentation triggers a code block.
# Detect prose text indented 4+ spaces that is NOT inside a code fence,
# NOT a list continuation, NOT admonition content, and NOT a table.
# -----------------------------------------------------------------------

def check_indented_paragraphs_as_code():
    """Find indented paragraphs that Markdown will render as code blocks."""
    issues = []

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False
        in_frontmatter = False
        frontmatter_count = 0
        prev_is_admonition = False
        admonition_indent = 0
        # Track list context: if recent lines are list items, indented
        # prose is likely a list continuation, not a bug.
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
                prev_is_admonition = False
                list_context_indent = -1
                continue
            if in_fence:
                continue

            # Track blank lines
            if line.strip() == "":
                blank_count += 1
                # Two consecutive blanks break list context
                if blank_count >= 2:
                    list_context_indent = -1
                continue
            else:
                blank_count = 0

            # Track admonition context
            if ADMONITION_RE.match(line):
                prev_is_admonition = True
                admonition_indent = len(line) - len(line.lstrip()) + 4
                continue
            if prev_is_admonition:
                indent = len(line) - len(line.lstrip())
                if indent >= admonition_indent:
                    continue  # admonition body
                else:
                    prev_is_admonition = False

            # Track list context
            lm = LIST_ITEM_RE.match(line)
            if lm:
                list_context_indent = len(line) - len(line.lstrip())
                continue

            # Skip table rows
            if TABLE_ROW_RE.match(line):
                continue

            # Skip HTML comments
            if HTML_COMMENT_RE.match(line):
                continue

            # Now check for indented prose
            m = INDENTED_PROSE_RE.match(line)
            if m:
                indent = len(m.group(1))
                # Skip if this is a list continuation (indented under a list item)
                if list_context_indent >= 0 and indent > list_context_indent:
                    continue

                # This is a 4+ space indented line that looks like prose
                # and is not in any known context — it will render as a code block
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "indent": indent,
                    "text": line.strip()[:120],
                    "issue": "Indented paragraph (4+ spaces) will render as code block",
                })

            # Reset list context on non-list, non-indented lines
            if not line.startswith(" ") and not line.startswith("\t"):
                list_context_indent = -1

    return issues


# -----------------------------------------------------------------------
# Check 2: Definition list-style content ":   text"  (Req 1.27)
# RST definition lists use indented content after a term.
# The converter sometimes produces ":   text" which is the
# Python-Markdown def_list syntax but may render incorrectly
# if the extension is not enabled or the format is wrong.
# -----------------------------------------------------------------------

def check_definition_list_content():
    """Find definition list-style content with ':   text' pattern."""
    issues = []

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False

        for i, line in enumerate(lines):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Check for ":   text" at start of line
            m = DEFLIST_RE.match(line)
            if m:
                content = m.group(1)
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "content": content.strip()[:100],
                    "text": line.rstrip()[:120],
                    "issue": "Definition list marker ':   ' at line start",
                })
                continue

            # Check for indented ":   text" (inside list context)
            m2 = INDENTED_DEFLIST_RE.match(line)
            if m2:
                indent = m2.group(1)
                content = m2.group(2)
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "indent_level": len(indent),
                    "content": content.strip()[:100],
                    "text": line.rstrip()[:120],
                    "issue": "Indented definition list marker ':   ' in nested context",
                })

    return issues


# -----------------------------------------------------------------------
# Check 3: Text starting with ": " that renders malformed  (Req 1.28)
# Some RST constructs produce lines starting with ": " (colon + space)
# that don't match the full ":   " def_list pattern but still render
# incorrectly in Markdown.
# -----------------------------------------------------------------------

def check_colon_prefix_text():
    """Find text starting with ': ' that may render as malformed syntax."""
    issues = []

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False

        for i, line in enumerate(lines):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Match lines starting with ": " but NOT ":   " (already caught above)
            if COLON_SPACE_RE.match(line):
                issues.append({
                    "file": rel,
                    "line": i + 1,
                    "text": line.rstrip()[:120],
                    "issue": "Line starts with ': ' — possible malformed definition syntax",
                })

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

    print("Indentation and Whitespace Issue Detection Report")
    print(f"Docs directory: {DOCS_DIR}\n")

    total = 0

    issues1 = check_indented_paragraphs_as_code()
    total += print_report(
        "Check 1: Indented Paragraphs Rendered as Code Blocks (Req 1.26)",
        issues1,
        ["file", "line", "indent", "text", "issue"],
    )

    issues2 = check_definition_list_content()
    total += print_report(
        "Check 2: Definition List-Style Content ':   text' (Req 1.27)",
        issues2,
        ["file", "line", "indent_level", "content", "text", "issue"],
    )

    issues3 = check_colon_prefix_text()
    total += print_report(
        "Check 3: Malformed ': ' Prefix Text (Req 1.28)",
        issues3,
        ["file", "line", "text", "issue"],
    )

    # Summary by file
    all_issues = issues1 + issues2 + issues3
    affected_files = sorted(set(issue["file"] for issue in all_issues))

    print(f"\n{'=' * 70}")
    print(f"  SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total issues found: {total}")
    print(f"  Affected files: {len(affected_files)}")

    # Breakdown by check
    print(f"\n  By category:")
    print(f"    Check 1 (indented paragraphs as code):  {len(issues1)}")
    print(f"    Check 2 (definition list ':   '):        {len(issues2)}")
    print(f"    Check 3 (malformed ': ' prefix):         {len(issues3)}")

    if affected_files:
        print(f"\n  Files with issues:")
        for f in affected_files:
            file_count = sum(1 for issue in all_issues if issue["file"] == f)
            print(f"    - {f} ({file_count} issue(s))")
    print()

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
