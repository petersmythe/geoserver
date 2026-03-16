#!/usr/bin/env python3
"""
Fix title/navigation mismatches in mkdocs.yml.

Synchronizes navigation section labels with the actual H1 page titles from
the Markdown files. The page titles (from the original RST docs) are treated
as the source of truth for *descriptiveness*, while the nav structure is
updated to use those titles.

For section labels that are bare directory names (e.g. "Webadmin", "Gettingstarted",
"Crshandling"), the nav label is updated to match the page's H1 title.

Bug Condition:  Page title in content doesn't match navigation tree
Expected:       Page title matches navigation entry
Preservation:   Matching titles remain unchanged
Requirements:   1.1, 2.1, 3.1
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MKDOCS_YML = ROOT / "mkdocs.yml"
DOCS_DIR = ROOT / "doc"


def get_h1_title(filepath: Path) -> str | None:
    """Extract the first H1 heading from a Markdown file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return None
    in_frontmatter = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        m = re.match(r"^#\s+(.+)$", stripped)
        if m:
            return m.group(1).strip()
    return None


def resolve_md_path(file_path: str) -> Path | None:
    """Resolve a nav file path to an actual file on disk."""
    candidates = [
        ROOT / file_path,
        DOCS_DIR / file_path,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def is_bare_dirname_label(label: str) -> bool:
    """
    Check if a nav label looks like a bare directory name rather than
    a proper human-readable title.

    Examples of bare dirname labels:
      "Webadmin", "Gettingstarted", "Crshandling", "Tipstricks",
      "Datadirectory", "Usergrouprole", "Backuprestore", "Vectortiles"

    Examples of acceptable labels (should NOT be flagged):
      "Web Map Service (WMS)", "Installation", "Security", "REST",
      "Developer Guide", "User Manual", "Documentation Guide"
    """
    if not label:
        return False

    # Skip labels that are already well-known human-readable names
    # These are top-level tabs or established section names
    KNOWN_GOOD_LABELS = {
        "Home",
        "User Manual", "Developer Guide", "Documentation Guide",
        "API Reference",
    }
    if label in KNOWN_GOOD_LABELS:
        return False

    # Single word, starts with uppercase — auto-generated from directory names
    # e.g. "Webadmin", "Gettingstarted", "Datadirectory", "Sld", "Wms", "Css"
    if re.match(r"^[A-Z][a-z]+$", label):
        return True

    # Multi-word but looks like title-cased directory segments
    # e.g. "App Schema", "Composite Blend", "Geofence Server"
    # These are from kebab-case dirs like "app-schema" -> "App Schema"
    words = label.split()
    if len(words) >= 2 and all(re.match(r"^[A-Z][a-z]*$", w) for w in words):
        return True

    return False


def labels_effectively_match(nav_label: str, page_title: str) -> bool:
    """
    Check if a nav label and page title are close enough to not need fixing.

    We consider them matching if:
    - They're equal (case-insensitive)
    - They're close in length AND one contains the other

    We do NOT consider them matching if the nav label is much shorter than
    the page title (bare dirname vs descriptive title), even if one contains
    the other. This catches cases like "Sld" vs "SLD Styling" or
    "Community" vs "Community modules".
    """
    nl = nav_label.lower().strip()
    pt = page_title.lower().strip()

    if nl == pt:
        return True

    # If one contains the other, only match if they're similar length
    # (within 5 chars difference, matching the test's threshold)
    if nl in pt or pt in nl:
        if len(pt) <= len(nl) + 5:
            return True

    return False


def collect_mismatches(nav, changes: list, parent_label: str | None = None) -> list:
    """
    Recursively walk the nav tree and collect:
    1. Section labels that are bare directory names and don't match their
       index page's H1 title.
    2. Bare index.md file entries (strings without explicit labels) where the
       inherited parent section label is a bare dirname that doesn't match
       the page title. Skips the section's own index.md (first child) since
       that's handled by the section label fix.
    3. Explicit label-to-file mappings where the label is a bare dirname
       that doesn't match the page title.

    Returns a list of dicts describing each mismatch.
    """
    if not isinstance(nav, list):
        return changes

    for item in nav:
        if isinstance(item, str):
            # Bare file entry — inherits parent_label
            # Only fix index.md entries (matching the test's filter)
            if (parent_label is not None
                    and item.endswith("index.md")
                    and is_bare_dirname_label(parent_label)):
                md_path = resolve_md_path(item)
                if md_path:
                    page_title = get_h1_title(md_path)
                    if page_title and not labels_effectively_match(parent_label, page_title):
                        changes.append({
                            "type": "bare_entry",
                            "file": item,
                            "parent_label": parent_label,
                            "new_label": page_title,
                        })

        elif isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str):
                    # Explicit label -> file mapping (e.g. "Home: index.md")
                    if is_bare_dirname_label(key):
                        md_path = resolve_md_path(value)
                        if md_path:
                            page_title = get_h1_title(md_path)
                            if page_title and not labels_effectively_match(key, page_title):
                                changes.append({
                                    "type": "explicit_label",
                                    "file": value,
                                    "old_label": key,
                                    "new_label": page_title,
                                })

                elif isinstance(value, list):
                    # Section label with children
                    section_index_path = None
                    for child in value:
                        if isinstance(child, str) and child.endswith("index.md"):
                            section_index_path = child
                            break

                    if section_index_path:
                        md_path = resolve_md_path(section_index_path)
                        if md_path:
                            page_title = get_h1_title(md_path)
                            if page_title and not labels_effectively_match(key, page_title):
                                if is_bare_dirname_label(key):
                                    changes.append({
                                        "type": "section_label",
                                        "file": section_index_path,
                                        "old_label": key,
                                        "new_label": page_title,
                                    })

                    # Recurse into children
                    _collect_children(value, changes, key, section_index_path)

    return changes


