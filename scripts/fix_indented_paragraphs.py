#!/usr/bin/env python3
"""Fix indented paragraphs that render as code blocks or blockquotes.

In Markdown, 4+ spaces of indentation triggers a code block. This script
finds indented text that is NOT inside a code fence, list continuation,
admonition body, or table, and applies the appropriate fix:

1. If the indented block is preceded by a line ending with ":" (RST-style
   code example), wrap it in a fenced code block with ```.
2. Otherwise, strip the leading 4-space indent so it renders as normal prose.

Consecutive indented lines are treated as a single block.

Requirements: 1.26, 2.26, 3.1
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
INDENTED_LINE_RE = re.compile(r"^( {4,})[A-Za-z]")
LIST_ITEM_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+")
ADMONITION_RE = re.compile(r"^\s*!!!\s+\w+")
FRONTMATTER_RE = re.compile(r"^---\s*$")
TABLE_ROW_RE = re.compile(r"^\s*\|")
HTML_COMMENT_RE = re.compile(r"^\s*<!--")


def iter_md_files():
    return sorted(DOCS_DIR.rglob("*.md"))


def _is_blank(line):
    return line.strip() == ""


def _prev_nonblank(lines, idx):
    """Return the previous non-blank line before idx, or ''."""
    for j in range(idx - 1, max(idx - 6, -1), -1):
        if j >= 0 and not _is_blank(lines[j]):
            return lines[j]
    return ""


def _guess_language(block_text):
    """Guess a code fence language hint from block content."""
    text = block_text.strip()
    # Shell commands
    if re.match(r"^(mvn|cd|git|npm|pip|python|java|docker|make|curl|wget|chmod|mkdir|cp|rm|ls|cat|echo|export|source|sudo|apt|yum|brew|gradle)\b", text):
        return "bash"
    # XML/HTML
    if text.startswith("<") and (">" in text):
        return "xml"
    # Java-ish
    if re.search(r"\b(public|private|protected|class|interface|void|new|import|package)\b", text):
        return "java"
    # Python
    if re.search(r"^(def |class |import |from |print\()", text, re.MULTILINE):
        return "python"
    # Properties files
    if re.match(r"^[\w.]+\s*=", text):
        return "properties"
    # SQL
    if re.match(r"^(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b", text, re.IGNORECASE):
        return "sql"
    # Directory listings / paths
    if re.match(r"^[\w\-./]+/?$", text) and "/" in text:
        return ""
    return ""


def _find_list_context(lines, idx):
    """Look backwards from idx to find if this line is inside a list item.

    Returns the list item's indent level if found, or -1 if not in a list.
    Scans backwards through blank lines, code fences, admonitions, and other
    content that can appear inside a list item, looking for the owning list
    item marker.
    """
    m = INDENTED_LINE_RE.match(lines[idx])
    if not m:
        return -1
    target_indent = len(m.group(1))

    in_fence = False
    double_blank = 0
    j = idx - 1
    while j >= 0:
        line = lines[j]

        # Track code fences (backwards — toggle)
        if FENCE_RE.match(line):
            in_fence = not in_fence
            # Reset blank counter when crossing a fence boundary —
            # blanks on opposite sides of a code block aren't consecutive
            double_blank = 0
            j -= 1
            continue
        if in_fence:
            j -= 1
            continue

        if _is_blank(line):
            double_blank += 1
            # Two consecutive blanks break list context in most parsers
            if double_blank >= 2:
                return -1
            j -= 1
            continue
        else:
            double_blank = 0

        # Check for a list item
        lm = LIST_ITEM_RE.match(line)
        if lm:
            li_indent = len(lm.group(1))
            # The content indent of a list item like "1.  text" is
            # li_indent + len(marker) + spaces. For "1.  " that's +4.
            # For "- " that's +2. We check if our target indent is
            # at or deeper than the list item's content indent.
            marker = lm.group(2)
            # Calculate content start position
            full_match = lm.group(0)
            content_indent = len(full_match)
            if target_indent >= content_indent:
                return li_indent
            # If our indent is less than this list item's content,
            # check if there's a parent list item
            if li_indent < target_indent:
                return li_indent

        # A line at indent 0 with no list marker means we've left any list
        if not line.startswith(" ") and not line.startswith("\t"):
            if not lm:
                return -1

        j -= 1

    return -1


def fix_lines(lines):
    """Process lines and fix indented paragraphs.

    Returns (new_lines, changes).
    """
    out = []
    changes = []
    n = len(lines)
    i = 0
    in_fence = False
    in_frontmatter = False
    fm_count = 0
    prev_is_admonition = False
    adm_indent = 0
    blank_count = 0

    while i < n:
        line = lines[i]

        # Front-matter
        if FRONTMATTER_RE.match(line):
            fm_count += 1
            if fm_count <= 2:
                in_frontmatter = not in_frontmatter
            out.append(line)
            i += 1
            continue
        if in_frontmatter:
            out.append(line)
            i += 1
            continue

        # Code fence toggle
        fm = FENCE_RE.match(line)
        if fm:
            in_fence = not in_fence
            prev_is_admonition = False
            out.append(line)
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue

        # Blank lines
        if _is_blank(line):
            blank_count += 1
            out.append(line)
            i += 1
            continue
        else:
            blank_count = 0

        # Admonition tracking
        if ADMONITION_RE.match(line):
            prev_is_admonition = True
            adm_indent = len(line) - len(line.lstrip()) + 4
            out.append(line)
            i += 1
            continue
        if prev_is_admonition:
            indent = len(line) - len(line.lstrip())
            if indent >= adm_indent:
                out.append(line)
                i += 1
                continue
            else:
                prev_is_admonition = False

        # Table rows — skip
        if TABLE_ROW_RE.match(line):
            out.append(line)
            i += 1
            continue

        # HTML comments — skip
        if HTML_COMMENT_RE.match(line):
            out.append(line)
            i += 1
            continue

        # List items — pass through
        lm = LIST_ITEM_RE.match(line)
        if lm:
            out.append(line)
            i += 1
            continue

        # Check for indented line (4+ spaces, starts with letter/digit)
        m = INDENTED_LINE_RE.match(line)
        if m:
            indent = len(m.group(1))

            # Skip list continuations (look backwards for owning list item)
            if _find_list_context(lines, i) >= 0:
                out.append(line)
                i += 1
                continue

            # Collect the full indented block (consecutive indented or blank lines)
            # Stop at code fences, list items, admonitions, tables, etc.
            block_start = i
            block_lines = []
            j = i
            while j < n:
                cur = lines[j]
                # Stop at code fences
                if FENCE_RE.match(cur):
                    break
                # Stop at list items
                if LIST_ITEM_RE.match(cur):
                    break
                # Stop at admonitions
                if ADMONITION_RE.match(cur):
                    break
                # Stop at table rows
                if TABLE_ROW_RE.match(cur):
                    break
                if _is_blank(cur):
                    # Blank line: include if next non-blank is also indented
                    # and not a fence/list/admonition/table
                    k = j + 1
                    while k < n and _is_blank(lines[k]):
                        k += 1
                    if k < n and INDENTED_LINE_RE.match(lines[k]) and \
                       not FENCE_RE.match(lines[k]) and \
                       not LIST_ITEM_RE.match(lines[k]) and \
                       not ADMONITION_RE.match(lines[k]) and \
                       not TABLE_ROW_RE.match(lines[k]):
                        block_lines.append(cur)
                        j += 1
                    else:
                        break
                elif INDENTED_LINE_RE.match(cur):
                    block_lines.append(cur)
                    j += 1
                else:
                    break
            block_end = j

            # Determine fix type based on preceding context
            prev = _prev_nonblank(lines, block_start)
            prev_stripped = prev.rstrip()

            # Check if this is an RST-style indented code block
            # (preceded by a line ending with ":")
            is_code_block = prev_stripped.endswith(":")

            # Also treat as code if all lines look like code/commands
            if not is_code_block:
                block_text = "\n".join(l.strip() for l in block_lines)
                # Short blocks with no sentence-like structure → likely code
                words_per_line = [len(l.split()) for l in block_lines if l.strip()]
                avg_words = sum(words_per_line) / max(len(words_per_line), 1)
                has_prose_markers = any(
                    l.strip()[0:1].isupper() and
                    any(l.strip().endswith(c) for c in ".?!,") and
                    len(l.split()) > 5
                    for l in block_lines if l.strip()
                )
                # If no line looks like prose and avg words is low, treat as code
                if not has_prose_markers and avg_words <= 4 and len(block_lines) <= 8:
                    is_code_block = True

            if is_code_block:
                # Convert to fenced code block
                # Strip common leading whitespace
                stripped = [l for l in block_lines if l.strip()]
                if stripped:
                    min_indent = min(len(l) - len(l.lstrip()) for l in stripped)
                else:
                    min_indent = 4
                code_content = [l[min_indent:] if len(l) > min_indent else l.lstrip()
                                for l in block_lines]
                # Remove trailing blank lines from code content
                while code_content and not code_content[-1].strip():
                    code_content.pop()
                lang = _guess_language("\n".join(code_content))
                out.append("```" + lang)
                out.extend(code_content)
                out.append("```")
                changes.append({
                    "line": block_start + 1,
                    "end_line": block_end,
                    "type": "indented_code_to_fenced",
                    "detail": "Fenced %d line(s) as ```%s" % (len(code_content), lang),
                })
            else:
                # De-indent prose: strip exactly 4 spaces from each line
                for bl in block_lines:
                    if bl.startswith("    "):
                        out.append(bl[4:])
                    else:
                        out.append(bl)
                changes.append({
                    "line": block_start + 1,
                    "end_line": block_end,
                    "type": "deindent_prose",
                    "detail": "De-indented %d line(s) of prose" % len(block_lines),
                })

            i = block_end
            continue

        out.append(line)
        i += 1

    return out, changes


def fix_file(fp, dry_run=False):
    try:
        text = fp.read_text(encoding="utf-8")
    except Exception:
        return {}
    lines = text.split("\n")
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

    results = []
    for f in iter_md_files():
        r = fix_file(f, dry_run=dry_run)
        if r:
            results.append(r)

    if not results:
        print("No indented paragraph issues found.")
        return 0

    total = sum(len(r["changes"]) for r in results)
    verb = "Would fix" if dry_run else "Fixed"
    print("%s %d block(s) across %d file(s):\n" % (verb, total, len(results)))
    for r in results:
        print("  %s:" % r["file"])
        for c in r["changes"]:
            print("    L%d-%d [%s] %s" % (c["line"], c["end_line"], c["type"], c["detail"]))
    print("\nDone: %s %d blocks in %d files." % (verb, total, len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
