#!/usr/bin/env python3
"""Fix pandoc-introduced backslash-escaped quotes and apostrophes.

The RST-to-Markdown conversion (pandoc) unnecessarily escaped ' and "
with backslashes. In Markdown these don't need escaping — the backslash
renders as a visible character.

Skips:
- Content inside code fences (``` blocks)
- Known intentional cases (documenting actual backslash escaping)
- Content inside inline code spans (backticks)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
# Match \' or \" that are NOT inside backtick code spans
ESCAPED_APOS = re.compile(r"\\'")
ESCAPED_QUOTE = re.compile(r'\\"')


def iter_md_files():
    return sorted(DOCS_DIR.rglob("*.md"))


def _in_code_span(line, pos):
    """Check if position pos in line is inside a backtick code span."""
    in_code = False
    i = 0
    while i < len(line) and i < pos:
        if line[i] == '`':
            # Count consecutive backticks
            j = i + 1
            while j < len(line) and line[j] == '`':
                j += 1
            ticks = j - i
            if in_code:
                in_code = False
            else:
                in_code = True
            i = j
        else:
            i += 1
    return in_code


SKIP_PATTERNS = [
    # valuetypes.md: intentional CSS escaping example
    (r"valuetypes\.md", r"prefixing them with a backslash"),
    (r"valuetypes\.md", r"single backslash followed by"),
    # coordtransforms.md: intentional backslash line continuation
    (r"coordtransforms\.md", r'adding a backslash'),
]


def _should_skip_line(rel_path, line):
    """Check if this line contains intentional backslash escapes."""
    for path_pat, line_pat in SKIP_PATTERNS:
        if re.search(path_pat, rel_path) and re.search(line_pat, line):
            return True
    return False


def fix_file(fp, dry_run=False):
    try:
        text = fp.read_text(encoding="utf-8")
    except Exception:
        return {}

    lines = text.split("\n")
    rel = str(fp.relative_to(ROOT))
    changes = []
    new_lines = []
    in_fence = False

    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            new_lines.append(line)
            continue
        if in_fence:
            new_lines.append(line)
            continue

        if _should_skip_line(rel, line):
            new_lines.append(line)
            continue

        # Replace \' and \" outside of inline code spans
        new_line = []
        j = 0
        changed = False
        while j < len(line):
            if line[j] == '`':
                # Skip through code span
                k = j + 1
                while k < len(line) and line[k] == '`':
                    k += 1
                ticks = k - j
                # Find closing backticks
                end = line.find('`' * ticks, k)
                if end == -1:
                    new_line.append(line[j:])
                    j = len(line)
                else:
                    new_line.append(line[j:end + ticks])
                    j = end + ticks
            elif line[j] == '\\' and j + 1 < len(line) and line[j + 1] == "'":
                new_line.append("'")
                j += 2
                changed = True
            elif line[j] == '\\' and j + 1 < len(line) and line[j + 1] == '"':
                new_line.append('"')
                j += 2
                changed = True
            else:
                new_line.append(line[j])
                j += 1

        result = "".join(new_line)
        new_lines.append(result)
        if changed:
            changes.append({
                "line": i + 1,
                "detail": result.strip()[:80],
            })

    if not changes:
        return {}

    if not dry_run:
        fp.write_text("\n".join(new_lines), encoding="utf-8")

    return {"file": rel, "changes": changes}


def main():
    import io
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace")
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN ===\n")

    results = []
    for f in iter_md_files():
        r = fix_file(f, dry_run=dry_run)
        if r:
            results.append(r)

    if not results:
        print("No backslash-escaped quotes found.")
        return 0

    total = sum(len(r["changes"]) for r in results)
    verb = "Would fix" if dry_run else "Fixed"
    print("%s %d line(s) across %d file(s):\n" % (verb, total, len(results)))
    for r in results:
        print("  %s:" % r["file"])
        for c in r["changes"]:
            print("    L%d: %s" % (c["line"], c["detail"]))
    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
