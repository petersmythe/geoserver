#!/usr/bin/env python3
"""
Detection script for code formatting issues (Task 13.1).

Scans all Markdown files for:
  1. Code blocks without syntax highlighting (Req 1.5)
  2. Inline code in nested lists without backticks (Req 1.6)
  3. YAML/JSON blocks without highlighting (Req 1.7)
  4. Code sections rendered as plain text (Req 1.8)

Generates a report of affected files with locations and line numbers.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Patterns that strongly suggest code content (used for plain-text detection)
CODE_INDICATORS = re.compile(
    r"(?:"
    r"^\s*<\?xml\b"            # XML declaration
    r"|^\s*<[a-zA-Z][\w:-]*[>\s/]"  # XML/HTML opening tag
    r"|^\s*\{[\s\n]"           # JSON object start
    r"|^\s*\[[\s\n]"           # JSON array start
    r"|^\s*[a-zA-Z_]\w*\s*[:=]\s*"  # key: value or key = value
    r"|^\s*(import|from|def|class|function|var|let|const|public|private)\s"
    r"|^\s*#\s*include\b"
    r"|^\s*curl\s+-"           # curl commands
    r"|^\s*SELECT\s|^\s*INSERT\s|^\s*UPDATE\s|^\s*DELETE\s"  # SQL
    r")",
    re.IGNORECASE,
)

# Known code-like tokens that should be backtick-wrapped in list items
INLINE_CODE_PATTERNS = re.compile(
    r"(?<![`])\b("
    r"[a-zA-Z_][\w]*\.[a-zA-Z_][\w]*"       # dotted.names
    r"|[a-zA-Z_][\w]*\(\)"                    # function()
    r"|[A-Z][a-z]+[A-Z]\w+"                   # CamelCase identifiers
    r"|(?:true|false|null|none|True|False|None)"  # literals
    r"|[a-z_]+(?:_[a-z_]+)+"                  # snake_case with 2+ segments
    r")\b(?![`])"
)

# Pandoc-style code fence attributes: ``` {.lang ...}
PANDOC_FENCE_RE = re.compile(r"^```\s*\{")

# Languages we can auto-detect from content
YAML_HINT = re.compile(r"^\s*[\w-]+:\s+\S", re.MULTILINE)
JSON_HINT = re.compile(r'^\s*[{\[]', re.MULTILINE)
XML_HINT = re.compile(r'^\s*<[?a-zA-Z]', re.MULTILINE)


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def read_lines(filepath):
    """Read file and return list of lines (strings)."""
    try:
        return filepath.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Check 1: Code blocks without syntax highlighting  (Req 1.5)
# ---------------------------------------------------------------------------

def check_unfenced_code_blocks():
    """
    Find fenced code blocks that have no language identifier.
    Matches opening ``` with nothing after it (or only whitespace).
    Also detects pandoc-style ``` {.lang ...} which MkDocs doesn't render.
    """
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)
        in_code_block = False
        fence_marker = None

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if in_code_block:
                if stripped == fence_marker:
                    in_code_block = False
                    fence_marker = None
                continue

            # Opening fence with a language → OK
            m = re.match(r"^(`{3,}|~{3,})\s*(.*)", stripped)
            if not m:
                continue

            marker = m.group(1)
            info = m.group(2).strip()
            in_code_block = True
            fence_marker = marker

            if not info:
                # Bare ``` with no language
                issues.append({
                    "file": str(rel),
                    "line": i,
                    "text": stripped,
                    "issue": "Code block without language identifier",
                })
            elif PANDOC_FENCE_RE.match(stripped):
                # Pandoc attribute syntax: ``` {.yaml ...}
                issues.append({
                    "file": str(rel),
                    "line": i,
                    "text": stripped,
                    "issue": f"Pandoc-style fence attributes (not rendered by MkDocs): {info}",
                })

    return issues


# ---------------------------------------------------------------------------
# Check 2: Inline code in nested lists without backticks  (Req 1.6)
# ---------------------------------------------------------------------------

def check_inline_code_in_lists():
    """
    Find list items (especially nested) that contain code-like tokens
    not wrapped in backticks.  Focuses on patterns that are almost
    certainly code: dotted names, function calls, snake_case identifiers.
    """
    issues = []
    # Match list items: lines starting with optional whitespace + - or * or 1.
    list_item_re = re.compile(r"^(\s{2,})[-*]|\s+\d+\.\s")

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)
        in_code_block = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Track code blocks to skip them
            if re.match(r"^(`{3,}|~{3,})", stripped):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Only check nested list items (indented 2+ spaces)
            if not list_item_re.match(line):
                continue

            # Remove already-backticked segments before scanning
            cleaned = re.sub(r"`[^`]+`", "", line)

            matches = INLINE_CODE_PATTERNS.findall(cleaned)
            if matches:
                # Deduplicate
                unique = sorted(set(matches))
                issues.append({
                    "file": str(rel),
                    "line": i,
                    "text": line.rstrip()[:120],
                    "tokens": ", ".join(unique),
                    "issue": "Inline code tokens in list item not wrapped in backticks",
                })

    return issues


# ---------------------------------------------------------------------------
# Check 3: YAML/JSON blocks without highlighting  (Req 1.7)
# ---------------------------------------------------------------------------

def check_yaml_json_no_highlighting():
    """
    Find fenced code blocks whose content looks like YAML or JSON but
    whose fence has no language identifier (or a wrong one).
    """
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)
        in_code_block = False
        fence_line = 0
        fence_lang = ""
        block_content = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if not in_code_block:
                m = re.match(r"^(`{3,}|~{3,})\s*(.*)", stripped)
                if m:
                    in_code_block = True
                    fence_line = i
                    fence_lang = m.group(2).strip().lower().split()[0] if m.group(2).strip() else ""
                    block_content = []
                continue

            # Inside code block
            if re.match(r"^(`{3,}|~{3,})\s*$", stripped):
                # Closing fence — analyze content
                if not fence_lang or PANDOC_FENCE_RE.match(lines[fence_line - 1].strip()):
                    content = "\n".join(block_content)
                    detected = _detect_data_language(content)
                    if detected:
                        issues.append({
                            "file": str(rel),
                            "line": fence_line,
                            "detected_lang": detected,
                            "issue": f"Code block contains {detected.upper()} content but has no language identifier",
                        })
                in_code_block = False
                continue

            block_content.append(line)

    return issues


def _detect_data_language(content):
    """Heuristic: return 'yaml', 'json', or None."""
    stripped = content.strip()
    if not stripped:
        return None

    # JSON: starts with { or [
    if stripped[0] in "{[":
        try:
            import json
            json.loads(stripped)
            return "json"
        except Exception:
            # Might still be JSON-ish
            if JSON_HINT.search(stripped):
                return "json"

    # YAML: key: value patterns (but not XML)
    if not XML_HINT.search(stripped) and YAML_HINT.search(stripped):
        # Count key: value lines
        kv_lines = sum(1 for l in stripped.splitlines()
                       if re.match(r"^\s*[\w-]+:\s", l))
        total = len([l for l in stripped.splitlines() if l.strip()])
        if total > 0 and kv_lines / total > 0.4:
            return "yaml"

    return None


# ---------------------------------------------------------------------------
# Check 4: Code sections rendered as plain text  (Req 1.8)
# ---------------------------------------------------------------------------

def check_indented_code_as_plaintext():
    """
    Find blocks of 4-space-indented lines that look like code but are NOT
    inside a fenced code block and NOT inside an admonition or list
    continuation.  These are Markdown "indented code blocks" that likely
    should be fenced code blocks with a language identifier.

    Also detects code blocks wrapped in blockquotes (> ```).
    """
    issues = []
    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)
        in_code_block = False
        indented_run_start = None
        indented_run_lines = []
        prev_is_list = False
        in_admonition = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Track fenced code blocks
            if re.match(r"^(`{3,}|~{3,})", stripped):
                in_code_block = not in_code_block
                _flush_indented(issues, rel, indented_run_start, indented_run_lines)
                indented_run_start = None
                indented_run_lines = []
                continue
            if in_code_block:
                continue

            # Track admonitions (!!!) — indented content under them is expected
            if re.match(r"^!!!\s+\w+", stripped):
                in_admonition = True
                continue
            if in_admonition:
                if line.startswith("    ") or stripped == "":
                    continue
                else:
                    in_admonition = False

            # Track list items — indented continuation is expected
            if re.match(r"^\s*[-*]\s|^\s*\d+\.\s", stripped):
                prev_is_list = True
                continue
            if prev_is_list and (line.startswith("    ") or stripped == ""):
                continue
            prev_is_list = False

            # Detect 4-space indented lines (potential code as plain text)
            if re.match(r"^    \S", line) and not line.startswith("    -") and not line.startswith("    *"):
                if indented_run_start is None:
                    indented_run_start = i
                indented_run_lines.append(line)
            else:
                _flush_indented(issues, rel, indented_run_start, indented_run_lines)
                indented_run_start = None
                indented_run_lines = []

        _flush_indented(issues, rel, indented_run_start, indented_run_lines)

    # Also check for blockquote-wrapped code blocks
    issues.extend(_check_blockquote_code_blocks())

    return issues