def _collect_children(nav_list, changes, parent_label, section_index_path):
    """Process children of a section, skipping the section's own index.md."""
    for item in nav_list:
        if isinstance(item, str):
            # Skip the section's own index.md — handled by section label fix
            if item == section_index_path:
                continue

            # Bare file entry — inherits parent_label
            if (item.endswith("index.md")
                    and is_bare_dirname_label(parent_label)):
                md_path = resolve_md_path(item)
                if md_path:
                    page_title = get_h1_title(md_path)
                    if page_title and not labels_effectively_match(parent_label, page_title):
                        changes.append({
                            "type": "bare_entry",
                            "file": item,
                            "parent_label": parent_label,
                            "new_label": page_title,
                        })

        elif isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, list):
                    # Nested section — find its own index
                    nested_index = None
                    for child in value:
                        if isinstance(child, str) and child.endswith("index.md"):
                            nested_index = child
                            break

                    if nested_index:
                        md_path = resolve_md_path(nested_index)
                        if md_path:
                            page_title = get_h1_title(md_path)
                            if page_title and not labels_effectively_match(key, page_title):
                                if is_bare_dirname_label(key):
                                    changes.append({
                                        "type": "section_label",
                                        "file": nested_index,
                                        "old_label": key,
                                        "new_label": page_title,
                                    })

                    # Recurse
                    _collect_children(value, changes, key, nested_index)


def apply_nav_fixes(content: str, changes: list) -> str:
    """
    Apply nav label fixes to the raw mkdocs.yml content.

    Handles two types of changes:
    1. section_label: Rename a section label (e.g. "Webadmin:" -> "Data settings:")
    2. bare_entry: Add explicit label to a bare file entry
       (e.g. "- en/user/foo.md" -> "- Foo Title: en/user/foo.md")
    """
    for change in changes:
        if change.get("type") == "bare_entry":
            content = _add_explicit_label(content, change["file"], change["new_label"])
        else:
            content = _rename_section_label(content, change)

    return content


def _rename_section_label(content: str, change: dict) -> str:
    """Rename a section label in the nav."""
    old_label = change["old_label"]
    new_label = change["new_label"]

    pattern = re.compile(
        r"^(\s*-\s*)" + re.escape(old_label) + r"(\s*:\s*)$",
        re.MULTILINE,
    )

    matches = list(pattern.finditer(content))
    if len(matches) == 1:
        m = matches[0]
        content = content[:m.start()] + m.group(1) + new_label + m.group(2) + content[m.end():]
    elif len(matches) > 1:
        file_path = change["file"]
        content = _replace_near_file_path(content, old_label, new_label, file_path)

    return content


def _add_explicit_label(content: str, file_path: str, label: str) -> str:
    """
    Convert a bare nav entry to one with an explicit label.
    e.g. "      - en/user/community/colormap/index.md"
      -> "      - Dynamic colormap generation: en/user/community/colormap/index.md"
    """
    # Match the bare entry line
    pattern = re.compile(
        r"^(\s*-\s*)" + re.escape(file_path) + r"\s*$",
        re.MULTILINE,
    )

    matches = list(pattern.finditer(content))
    if len(matches) == 1:
        m = matches[0]
        replacement = f"{m.group(1)}{label}: {file_path}"
        content = content[:m.start()] + replacement + content[m.end():]

    return content


