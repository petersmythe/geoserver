#!/usr/bin/env python3
"""Fix RST-style dot-notation anchor references in Markdown files.

Converts links like [text](#app-schema.mapping-file) to proper relative
Markdown links like [text](mapping-file.md).

The dot-notation pattern comes from RST :ref: cross-references that were
converted to Markdown anchors but don't resolve in MkDocs because MkDocs
uses dash-separated heading IDs, not dot-separated RST label references.

Requirements: 1.24, 2.24
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"
USER_DIR = DOCS_DIR / "user"

# Mapping from dot-notation anchor labels to (target_file_relative_to_user_dir, anchor_or_None)
# Built by examining the actual app-schema .md files and their content
DOT_ANCHOR_MAP = {
    # app-schema pages (relative to doc/en/user/data/app-schema/)
    "app-schema.mapping-file": ("data/app-schema/mapping-file.md", None),
    "app-schema.property-interpolation": ("data/app-schema/property-interpolation.md", None),
    "app-schema.joining": ("data/app-schema/joining.md", None),
    "app-schema.configuration": ("data/app-schema/configuration.md", None),
    "app-schema.filtering-nested": ("data/app-schema/feature-chaining.md", None),
    "app-schema.feature-chaining-by-reference": ("data/app-schema/feature-chaining.md", None),
    "app-schema.feature-chaining": ("data/app-schema/feature-chaining.md", None),
    "app-schema.data-stores": ("data/app-schema/data-stores.md", None),
    "app-schema.app-schema-resolution": ("data/app-schema/app-schema-resolution.md", None),
    "app-schema.denormalised-sources": ("data/app-schema/mapping-file.md", "app-schema.denormalised-sources"),
    "app-schema.cql-functions": ("data/app-schema/cql-functions.md", None),
    "app-schema.polymorphism": ("data/app-schema/polymorphism.md", None),
    "app-schema.complex-features": ("data/app-schema/complex-features.md", None),
    "app-schema.secondary-namespaces": ("data/app-schema/secondary-namespaces.md", None),
    "app-schema.mapping-file.targetAttributeNode": ("data/app-schema/mapping-file.md", "targetattributenode-optional"),
}

# Regex for dot-notation anchor links
DOT_ANCHOR_RE = re.compile(
    r'\[([^\]]+)\]\(#([a-z][\w-]*\.[a-z][\w.-]*)\)'
)


def compute_relative_path(from_file: Path, to_file_rel_user: str) -> str:
    """Compute relative path from from_file to a file specified relative to USER_DIR."""
    target_abs = (USER_DIR / to_file_rel_user).resolve()
    from_dir = from_file.resolve().parent
    return os.path.relpath(target_abs, from_dir).replace("\\", "/")


def fix_dot_anchor(match: re.Match, md_file: Path) -> str:
    """Replace a single dot-notation anchor with a proper relative link."""
    link_text = match.group(1)
    anchor_label = match.group(2)

    if anchor_label not in DOT_ANCHOR_MAP:
        # Unknown label - convert dots to dashes for a same-page anchor
        slug = anchor_label.replace(".", "-")
        return f"[{link_text}](#{slug})"

    target_rel, anchor = DOT_ANCHOR_MAP[anchor_label]
    rel_path = compute_relative_path(md_file, target_rel)

    if anchor:
        return f"[{link_text}]({rel_path}#{anchor})"
    return f"[{link_text}]({rel_path})"


def fix_file(md_file: Path) -> int:
    """Fix all dot-notation anchors in a single file. Returns count of fixes."""
    text = md_file.read_text(encoding="utf-8")
    lines = text.split("\n")
    fixes = 0
    in_fence = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        new_line = DOT_ANCHOR_RE.sub(
            lambda m: fix_dot_anchor(m, md_file), line
        )
        if new_line != line:
            count = len(DOT_ANCHOR_RE.findall(line))
            fixes += count
            lines[i] = new_line

    if fixes:
        md_file.write_text("\n".join(lines), encoding="utf-8")
    return fixes


def main():
    print("Dot-Notation Anchor Fix Script")
    print(f"Docs directory: {DOCS_DIR}\n")

    total_fixes = 0
    files_fixed = 0

    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        rel = str(md_file.relative_to(ROOT))
        n = fix_file(md_file)
        if n:
            files_fixed += 1
            total_fixes += n
            print(f"  Fixed: {rel} ({n} anchor(s))")

    print(f"\nSummary:")
    print(f"  Total dot-notation anchors fixed: {total_fixes}")
    print(f"  Files modified: {files_fixed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
