#!/usr/bin/env python3
"""
Fix missing syntax highlighting on indented YAML/JSON code blocks (Task 13.4).

Converts 4-space-indented code blocks that contain YAML or JSON content
into properly fenced code blocks with ```yaml or ```json identifiers.

Bug Condition:  YAML/JSON blocks lack syntax highlighting
Expected:       YAML/JSON blocks have appropriate highlighting
Preservation:   Correctly highlighted YAML/JSON remains unchanged
Requirements:   1.7, 2.7, 3.2
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc"


# ---------------------------------------------------------------------------
# Content-based language detection (strict, for indented blocks)
# ---------------------------------------------------------------------------

# Patterns that indicate this is NOT YAML/JSON
_CSS_RE = re.compile(
    r"^\s*[a-zA-Z.#@\[\]][a-zA-Z0-9.#@\[\]:, >+~_-]*\s*\{\s*$", re.MULTILINE
)
_HTTP_HEADER_RE = re.compile(
    r"^(HTTP/\d|Status:\s*\d|Date:|Server:|Content-Type:|Transfer-Encoding:|Location:|X-)", re.MULTILINE
)
_SHELL_PROMPT_RE = re.compile(r"^\s*[$>%#]\s+\w", re.MULTILINE)
_LOG_LINE_RE = re.compile(
    r"^\s*(INFO|WARNING|ERROR|DEBUG|WARN|\[INFO\]|\[ERROR\]|May |Jun |Jul |Aug |Sep |Oct |Nov |Dec |Jan |Feb |Mar |Apr )",
    re.MULTILINE,
)
_MARKDOWN_RE = re.compile(r"^#{1,6}\s|\!\[|\[.*\]\(|^\*\*\w", re.MULTILINE)
_TABLE_RE = re.compile(r"^\s*num\s+#instances\s+#bytes", re.MULTILINE)


_LDIF_RE = re.compile(r"^dn:\s|^objectclass:\s|^ou:\s|^uid:\s|^cn:\s|^member:\s", re.MULTILINE)
_JAVA_REFLECT_RE = re.compile(r"^class:\s+[\w.]+\.(http|servlet|Request|Response)", re.MULTILINE)


def _is_prose_or_other(content: str) -> bool:
    """Reject content that is clearly not YAML/JSON."""
    stripped = content.strip()
    if _CSS_RE.search(stripped):
        return True
    if _HTTP_HEADER_RE.search(stripped):
        return True
    if _SHELL_PROMPT_RE.search(stripped):
        return True
    if _LOG_LINE_RE.search(stripped):
        return True
    if _MARKDOWN_RE.search(stripped):
        return True
    if _TABLE_RE.search(stripped):
        return True
    if _LDIF_RE.search(stripped):
        return True
    if _JAVA_REFLECT_RE.search(stripped):
        return True
    # Reject if most lines are plain English sentences (contain spaces, no colons)
    lines = [l for l in stripped.splitlines() if l.strip()]
    if not lines:
        return True
    prose_lines = sum(
        1 for l in lines
        if " " in l.strip()
        and not re.match(r"^\s*[\w][\w._-]*:\s", l)
        and not re.match(r'^\s*"[\w]', l)  # JSON quoted keys
        and not re.match(r"^\s*-\s", l)
        and not re.search(r'[{}\[\],]', l)  # JSON structural chars
        and not l.strip().startswith("{")
        and not l.strip().startswith("}")
    )
    if len(lines) > 2 and prose_lines / len(lines) > 0.4:
        return True
    return False


def _detect_json(content: str) -> bool:
    """Detect if content is JSON (strict)."""
    stripped = content.strip()
    if not stripped or stripped[0] not in "{[":
        return False
    # Reject CSS blocks that start with {
    if re.search(r"[\w.#][\w.#-]*\s*\{", stripped):
        # Could be CSS, check more carefully
        if re.search(r":\s*\d+px|font-|color:|background:|margin:|padding:", stripped):
            return False
    try:
        json.loads(stripped)
        return True
    except Exception:
        # Relaxed: JSON-like with braces, colons, quotes
        brace_lines = sum(
            1 for l in stripped.splitlines()
            if re.search(r'[{}\[\]",:]', l)
        )
        total = len([l for l in stripped.splitlines() if l.strip()])
        if total > 1 and brace_lines / total > 0.6:
            # Extra check: must have quoted keys or JSON-like structure
            if re.search(r'"[\w]+":', stripped) or re.search(r"'[\w]+':", stripped):
                return True
            # Or typical JSON array/object nesting
            if stripped.count("{") >= 2 or stripped.count("[") >= 2:
                return True
    return False


def _detect_yaml(content: str) -> bool:
    """Detect if content is YAML (strict, for indented blocks)."""
    lines = [l for l in content.splitlines() if l.strip()]
    if not lines:
        return False
    # Reject XML
    if any(l.strip().startswith("<") for l in lines[:3]):
        return False
    # YAML key: value patterns (strict: key must be a simple identifier)
    kv = sum(
        1 for l in lines
        if re.match(r"^\s*[\w][\w._-]*:\s", l) or re.match(r"^\s*[\w][\w._-]*:$", l)
    )
    # YAML list items under keys
    yaml_list = sum(1 for l in lines if re.match(r"^\s*-\s+[\w]", l))
    yaml_score = kv + yaml_list * 0.5
    # Require strong YAML signal
    return kv >= 2 and yaml_score / len(lines) > 0.5


def detect_data_language(content: str) -> str:
    """Return 'json', 'yaml', or '' for content."""
    stripped = content.strip()
    if not stripped:
        return ""
    if _is_prose_or_other(stripped):
        return ""
    if _detect_json(stripped):
        return "json"
    if _detect_yaml(stripped):
        return "yaml"
    return ""


# ---------------------------------------------------------------------------
# Indented code block finder
# ---------------------------------------------------------------------------

def find_indented_yaml_json_blocks(lines: list[str]) -> list[dict]:
    """
    Find 4-space-indented code blocks containing YAML/JSON content.

    Skips blocks inside fenced code blocks, admonitions, and list continuations.
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

        # Skip content inside HTML blocks (e.g., <style> tags)
        if re.match(r"^\s*<(style|script)\b", stripped, re.IGNORECASE):
            i += 1
            tag = re.match(r"^\s*<(\w+)", stripped).group(1).lower()
            close_tag = f"</{tag}>"
            while i < n:
                if close_tag in lines[i].lower():
                    i += 1
                    break
                i += 1
            continue

        # Skip admonition blocks
        if re.match(r"^\s*!!!\s+\w+", stripped):
            i += 1
            adm_indent = len(line) - len(line.lstrip())
            while i < n:
                if lines[i].strip() == "":
                    i += 1
                    continue
                if lines[i].startswith(" " * (adm_indent + 4)):
                    i += 1
                    continue
                break
            continue

        # Check for 4-space indented block start (not inside a list)
        if re.match(r"^    \S", line):
            # Skip if we're inside a list context (list continuation)
            if i > 0:
                j = i - 1
                while j >= 0 and lines[j].strip() == "":
                    j -= 1
                if j >= 0:
                    prev = lines[j]
                    prev_stripped = prev.strip()
                    # Direct list item predecessor
                    if re.match(r"^\s*[-*]\s|^\s*\d+\.\s", prev):
                        i += 1
                        continue
                    # Indented content that's part of a list (look further back)
                    if prev.startswith("    "):
                        # Scan back to find if we're in a list context
                        k = j
                        in_list = False
                        while k >= 0:
                            lk = lines[k]
                            if not lk.strip():
                                k -= 1
                                continue
                            if re.match(r"^\s*\d+\.\s", lk) or re.match(r"^\s*[-*]\s", lk):
                                in_list = True
                                break
                            if not lk.startswith("    "):
                                break
                            k -= 1
                        if in_list:
                            i += 1
                            continue

            # Collect the indented block
            block_start = i
            block_lines = []
            while i < n:
                if re.match(r"^    ", lines[i]) or lines[i].strip() == "":
                    block_lines.append(lines[i])
                    i += 1
                else:
                    break

            # Trim trailing blank lines
            while block_lines and not block_lines[-1].strip():
                block_lines.pop()

            if len(block_lines) < 2:
                continue

            # Dedent content (remove 4-space prefix)
            dedented = "\n".join(
                l[4:] if l.startswith("    ") else l for l in block_lines
            )

            lang = detect_data_language(dedented)
            if lang:
                results.append({
                    "start": block_start,
                    "end": block_start + len(block_lines),
                    "content": dedented,
                    "lang": lang,
                    "raw_lines": block_lines,
                })
            continue

        i += 1

    return results


