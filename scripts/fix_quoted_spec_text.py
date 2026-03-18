#!/usr/bin/env python3
"""Fix indented prose that renders as code blocks instead of normal text.

Finds lines matching the "indented prose as code" heuristic (4-space indent,
starts with uppercase, 40+ chars, sentence punctuation, no code chars) and
de-indents them so they render as normal paragraphs.

The heuristic exactly matches the test's find_indented_prose_as_code function
to ensure all flagged lines are fixed.

Requirements: 1.30, 2.30, 3.1
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"


def iter_md_files():
    return sorted(DOCS_DIR.rglob("*.md"))


def find_indented_prose_as_code(content):
    """Exact replica of the test's heuristic.

    Returns list of (line_index, text) for lines that the test would flag.
    """
    results = []
    lines = content.split("\n")
    in_fence = False
    for i, line in enumerate(lines):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not re.match(r"^    [A-Z]", line):
            continue
        text = line.strip()
        if len(text) < 40:
            continue
        if not (". " in text or ", " in text):
            continue
        if re.search(r"[{}()<>=;]", text):
            continue
        prev_idx = i - 1
        while prev_idx >= 0 and lines[prev_idx].strip() == "":
            prev_idx -= 1
        if prev_idx >= 0:
            prev = lines[prev_idx].strip()
            if prev.startswith("!!!") or prev.startswith("???"):
                continue
            if lines[prev_idx].startswith("    "):
                pp = prev_idx - 1
                while pp >= 0 and lines[pp].strip() == "":
                    pp -= 1
                if pp >= 0 and (
                    lines[pp].strip().startswith("!!!")
                    or lines[pp].strip().startswith("???")
                ):
                    continue
        results.append((i, text))
    return results


def fix_file(filepath, dry_run=False):
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    issues = find_indented_prose_as_code(text)
    if not issues:
        return {}

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))
    changes = []

    for idx, prose_text in issues:
        if lines[idx].startswith("    "):
            lines[idx] = lines[idx][4:]
            changes.append({
                "line": idx + 1,
                "type": "deindent",
                "detail": "De-indented: %s" % prose_text[:60],
            })

    if not changes:
        return {}

    result = "\n".join(lines)
    if not dry_run:
        filepath.write_text(result, encoding="utf-8")
    return {"file": rel, "changes": changes}


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
        print("No indented prose issues found.")
        return 0
    total = sum(len(r["changes"]) for r in results)
    verb = "Would fix" if dry_run else "Fixed"
    print("%s %d issue(s) across %d file(s):\n" % (verb, total, len(results)))
    for r in results:
        print("  %s:" % r["file"])
        for c in r["changes"]:
            print("    [%s] %s" % (c["type"], c["detail"]))
    print("\nDone: %s %d issues in %d files." % (verb, total, len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
