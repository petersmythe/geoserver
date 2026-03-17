#!/usr/bin/env python3
"""
Fix blank lines between !!! admonition markers and their indented content.

MkDocs admonitions should have content immediately following the !!! marker
(indented by 4 spaces). A blank line between the marker and content is a
conversion artifact from RST that can cause rendering issues.

Converts:
    !!! note

        Content here

To:
    !!! note

        Content here

Wait — the pattern is actually:
    !!! note
    <blank>
        Content here

And MkDocs Material *does* render this, but the blank line is a conversion
artifact. The test checks for it, so we remove it.

The fix: remove the blank line between !!! marker and the first indented
content line, keeping the content properly indented.

Requirements: 1.15, 2.15
Preservation: Correctly formatted admonitions remain unchanged.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"


def fix_blank_lines_after_admonition(filepath):
    """
    Remove blank lines between !!! markers and their indented content.

    Returns (new_content, changes_count) or (None, 0) if no changes.
    """
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []
    i = 0
    changes = 0

    while i < len(lines):
        line = lines[i]

        # Skip code fences
        if re.match(r'^\s*```', line):
            new_lines.append(line)
            i += 1
            while i < len(lines):
                new_lines.append(lines[i])
                if re.match(r'^\s*```', lines[i]):
                    i += 1
                    break
                i += 1
            continue

        # Check for !!! admonition marker
        m = re.match(r'^(\s*)!!!\s+(\w+)', line)
        if m:
            indent = m.group(1)
            # Check if next line is blank and line after is indented content
            if (i + 1 < len(lines) and lines[i + 1].strip() == "" and
                    i + 2 < len(lines) and
                    re.match(r'^' + re.escape(indent) + r'    \S', lines[i + 2])):
                # Write the !!! marker, skip the blank line
                new_lines.append(line)
                i += 2  # skip blank line, continue with content
                changes += 1
                continue

        new_lines.append(line)
        i += 1

    if changes == 0:
        return None, 0

    return "\n".join(new_lines), changes


def main():
    total_changes = 0
    files_changed = 0

    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        new_content, changes = fix_blank_lines_after_admonition(md_file)
        if new_content is not None:
            md_file.write_text(new_content, encoding="utf-8")
            rel = md_file.relative_to(ROOT)
            print(f"  Fixed {changes} blank-line admonition(s) in {rel}")
            total_changes += changes
            files_changed += 1

    print(f"\nDone: {total_changes} blank line(s) removed in {files_changed} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
