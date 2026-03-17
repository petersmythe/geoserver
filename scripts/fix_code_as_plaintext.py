#!/usr/bin/env python3
"""
Fix code sections rendered as plain text (Task 13.5).

Handles two categories:
  1. Indented code blocks: 4-space-indented lines that look like code but lack
     fenced code block markers. Converts them to fenced code blocks with
     auto-detected language identifiers.
  2. Blockquote-wrapped code blocks: Lines prefixed with "> " that contain
     fenced code blocks. Strips the blockquote prefix so the code block
     renders properly.

Bug Condition:  Code sections render as plain text paragraphs
Expected:       Code sections maintain code block formatting
Preservation:   Non-code text remains as paragraphs
Requirements:   1.8, 2.8, 3.2
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc"

# ---------------------------------------------------------------------------
# Language detection (reused from fix_syntax_highlighting.py)
# ---------------------------------------------------------------------------

def _detect_xml(content: str) -> bool:
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if not lines:
        return False
    first = lines[0]
    if first.startswith("<?xml") or re.match(r"^<\w[\w:-]*[\s/>]", first):
        return True
    tag_lines = sum(1 for l in lines if re.search(r"</?[a-zA-Z][\w:-]*[\s/>]", l))
    return len(lines) > 1 and tag_lines / len(lines) > 0.5


def _detect_json(content: str) -> bool:
    stripped = content.strip()
    if not stripped or stripped[0] not in "{[":
        return False
    try:
        json.loads(stripped)
        return True
    except Exception:
        brace_lines = sum(1 for l in stripped.splitlines()
                          if re.search(r'[{}\[\]",:]', l))
        total = len([l for l in stripped.splitlines() if l.strip()])
        return total > 1 and brace_lines / total > 0.6


def _detect_yaml(content: str) -> bool:
    lines = [l for l in content.splitlines() if l.strip()]
    if not lines:
        return False
    if any(l.strip().startswith("<") for l in lines[:3]):
        return False
    kv = sum(1 for l in lines if re.match(r"^\s*[\w][\w. -]*:\s", l))
    return kv >= 2 and kv / len(lines) > 0.4


def _detect_sql(content: str) -> bool:
    upper = content.upper()
    keywords = ["SELECT ", "INSERT ", "UPDATE ", "DELETE ", "CREATE ", "ALTER ",
                "DROP ", "FROM ", "WHERE ", "JOIN "]
    hits = sum(1 for kw in keywords if kw in upper)
    return hits >= 2


def _detect_java(content: str) -> bool:
    indicators = [
        re.compile(r"^\s*(public|private|protected)\s+(static\s+)?(class|void|int|String|boolean)\s"),
        re.compile(r"^\s*import\s+[\w.]+;"),
        re.compile(r"^\s*package\s+[\w.]+;"),
        re.compile(r"\bSystem\.out\.print"),
        re.compile(r"@(Override|Test|Autowired|Bean)\b"),
    ]
    lines = content.splitlines()
    hits = sum(1 for l in lines for pat in indicators if pat.search(l))
    return hits >= 2


def _detect_python(content: str) -> bool:
    indicators = [
        re.compile(r"^\s*(def|class)\s+\w+.*:"),
        re.compile(r"^\s*import\s+\w+"),
        re.compile(r"^\s*from\s+\w+\s+import\s"),
        re.compile(r"^\s*print\s*\("),
        re.compile(r"^\s*if\s+__name__\s*=="),
    ]
    lines = content.splitlines()
    hits = sum(1 for l in lines for pat in indicators if pat.search(l))
    return hits >= 2


def _detect_css(content: str) -> bool:
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if not lines:
        return False
    css_selector_re = re.compile(
        r"^(?:[.#@][\w-]|(?:html|body|div|span|p|a|ul|ol|li|table|tr|td|th|"
        r"h[1-6]|img|form|input|button|header|footer|nav|section|article|main|"
        r"aside|figure|figcaption)\b|[\w.#\[\]:, >+~-]+\s*,\s*[\w.#])"
        r".*\{\s*$"
    )
    selector_lines = sum(1 for l in lines if css_selector_re.match(l))
    if selector_lines == 0:
        return False
    closing = sum(1 for l in lines if l == "}")
    prop_lines = sum(1 for l in lines if re.match(r"^\s*[\w-]+\s*:\s*.+;", l))
    return (selector_lines + closing + prop_lines) / len(lines) > 0.4


def _detect_properties(content: str) -> bool:
    lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
    if not lines:
        return False
    kv = sum(1 for l in lines if re.match(r"^[\w.-]+=", l))
    return len(lines) > 1 and kv / len(lines) > 0.6


def _detect_shell(content: str) -> bool:
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if not lines:
        return False
    indicators = 0
    for l in lines:
        if l.startswith("$ ") or l.startswith("# ") or l.startswith("% "):
            indicators += 1
        elif re.match(r"^(curl|wget|docker|make|cd|ls|cat|echo|export|sudo|chmod|mkdir|cp|mv|rm|pip|npm|mvn|gradle|git|java|python)\s", l):
            indicators += 1
        elif l.startswith("./") or l.startswith("source "):
            indicators += 1
    return indicators / len(lines) > 0.3


def _detect_html(content: str) -> bool:
    lower = content.lower()
    if "<!doctype html" in lower or "<html" in lower:
        return True
    html_tags = ["<head", "<body", "<div", "<script", "<style", "<form", "<table"]
    hits = sum(1 for t in html_tags if t in lower)
    return hits >= 2


def _detect_http(content: str) -> bool:
    """Detect HTTP request/response content."""
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if not lines:
        return False
    first = lines[0]
    if re.match(r"^HTTP/\d", first):
        return True
    if re.match(r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+/", first):
        return True
    header_lines = sum(1 for l in lines if re.match(r"^[\w-]+:\s", l))
    return header_lines >= 2 and header_lines / len(lines) > 0.3


def detect_language(content: str) -> str:
    """Detect the most likely language for a code block's content."""
    stripped = content.strip()
    if not stripped:
        return ""

    # If the block contains markdown headings, skip
    if re.search(r"^#{1,6}\s+\S", stripped, re.MULTILINE):
        return ""

    # If the block contains fence markers, skip
    if re.search(r"`{3,}|~{3,}", stripped):
        return ""

    checks = [
        ("json", _detect_json),
        ("sql", _detect_sql),
        ("java", _detect_java),
        ("python", _detect_python),
        ("css", _detect_css),
        ("http", _detect_http),
        ("html", _detect_html),
        ("xml", _detect_xml),
        ("yaml", _detect_yaml),
        ("properties", _detect_properties),
        ("bash", _detect_shell),
    ]

    for lang, check_fn in checks:
        try:
            if check_fn(stripped):
                return lang
        except Exception:
            continue

    return ""


