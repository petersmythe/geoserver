#!/usr/bin/env python3
"""Fix broken include statements from RST-to-Markdown conversion.

Replaces {%raw%}{% include-markdown "path" %}{%endraw%} statements (outside
code blocks) with the actual content of the referenced file.  When the
included file still contains RST syntax (.txt files from the original RST
docs), a lightweight RST-to-Markdown conversion is applied before inlining.

Include statements inside fenced code blocks are left untouched — those are
intentional examples showing users the include syntax.

Requirements: 1.25, 2.25, 3.6
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

# Pattern for include-markdown wrapped in raw tags (outside code blocks)
INCLUDE_MD_RE = re.compile(
    r'^(?P<indent>\s*)'
    r'\{%raw%\}\{%\s*include-markdown\s+"(?P<path>[^"]+)"\s*%\}\{%endraw%\}',
)


def rst_to_markdown(text: str) -> str:
    """Convert basic RST constructs to Markdown.

    Handles the subset of RST found in the .txt include files:
    - Section headings (underlines with -, ^, ~)
    - ``inline code`` -> `inline code`
    - .. code-block:: lang -> ```lang
    - RST links `text <url>`__ -> [text](url)
    - Indented literal blocks (lines after ::)
    """
    lines = text.split("\n")
    result = []
    i = 0
    in_code_block = False
    code_indent = 0

    while i < len(lines):
        line = lines[i]

        # Handle RST section underlines (next line is all same char)
        if (i + 1 < len(lines) and
                len(lines[i + 1].strip()) > 0 and
                all(c == lines[i + 1].strip()[0] for c in lines[i + 1].strip()) and
                lines[i + 1].strip()[0] in "-^~=" and
                len(lines[i + 1].strip()) >= 3 and
                len(line.strip()) > 0):
            char = lines[i + 1].strip()[0]
            level_map = {"=": "##", "-": "###", "^": "####", "~": "#####"}
            prefix = level_map.get(char, "###")
            result.append(f"{prefix} {line.strip()}")
            i += 2  # skip underline
            continue

        # Handle .. code-block:: lang
        code_match = re.match(r'^(\s*)\.\.\s*code-block::\s*(\w+)', line)
        if code_match:
            lang = code_match.group(2)
            result.append(f"```{lang}")
            i += 1
            # Skip blank line after directive
            if i < len(lines) and lines[i].strip() == "":
                i += 1
            # Determine code indentation from first non-blank line
            if i < len(lines):
                code_match2 = re.match(r'^(\s+)', lines[i])
                code_indent = len(code_match2.group(1)) if code_match2 else 3
            # Collect indented code lines
            while i < len(lines):
                if lines[i].strip() == "":
                    # Blank line — include it but check if code block continues
                    if (i + 1 < len(lines) and
                            (lines[i + 1].startswith(" " * code_indent) or
                             lines[i + 1].strip() == "")):
                        result.append("")
                        i += 1
                        continue
                    else:
                        break
                elif lines[i].startswith(" " * code_indent):
                    result.append(lines[i][code_indent:])
                    i += 1
                else:
                    break
            result.append("```")
            continue

        # Handle RST literal block marker (line ending with ::)
        if line.rstrip().endswith("::") and not line.strip().startswith(".."):
            # Replace trailing :: with : and apply inline conversions
            prefix_line = line.rstrip()[:-1]
            prefix_line = re.sub(r'``([^`]+)``', r'`\1`', prefix_line)
            prefix_line = re.sub(
                r'`([^<]+)<([^>]+)>`(?:__?)?',
                lambda m: f"[{m.group(1).strip()}]({m.group(2).strip()})",
                prefix_line,
            )
            result.append(prefix_line)
            i += 1
            # Skip blank line
            if i < len(lines) and lines[i].strip() == "":
                result.append("")
                i += 1
            # Determine indentation
            if i < len(lines):
                m = re.match(r'^(\s+)', lines[i])
                code_indent = len(m.group(1)) if m else 3
            result.append("```")
            while i < len(lines):
                if lines[i].strip() == "":
                    if (i + 1 < len(lines) and
                            (lines[i + 1].startswith(" " * code_indent) or
                             lines[i + 1].strip() == "")):
                        result.append("")
                        i += 1
                        continue
                    else:
                        break
                elif lines[i].startswith(" " * code_indent):
                    result.append(lines[i][code_indent:])
                    i += 1
                else:
                    break
            result.append("```")
            continue

        # Inline replacements
        converted = line
        # ``code`` -> `code`
        converted = re.sub(r'``([^`]+)``', r'`\1`', converted)
        # RST link `text <url>`__ or `text <url>` -> [text](url)
        converted = re.sub(
            r'`([^<]+)<([^>]+)>`(?:__?)?',
            lambda m: f"[{m.group(1).strip()}]({m.group(2).strip()})",
            converted,
        )

        result.append(converted)
        i += 1

    return "\n".join(result)



