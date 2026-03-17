#!/usr/bin/env python3
"""Fix definition list-style content that renders as malformed text.

Two-pronged approach:
1. Enable def_list extension in mkdocs.yml for genuine definition lists.
2. Fix non-genuine patterns: list items, empty markers, RST directives,
   and wrapped continuations.

Requirements: 1.27, 2.27, 3.4
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
DEFLIST_RE = re.compile(r"^: {3}(.*)$")
RST_DIRECTIVE_RE = re.compile(r"^: \.\. (\w+):?\s*$")
LIST_ITEM_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+")


def iter_md_files():
    return sorted(DOCS_DIR.rglob("*.md"))


def _is_blank(line):
    return line.strip() == ""


def _prev_nonblank(buf):
    for j in range(len(buf) - 1, -1, -1):
        if not _is_blank(buf[j]):
            return buf[j]
    return None


def _is_genuine(prev, content):
    """True if prev + ':   content' is a genuine definition list."""
    if prev is None:
        return False
    p = prev.strip()
    if not p:
        return False
    if content.lstrip().startswith("- ") or content.lstrip().startswith("* "):
        return False
    if p.startswith("#") or p.startswith("|"):
        return False
    return True


def fix_lines(lines):
    out = []
    changes = []
    n = len(lines)
    i = 0
    in_fence = False

    while i < n:
        line = lines[i]

        fm = FENCE_RE.match(line)
        if fm:
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue

        # Malformed RST directive: `: .. warning:`
        rst_m = RST_DIRECTIVE_RE.match(line)
        if rst_m:
            dt = rst_m.group(1).lower()
            cont = []
            j = i + 1
            while j < n:
                cl = lines[j]
                if cl.startswith("    ") and cl.strip():
                    cont.append(cl)
                    j += 1
                elif _is_blank(cl) and j + 1 < n and lines[j + 1].startswith("    "):
                    cont.append(cl)
                    j += 1
                else:
                    break
            out.append("!!! " + dt)
            out.extend(cont)
            changes.append({"line": i + 1, "type": "rst_directive",
                            "detail": "Converted to !!! " + dt})
            i = j
            continue

        dm = DEFLIST_RE.match(line)
        if dm:
            content = dm.group(1)

            # Empty marker
            if not content.strip():
                changes.append({"line": i + 1, "type": "empty_marker",
                                "detail": "Removed empty def marker"})
                i += 1
                continue

            # List item under def marker
            if content.lstrip().startswith("- ") or content.lstrip().startswith("* "):
                out.append(content)
                changes.append({"line": i + 1, "type": "list_under_def",
                                "detail": "Promoted: " + content.strip()[:60]})
                i += 1
                continue

            # Wrapped continuation of a list item
            prev = _prev_nonblank(out)
            if prev is not None and LIST_ITEM_RE.match(prev):
                if out and not _is_blank(out[-1]):
                    out[-1] = out[-1].rstrip() + " " + content.strip()
                    changes.append({"line": i + 1, "type": "wrapped",
                                    "detail": "Joined: " + content.strip()[:60]})
                    i += 1
                    continue

            # Genuine definition list - keep for def_list extension
            if _is_genuine(prev, content):
                out.append(line)
                i += 1
                continue

            # Fallback: strip the `:   ` prefix
            out.append(content)
            changes.append({"line": i + 1, "type": "generic",
                            "detail": "Stripped: " + content.strip()[:60]})
            i += 1
            continue

        out.append(line)
        i += 1

    return out, changes


def enable_def_list(dry_run=False):
    p = ROOT / "mkdocs.yml"
    t = p.read_text(encoding="utf-8")
    if "def_list" in t:
        return False
    t = t.replace(
        "markdown_extensions:\n  - admonition",
        "markdown_extensions:\n  - def_list\n  - admonition",
    )
    if not dry_run:
        p.write_text(t, encoding="utf-8")
    return True


def fix_file(fp, dry_run=False):
    try:
        t = fp.read_text(encoding="utf-8")
    except Exception:
        return {}
    lines = t.split("\n")
    rel = str(fp.relative_to(ROOT))
    new_lines, changes = fix_lines(lines)
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

    added = enable_def_list(dry_run)
    v = "Would add" if dry_run else "Added"
    if added:
        print(v + " `def_list` to mkdocs.yml\n")
    else:
        print("`def_list` already in mkdocs.yml\n")

    results = []
    for f in iter_md_files():
        r = fix_file(f, dry_run=dry_run)
        if r:
            results.append(r)

    if not results:
        print("No malformed definition list content found.")
        return 0

    total = sum(len(r["changes"]) for r in results)
    v = "Would fix" if dry_run else "Fixed"
    print("%s %d pattern(s) across %d file(s):\n" % (v, total, len(results)))
    for r in results:
        for c in r["changes"]:
            print("  %s:%d [%s] %s" % (r["file"], c["line"], c["type"], c["detail"]))
    print("\nDone: %s %d patterns in %d files." % (v, total, len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