# ---------------------------------------------------------------------------
# Prose / non-code rejection (avoid converting real prose to code blocks)
# ---------------------------------------------------------------------------

_PROSE_INDICATORS = re.compile(
    r"(?:"
    r"^\s*<\?xml\b"
    r"|^\s*<[a-zA-Z][\w:-]*[\s/>]"
    r"|^\s*\{[\s\n]"
    r"|^\s*\[[\s\n]"
    r"|^\s*[a-zA-Z_]\w*\s*[:=]\s*"
    r"|^\s*(import|from|def|class|function|var|let|const|public|private)\s"
    r"|^\s*#\s*include\b"
    r"|^\s*curl\s+-"
    r"|^\s*SELECT\s|^\s*INSERT\s|^\s*UPDATE\s|^\s*DELETE\s"
    r"|^\s*@\w+"
    r"|^\s*<!"
    r"|^\s*(GET|POST|PUT|DELETE|PATCH)\s+/"
    r"|^\s*HTTP/\d"
    r"|^\s*[\w-]+:\s+\S"
    r"|^\s*\$\s+\w"
    r"|^\s*[{}()\[\];]"
    r"|^\s*//\s"
    r"|^\s*/\*"
    r"|^\s*\*\s"
    r"|^\s*\*/\s*$"
    r"|^\s*#!\s*/\w"
    r"|^\s*-D\w+"
    r"|^\s*export\s+\w+="
    r")",
    re.IGNORECASE,
)