def _flush_indented(issues, rel, start_line, lines):
    """If the accumulated indented block looks like code, record an issue."""
    if not lines or len(lines) < 2:
        return
    content = "\n".join(l[4:] for l in lines)  # strip 4-space indent
    # Check if it looks like code
    for l in lines:
        if CODE_INDICATORS.match(l[4:]):
            issues.append({
                "file": str(rel),
                "line": start_line,
                "num_lines": len(lines),
                "preview": lines[0].rstrip()[:100],
                "issue": "Indented block looks like code but is not in a fenced code block",
            })
            return


def _check_blockquote_code_blocks():
    """Find code blocks wrapped in blockquote syntax (> ```)."""
    issues = []
    bq_fence_re = re.compile(r"^>\s*(`{3,}|~{3,})")

    for md_file in iter_md_files():
        lines = read_lines(md_file)
        rel = md_file.relative_to(ROOT)

        for i, line in enumerate(lines, 1):
            if bq_fence_re.match(line.strip()):
                issues.append({
                    "file": str(rel),
                    "line": i,
                    "text": line.rstrip()[:120],
                    "issue": "Code block wrapped in blockquote syntax (> ```)",
                })

    return issues


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def print_report(title, issues, fields):
    """Print a formatted section of the report."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    if not issues:
        print("  ✓ No issues found.")
        return 0
    print(f"  Found {len(issues)} issue(s):\n")
    for idx, issue in enumerate(issues, 1):
        print(f"  [{idx}]")
        for field in fields:
            if field in issue and issue[field]:
                print(f"      {field}: {issue[field]}")
        print()
    return len(issues)


def main():
    print("Code Formatting Issue Detection Report")
    print(f"Docs directory: {DOCS_DIR}")

    total = 0

    # Check 1
    issues1 = check_unfenced_code_blocks()
    total += print_report(
        "Check 1: Code Blocks Without Language Identifier (Req 1.5)",
        issues1,
        ["file", "line", "text", "issue"],
    )

    # Check 2
    issues2 = check_inline_code_in_lists()
    total += print_report(
        "Check 2: Inline Code in Nested Lists Without Backticks (Req 1.6)",
        issues2,
        ["file", "line", "tokens", "issue"],
    )

    # Check 3
    issues3 = check_yaml_json_no_highlighting()
    total += print_report(
        "Check 3: YAML/JSON Blocks Without Highlighting (Req 1.7)",
        issues3,
        ["file", "line", "detected_lang", "issue"],
    )

    # Check 4
    issues4 = check_indented_code_as_plaintext()
    total += print_report(
        "Check 4: Code Sections Rendered as Plain Text (Req 1.8)",
        issues4,
        ["file", "line", "num_lines", "preview", "text", "issue"],
    )

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY: {total} total issue(s) found across all checks.")
    print(f"{'='*70}\n")

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
