#!/usr/bin/env python3
"""Fix list items that lost their content during RST-to-Markdown conversion.

Bug condition: The converter produced empty bullet markers ("- ") followed by
a blank line, then the content that should have been inline with the bullet.
Often the content is followed by definition-list syntax (":   - text") that
should become sub-list items.

Pattern detected (most common):
    - \n
    \n
      **preceding/succeeding**:\n
    \n
      :   - optional, succeeding is used by default
          - not case sensitive

Fix: Merge the empty bullet with the next non-blank content line, producing:
    - **preceding/succeeding**:
      - optional, succeeding is used by default
      - not case sensitive

Also handles the simpler variant without definition-list content:
    - \n
    \n
      `OGC` (default): the scale denominator is computed...
    \n
      :   imposes simplified formulas...

Becomes:
    - `OGC` (default): the scale denominator is computed...
      imposes simplified formulas...

Preservation: Only targets empty bullet markers (lines matching "^- $" or
"^-$" outside code fences). Non-empty list items are left untouched.

Requirements: 1.13, 2.13, 3.4
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
# Empty bullet: "- " with optional trailing whitespace, nothing else
EMPTY_BULLET_RE = re.compile(r"^(\s*)-\s*$")


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def fix_lost_list_content(lines: list[str]) -> tuple[list[str], list[dict]]:
    """Merge empty bullet markers with their displaced content.

    Scans for empty bullets ("- " alone on a line) followed by blank lines
    and then indented content that should have been part of the bullet.
    Merges the content back into the bullet and converts any definition-list
    syntax into proper sub-list items.

    Returns (new_lines, list_of_changes).
    """
    result: list[str] = []
    changes: list[dict] = []
    n = len(lines)
    i = 0
    in_fence = False

    while i < n:
        line = lines[i]

        # Track code fences
        if FENCE_RE.match(line):
            in_fence = not in_fence
            result.append(line)
            i += 1
            continue
        if in_fence:
            result.append(line)
            i += 1
            continue

        # Detect empty bullet
        m = EMPTY_BULLET_RE.match(line)
        if not m:
            result.append(line)
            i += 1
            continue

        bullet_indent = m.group(1)  # leading whitespace before "-"
        content_indent = bullet_indent + "  "  # where content should align

        # Skip blank lines after the empty bullet
        j = i + 1
        while j < n and lines[j].strip() == "":
            j += 1

        # If no content follows, leave the bullet as-is
        if j >= n:
            result.append(line)
            i += 1
            continue

        # The next non-blank line should be indented content
        next_line = lines[j]
        next_stripped = next_line.strip()

        # Only proceed if the next line is indented (content displaced from bullet)
        next_indent = len(next_line) - len(next_line.lstrip())
        if next_indent <= len(bullet_indent):
            # Not indented enough to be displaced content — leave as-is
            result.append(line)
            i += 1
            continue

        # Merge: create the bullet with the content inline
        result.append(f"{bullet_indent}- {next_stripped}")
        original_line = i + 1  # 1-based

        # Skip the blank lines and the content line we just merged
        i = j + 1

        # Now handle any continuation lines that belong to this bullet:
        # - blank lines followed by definition-list content (:   text)
        # - additional indented content
        while i < n:
            cline = lines[i]
            cstripped = cline.strip()

            # Blank line — peek ahead to see if more content follows
            if cstripped == "":
                peek = i + 1
                while peek < n and lines[peek].strip() == "":
                    peek += 1
                if peek >= n:
                    break

                peek_line = lines[peek]
                peek_stripped = peek_line.strip()
                peek_indent = len(peek_line) - len(peek_line.lstrip())

                # If next content is a definition-list line (:   text)
                if peek_stripped.startswith(":"):
                    # Skip blanks, we'll handle the def-list line next
                    result.append("")
                    i += 1
                    continue

                # If next content is indented at the same level as the
                # original displaced content, it's a continuation
                if peek_indent >= next_indent:
                    result.append("")
                    i += 1
                    continue

                # Otherwise, this blank line ends the bullet's content
                break

            # Definition-list line: ":   text" or ":   - text"
            # Convert to properly indented content under the bullet
            deflist_match = re.match(r"^\s*:\s{2,}(.*)", cline)
            if deflist_match:
                defcontent = deflist_match.group(1)
                if defcontent.startswith("- ") or defcontent.startswith("* "):
                    # Sub-list item: indent under the bullet
                    result.append(f"{content_indent}{defcontent}")
                else:
                    # Plain continuation text
                    result.append(f"{content_indent}{defcontent}")
                i += 1
                continue

            # Indented continuation content (part of the same bullet)
            c_indent = len(cline) - len(cline.lstrip())
            if c_indent >= next_indent:
                # Re-indent relative to the bullet's content indent
                extra = c_indent - next_indent
                result.append(f"{content_indent}{' ' * extra}{cstripped}")
                i += 1
                continue

            # Not part of this bullet anymore
            break

        changes.append({
            "line": original_line,
            "preview": f"- {next_stripped}"[:80],
        })

    return result, changes


def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Apply lost-list-content fix to a single file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))

    new_lines, changes = fix_lost_list_content(lines)

    if not changes:
        return {}

    if not dry_run:
        filepath.write_text("\n".join(new_lines), encoding="utf-8")

    return {"file": rel, "changes": changes}


def main():
    import io

    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN -- no files will be modified ===\n")

    all_results = []
    for md_file in iter_md_files():
        result = fix_file(md_file, dry_run=dry_run)
        if result:
            all_results.append(result)

    if not all_results:
        print("No empty list items with lost content found. Nothing to fix.")
        return 0

    total = sum(len(r["changes"]) for r in all_results)
    verb = "Would fix" if dry_run else "Fixed"

    print(
        f"{verb} {total} empty list item(s) with lost content "
        f"across {len(all_results)} file(s):\n"
    )

    for r in all_results:
        for c in r["changes"]:
            print(f"  {r['file']}:{c['line']}  {c['preview']}")

    print(f"\nSummary: {verb} {total} empty list item(s) across {len(all_results)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