def _looks_like_code(lines: list[str]) -> bool:
    """Check if a set of dedented lines look like code content."""
    if not lines:
        return False
    for l in lines:
        if _PROSE_INDICATORS.match(l):
            return True
    return False


# ---------------------------------------------------------------------------
# Fix 1: Indented code blocks → fenced code blocks
# ---------------------------------------------------------------------------

def find_indented_code_blocks(lines: list[str]) -> list[dict]:
    """
    Find indented code blocks that should be fenced code blocks.

    Detects two patterns:
    1. Standard 4-space-indented blocks (Markdown indented code blocks)
    2. Deeper-indented blocks inside list items (e.g., 6-space indent under
       a `- ` list item = 2 for list marker + 4 for code)
    """
    results = []
    i = 0
    n = len(lines)
    in_fence = False

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Track fenced code blocks
        if re.match(r"^\s*(`{3,}|~{3,})", stripped):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue

        # Skip HTML blocks (<style>, <script>)
        if re.match(r"^\s*<(style|script)\b", stripped, re.IGNORECASE):
            tag_m = re.match(r"^\s*<(\w+)", stripped)
            if tag_m:
                close_tag = f"</{tag_m.group(1).lower()}>"
                i += 1
                while i < n:
                    if close_tag in lines[i].lower():
                        i += 1
                        break
                    i += 1
                continue

        # Skip admonition blocks
        if re.match(r"^\s*!!!\s+\w+", stripped):
            i += 1
            while i < n:
                if lines[i].strip() == "":
                    i += 1
                    continue
                if lines[i].startswith("    "):
                    i += 1
                    continue
                break
            continue

        # Determine if we're looking at an indented block (4+ spaces)
        indent_m = re.match(r"^( {4,})\S", line)
        if indent_m:
            block_indent = len(indent_m.group(1))

            # Determine list context
            list_indent = ""
            in_list_context = False
            expected_code_indent = 4  # default: top-level indented code

            if i > 0:
                j = i - 1
                while j >= 0 and lines[j].strip() == "":
                    j -= 1
                if j >= 0:
                    prev = lines[j]
                    # Direct list item predecessor
                    list_m = re.match(r"^(\s*)([-*]\s+|\d+\.\s+)", prev)
                    if list_m:
                        in_list_context = True
                        marker_end = len(list_m.group(1)) + len(list_m.group(2))
                        list_indent = " " * marker_end
                        expected_code_indent = marker_end + 4
                    # Indented content that's part of a list
                    elif prev.startswith("    "):
                        k = j
                        while k >= 0:
                            lk = lines[k]
                            if not lk.strip():
                                k -= 1
                                continue
                            lm = re.match(r"^(\s*)([-*]\s+|\d+\.\s+)", lk)
                            if lm:
                                in_list_context = True
                                marker_end = len(lm.group(1)) + len(lm.group(2))
                                list_indent = " " * marker_end
                                expected_code_indent = marker_end + 4
                                break
                            if not lk.startswith("    "):
                                break
                            k -= 1

            # For list-context blocks, the code indent must match
            # list_marker_width + 4. For non-list, it must be exactly 4.
            if in_list_context:
                if block_indent < expected_code_indent:
                    i += 1
                    continue
                dedent_amount = expected_code_indent
            else:
                if block_indent != 4:
                    i += 1
                    continue
                dedent_amount = 4

            # Collect the indented block
            block_start = i
            block_lines = []
            min_indent = " " * dedent_amount
            while i < n:
                if lines[i].startswith(min_indent) or lines[i].strip() == "":
                    block_lines.append(lines[i])
                    i += 1
                else:
                    break

            # Trim trailing blank lines
            while block_lines and not block_lines[-1].strip():
                block_lines.pop()

            # Dedent content
            dedented_lines = [
                l[dedent_amount:] if l.startswith(min_indent) else l
                for l in block_lines
            ]
            dedented = "\n".join(dedented_lines)

            if len(block_lines) < 2:
                # Allow single-line blocks in list context if they look
                # strongly like code (system properties, exports, etc.)
                if len(block_lines) == 1 and in_list_context:
                    single = dedented_lines[0].strip()
                    if re.match(
                        r"^(-D\w|export\s+\w+=|curl\s|<\w+|<\?xml|\$\s|\{)",
                        single,
                    ):
                        # Strong code signal - skip the language requirement
                        lang = detect_language(dedented)
                        results.append({
                            "start": block_start,
                            "end": block_start + len(block_lines),
                            "content": dedented,
                            "lang": lang,
                            "raw_lines": block_lines,
                            "list_indent": list_indent,
                        })
                    continue
                # Allow single-line non-list blocks if they look like
                # property assignments or code
                elif len(block_lines) == 1 and not in_list_context:
                    single = dedented_lines[0].strip()
                    if _looks_like_code([single]):
                        lang = detect_language(dedented)
                        # Also recognize single-line property assignments
                        # (key=value where key is a word and value is non-trivial)
                        if not lang and re.match(r"^[\w][\w.-]*=\S", single):
                            lang = "properties"
                        if lang:
                            results.append({
                                "start": block_start,
                                "end": block_start + len(block_lines),
                                "content": dedented,
                                "lang": lang,
                                "raw_lines": block_lines,
                                "list_indent": "",
                            })
                    continue
                else:
                    continue

            # Check if it looks like code
            if not _looks_like_code(dedented_lines):
                continue

            lang = detect_language(dedented)

            # For list-context blocks, require stronger code signal
            # (must have a detected language) to avoid converting prose
            if in_list_context and not lang:
                continue

            # Extra safety: reject list-context blocks that look like
            # Markdown content (images, includes, prose with formatting)
            if in_list_context:
                first_stripped = dedented_lines[0].strip() if dedented_lines else ""
                # Markdown images
                if first_stripped.startswith("!["):
                    continue
                # Jinja/template includes
                if "{%" in first_stripped or "{{" in first_stripped:
                    continue
                # Prose starting with a sentence (capital letter + spaces)
                words = first_stripped.split()
                if len(words) > 4 and not any(c in first_stripped for c in "<{[=;"):
                    continue

            results.append({
                "start": block_start,
                "end": block_start + len(block_lines),
                "content": dedented,
                "lang": lang,
                "raw_lines": block_lines,
                "list_indent": list_indent if in_list_context else "",
            })
            continue

        i += 1

    return results