# ---------------------------------------------------------------------------
# Fix logic
# ---------------------------------------------------------------------------

def fix_file(filepath: Path, dry_run: bool = False) -> list[dict]:
    """
    Fix indented YAML/JSON blocks in a single Markdown file by converting
    them to fenced code blocks with proper language identifiers.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    lines = text.split("\n")
    rel = str(filepath.relative_to(ROOT))
    blocks = find_indented_yaml_json_blocks(lines)

    if not blocks:
        return []

    changes = []
    # Process in reverse so line indices stay valid
    for block in reversed(blocks):
        start = block["start"]
        end = block["end"]
        lang = block["lang"]
        content = block["content"]

        replacement = [f"```{lang}"]
        replacement.extend(content.split("\n"))
        replacement.append("```")

        changes.append({
            "file": rel,
            "line": start + 1,
            "lang": lang,
            "num_lines": end - start,
            "preview": block["raw_lines"][0].rstrip()[:100],
        })

        lines[start:end] = replacement

    if changes and not dry_run:
        filepath.write_text("\n".join(lines), encoding="utf-8")

    return changes


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN -- no files will be modified ===\n")

    all_changes = []
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        file_changes = fix_file(md_file, dry_run=dry_run)
        all_changes.extend(file_changes)

    if not all_changes:
        print("No indented YAML/JSON blocks found. Nothing to fix.")
        return 0

    json_changes = [c for c in all_changes if c["lang"] == "json"]
    yaml_changes = [c for c in all_changes if c["lang"] == "yaml"]

    print(f"{'Would fix' if dry_run else 'Fixed'} {len(all_changes)} indented YAML/JSON block(s):\n")

    if json_changes:
        print(f"  JSON blocks: {len(json_changes)}")
        for c in json_changes:
            print(f"    {c['file']}:{c['line']} ({c['num_lines']} lines)")
            print(f"      {c['preview']}")
        print()

    if yaml_changes:
        print(f"  YAML blocks: {len(yaml_changes)}")
        for c in yaml_changes:
            print(f"    {c['file']}:{c['line']} ({c['num_lines']} lines)")
            print(f"      {c['preview']}")
        print()

    if not dry_run:
        print(f"\nAll {len(all_changes)} changes written to disk.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
