#!/usr/bin/env python3
"""
Detection script for navigation and title issues (Task 12.1).

Scans all Markdown files for:
  1. "path/index" style link labels (Req 1.2)
  2. Page title vs navigation entry mismatches (Req 1.1)
  3. "Table of contents" vs "Page contents" labeling (Req 1.3)
  4. Installation section hierarchy issues (Req 1.4)

Generates a report of affected files.
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc"
MKDOCS_YML = ROOT / "mkdocs.yml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_mkdocs_config():
    """Load and return the parsed mkdocs.yml."""
    with open(MKDOCS_YML, encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_nav_entries(nav, parent_label=None):
    """
    Recursively extract (label, file_path) pairs from the mkdocs nav tree.
    Handles both string entries and dict entries.
    """
    entries = []
    if isinstance(nav, list):
        for item in nav:
            if isinstance(item, str):
                entries.append((parent_label, item))
            elif isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        entries.append((key, value))
                    elif isinstance(value, list):
                        entries.extend(extract_nav_entries(value, key))
    return entries


def get_md_title(filepath):
    """Extract the first H1 title from a markdown file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return None
    for line in content.splitlines():
        line = line.strip()
        # Skip frontmatter
        if line == "---":
            continue
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            return m.group(1).strip()
    return None


def get_link_labels(filepath):
    """
    Return a list of (label, target) for all markdown links in the file
    where the label looks like a path (contains '/').
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return []
    # Match [label](target) where label contains a slash
    return re.findall(r"\[([\w./-]+/[\w./-]+)\]\(([^)]+)\)", content)


# ---------------------------------------------------------------------------
# Check 1: "path/index" link labels  (Req 1.2)
# ---------------------------------------------------------------------------

def check_path_index_labels():
    """Find markdown files containing links with path-like labels pointing to local files."""
    issues = []
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        links = get_link_labels(md_file)
        for label, target in links:
            # Only flag local .md targets (not external URLs)
            if target.startswith("http"):
                continue
            # Flag labels that look like "something/index" or bare path segments
            if re.match(r"^[\w-]+/index$", label) or re.match(r"^[\w-]+/[\w-]+$", label):
                rel = md_file.relative_to(ROOT)
                issues.append({
                    "file": str(rel),
                    "label": label,
                    "target": target,
                })
    return issues


# ---------------------------------------------------------------------------
# Check 2: Title / navigation mismatch  (Req 1.1)
# ---------------------------------------------------------------------------

def extract_explicit_nav_entries(nav):
    """
    Extract only entries where the nav has an EXPLICIT label for a specific
    file (i.e. `- Label: path/to/file.md`), not section-level labels that
    are inherited by child pages.

    Returns list of (explicit_label, file_path).
    """
    entries = []
    if isinstance(nav, list):
        for item in nav:
            if isinstance(item, str):
                # Bare path, no explicit label
                continue
            elif isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        # Explicit label → file mapping
                        entries.append((key, value))
                    elif isinstance(value, list):
                        entries.extend(extract_explicit_nav_entries(value))
    return entries


def check_title_nav_mismatch():
    """
    Compare the H1 title in each markdown file against its EXPLICIT nav
    label in mkdocs.yml.  Only flags pages where mkdocs.yml assigns a
    specific label to a file and that label differs from the page's H1.

    Pages listed without an explicit label (bare paths) or pages that
    inherit a section label are NOT flagged — that's normal MkDocs behavior.
    """
    cfg = load_mkdocs_config()
    nav = cfg.get("nav", [])
    entries = extract_explicit_nav_entries(nav)

    issues = []
    for nav_label, file_path in entries:
        # Skip external links
        if file_path.endswith(".html") or file_path.startswith("http"):
            continue

        md_path = DOCS_DIR.parent / file_path
        if not md_path.exists():
            md_path = DOCS_DIR / file_path
        if not md_path.exists():
            md_path = ROOT / file_path
        if not md_path.exists():
            continue

        page_title = get_md_title(md_path)
        if page_title is None:
            continue

        # Normalize for comparison
        norm_nav = nav_label.lower().strip()
        norm_title = page_title.lower().strip()

        if norm_nav == norm_title:
            continue

        # Allow if one is a substring of the other (reasonable abbreviation)
        if norm_nav in norm_title or norm_title in norm_nav:
            continue

        issues.append({
            "file": file_path,
            "nav_label": nav_label,
            "page_title": page_title,
        })
    return issues


# ---------------------------------------------------------------------------
# Check 3: "Table of contents" labeling  (Req 1.3)
# ---------------------------------------------------------------------------

def check_toc_labeling():
    """
    Check theme files for 'Table of contents' / 'Table Of Contents' labels
    that should be 'Page contents'.
    """
    issues = []

    # Check layout.html (old Sphinx template)
    layout = DOCS_DIR / "themes" / "geoserver" / "layout.html"
    if layout.exists():
        content = layout.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            if re.search(r"Table\s+Of\s+Contents", line, re.IGNORECASE):
                issues.append({
                    "file": str(layout.relative_to(ROOT)),
                    "line": i,
                    "text": line.strip(),
                    "issue": "Contains 'Table Of Contents' — should use 'Page Contents'",
                })

    # Check extra.css for the CSS override
    css = DOCS_DIR / "themes" / "geoserver" / "stylesheets" / "extra.css"
    has_page_contents_override = False
    if css.exists():
        content = css.read_text(encoding="utf-8")
        if 'content: "Page Contents"' in content:
            has_page_contents_override = True
    if not has_page_contents_override:
        issues.append({
            "file": str(css.relative_to(ROOT)) if css.exists() else "MISSING",
            "line": 0,
            "text": "",
            "issue": "Missing CSS override: content: \"Page Contents\"",
        })

    # Check any other template/partial files
    theme_dir = DOCS_DIR / "themes" / "geoserver"
    if theme_dir.exists():
        for f in theme_dir.rglob("*.html"):
            if f.name == "layout.html":
                continue  # already checked
            content = f.read_text(encoding="utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                if re.search(r"Table\s+Of\s+Contents", line, re.IGNORECASE):
                    issues.append({
                        "file": str(f.relative_to(ROOT)),
                        "line": i,
                        "text": line.strip(),
                        "issue": "Contains 'Table Of Contents'",
                    })

    return issues


# ---------------------------------------------------------------------------
# Check 4: Installation section hierarchy  (Req 1.4)
# ---------------------------------------------------------------------------

def check_installation_hierarchy():
    """
    Check the Installation index page for hierarchy issues:
    - Missing 'Section contents' label
    - Garbled link labels (e.g. 'InstallationWin' instead of 'Windows Installer')
    - Unclear hierarchy / inconsistent formatting
    """
    issues = []
    install_index = ROOT / "doc" / "en" / "user" / "installation" / "index.md"
    if not install_index.exists():
        issues.append({
            "file": "doc/en/user/installation/index.md",
            "issue": "File not found",
        })
        return issues

    content = install_index.read_text(encoding="utf-8")

    # Check for "Section contents" label
    if "Section contents" not in content and "section contents" not in content.lower():
        issues.append({
            "file": "doc/en/user/installation/index.md",
            "issue": "Missing 'Section contents' label for clear hierarchy",
        })

    # Check for garbled link labels like "InstallationWin"
    garbled = re.findall(r"\[([A-Z][a-z]+[A-Z][a-z]+[^\]]*)\]", content)
    for label in garbled:
        # CamelCase labels that look like concatenated words
        if re.match(r"^[A-Z][a-z]+[A-Z]", label):
            issues.append({
                "file": "doc/en/user/installation/index.md",
                "issue": f"Garbled link label: '{label}' — likely missing space",
            })

    # Check nav entry labels vs page structure
    cfg = load_mkdocs_config()
    nav = cfg.get("nav", [])
    nav_entries = extract_nav_entries(nav)
    install_entries = [
        (lbl, fp) for lbl, fp in nav_entries
        if fp.startswith("en/user/installation/") and lbl is not None
    ]

    # The nav section label should be "Installation" not "installation"
    for lbl, fp in install_entries:
        if fp.endswith("index.md") and lbl.lower() == "installation":
            # Check if the nav uses a generic section label without explicit title
            pass  # This is fine

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
    for i, issue in enumerate(issues, 1):
        print(f"  [{i}]")
        for field in fields:
            if field in issue and issue[field]:
                print(f"      {field}: {issue[field]}")
        print()
    return len(issues)


def main():
    print("Navigation & Title Issue Detection Report")
    print(f"Docs directory: {DOCS_DIR}")
    print(f"Config file:    {MKDOCS_YML}")

    total = 0

    # Check 1
    issues1 = check_path_index_labels()
    total += print_report(
        "Check 1: Path/Index Link Labels (Req 1.2)",
        issues1,
        ["file", "label", "target"],
    )

    # Check 2
    issues2 = check_title_nav_mismatch()
    total += print_report(
        "Check 2: Title / Navigation Mismatch (Req 1.1)",
        issues2,
        ["file", "nav_label", "page_title"],
    )

    # Check 3
    issues3 = check_toc_labeling()
    total += print_report(
        "Check 3: 'Table of Contents' Labeling (Req 1.3)",
        issues3,
        ["file", "line", "text", "issue"],
    )

    # Check 4
    issues4 = check_installation_hierarchy()
    total += print_report(
        "Check 4: Installation Section Hierarchy (Req 1.4)",
        issues4,
        ["file", "issue"],
    )

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY: {total} total issue(s) found across all checks.")
    print(f"{'='*70}\n")

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