# ---------------------------------------------------------------------------
# Fix 2: Blockquote-wrapped code blocks → unwrapped code blocks
# ---------------------------------------------------------------------------

def find_blockquote_code_blocks(lines: list[str]) -> list[dict]:
    """
    Find code blocks wrapped in blockquote syntax (> ``` ... > ```).
    These need the > prefix stripped so the code block renders properly.
    """
    results = []
    i = 0
    n = len(lines)
    in_fence = False

    # Track non-blockquote fenced blocks to skip them
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Skip normal fenced code blocks (not blockquote-wrapped)
        if not stripped.startswith(">") and re.match(r"^\s*(`{3,}|~{3,})", stripped):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue

        # Detect blockquote-wrapped fence opening
        bq_fence_m = re.match(r"^(\s*)>\s*(`{3,}|~{3,})(.*)", line)
        if bq_fence_m:
            indent = bq_fence_m.group(1)
            ticks = bq_fence_m.group(2)
            lang_info = bq_fence_m.group(3).strip()
            tick_char = ticks[0]
            tick_len = len(ticks)
            block_start = i

            # Collect lines until closing fence
            block_lines = [line]
            i += 1
            close_re = re.compile(
                r"^\s*>\s*" + re.escape(tick_char) + r"{" + str(tick_len) + r",}\s*$"
            )
            while i < n:
                block_lines.append(lines[i])
                if close_re.match(lines[i]):
                    i += 1
                    break
                i += 1
            else:
                # No closing fence found, skip
                continue

            results.append({
                "start": block_start,
                "end": block_start + len(block_lines),
                "indent": indent,
                "ticks": ticks,
                "lang_info": lang_info,
                "raw_lines": block_lines,
            })
            continue

        i += 1

    return results


