#!/usr/bin/env python3
"""
Detection script for image and caption rendering issues.

Scans all Markdown files under doc/en/ for image/caption bugs:
  1. Images wrapped in blockquote syntax (> ![...](path)) — Req 1.18
  2. Image captions inside blockquotes (> *Caption text*) — Req 1.17
  3. Images trapped inside ``` raw_markdown code blocks — Req 1.17
  4. Unfigured captions (plain italic text after image, no figure markup) — Req 1.17

Usage:
    python scripts/detect_image_caption_issues.py
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
# Check 1: Images wrapped in blockquote syntax  (Req 1.18)
# -----------------------------------------------------------------------

def check_blockquote_wrapped_images():
    """Find images incorrectly wrapped in blockquote syntax (> ![...](path))."""
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

            m = re.match(r'^>\s*!\[([^\]]*)\]\(([^)]+)\)', line)
            if m:
                issues.append({
                    "file": rel,
                    "line": i,
                    "image_ref": m.group(2),
                    "alt_text": m.group(1),
                    "text": line.strip()[:120],
                    "issue": "Image wrapped in blockquote syntax",
                })

    return issues


# -----------------------------------------------------------------------
# Check 2: Image captions inside blockquotes  (Req 1.17)
# -----------------------------------------------------------------------

def check_blockquote_captions():
    """Find image captions inside blockquotes alongside their images."""
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False
        prev_was_bq_image = False

        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                prev_was_bq_image = False
                continue
            if in_fence:
                prev_was_bq_image = False
                continue

            is_bq_image = bool(re.match(r'^>\s*!\[', line))

            # Caption line: "> *Some caption text*"
            m = re.match(r'^>\s*\*(.+)\*\s*$', line)
            if m and prev_was_bq_image:
                issues.append({
                    "file": rel,
                    "line": i,
                    "caption": m.group(1),
                    "text": line.strip()[:120],
                    "issue": "Image caption inside blockquote",
                })

            prev_was_bq_image = is_bq_image

    return issues


# -----------------------------------------------------------------------
# Check 3: Images trapped in ``` raw_markdown code blocks  (Req 1.17)
# -----------------------------------------------------------------------

def check_images_in_raw_markdown_blocks():
    """Find images trapped inside ``` raw_markdown fenced code blocks."""
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_raw_block = False

        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*```\s*raw_markdown', line):
                in_raw_block = True
                continue
            if in_raw_block and re.match(r'^\s*```\s*$', line):
                in_raw_block = False
                continue
            if in_raw_block:
                m = re.match(r'^\s*!\[([^\]]*)\]\(([^)]+)\)', line)
                if m:
                    issues.append({
                        "file": rel,
                        "line": i,
                        "image_ref": m.group(2),
                        "alt_text": m.group(1),
                        "text": line.strip()[:120],
                        "issue": "Image trapped in raw_markdown code block",
                    })

    return issues


# -----------------------------------------------------------------------
# Check 4: Unfigured captions (plain italic after image)  (Req 1.17)
# -----------------------------------------------------------------------

def check_unfigured_captions():
    """Find image captions that are plain italic text after an image without figure markup."""
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))
        in_fence = False
        prev_was_image = False

        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                prev_was_image = False
                continue
            if in_fence:
                prev_was_image = False
                continue

            is_image = bool(re.match(r'^\s*!\[', line))

            # Caption line: indented "*Some Caption Text*" (starts with uppercase)
            m = re.match(r'^\s+\*([A-Z].*)\*\s*$', line)
            if m and prev_was_image:
                issues.append({
                    "file": rel,
                    "line": i,
                    "caption": m.group(1),
                    "text": line.strip()[:120],
                    "issue": "Unfigured caption (plain italic text after image)",
                })

            prev_was_image = is_image

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
            if field in issue and issue[field]:
                print(f"      {field}: {issue[field]}")
        print()
    return len(issues)


def main():
    print("Image and Caption Issue Detection Report")
    print(f"Docs directory: {DOCS_DIR}\n")

    total = 0

    issues1 = check_blockquote_wrapped_images()
    total += print_report(
        "Check 1: Images Wrapped in Blockquote Syntax (Req 1.18)",
        issues1,
        ["file", "line", "image_ref", "alt_text", "text", "issue"],
    )

    issues2 = check_blockquote_captions()
    total += print_report(
        "Check 2: Image Captions Inside Blockquotes (Req 1.17)",
        issues2,
        ["file", "line", "caption", "text", "issue"],
    )

    issues3 = check_images_in_raw_markdown_blocks()
    total += print_report(
        "Check 3: Images Trapped in raw_markdown Code Blocks (Req 1.17)",
        issues3,
        ["file", "line", "image_ref", "alt_text", "text", "issue"],
    )

    issues4 = check_unfigured_captions()
    total += print_report(
        "Check 4: Unfigured Captions (Plain Italic After Image) (Req 1.17)",
        issues4,
        ["file", "line", "caption", "text", "issue"],
    )

    # Summary by file
    all_issues = issues1 + issues2 + issues3 + issues4
    affected_files = sorted(set(issue["file"] for issue in all_issues))

    print(f"\n{'=' * 70}")
    print(f"  SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total issues found: {total}")
    print(f"  Affected files: {len(affected_files)}")
    if affected_files:
        print(f"\n  Files with issues:")
        for f in affected_files:
            file_count = sum(1 for issue in all_issues if issue["file"] == f)
            print(f"    - {f} ({file_count} issue(s))")
    print()

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
