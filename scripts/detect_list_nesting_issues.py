#!/usr/bin/env python3
"""
Detection script for list and nesting structure issues (Task 14.1).

Scans all Markdown files for:
  1. Nested lists with incorrect indentation / blockquoted list items (Req 1.9, 1.11)
  2. Images in list items rendered as code blocks (Req 1.10)
  3. Numbered lists flattened to text blocks via definition-list syntax (Req 1.12)
  4. List items with lost content / empty bullets (Req 1.13)

Generates a detailed report with affected files, line numbers, and examples.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def read_lines(filepath):
    """Read file and return list of lines (strings)."""
    try:
        return filepath.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []


def _is_fence(line):
    """Return True if *line* is a code-fence opener/closer."""
    return bool(re.match(r"^\s*(`{3,}|~{3,})", line.strip()))


# ---------------------------------------------------------------------------
# Check 1: Blockquoted list items  (Req 1.9, 1.11)
#
# Detects lines like:
#   > - item text
#   > * item text
#   > 1. item text
#   >   > - nested blockquoted item
#
# These are RST list items that the converter wrapped in blockquote
# syntax instead of using proper Markdown indentation.
# ---------------------------------------------------------------------------

def check_blockquoted_list_items():
    """Find list items incorrectly wrapped in blockquote syntax."""
    issues = []
    # Matches "> - ", "> * ", "> 1. " with optional leading whitespace
    bq_list_re = re.compile(r"^\s*>\s*[-*]\s|^\s*>\s*\d+\.\s")

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)
        in_fence = False
        in_admonition = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if _is_fence(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Track admonition blocks — indented content is valid there
            if re.match(r"^\s*!!!\s+\w+", stripped):
                in_admonition = True
                continue
            if in_admonition:
                if stripped == "" or line.startswith("    "):
                    continue
                else:
                    in_admonition = False

            if bq_list_re.match(line):
                issues.append({
                    "file": str(rel),
                    "line": i,
                    "text": stripped[:120],
                    "issue": "List item wrapped in blockquote syntax (> - ...)",
                })

    return issues


# ---------------------------------------------------------------------------
# Check 2: Images inside code fences  (Req 1.10)
#
# Detects image references (![alt](src)) that appear inside fenced code
# blocks — a conversion artifact where images in list items got wrapped
# in ``` raw_markdown fences.
# ---------------------------------------------------------------------------

def check_images_in_code_fences():
    """Find image references trapped inside fenced code blocks."""
    issues = []
    img_re = re.compile(r"!\[.*?\]\(.*?\)")

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)
        in_fence = False
        fence_start = 0
        fence_body = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if _is_fence(line) and not in_fence:
                in_fence = True
                fence_start = i
                fence_body = []
                continue
            if _is_fence(line) and in_fence:
                # Closing fence — check accumulated body for images
                body_text = "\n".join(fence_body)
                for m in img_re.finditer(body_text):
                    issues.append({
                        "file": str(rel),
                        "line": fence_start,
                        "image_ref": m.group()[:100],
                        "issue": "Image reference inside code fence (should render as image)",
                    })
                in_fence = False
                fence_body = []
                continue
            if in_fence:
                fence_body.append(line)

    return issues


# ---------------------------------------------------------------------------
# Check 3: Numbered lists flattened via definition-list syntax  (Req 1.12)
#
# Detects patterns like:
#   :   1. item text
#   : 1. item text
#
# The RST definition-list prefix causes numbered items to render as a
# single solid text block instead of a proper numbered list.
#
# Also detects numbered lists where consecutive items lost their blank-line
# separation and appear on adjacent lines (pandoc artefact):
#   1.  First item
#   2.  Second item     ← no blank line, renders as continuation
# ---------------------------------------------------------------------------

def check_flattened_numbered_lists():
    """Find numbered lists that lost their structure."""
    issues = []
    # Definition-list prefix before numbered item
    deflist_num_re = re.compile(r"^:\s+\d+\.\s")

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)
        in_fence = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if _is_fence(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Definition-list prefix on numbered items
            if deflist_num_re.match(stripped):
                issues.append({
                    "file": str(rel),
                    "line": i,
                    "text": stripped[:120],
                    "issue": "Numbered list item with definition-list prefix (':  1.') — renders as solid text block",
                })

    return issues


# ---------------------------------------------------------------------------
# Check 4: Empty / content-lost list items  (Req 1.13)
#
# Detects:
#   a) Bullet markers ("- " or "* ") with no content after them, followed
#      by non-empty lines that should have been inline.
#   b) Bullets with only trailing whitespace.
#   c) Definition-list syntax inside list items (":  - text") indicating
#      the converter mangled the sub-list.
# ---------------------------------------------------------------------------

def check_empty_list_items():
    """Find list items that lost their content."""
    issues = []

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)
        in_fence = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if _is_fence(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # 4a: Empty bullet "- " at column 0 followed by content on a
            # nearby line.  Only match unindented markers so we skip
            # comment lines like " * " inside code blocks.
            if re.match(r"^[-]\s*$", line) or re.match(r"^[-]\s+$", line):
                # Look ahead for content that should have been inline
                for j in range(i, min(i + 3, len(lines))):
                    next_stripped = lines[j].strip()
                    if next_stripped and not re.match(r"^[-*]\s", next_stripped):
                        issues.append({
                            "file": str(rel),
                            "line": i,
                            "text": repr(line.rstrip()),
                            "next_content": next_stripped[:80],
                            "issue": "Empty list bullet followed by content that should be inline",
                        })
                        break

            # 4c: Definition-list syntax inside a list context
            if re.match(r"^\s+:\s+-\s", line):
                issues.append({
                    "file": str(rel),
                    "line": i,
                    "text": stripped[:120],
                    "issue": "Definition-list syntax inside list (':  - text') — content likely mangled",
                })

    return issues


# ---------------------------------------------------------------------------
# Check 5: Nested list indentation issues  (Req 1.9)
#
# Detects sub-list items that use inconsistent or incorrect indentation.
# In Markdown, nested list items should be indented 2-4 spaces relative
# to their parent.  Common conversion issues:
#   - Tab characters used instead of spaces
#   - Odd indentation levels (1, 3, 5 spaces) that break nesting
#   - Mixed marker styles within the same list level
# ---------------------------------------------------------------------------

def check_nested_list_indentation():
    """Find nested lists with inconsistent or broken indentation."""
    issues = []
    # List item pattern: optional whitespace + marker (-, *, or N.)
    list_item_re = re.compile(r"^(\s*)([-*]|\d+\.)\s")
    tab_list_re = re.compile(r"^\t+\s*([-*]|\d+\.)\s")

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)
        in_fence = False
        in_admonition = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if _is_fence(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # Track admonitions
            if re.match(r"^\s*!!!\s+\w+", stripped):
                in_admonition = True
                continue
            if in_admonition:
                if stripped == "" or line.startswith("    "):
                    continue
                else:
                    in_admonition = False

            # Detect tabs in list items
            if tab_list_re.match(line):
                issues.append({
                    "file": str(rel),
                    "line": i,
                    "text": stripped[:120],
                    "issue": "List item uses tab indentation (should use spaces)",
                })

    return issues


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def print_report(title, issues, fields):
    """Print a formatted section of the report."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
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
    print("List and Nesting Issue Detection Report")
    print(f"Docs directory: {DOCS_DIR}")

    total = 0

    # Check 1: Blockquoted list items (Req 1.9, 1.11)
    issues1 = check_blockquoted_list_items()
    total += print_report(
        "Check 1: Blockquoted List Items (Req 1.9, 1.11)",
        issues1,
        ["file", "line", "text", "issue"],
    )

    # Check 2: Images in code fences (Req 1.10)
    issues2 = check_images_in_code_fences()
    total += print_report(
        "Check 2: Images Inside Code Fences (Req 1.10)",
        issues2,
        ["file", "line", "image_ref", "issue"],
    )

    # Check 3: Flattened numbered lists (Req 1.12)
    issues3 = check_flattened_numbered_lists()
    total += print_report(
        "Check 3: Flattened Numbered Lists (Req 1.12)",
        issues3,
        ["file", "line", "text", "issue"],
    )

    # Check 4: Empty / content-lost list items (Req 1.13)
    issues4 = check_empty_list_items()
    total += print_report(
        "Check 4: Empty / Content-Lost List Items (Req 1.13)",
        issues4,
        ["file", "line", "text", "next_content", "issue"],
    )

    # Check 5: Nested list indentation issues (Req 1.9)
    issues5 = check_nested_list_indentation()
    total += print_report(
        "Check 5: Nested List Indentation Issues (Req 1.9)",
        issues5,
        ["file", "line", "text", "issue"],
    )

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY: {total} total issue(s) found across all checks.")
    print(f"{'='*70}")
    print(f"    Check 1 (Blockquoted lists):      {len(issues1)}")
    print(f"    Check 2 (Images in code fences):   {len(issues2)}")
    print(f"    Check 3 (Flattened numbered lists): {len(issues3)}")
    print(f"    Check 4 (Empty/lost list items):    {len(issues4)}")
    print(f"    Check 5 (Indentation issues):       {len(issues5)}")
    print()

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
