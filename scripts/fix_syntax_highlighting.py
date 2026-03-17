#!/usr/bin/env python3
"""
Fix missing syntax highlighting on fenced code blocks (Task 13.2).

Handles two categories:
  1. Pandoc-style fences:  ``` {.lang emphasize-lines="..."} -> ```lang hl_lines="..."
  2. Bare fences (``` with no language): detect language from content and add identifier.

Bug Condition:  Code blocks lack syntax highlighting
Expected:       Code blocks have consistent syntax highlighting
Preservation:   Correctly highlighted code remains unchanged
Requirements:   1.5, 2.5, 3.2
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc"

# ---------------------------------------------------------------------------
# Pandoc attribute parsing
# ---------------------------------------------------------------------------

PANDOC_FENCE_RE = re.compile(
    r"^(?P<indent>\s*)(?P<ticks>`{3,})\s*\{(?P<attrs>[^}]*)\}\s*$"
)
PANDOC_LANG_RE = re.compile(r"\.(\w+)")
PANDOC_EMPH_RE = re.compile(r'emphasize-lines\s*=\s*"([^"]*)"')


def convert_pandoc_fence(line: str) -> tuple[str, bool]:
    """Convert a Pandoc-style fence to MkDocs-compatible syntax."""
    m = PANDOC_FENCE_RE.match(line)
    if not m:
        return line, False

    indent = m.group("indent")
    ticks = m.group("ticks")
    attrs = m.group("attrs").strip()

    lang_m = PANDOC_LANG_RE.search(attrs)
    lang = lang_m.group(1) if lang_m else ""
    if lang == "none":
        lang = "text"

    emph_m = PANDOC_EMPH_RE.search(attrs)
    hl_lines = ""
    if emph_m:
        raw = emph_m.group(1).strip()
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        hl_lines = " ".join(parts)

    suffix = ""
    if hl_lines:
        suffix = f' hl_lines="{hl_lines}"'

    new_line = f"{indent}{ticks}{lang}{suffix}"
    return new_line, True


# ---------------------------------------------------------------------------
# Content-based language detection for bare fences
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
    if not stripped:
        return False
    if stripped[0] in "{[":
        try:
            json.loads(stripped)
            return True
        except Exception:
            brace_lines = sum(1 for l in stripped.splitlines()
                              if re.search(r'[{}\[\]",:]', l))
            total = len([l for l in stripped.splitlines() if l.strip()])
            return total > 1 and brace_lines / total > 0.6
    return False


def _detect_yaml(content: str) -> bool:
    lines = [l for l in content.splitlines() if l.strip()]
    if not lines:
        return False
    if _detect_xml(content):
        return False
    # Require at least 2 key-value lines to avoid false positives on single-line content
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
    # CSS selectors: must start with ., #, @, or a known HTML tag, followed by {
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


def detect_language(content: str) -> str:
    """Detect the most likely language for a code block's content."""
    stripped = content.strip()
    if not stripped:
        return ""

    # If the block contains markdown headings, it's likely a mis-paired fence
    if re.search(r"^#{1,6}\s+\S", stripped, re.MULTILINE):
        return ""

    # If the block contains fence markers, it's likely a mis-paired fence
    if re.search(r"`{3,}|~{3,}", stripped):
        return ""

    checks = [
        ("json", _detect_json),
        ("sql", _detect_sql),
        ("java", _detect_java),
        ("python", _detect_python),
        ("css", _detect_css),
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
# Main fix logic
# ---------------------------------------------------------------------------


def fix_file(filepath: Path, dry_run: bool = False) -> list[dict]:
    """
    Fix syntax highlighting in a single Markdown file.

    Two-pass approach:
      Pass 1: Pair up all fenced code blocks (opening + closing fence indices).
      Pass 2: For each pair, fix Pandoc-style or add detected language to bare fences.

    Returns list of changes made.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    lines = text.split("\n")
    changes = []
    rel = str(filepath.relative_to(ROOT))

    # ------------------------------------------------------------------
    # Pass 1: identify all fenced code block pairs
    # ------------------------------------------------------------------
    pairs: list[tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        m = re.match(r"^(`{3,}|~{3,})(.*)", stripped)
        if m:
            ticks = m.group(1)
            tick_char = ticks[0]
            tick_len = len(ticks)

            # Find closing fence
            j = i + 1
            close_re = re.compile(
                r"^\s*" + re.escape(tick_char) + r"{" + str(tick_len) + r",}\s*$"
            )
            while j < len(lines):
                if close_re.match(lines[j]):
                    break
                j += 1

            if j < len(lines):
                pairs.append((i, j, ticks))
                i = j + 1
                continue

        i += 1

    # ------------------------------------------------------------------
    # Pass 2: decide which opening fences to fix
    # ------------------------------------------------------------------
    replacements: dict[int, str] = {}

    for open_idx, close_idx, ticks in pairs:
        line = lines[open_idx]

        # Case 1: Pandoc-style fence
        if PANDOC_FENCE_RE.match(line):
            new_line, changed = convert_pandoc_fence(line)
            if changed:
                changes.append({
                    "file": rel,
                    "line": open_idx + 1,
                    "type": "pandoc",
                    "old": line.rstrip(),
                    "new": new_line.rstrip(),
                })
                replacements[open_idx] = new_line.rstrip()
            continue

        # Case 2: Bare fence (no language identifier)
        bare_m = re.match(r"^(\s*)(`{3,}|~{3,})\s*$", line)
        if not bare_m:
            continue

        indent = bare_m.group(1)
        tick_str = bare_m.group(2)

        block_content = "\n".join(lines[open_idx + 1 : close_idx])
        lang = detect_language(block_content)

        if lang:
            new_fence = f"{indent}{tick_str}{lang}"
            changes.append({
                "file": rel,
                "line": open_idx + 1,
                "type": "bare",
                "detected_lang": lang,
                "old": line.rstrip(),
                "new": new_fence,
            })
            replacements[open_idx] = new_fence

    # ------------------------------------------------------------------
    # Apply replacements
    # ------------------------------------------------------------------
    if replacements:
        new_lines = [
            replacements.get(idx, line)
            for idx, line in enumerate(lines)
        ]
        if not dry_run:
            filepath.write_text("\n".join(new_lines), encoding="utf-8")

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
        print("No syntax highlighting issues found. Nothing to fix.")
        return 0

    pandoc_changes = [c for c in all_changes if c["type"] == "pandoc"]
    bare_changes = [c for c in all_changes if c["type"] == "bare"]

    print(f"{'Would fix' if dry_run else 'Fixed'} {len(all_changes)} code fence(s):\n")

    if pandoc_changes:
        print(f"  Pandoc-style conversions: {len(pandoc_changes)}")
        for c in pandoc_changes:
            print(f"    {c['file']}:{c['line']}")
            print(f"      {c['old']}")
            print(f"      -> {c['new']}")
        print()

    if bare_changes:
        print(f"  Bare fence language detection: {len(bare_changes)}")
        for c in bare_changes:
            print(f"    {c['file']}:{c['line']}  (detected: {c['detected_lang']})")
            print(f"      {c['old']}")
            print(f"      -> {c['new']}")
        print()

    # Summary by detected language
    lang_counts: dict[str, int] = {}
    for c in all_changes:
        lang = c.get("detected_lang", "")
        if not lang and c["type"] == "pandoc":
            m = re.match(r"^\s*`{3,}(\w+)", c["new"])
            lang = m.group(1) if m else "unknown"
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    print("  Language breakdown:")
    for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
        print(f"    {lang}: {count}")

    if not dry_run:
        print(f"\nAll {len(all_changes)} changes written to disk.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
