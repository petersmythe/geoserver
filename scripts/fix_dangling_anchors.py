#!/usr/bin/env python3
"""Fix dangling anchor and broken internal link issues from RST-to-Markdown conversion.

Two categories of issues are addressed:

1. RST-style anchor labels embedded in Markdown links (Req 1.24)
   Pattern: [visible text<rst_label>](#visible text<rst_label>)
   These are RST :ref: cross-references that were incorrectly converted.
   Fix: Convert to proper Markdown links [visible text](target_file.md#anchor)

2. Broken absolute-path internal links (Req 1.24)
   Pattern: [text](/absolute/path.md) where path is absolute from doc/en/user/
   Fix: Convert to relative path from the file's location

Preservation: Working links with correct syntax remain unchanged.

Requirements: 1.24, 2.24, 3.6
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en"
USER_DIR = DOCS_DIR / "user"

# ---------------------------------------------------------------------------
# RST anchor label -> (target_file_relative_to_user_dir, anchor_id) mapping
# Built from grepping {: #anchor_id } definitions across the docs
# ---------------------------------------------------------------------------
RST_ANCHOR_MAP = {
    # community
    "geopkgoutput": ("community/geopkg/output.md", None),
    # opensearch-eo
    "oseo_html_templates": ("community/opensearch-eo/configuration.md", "oseo_html_templates"),
    "oseo_metadata_templates": ("community/opensearch-eo/configuration.md", "oseo_metadata_templates"),
    # configuration
    "application_properties": ("configuration/properties/index.md", "application_properties_setting"),
    # services/wms
    "wms_configuration_limits": ("services/wms/configuration.md", "wms_configuration_limits"),
    "wms_dynamic_decorations": ("services/wms/decoration.md", "wms_dynamic_decorations"),
    "wms_vendor_parameters": ("services/wms/vendor.md", None),
    # gwc
    "gwc_webadmin": ("geowebcache/webadmin/index.md", None),
    # security
    "security_rolesystem_usergroupxml": ("security/usergrouprole/usergroupservices.md", "security_rolesystem_usergroupxml"),
    "security_rolesystem_usergroupjdbc": ("security/usergrouprole/usergroupservices.md", "security_rolesystem_usergroupjdbc"),
    "security_rolesystem_usergroupldap": ("security/usergrouprole/usergroupservices.md", "security_rolesystem_usergroupldap"),
    "authkey": ("extensions/authkey/index.md", None),
    # csw
    "csw_iso": ("extensions/csw-iso/index.md", None),
    # data/webadmin
    "data_webadmin_layers": ("data/webadmin/layers.md", "data_webadmin_layers_edit_data"),
    # filter
    "filter_ecql_reference": ("filter/ecql_reference.md", None),
    # styling/sld labeling vendor parameters
    "labeling_space_around": ("styling/sld/reference/labeling.md", "labeling_space_around"),
    "labeling_group": ("styling/sld/reference/labeling.md", "labeling_group"),
    "labeling_max_displacement": ("styling/sld/reference/labeling.md", "labeling_max_displacement"),
    "labeling_repeat": ("styling/sld/reference/labeling.md", "labeling_repeat"),
    "labeling_all_group": ("styling/sld/reference/labeling.md", "labeling_all_group"),
    "labeling_follow_line": ("styling/sld/reference/labeling.md", "labeling_follow_line"),
    "labeling_max_angle_delta": ("styling/sld/reference/labeling.md", "labeling_max_angle_delta"),
    "labeling_autowrap": ("styling/sld/reference/labeling.md", "labeling_autowrap"),
    "labeling_force_left_to_right": ("styling/sld/reference/labeling.md", "labeling_force_left_to_right"),
    "labeling_conflict_resolution": ("styling/sld/reference/labeling.md", "labeling_conflict_resolution"),
    "labeling_goodness_of_fit": ("styling/sld/reference/labeling.md", "labeling_goodness_of_fit"),
    "labeling_priority": ("styling/sld/reference/labeling.md", "labeling_priority"),
}


def compute_relative_path(from_file: Path, to_file_rel_user: str) -> str:
    """Compute relative path from from_file to a file specified relative to USER_DIR."""
    target_abs = (USER_DIR / to_file_rel_user).resolve()
    from_dir = from_file.resolve().parent
    return os.path.relpath(target_abs, from_dir).replace("\\", "/")



# ---------------------------------------------------------------------------
# Fix 1: RST-style anchor links  [text<label>](#text<label>)
# ---------------------------------------------------------------------------

RST_ANCHOR_LINK_RE = re.compile(
    r'\[([^\]]*)<([a-zA-Z_][a-zA-Z0-9_]*)>\]'   # [visible text<label>]
    r'\(#[^)]*<[a-zA-Z_][a-zA-Z0-9_]*>\)'        # (#visible text<label>)
)


def fix_rst_anchor_link(match: re.Match, md_file: Path) -> str:
    """Replace a single RST-style anchor link with a proper Markdown link."""
    visible_text = match.group(1).strip()
    rst_label = match.group(2)

    if rst_label not in RST_ANCHOR_MAP:
        # Unknown label — leave as plain text link to same-page anchor
        slug = rst_label.replace("_", "-")
        return f"[{visible_text}](#{slug})"

    target_rel, anchor = RST_ANCHOR_MAP[rst_label]
    rel_path = compute_relative_path(md_file, target_rel)

    if anchor:
        return f"[{visible_text}]({rel_path}#{anchor})"
    return f"[{visible_text}]({rel_path})"


def fix_rst_anchors_in_file(md_file: Path) -> int:
    """Fix all RST-style anchor links in a single file. Returns count of fixes."""
    text = md_file.read_text(encoding="utf-8")
    lines = text.split("\n")
    fixes = 0
    in_fence = False

    for i, line in enumerate(lines):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        new_line = RST_ANCHOR_LINK_RE.sub(
            lambda m: fix_rst_anchor_link(m, md_file), line
        )
        if new_line != line:
            fixes += line.count("<") // 2  # rough count
            lines[i] = new_line

    if fixes:
        md_file.write_text("\n".join(lines), encoding="utf-8")
    return fixes


# ---------------------------------------------------------------------------
# Fix 2: Absolute-path internal links  [text](/path/to/file.md)
# These use paths absolute from doc/en/user/ but MkDocs needs relative paths
# ---------------------------------------------------------------------------

ABS_LINK_RE = re.compile(
    r'\[([^\]]*)\]\((/[a-zA-Z][^)]*\.md(?:#[^)]*)?)\)'
)


def fix_abs_link(match: re.Match, md_file: Path) -> str:
    """Convert an absolute-path link to a relative path."""
    link_text = match.group(1)
    target = match.group(2)

    # Split off anchor
    if "#" in target:
        path_part, anchor = target.split("#", 1)
        anchor = "#" + anchor
    else:
        path_part = target
        anchor = ""

    # Check if the target exists relative to USER_DIR
    abs_target = USER_DIR / path_part.lstrip("/")
    if not abs_target.resolve().exists():
        return match.group(0)  # leave unchanged if target doesn't exist

    rel_path = compute_relative_path(md_file, path_part.lstrip("/"))
    return f"[{link_text}]({rel_path}{anchor})"


def fix_abs_links_in_file(md_file: Path) -> int:
    """Fix all absolute-path internal links in a single file. Returns count of fixes."""
    text = md_file.read_text(encoding="utf-8")
    lines = text.split("\n")
    fixes = 0
    in_fence = False

    for i, line in enumerate(lines):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        new_line = ABS_LINK_RE.sub(
            lambda m: fix_abs_link(m, md_file), line
        )
        if new_line != line:
            fixes += 1
            lines[i] = new_line

    if fixes:
        md_file.write_text("\n".join(lines), encoding="utf-8")
    return fixes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def iter_md_files():
    """Yield all .md files under DOCS_DIR, sorted."""
    return sorted(DOCS_DIR.rglob("*.md"))


def main():
    print("Dangling Anchor & Broken Link Fix Script")
    print(f"Docs directory: {DOCS_DIR}\n")

    total_rst = 0
    total_abs = 0
    files_rst = 0
    files_abs = 0

    for md_file in iter_md_files():
        rel = str(md_file.relative_to(ROOT))

        n_rst = fix_rst_anchors_in_file(md_file)
        if n_rst:
            files_rst += 1
            total_rst += n_rst
            print(f"  RST anchors fixed: {rel} ({n_rst} fix(es))")

        n_abs = fix_abs_links_in_file(md_file)
        if n_abs:
            files_abs += 1
            total_abs += n_abs
            print(f"  Abs links fixed:   {rel} ({n_abs} fix(es))")

    print(f"\nSummary:")
    print(f"  RST-style anchor fixes: {total_rst} in {files_rst} file(s)")
    print(f"  Absolute path fixes:    {total_abs} in {files_abs} file(s)")
    print(f"  Total fixes:            {total_rst + total_abs}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