# ---------------------------------------------------------------------------
# Fix logic
# ---------------------------------------------------------------------------

def fix_file(filepath: Path, dry_run: bool = False) -> list[dict]:
    """Fix code-as-plaintext issues in a single Markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))
    changes = []

    # Find both types of issues
    indented_blocks = find_indented_code_blocks(lines)
    bq_blocks = find_blockquote_code_blocks(lines)

    if not indented_blocks and not bq_blocks:
        return []

    # Process in reverse order so line indices stay valid
    all_blocks = []
    for b in indented_blocks:
        b["type"] = "indented"
        all_blocks.append(b)
    for b in bq_blocks:
        b["type"] = "blockquote"
        all_blocks.append(b)

    all_blocks.sort(key=lambda b: b["start"], reverse=True)

    for block in all_blocks:
        start = block["start"]
        end = block["end"]

        if block["type"] == "indented":
            lang = block["lang"]
            content = block["content"]
            list_indent = block.get("list_indent", "")
            replacement = [f"{list_indent}```{lang}"]
            replacement.extend(content.split("\n"))
            replacement.append(f"{list_indent}```")

            changes.append({
                "file": rel,
                "line": start + 1,
                "type": "indented",
                "lang": lang or "(none)",
                "num_lines": end - start,
                "preview": block["raw_lines"][0].rstrip()[:100],
            })
            lines[start:end] = replacement

        elif block["type"] == "blockquote":
            raw = block["raw_lines"]
            indent = block["indent"]
            replacement = []
            for raw_line in raw:
                # Strip the "> " prefix, preserving any leading indent
                stripped = raw_line
                # Match: optional indent + > + optional space + content
                m = re.match(r"^(\s*)>\s?(.*)", stripped)
                if m:
                    replacement.append(indent + m.group(2))
                else:
                    replacement.append(raw_line)

            changes.append({
                "file": rel,
                "line": start + 1,
                "type": "blockquote",
                "lang": block["lang_info"] or "(none)",
                "num_lines": end - start,
                "preview": raw[0].rstrip()[:100],
            })
            lines[start:end] = replacement

    if changes and not dry_run:
        filepath.write_text("\n".join(lines), encoding="utf-8")

    return changes


def main():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN -- no files will be modified ===\n")

    all_changes = []
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        file_changes = fix_file(md_file, dry_run=dry_run)
        all_changes.extend(file_changes)

    if not all_changes:
        print("No code-as-plaintext issues found. Nothing to fix.")
        return 0

    indented_changes = [c for c in all_changes if c["type"] == "indented"]
    bq_changes = [c for c in all_changes if c["type"] == "blockquote"]

    print(f"{'Would fix' if dry_run else 'Fixed'} {len(all_changes)} code-as-plaintext issue(s):\n")

    if indented_changes:
        print(f"  Indented code blocks converted to fenced: {len(indented_changes)}")
        for c in indented_changes:
            print(f"    {c['file']}:{c['line']} ({c['num_lines']}L, lang={c['lang']})")
            print(f"      {c['preview']}")
        print()

    if bq_changes:
        print(f"  Blockquote-wrapped code blocks unwrapped: {len(bq_changes)}")
        for c in bq_changes:
            print(f"    {c['file']}:{c['line']} ({c['num_lines']}L, lang={c['lang']})")
            print(f"      {c['preview']}")
        print()

    # Language breakdown for indented blocks
    if indented_changes:
        lang_counts: dict[str, int] = {}
        for c in indented_changes:
            lang_counts[c["lang"]] = lang_counts.get(c["lang"], 0) + 1
        print("  Language breakdown (indented blocks):")
        for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
            print(f"    {lang}: {count}")

    if not dry_run:
        print(f"\nAll {len(all_changes)} changes written to disk.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