def resolve_include_path(md_file: Path, include_path: str) -> Path | None:
    """Resolve the include path relative to the markdown file's directory."""
    target = (md_file.parent / include_path).resolve()
    if target.exists():
        return target
    return None


def read_include_content(include_file: Path) -> str:
    """Read and optionally convert include file content."""
    content = include_file.read_text(encoding="utf-8").strip()

    # If the file has RST syntax markers, convert to Markdown
    has_rst = (
        ".. code-block::" in content
        or re.search(r'^-{3,}$', content, re.MULTILINE)
        or re.search(r'^\^{3,}$', content, re.MULTILINE)
        or '``' in content
        or re.search(r'::$', content, re.MULTILINE)  # any line ending with ::
        or re.search(r'`[^`]+<[^>]+>`', content)  # RST links (with or without __)
    )

    if has_rst and include_file.suffix == ".txt":
        content = rst_to_markdown(content)

    return content


def indent_content(content: str, indent: str) -> str:
    """Apply indentation to each line of content."""
    if not indent:
        return content
    lines = content.split("\n")
    result = []
    for line in lines:
        if line.strip():
            result.append(indent + line)
        else:
            result.append("")
    return "\n".join(result)


def fix_includes_in_file(md_file: Path) -> int:
    """Replace include-markdown statements with actual content. Returns fix count."""
    text = md_file.read_text(encoding="utf-8")
    lines = text.split("\n")
    new_lines = []
    fixes = 0
    in_fence = False

    for line in lines:
        # Track fenced code blocks
        if re.match(r'^\s*```', line) or re.match(r'^\s*~~~', line):
            in_fence = not in_fence

        if in_fence:
            new_lines.append(line)
            continue

        match = INCLUDE_MD_RE.match(line)
        if match:
            indent = match.group("indent")
            include_path = match.group("path")
            target = resolve_include_path(md_file, include_path)

            if target:
                content = read_include_content(target)
                indented = indent_content(content, indent)
                new_lines.append(indented)
                fixes += 1
            else:
                # File not found — leave a comment
                new_lines.append(
                    f"{indent}<!-- Include file not found: {include_path} -->"
                )
                fixes += 1
        else:
            new_lines.append(line)

    if fixes:
        md_file.write_text("\n".join(new_lines), encoding="utf-8")

    return fixes


def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def main():
    print("Include Statement Fix Script")
    print(f"Docs directory: {DOCS_DIR}\n")

    total_fixes = 0
    files_fixed = 0

    for md_file in iter_md_files():
        rel = str(md_file.relative_to(ROOT))
        n = fix_includes_in_file(md_file)
        if n:
            files_fixed += 1
            total_fixes += n
            print(f"  Fixed: {rel} ({n} include(s) replaced)")

    print(f"\nSummary:")
    print(f"  Total includes replaced: {total_fixes}")
    print(f"  Files modified: {files_fixed}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