def _replace_near_file_path(content: str, old_label: str, new_label: str, file_path: str) -> str:
    """
    When a label appears multiple times in the nav, replace only the one
    that's near (above) the line containing the associated file path.
    """
    lines = content.split("\n")
    label_pattern = re.compile(r"^(\s*-\s*)" + re.escape(old_label) + r"(\s*:\s*)$")

    # Find all line indices with the label
    label_indices = []
    for i, line in enumerate(lines):
        if label_pattern.match(line):
            label_indices.append(i)

    # Find the line index containing the file path
    file_line_idx = None
    for i, line in enumerate(lines):
        if file_path in line:
            file_line_idx = i
            break

    if file_line_idx is None:
        return content

    # Find the label line that's closest above the file path line
    best_idx = None
    for idx in label_indices:
        if idx < file_line_idx:
            if best_idx is None or idx > best_idx:
                best_idx = idx

    if best_idx is not None:
        m = label_pattern.match(lines[best_idx])
        if m:
            lines[best_idx] = m.group(1) + new_label + m.group(2)

    return "\n".join(lines)


def fix_title_nav_mismatches(dry_run: bool = False) -> list[dict]:
    """
    Find and fix all title/navigation mismatches in mkdocs.yml.

    Returns a list of changes made (or that would be made in dry-run mode).
    """
    with open(MKDOCS_YML, encoding="utf-8") as f:
        raw_content = f.read()

    cfg = yaml.safe_load(raw_content)
    nav = cfg.get("nav", [])

    changes = collect_mismatches(nav, [])

    if not changes:
        return []

    if not dry_run:
        new_content = apply_nav_fixes(raw_content, changes)
        with open(MKDOCS_YML, "w", encoding="utf-8") as f:
            f.write(new_content)

    return changes


# ---------------------------------------------------------------------------
# Garbled link label fix (content-level)
# ---------------------------------------------------------------------------

# Pattern: link labels that start with a known section prefix followed by
# a CamelCase word, e.g. "DataApp SchemaIndex", "InstallationWin Binary"
GARBLED_PREFIX_RE = re.compile(
    r"^(Data|Installation|Services|Styling|Security|Configuration|"
    r"Extensions|Community|Geowebcache|Filter|Production|Rest|Tutorials)"
    r"([A-Z]\w+)"
)


def fix_garbled_link_labels(dry_run: bool = False) -> list[dict]:
    """
    Fix garbled link labels in Markdown content.

    These are labels like [DataApp SchemaIndex](app-schema/index.md) that
    should be replaced with the H1 title from the target file.

    Returns a list of changes made.
    """
    changes = []

    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        original = content
        file_dir = md_file.parent

        def replace_garbled(match: re.Match) -> str:
            label = match.group(1)
            target = match.group(2)

            if target.startswith("http"):
                return match.group(0)

            if not GARBLED_PREFIX_RE.match(label):
                return match.group(0)

            # Resolve target file
            target_path = (file_dir / target.split("#")[0]).resolve()
            if not target_path.exists():
                return match.group(0)

            title = get_h1_title(target_path)
            if not title:
                return match.group(0)

            changes.append({
                "file": str(md_file.relative_to(ROOT)),
                "old_label": label,
                "new_label": title,
                "target": target,
            })
            return f"[{title}]({target})"

        content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_garbled, content)

        if content != original and not dry_run:
            md_file.write_text(content, encoding="utf-8")

    return changes


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN — no files will be modified ===\n")

    # Fix 1: Nav label mismatches in mkdocs.yml
    changes = fix_title_nav_mismatches(dry_run=dry_run)

    if changes:
        print(f"{'Would fix' if dry_run else 'Fixed'} {len(changes)} nav label(s):\n")
        for i, c in enumerate(changes, 1):
            if c.get("type") == "bare_entry":
                print(f"  [{i}] {c['file']}")
                print(f"      (bare entry) add label: \"{c['new_label']}\"")
            else:
                print(f"  [{i}] {c['file']}")
                print(f"      nav: \"{c['old_label']}\"  ->  \"{c['new_label']}\"")
            print()

        if not dry_run:
            print("Nav label changes written to mkdocs.yml.\n")
    else:
        print("No nav label mismatches found.\n")

    # Fix 2: Garbled link labels in Markdown content
    garbled_changes = fix_garbled_link_labels(dry_run=dry_run)

    if garbled_changes:
        print(f"{'Would fix' if dry_run else 'Fixed'} {len(garbled_changes)} garbled link label(s):\n")
        for i, c in enumerate(garbled_changes, 1):
            print(f"  [{i}] {c['file']}")
            print(f"      [{c['old_label']}]({c['target']})  ->  [{c['new_label']}]({c['target']})")
            print()

        if not dry_run:
            print("Garbled link label changes written to disk.")
    else:
        print("No garbled link labels found.")


if __name__ == "__main__":
    main()
