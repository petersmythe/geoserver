#!/usr/bin/env python3
"""Fix plain {%raw%}{% include "file" %}{%endraw%} statements.

These are RST ``.. include::`` directives that were converted to Jinja2-style
include statements wrapped in {%raw%} tags. The {%raw%} wrapper prevents
MkDocs from processing them, so the literal template syntax is displayed
instead of the actual file content.

This script replaces the include statement with the actual file content,
keeping it inside whatever code fence context it's in.

Also handles unclosed {%raw%} tags (missing {%endraw%}).

Requirements: 1.25, 2.25
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"

# Pattern for {%raw%}{% include "path" %}{%endraw%} (with or without endraw)
RAW_INCLUDE_RE = re.compile(
    r'^(?P<indent>\s*)'
    r'\{%\s*raw\s*%\}\s*'
    r'\{%\s*include\s+'
    r'["\'](?P<path>[^"\']+)["\']\s*'
    r'%\}'
    r'(?:\s*\{%\s*endraw\s*%\})?'
    r'\s*$'
)


def resolve_include_path(md_file: Path, include_path: str) -> Path | None:
    """Resolve the include path relative to the markdown file's directory."""
    target = (md_file.parent / include_path).resolve()
    if target.exists():
        return target
    return None


def fix_file(md_file: Path) -> int:
    """Replace raw include statements with actual file content. Returns fix count."""
    text = md_file.read_text(encoding="utf-8")
    lines = text.split("\n")
    new_lines = []
    fixes = 0

    for line in lines:
        match = RAW_INCLUDE_RE.match(line)
        if match:
            indent = match.group("indent")
            include_path = match.group("path")
            target = resolve_include_path(md_file, include_path)

            if target:
                content = target.read_text(encoding="utf-8").rstrip("\n")
                # Apply indentation to each line
                for cline in content.split("\n"):
                    if cline.strip():
                        new_lines.append(indent + cline)
                    else:
                        new_lines.append("")
                fixes += 1
            else:
                # File not found - leave a comment
                new_lines.append(f"{indent}<!-- Include file not found: {include_path} -->")
                fixes += 1
        else:
            new_lines.append(line)

    if fixes:
        md_file.write_text("\n".join(new_lines), encoding="utf-8")
    return fixes


def main():
    print("Raw Include Statement Fix Script")
    print(f"Docs directory: {DOCS_DIR}\n")

    total_fixes = 0
    files_fixed = 0

    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        rel = str(md_file.relative_to(ROOT))
        n = fix_file(md_file)
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
