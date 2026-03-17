#!/usr/bin/env python3
"""
Fix low-level heading hierarchy issues in Markdown files.

Two categories of fixes:
  1. Bold text on its own line (surrounded by blank lines) that should be
     proper Markdown headings.  The heading level is determined by the
     nearest preceding *real* heading (one level deeper).  All consecutive
     bold-as-heading lines at the same context get the same level (siblings).
  2. Heading hierarchy skips (e.g. # followed by ### with no ##).
     The skipped heading is adjusted to be one level deeper than the
     previous heading.

Usage:
    python scripts/fix_heading_hierarchy.py [--dry-run]
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
FRONTMATTER_RE = re.compile(r"^---\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
BOLD_LINE_RE = re.compile(r"^\*\*([^*]+)\*\*$")


def iter_md_files():
    return sorted(DOCS_DIR.rglob("*.md"))


def fix_bold_as_headings(lines):
    """Convert bold-only lines (surrounded by blanks) to headings.

    The heading level is one deeper than the nearest preceding *original*
    heading.  Bold-as-heading lines do NOT affect the tracked heading level,
    so consecutive bold lines become siblings at the same depth.

    Returns (new_lines, changes).
    """
    new_lines = list(lines)
    changes = []
    in_fence = False
    in_frontmatter = False
    frontmatter_count = 0
    last_real_heading_level = 0  # only tracks actual # headings

    for i, line in enumerate(lines):
        # Front-matter
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

        # Track real heading levels (original headings only)
        hm = HEADING_RE.match(line)
        if hm:
            last_real_heading_level = len(hm.group(1))
            continue

        stripped = line.strip()
        m = BOLD_LINE_RE.match(stripped)
        if not m:
            continue

        # Must be short enough to be a heading
        if len(stripped) > 80:
            continue

        # Skip indented bold lines — these are list continuations,
        # admonition content, or code-block examples, not headings.
        if line != line.lstrip():
            continue

        # Must be surrounded by blank lines (heading-like placement)
        prev_blank = (i == 0) or (lines[i - 1].strip() == "")
        next_blank = (i == len(lines) - 1) or (lines[i + 1].strip() == "")
        if not (prev_blank and next_blank):
            continue

        title = m.group(1).strip()

        # Determine heading level: one deeper than the last real heading.
        # If no heading seen yet, default to h2.
        # Cap at h6 (Markdown max).
        if last_real_heading_level == 0:
            level = 2
        else:
            level = min(last_real_heading_level + 1, 6)

        new_heading = "#" * level + " " + title
        new_lines[i] = new_heading
        # Do NOT update last_real_heading_level — these are siblings
        changes.append({
            "line": i + 1,
            "type": "bold_to_heading",
            "detail": f"'{stripped}' -> '{new_heading}'",
        })

    return new_lines, changes


def fix_heading_skips(lines):
    """Fix headings that skip levels (e.g. h1 -> h3 becomes h1 -> h2).

    Returns (new_lines, changes).
    """
    new_lines = list(lines)
    changes = []
    in_fence = False
    in_frontmatter = False
    frontmatter_count = 0
    prev_level = 0

    for i, line in enumerate(lines):
        # Front-matter
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

        hm = HEADING_RE.match(line)
        if not hm:
            continue

        level = len(hm.group(1))
        title = hm.group(2)

        if prev_level > 0 and level > prev_level + 1:
            correct_level = prev_level + 1
            new_heading = "#" * correct_level + " " + title
            new_lines[i] = new_heading
            changes.append({
                "line": i + 1,
                "type": "heading_skip",
                "detail": f"h{level} -> h{correct_level}: '{title.strip()}'",
            })
            prev_level = correct_level
        else:
            prev_level = level

    return new_lines, changes


def fix_file(filepath, dry_run=False):
    """Apply both fixes to a single file. Returns dict with changes or {}."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    # Pass 1: fix bold-as-headings
    lines, changes1 = fix_bold_as_headings(lines)
    # Pass 2: fix heading skips (run on result of pass 1, catches both
    #         original skips and any introduced by pass 1)
    lines, changes2 = fix_heading_skips(lines)

    all_changes = changes1 + changes2
    if not all_changes:
        return {}

    if not dry_run:
        filepath.write_text("\n".join(lines), encoding="utf-8")

    return {"file": rel, "changes": all_changes}


def main():
    import io
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN ===\n")

    results = []
    for f in iter_md_files():
        r = fix_file(f, dry_run=dry_run)
        if r:
            results.append(r)

    if not results:
        print("No heading hierarchy issues found.")
        return 0

    total = sum(len(r["changes"]) for r in results)
    verb = "Would fix" if dry_run else "Fixed"
    print(f"{verb} {total} heading(s) across {len(results)} file(s):\n")
    for r in results:
        print(f"  {r['file']}:")
        for c in r["changes"]:
            print(f"    L{c['line']} [{c['type']}] {c['detail']}")
    print(f"\nDone: {verb} {total} headings in {len(results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
