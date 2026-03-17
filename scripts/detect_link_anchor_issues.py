#!/usr/bin/env python3
"""
Detection script for link and anchor resolution issues.

Scans all Markdown files under doc/en/ for link/anchor bugs:
  1. Dangling RST-style anchors embedded in Markdown links — Req 1.24
     Pattern: [text<rst_label>](#text<rst_label>)
  2. Failed include statements replaced with HTML comments — Req 1.25
     Pattern: <!-- Include path goes outside docs directory: ... -->
  3. Broken internal links pointing to non-existent .md files — Req 1.24
  4. Include directives wrapped in {%raw%} tags — Req 1.25
     Pattern: {%raw%}{% include ... %}{%endraw%}

Usage:
    python scripts/detect_link_anchor_issues.py
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
# Check 1: Dangling RST-style anchors in Markdown links  (Req 1.24)
# Pattern: [visible text<rst_label>](#visible text<rst_label>)
# These are RST :ref: cross-references that were incorrectly converted
# -----------------------------------------------------------------------

def check_rst_anchor_links():
    """Find links with embedded RST-style anchor labels like [text<label>](#text<label>)."""
    issues = []
    # Matches [anything<word_chars>](#anything<word_chars>)
    pattern = re.compile(r'\[([^\]]*<[a-zA-Z_][a-zA-Z0-9_]*>)\]\(#([^)]*<[a-zA-Z_][a-zA-Z0-9_]*>)\)')

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

            for m in pattern.finditer(line):
                issues.append({
                    "file": rel,
                    "line": i,
                    "link_text": m.group(1),
                    "link_target": "#" + m.group(2),
                    "text": line.strip()[:120],
                    "issue": "RST-style anchor label embedded in Markdown link",
                })

    return issues


# -----------------------------------------------------------------------
# Check 2: Failed include statements (HTML comment placeholders)  (Req 1.25)
# Pattern: <!-- Include path goes outside docs directory: path -->
# These are RST .. include:: directives that couldn't be resolved
# -----------------------------------------------------------------------

def check_failed_include_comments():
    """Find HTML comment placeholders for failed include statements."""
    issues = []
    pattern = re.compile(r'<!--\s*Include path goes outside docs directory:\s*(.+?)\s*-->')

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))

        for i, line in enumerate(lines, 1):
            m = pattern.search(line)
            if m:
                issues.append({
                    "file": rel,
                    "line": i,
                    "original_path": m.group(1),
                    "text": line.strip()[:120],
                    "issue": "Failed include statement (path outside docs directory)",
                })

    return issues


# -----------------------------------------------------------------------
# Check 3: Broken internal links to non-existent .md files  (Req 1.24)
# Checks relative links like [text](path/to/file.md) or
# [text](path/to/file.md#anchor) where the target file doesn't exist
# -----------------------------------------------------------------------

def check_broken_internal_links():
    """Find internal links pointing to non-existent Markdown files."""
    issues = []
    # Match [text](relative_path.md) or [text](relative_path.md#anchor)
    # Exclude absolute URLs (http://, https://, mailto:, etc.)
    link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')

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

            for m in link_pattern.finditer(line):
                target = m.group(2).strip()

                # Skip external URLs, anchors-only, and images
                if target.startswith(('http://', 'https://', 'mailto:', '#', 'ftp://')):
                    continue

                # Strip anchor fragment
                target_path = target.split('#')[0]
                if not target_path:
                    continue

                # Skip non-md targets (images, pdfs, etc.)
                if not target_path.endswith('.md'):
                    continue

                # Resolve relative to the file's directory
                resolved = (md_file.parent / target_path).resolve()
                if not resolved.exists():
                    issues.append({
                        "file": rel,
                        "line": i,
                        "link_text": m.group(1)[:60],
                        "link_target": target,
                        "resolved_path": str(resolved),
                        "text": line.strip()[:120],
                        "issue": "Broken internal link (target file not found)",
                    })

    return issues


# -----------------------------------------------------------------------
# Check 4: Include directives wrapped in {%raw%} tags  (Req 1.25)
# Pattern: {%raw%}{% include "path" %}{%endraw%}
# or: {%raw%}{% include-markdown "path" %}{%endraw%}
# These are Jinja-style includes that may or may not resolve at build time
# -----------------------------------------------------------------------

def check_raw_include_directives():
    """Find include directives wrapped in {%raw%} tags."""
    issues = []
    pattern = re.compile(r'\{%\s*raw\s*%\}.*?\{%\s*include(?:-markdown)?\s+"([^"]+)"\s*%\}')

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = str(md_file.relative_to(ROOT))

        for i, line in enumerate(lines, 1):
            m = pattern.search(line)
            if m:
                include_path = m.group(1)
                # Check if the included file actually exists
                resolved = (md_file.parent / include_path).resolve()
                exists = resolved.exists()
                issues.append({
                    "file": rel,
                    "line": i,
                    "include_path": include_path,
                    "exists": exists,
                    "text": line.strip()[:120],
                    "issue": "Include directive wrapped in {%raw%} tags"
                           + (" (file exists)" if exists else " (FILE NOT FOUND)"),
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
    print("Link and Anchor Issue Detection Report")
    print(f"Docs directory: {DOCS_DIR}\n")

    total = 0

    issues1 = check_rst_anchor_links()
    total += print_report(
        "Check 1: RST-Style Anchor Labels in Markdown Links (Req 1.24)",
        issues1,
        ["file", "line", "link_text", "link_target", "text", "issue"],
    )

    issues2 = check_failed_include_comments()
    total += print_report(
        "Check 2: Failed Include Statements (Req 1.25)",
        issues2,
        ["file", "line", "original_path", "text", "issue"],
    )

    issues3 = check_broken_internal_links()
    total += print_report(
        "Check 3: Broken Internal Links (Req 1.24)",
        issues3,
        ["file", "line", "link_text", "link_target", "text", "issue"],
    )

    issues4 = check_raw_include_directives()
    total += print_report(
        "Check 4: Include Directives in {%raw%} Tags (Req 1.25)",
        issues4,
        ["file", "line", "include_path", "exists", "text", "issue"],
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
