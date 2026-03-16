#!/usr/bin/env python3
"""
Fix "path/index" link labels in Markdown files.

Scans all Markdown files under the docs directory for links whose visible label
looks like "something/index" (e.g. [wms/index](wms/index.md)) and replaces the
label with the human-readable H1 title extracted from the target file.

Bug Condition:  Page title displays as "path/index"
Expected:       Page titles display human-readable names
Preservation:   Correctly formatted titles remain unchanged
Requirements:   1.2, 2.2, 3.1
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc"

# Pattern: [something/index](target) where label contains a slash
PATH_INDEX_LINK_RE = re.compile(r"\[([\w.-]+/[\w.-]+)\]\(([^)]+)\)")


def get_h1_title(filepath: Path) -> str | None:
    """Extract the first H1 heading from a Markdown file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return None
    in_frontmatter = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        m = re.match(r"^#\s+(.+)$", stripped)
        if m:
            return m.group(1).strip()
    return None


def is_path_index_label(label: str) -> bool:
    """Check if a link label looks like a path/index pattern."""
    return bool(re.match(r"^[\w.-]+/[\w.-]+$", label))


def fix_path_index_links(dry_run: bool = False) -> list[dict]:
    """
    Find and fix all path/index link labels in Markdown files.

    For each link like [wms/index](wms/index.md), resolves the target file
    relative to the source file's directory, extracts the H1 title, and
    replaces the label.

    Returns a list of changes made (or that would be made in dry-run mode).
    """
    changes = []

    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        original = content
        file_dir = md_file.parent

        def replace_link(match: re.Match) -> str:
            label = match.group(1)
            target = match.group(2)

            if not is_path_index_label(label):
                return match.group(0)

            # Resolve target file relative to the source file's directory
            target_path = (file_dir / target).resolve()
            if not target_path.exists():
                return match.group(0)

            title = get_h1_title(target_path)
            if not title:
                return match.group(0)

            changes.append({
                "file": str(md_file.relative_to(ROOT)),
                "old_label": label,
                "new_label": title,
                "target": target,
            })
            return f"[{title}]({target})"

        content = PATH_INDEX_LINK_RE.sub(replace_link, content)

        if content != original and not dry_run:
            md_file.write_text(content, encoding="utf-8")

    return changes


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN — no files will be modified ===\n")

    changes = fix_path_index_links(dry_run=dry_run)

    if not changes:
        print("No path/index link labels found. Nothing to fix.")
        return

    print(f"{'Would fix' if dry_run else 'Fixed'} {len(changes)} path/index link label(s):\n")
    for i, c in enumerate(changes, 1):
        print(f"  [{i}] {c['file']}")
        print(f"      [{c['old_label']}]({c['target']})  →  [{c['new_label']}]({c['target']})")
        print()

    if not dry_run:
        print("All changes written to disk.")


if __name__ == "__main__":
    main()
