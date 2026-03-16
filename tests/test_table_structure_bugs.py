#!/usr/bin/env python3
"""
Bug Condition Exploration Test: Table Structure and Content Bugs

**Property 1: Bug Condition** - Table Structure and Content Issues
**CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
**DO NOT attempt to fix the test or the code when it fails.**

Validates: Requirements 1.19, 1.20, 1.21, 1.22, 1.23, 2.19, 2.20, 2.21, 2.22, 2.23

Tests concrete failing cases from Andrea's review feedback:
- Lists in table cells don't split across multiple cells (Req 1.19, 2.19)
- Notes/admonitions in cells don't break table structure (Req 1.20, 2.20)
- Multi-line cell content stays in single cells (Req 1.21, 2.21)
- Complex tables maintain structure and alignment (Req 1.22, 2.22)
- Tables don't have empty rows/cells that had content (Req 1.23, 2.23)
"""

import re
import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, Phase

# Project root
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "doc" / "en" / "user"


def read_md_file(rel_path):
    """Read a markdown file and return its content."""
    full_path = ROOT / rel_path
    if not full_path.exists():
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def find_list_items_splitting_cells(content):
    """
    Find tables where list items in cells have split across multiple rows,
    creating continuation rows with empty first columns. This happens when
    the converter puts list items (- item) on separate table rows instead
    of keeping them in a single cell.

    Returns list of (context, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Pattern: a table continuation row where the content column has
        # a list item (- text) but the first column(s) are empty.
        # This indicates a list item that was split out of its parent cell.
        m = re.match(r'^\|\s{2,}\|\s*\|\s*-\s+\S', line)
        if m:
            results.append((line.strip()[:100], i + 1))
            continue

        # Also detect list items in continuation rows for 2-column tables
        m = re.match(r'^\|\s{2,}\|\s*-\s+\S', line)
        if m:
            results.append((line.strip()[:100], i + 1))

    return results


def find_definition_list_syntax_in_tables(content):
    """
    Find table cells containing RST definition list syntax (": text")
    that wasn't properly converted. This is a conversion artifact where
    RST definition lists inside table cells get rendered with visible
    colon-space-text syntax.

    Returns list of (context, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Pattern: table cell containing ":   text" (definition list syntax)
        if re.match(r'^\|', line) and re.search(r'\|\s*:\s{2,}\S', line):
            results.append((line.strip()[:120], i + 1))

    return results


def find_grid_table_remnants(content):
    """
    Find RST grid-style table syntax (+----+----+) that wasn't converted
    to Markdown pipe tables. These are remnants of the RST conversion
    that render as plain text instead of tables.

    Returns list of (context, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Pattern: grid table border row +----+----+
        if re.match(r'^\+[-]+\+[-]+\+', line):
            results.append((line.strip()[:100], i + 1))

    return results


def find_mixed_grid_pipe_tables(content):
    """
    Find tables that mix pipe (|) and grid (+---+) syntax within the
    same table. This happens when the converter partially converts an
    RST grid table, leaving +---+ row separators between pipe rows.

    Returns list of (context, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False
    prev_was_pipe_row = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            prev_was_pipe_row = False
            continue
        if in_fence:
            prev_was_pipe_row = False
            continue

        is_pipe_row = bool(re.match(r'^\|', line))
        is_grid_separator = bool(re.match(r'^\|.*\+[-]+\+', line))

        if is_grid_separator:
            results.append((line.strip()[:100], i + 1))

        if is_pipe_row:
            prev_was_pipe_row = True
        elif line.strip() == "":
            pass  # blank lines between table sections
        else:
            prev_was_pipe_row = False

    return results


def find_duplicate_table_rows(content):
    """
    Find tables with duplicate rows - a conversion artifact where the
    same content row appears twice in succession.

    Returns list of (context, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False
    prev_table_row = None

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            prev_table_row = None
            continue
        if in_fence:
            prev_table_row = None
            continue

        if re.match(r'^\|', line):
            # Skip separator rows
            if re.match(r'^\|[-| ]+\|$', line.strip()):
                continue
            # Skip continuation rows (empty first cell)
            stripped = line.strip()
            if prev_table_row and stripped == prev_table_row:
                results.append((stripped[:100], i + 1))
            prev_table_row = stripped
        else:
            prev_table_row = None

    return results


def find_empty_description_cells(content):
    """
    Find tables where description/value cells are empty but should have
    content. Specifically targets parameter tables where the Description
    column is empty for rows that clearly should have descriptions.

    Returns list of (param_name, line_number) tuples.
    """
    results = []
    lines = content.split("\n")
    in_fence = False
    is_in_table = False
    has_header = False

    for i, line in enumerate(lines):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            is_in_table = False
            has_header = False
            continue
        if in_fence:
            continue

        if re.match(r'^\|', line):
            if not is_in_table:
                is_in_table = True
                has_header = False
                continue
            if re.match(r'^\|[-| :]+\|$', line.strip()):
                has_header = True
                continue
            if has_header:
                # Check for rows where first cell has content but
                # remaining cells are all empty
                cells = [c.strip() for c in line.split("|")]
                # Remove empty strings from split
                cells = [c for c in cells if c is not None]
                # Filter: first cell has content, all others empty
                if len(cells) >= 3:
                    non_empty = [c for c in cells if c.strip()]
                    if len(non_empty) == 1 and cells[1].strip():
                        results.append((cells[1].strip()[:60], i + 1))
        else:
            is_in_table = False
            has_header = False

    return results


# ---------------------------------------------------------------------------
# Requirement 1.19 / 2.19: Lists in table cells must not split across
# multiple cells
# ---------------------------------------------------------------------------

LIST_IN_CELL_PAGES = [
    "doc/en/user/data/raster/imagemosaic/configuration.md",
    "doc/en/user/extensions/geopkg-output/usage.md",
    "doc/en/user/extensions/importer/configuring.md",
    "doc/en/user/extensions/metadata/uiconfiguration.md",
    "doc/en/user/extensions/metadata/advanced.md",
    "doc/en/user/geowebcache/responseheaders.md",
]

# ---------------------------------------------------------------------------
# Requirement 1.20 / 2.20: Notes/admonitions in cells must not break
# table structure
# ---------------------------------------------------------------------------

ADMONITION_IN_TABLE_PAGES = [
    "doc/en/user/data/raster/imagemosaic/configuration.md",
    "doc/en/user/extensions/importer/configuring.md",
    "doc/en/user/extensions/sldservice/index.md",
]

# ---------------------------------------------------------------------------
# Requirement 1.21 / 2.21: Multi-line cell content must stay in single cells
# ---------------------------------------------------------------------------

MULTILINE_CELL_PAGES = [
    "doc/en/user/extensions/importer/configuring.md",
    "doc/en/user/extensions/metadata/uiconfiguration.md",
    "doc/en/user/extensions/metadata/advanced.md",
    "doc/en/user/data/raster/imagemosaic/configuration.md",
    "doc/en/user/security/webadmin/ugr.md",
    "doc/en/user/security/webadmin/auth.md",
    "doc/en/user/extensions/sldservice/index.md",
]

# ---------------------------------------------------------------------------
# Requirement 1.22 / 2.22: Complex tables must maintain structure and
# alignment
# ---------------------------------------------------------------------------

COMPLEX_TABLE_PAGES = [
    "doc/en/user/services/wps/operations.md",
    "doc/en/user/extensions/mapml/installation.md",
    "doc/en/user/extensions/geofence-server/rest-batch-op.md",
    "doc/en/user/filter/function_reference.md",
    "doc/en/user/extensions/netcdf/netcdf.md",
    "doc/en/user/styling/workshop/css/polygon.md",
    "doc/en/user/styling/workshop/mbstyle/polygon.md",
]

# ---------------------------------------------------------------------------
# Requirement 1.23 / 2.23: Tables must not have empty rows/cells that
# had content
# ---------------------------------------------------------------------------

EMPTY_CELL_PAGES = [
    "doc/en/user/extensions/netcdf/netcdf.md",
    "doc/en/user/extensions/sldservice/index.md",
    "doc/en/user/extensions/importer/configuring.md",
]



class TestListsInTableCells:
    """Test that lists in table cells don't split across multiple cells."""

    def test_imagemosaic_configuration_lists_in_cells(self):
        """
        Requirement 1.19: imagemosaic/configuration.md has tables where
        list items in cells (e.g. SPI DataStoreFactory options) split
        across multiple table rows instead of staying in a single cell.

        Andrea specifically called out this page: "list in cell example,
        but also note in cell in the same table ending up as multiple cells"
        """
        content = read_md_file(
            "doc/en/user/data/raster/imagemosaic/configuration.md"
        )
        assert content is not None, "imagemosaic/configuration.md not found"

        issues = find_list_items_splitting_cells(content)

        assert len(issues) == 0, (
            f"Bug 1.19 confirmed: imagemosaic/configuration.md has "
            f"{len(issues)} list item(s) split across table cells:\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in issues
            )
            + "\n  List items should remain within a single table cell"
        )

    def test_geopkg_output_table_multiline_cells(self):
        """
        Requirement 1.19: geopkg-output/usage.md has tables where
        multi-line descriptions split across rows. Andrea noted
        "basically the whole table" has issues.
        """
        content = read_md_file(
            "doc/en/user/extensions/geopkg-output/usage.md"
        )
        assert content is not None, "geopkg-output/usage.md not found"

        # Check for continuation rows with empty first column
        # These indicate content that should be in a single cell
        lines = content.split("\n")
        continuation_rows = []
        in_fence = False
        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            # Continuation row: pipe, spaces, pipe (empty first cell)
            if re.match(r'^\|\s+\|', line) and not re.match(r'^\|[-| :]+\|$', line.strip()):
                continuation_rows.append((line.strip()[:100], i + 1))

        assert len(continuation_rows) == 0, (
            f"Bug 1.19 confirmed: geopkg-output/usage.md has "
            f"{len(continuation_rows)} continuation row(s) where cell "
            f"content split across multiple rows:\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in continuation_rows[:10]
            )
            + "\n  Multi-line cell content should stay in single cells"
        )

    def test_importer_configuring_definition_list_in_table(self):
        """
        Requirement 1.19/1.21: importer/configuring.md has table cells
        with RST definition list syntax (":   text") that wasn't properly
        converted. The "Maximum asynchronous jobs" row has content split
        with ":   and all jobs started from the GUI are asynchronous."
        """
        content = read_md_file(
            "doc/en/user/extensions/importer/configuring.md"
        )
        assert content is not None, "importer/configuring.md not found"

        deflist_issues = find_definition_list_syntax_in_tables(content)

        assert len(deflist_issues) == 0, (
            f"Bug 1.19/1.21 confirmed: importer/configuring.md has "
            f"{len(deflist_issues)} table cell(s) with definition list "
            f"syntax artifact:\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in deflist_issues
            )
            + "\n  Definition list syntax ':   text' should be converted "
            "to normal cell content"
        )

    @given(
        page_path=st.sampled_from(LIST_IN_CELL_PAGES)
    )
    @settings(
        max_examples=len(LIST_IN_CELL_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_list_items_splitting_cells(self, page_path):
        """
        Requirement 1.19 (PBT): No page should have list items in table
        cells that split across multiple rows.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = find_list_items_splitting_cells(content)
        deflist_issues = find_definition_list_syntax_in_tables(content)
        all_issues = issues + deflist_issues

        assert len(all_issues) == 0, (
            f"Bug 1.19: {page_path} has {len(all_issues)} table cell(s) "
            f"with split list items or definition list syntax:\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in all_issues[:10]
            )
        )


class TestMultilineCellContent:
    """Test that multi-line cell content stays in single cells."""

    def test_importer_configuring_duplicate_rows(self):
        """
        Requirement 1.21: importer/configuring.md has the "Maximum
        asynchronous jobs" row duplicated - the same content appears
        twice because the converter split multi-line content into
        separate rows. The two rows have the same first-cell content
        ("Maximum asynchronous jobs") but may differ in whitespace.
        """
        content = read_md_file(
            "doc/en/user/extensions/importer/configuring.md"
        )
        assert content is not None, "importer/configuring.md not found"

        # Find rows with duplicate first-cell content (same parameter name)
        lines = content.split("\n")
        first_cells = {}
        duplicates = []
        in_fence = False
        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if re.match(r'^\|', line) and not re.match(r'^\|[-| :]+\|$', line.strip()):
                cells = line.split("|")
                if len(cells) >= 3:
                    first_cell = cells[1].strip()
                    if first_cell and first_cell not in ("", "Entry"):
                        if first_cell in first_cells:
                            duplicates.append((first_cell, i + 1))
                        else:
                            first_cells[first_cell] = i + 1

        assert len(duplicates) == 0, (
            f"Bug 1.21 confirmed: importer/configuring.md has "
            f"{len(duplicates)} duplicate table row(s) with the same "
            f"parameter name:\n"
            + "\n".join(
                f"  - Line {line}: '{name}' appears multiple times"
                for name, line in duplicates
            )
            + "\n  Duplicate rows indicate content that was incorrectly "
            "split during conversion"
        )

    def test_metadata_uiconfiguration_fieldtype_table(self):
        """
        Requirement 1.21: metadata/uiconfiguration.md has the fieldType
        table where the value column contains definition list syntax
        (":   - TEXT", etc.) split across multiple rows with visible
        RST definition list markers.
        """
        content = read_md_file(
            "doc/en/user/extensions/metadata/uiconfiguration.md"
        )
        assert content is not None, "metadata/uiconfiguration.md not found"

        deflist_issues = find_definition_list_syntax_in_tables(content)

        assert len(deflist_issues) == 0, (
            f"Bug 1.21 confirmed: metadata/uiconfiguration.md has "
            f"{len(deflist_issues)} table cell(s) with definition list "
            f"syntax that should be plain content:\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in deflist_issues
            )
            + "\n  Definition list syntax ':   - TEXT' should be converted "
            "to a proper list or plain text in the cell"
        )

    @given(
        page_path=st.sampled_from(MULTILINE_CELL_PAGES)
    )
    @settings(
        max_examples=len(MULTILINE_CELL_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_multiline_cell_splitting(self, page_path):
        """
        Requirement 1.21 (PBT): No page should have multi-line cell
        content that splits into multiple rows or contains definition
        list syntax artifacts.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        deflist_issues = find_definition_list_syntax_in_tables(content)
        dup_rows = find_duplicate_table_rows(content)
        all_issues = deflist_issues + dup_rows

        assert len(all_issues) == 0, (
            f"Bug 1.21: {page_path} has {len(all_issues)} multi-line "
            f"cell content issue(s):\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in all_issues[:10]
            )
        )


class TestComplexTableStructure:
    """Test that complex tables maintain structure and alignment."""

    def test_wps_operations_grid_table_remnants(self):
        """
        Requirement 1.22: services/wps/operations.md has an RST grid-style
        table (+----+----+) that wasn't converted to Markdown pipe table
        format. The DescribeProcess response table uses +---+ borders
        mixed with | pipe rows.

        Andrea noted: "scroll down a bit" to see the broken table.
        """
        content = read_md_file("doc/en/user/services/wps/operations.md")
        assert content is not None, "wps/operations.md not found"

        grid_remnants = find_grid_table_remnants(content)

        assert len(grid_remnants) == 0, (
            f"Bug 1.22 confirmed: wps/operations.md has "
            f"{len(grid_remnants)} RST grid table border(s) that weren't "
            f"converted to Markdown:\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in grid_remnants
            )
            + "\n  Grid tables (+----+) should be converted to pipe "
            "tables (|---|)"
        )

    def test_mapml_installation_mixed_grid_pipe_table(self):
        """
        Requirement 1.22: mapml/installation.md has tables that mix pipe
        (|) and grid (+---+) syntax. The SLD symbolizer support table
        has +----+----+ separators between pipe rows, creating a broken
        hybrid format.
        """
        content = read_md_file(
            "doc/en/user/extensions/mapml/installation.md"
        )
        assert content is not None, "mapml/installation.md not found"

        mixed_issues = find_mixed_grid_pipe_tables(content)

        assert len(mixed_issues) == 0, (
            f"Bug 1.22 confirmed: mapml/installation.md has "
            f"{len(mixed_issues)} mixed grid/pipe table syntax issue(s):\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in mixed_issues
            )
            + "\n  Tables should use consistent pipe (|) syntax only"
        )

    def test_geofence_batch_mixed_grid_pipe_table(self):
        """
        Requirement 1.22: geofence-server/rest-batch-op.md has a table
        that mixes pipe rows with +---+ grid separators for multi-row
        cells showing different response codes.
        """
        content = read_md_file(
            "doc/en/user/extensions/geofence-server/rest-batch-op.md"
        )
        assert content is not None, "rest-batch-op.md not found"

        mixed_issues = find_mixed_grid_pipe_tables(content)

        assert len(mixed_issues) == 0, (
            f"Bug 1.22 confirmed: rest-batch-op.md has "
            f"{len(mixed_issues)} mixed grid/pipe table syntax issue(s):\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in mixed_issues
            )
            + "\n  Tables should use consistent pipe (|) syntax"
        )

    def test_function_reference_grid_table(self):
        """
        Requirement 1.22: filter/function_reference.md has the
        "Transformation functions" section using RST grid-style table
        format (+---+---+) instead of Markdown pipe tables.

        Andrea noted: "Press free locks" for an example of cell content
        with newlines split over 3 cells.
        """
        content = read_md_file("doc/en/user/filter/function_reference.md")
        assert content is not None, "function_reference.md not found"

        grid_remnants = find_grid_table_remnants(content)

        assert len(grid_remnants) == 0, (
            f"Bug 1.22 confirmed: function_reference.md has "
            f"{len(grid_remnants)} RST grid table border(s):\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in grid_remnants
            )
            + "\n  Grid tables should be converted to Markdown pipe tables"
        )

    @given(
        page_path=st.sampled_from(COMPLEX_TABLE_PAGES)
    )
    @settings(
        max_examples=len(COMPLEX_TABLE_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_complex_table_structure_issues(self, page_path):
        """
        Requirement 1.22 (PBT): No page should have RST grid table
        remnants or mixed grid/pipe table syntax.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []
        grid_remnants = find_grid_table_remnants(content)
        for ctx, line in grid_remnants:
            issues.append(f"Grid table remnant at line {line}: {ctx}")

        mixed_issues = find_mixed_grid_pipe_tables(content)
        for ctx, line in mixed_issues:
            issues.append(f"Mixed grid/pipe syntax at line {line}: {ctx}")

        assert len(issues) == 0, (
            f"Bug 1.22: {page_path} has {len(issues)} table structure "
            f"issue(s):\n"
            + "\n".join(f"  - {issue}" for issue in issues[:10])
        )


class TestEmptyTableCells:
    """Test that tables don't have empty rows/cells that had content."""

    def test_netcdf_empty_description_cells(self):
        """
        Requirement 1.23: netcdf/netcdf.md has a configuration table
        where the Description column is completely empty for all rows
        (Workspace, Data Source Name, Description, Enabled, URL).
        These cells should have descriptions.
        """
        content = read_md_file("doc/en/user/extensions/netcdf/netcdf.md")
        assert content is not None, "netcdf/netcdf.md not found"

        empty_cells = find_empty_description_cells(content)

        assert len(empty_cells) == 0, (
            f"Bug 1.23 confirmed: netcdf/netcdf.md has "
            f"{len(empty_cells)} table row(s) with empty description "
            f"cells that should have content:\n"
            + "\n".join(
                f"  - Line {line}: '{param}' has empty description"
                for param, line in empty_cells
            )
            + "\n  Description cells should contain the original content "
            "from the RST documentation"
        )

    def test_sldservice_empty_trailing_cells(self):
        """
        Requirement 1.23: sldservice/index.md has tables where trailing
        rows have mostly empty cells with only conversion artifacts like
        a bare ":" in one cell. Andrea noted "two empty rows" at the
        bottom of a table.
        """
        content = read_md_file(
            "doc/en/user/extensions/sldservice/index.md"
        )
        assert content is not None, "sldservice/index.md not found"

        # Look for table rows that are effectively empty - all cells are
        # either whitespace-only or contain only conversion artifacts
        # like a bare ":" (definition list remnant)
        lines = content.split("\n")
        empty_rows = []
        in_fence = False

        for i, line in enumerate(lines):
            if re.match(r'^\s*```', line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            if re.match(r'^\|', line):
                # Skip separator rows (must contain dashes)
                if re.match(r'^\|[-| :]+\|$', line.strip()) and '-' in line:
                    continue
                # Check for rows where all cells are empty or contain
                # only artifact characters (bare ":" from definition lists)
                cells = line.split("|")
                content_cells = [c.strip() for c in cells[1:-1]]
                if content_cells and all(
                    c in ("", ":") for c in content_cells
                ):
                    empty_rows.append((line.strip()[:80], i + 1))

        assert len(empty_rows) == 0, (
            f"Bug 1.23 confirmed: sldservice/index.md has "
            f"{len(empty_rows)} effectively empty table row(s) "
            f"(containing only whitespace or ':' artifacts):\n"
            + "\n".join(
                f"  - Line {line}: {ctx}"
                for ctx, line in empty_rows
            )
            + "\n  Empty rows likely had content in the original RST "
            "or are conversion artifacts that should be removed"
        )

    @given(
        page_path=st.sampled_from(EMPTY_CELL_PAGES)
    )
    @settings(
        max_examples=len(EMPTY_CELL_PAGES),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_empty_cells_with_lost_content(self, page_path):
        """
        Requirement 1.23 (PBT): No page should have table cells that
        are empty but should have content.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        empty_cells = find_empty_description_cells(content)

        assert len(empty_cells) == 0, (
            f"Bug 1.23: {page_path} has {len(empty_cells)} table row(s) "
            f"with empty cells that should have content:\n"
            + "\n".join(
                f"  - Line {line}: '{param}' has empty description"
                for param, line in empty_cells[:10]
            )
        )


# ---------------------------------------------------------------------------
# Combined property-based test across all table requirements
# ---------------------------------------------------------------------------

ALL_TABLE_ISSUE_PAGES = list(set(
    LIST_IN_CELL_PAGES +
    ADMONITION_IN_TABLE_PAGES +
    MULTILINE_CELL_PAGES +
    COMPLEX_TABLE_PAGES +
    EMPTY_CELL_PAGES
))


class TestTableStructureProperty:
    """Property-based tests across all table structure requirements."""

    @given(
        page_path=st.sampled_from(ALL_TABLE_ISSUE_PAGES)
    )
    @settings(
        max_examples=min(len(ALL_TABLE_ISSUE_PAGES), 30),
        phases=[Phase.explicit, Phase.generate],
    )
    def test_no_table_structure_issues(self, page_path):
        """
        Combined property (Req 1.19, 1.20, 1.21, 1.22, 1.23): Pages
        should not have any table structure issues including split list
        items, definition list syntax, grid table remnants, mixed
        grid/pipe syntax, duplicate rows, or empty cells.
        """
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"{page_path} not found")

        issues = []

        # Check for list items splitting cells (Req 1.19)
        split_lists = find_list_items_splitting_cells(content)
        for ctx, line in split_lists:
            issues.append(
                f"List item split across cells at line {line} (Req 1.19)"
            )

        # Check for definition list syntax in tables (Req 1.19/1.21)
        deflist = find_definition_list_syntax_in_tables(content)
        for ctx, line in deflist:
            issues.append(
                f"Definition list syntax in table at line {line} (Req 1.21)"
            )

        # Check for grid table remnants (Req 1.22)
        grid = find_grid_table_remnants(content)
        for ctx, line in grid:
            issues.append(
                f"Grid table remnant at line {line} (Req 1.22)"
            )

        # Check for mixed grid/pipe tables (Req 1.22)
        mixed = find_mixed_grid_pipe_tables(content)
        for ctx, line in mixed:
            issues.append(
                f"Mixed grid/pipe table at line {line} (Req 1.22)"
            )

        # Check for duplicate rows (Req 1.21)
        dups = find_duplicate_table_rows(content)
        for ctx, line in dups:
            issues.append(
                f"Duplicate table row at line {line} (Req 1.21)"
            )

        # Check for empty description cells (Req 1.23)
        empty = find_empty_description_cells(content)
        for param, line in empty:
            issues.append(
                f"Empty description for '{param}' at line {line} (Req 1.23)"
            )

        assert len(issues) == 0, (
            f"Table structure issues in {page_path}:\n"
            + "\n".join(f"  - {issue}" for issue in issues[:15])
        )
