#!/usr/bin/env python3
"""
Preservation Property Tests: MkDocs Configuration

**Property 2: Preservation** - MkDocs Configuration Preservation
These tests MUST PASS on UNFIXED code, establishing baseline behavior to preserve.

Validates: Requirements 3.7, 3.8, 3.9, 3.10

Tests that MkDocs configuration continues to work correctly:
- MkDocs builds successfully without errors (Req 3.10)
- Navigation structure functions properly (Req 3.8)
- Page metadata is preserved (Req 3.9)
- Theme and styling work correctly (Req 3.7)
"""

import os
import re
import pytest
import yaml
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent
MKDOCS_YML = ROOT / "mkdocs.yml"
DOCS_DIR = ROOT / "doc"


def load_mkdocs_config():
    """Load and parse the mkdocs.yml configuration file."""
    with open(MKDOCS_YML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_md_file(rel_path):
    """Read a markdown file relative to the project root."""
    full = ROOT / rel_path
    if not full.exists():
        return None
    return full.read_text(encoding="utf-8", errors="replace")


def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError:
        return {}


def collect_nav_paths(nav, prefix=""):
    """Recursively collect all file paths from the nav structure."""
    paths = []
    if isinstance(nav, list):
        for item in nav:
            paths.extend(collect_nav_paths(item, prefix))
    elif isinstance(nav, dict):
        for key, value in nav.items():
            if isinstance(value, str):
                paths.append(value)
            elif isinstance(value, list):
                paths.extend(collect_nav_paths(value, prefix))
    elif isinstance(nav, str):
        paths.append(nav)
    return paths


# ---------------------------------------------------------------------------
# Requirement 3.10: MkDocs builds successfully without errors
# ---------------------------------------------------------------------------

class TestMkDocsBuildConfig:
    """Preservation: MkDocs configuration must remain valid and buildable."""

    def test_mkdocs_yml_exists(self):
        """Req 3.10: mkdocs.yml must exist at project root."""
        assert MKDOCS_YML.exists(), "mkdocs.yml not found at project root"

    def test_mkdocs_yml_is_valid_yaml(self):
        """Req 3.10: mkdocs.yml must be valid YAML."""
        config = load_mkdocs_config()
        assert config is not None, "mkdocs.yml failed to parse as YAML"
        assert isinstance(config, dict), "mkdocs.yml root must be a mapping"

    def test_required_top_level_keys(self):
        """Req 3.10: mkdocs.yml must have required top-level configuration keys."""
        config = load_mkdocs_config()
        required_keys = ["site_name", "docs_dir", "nav", "theme", "markdown_extensions"]
        for key in required_keys:
            assert key in config, f"Missing required key: {key}"

    def test_site_name_is_set(self):
        """Req 3.10: site_name must be a non-empty string."""
        config = load_mkdocs_config()
        assert isinstance(config["site_name"], str)
        assert len(config["site_name"]) > 0

    def test_docs_dir_exists(self):
        """Req 3.10: The configured docs_dir must exist on disk."""
        config = load_mkdocs_config()
        docs_dir = ROOT / config["docs_dir"]
        assert docs_dir.is_dir(), f"docs_dir '{config['docs_dir']}' does not exist"

    def test_plugins_configured(self):
        """Req 3.10: Required plugins must be configured."""
        config = load_mkdocs_config()
        assert "plugins" in config, "plugins section missing"
        plugin_names = []
        for p in config["plugins"]:
            if isinstance(p, str):
                plugin_names.append(p)
            elif isinstance(p, dict):
                plugin_names.extend(p.keys())
        assert "search" in plugin_names, "search plugin must be configured"
        assert "macros" in plugin_names, "macros plugin must be configured"

    def test_markdown_extensions_configured(self):
        """Req 3.10: Required markdown extensions must be present."""
        config = load_mkdocs_config()
        extensions = []
        for ext in config["markdown_extensions"]:
            if isinstance(ext, str):
                extensions.append(ext)
            elif isinstance(ext, dict):
                extensions.extend(ext.keys())
        required = ["admonition", "attr_list", "md_in_html", "toc"]
        for req in required:
            assert req in extensions, f"Missing required extension: {req}"

    def test_hooks_file_exists(self):
        """Req 3.10: Build hooks referenced in config must exist."""
        config = load_mkdocs_config()
        hooks = config.get("hooks", [])
        for hook_path in hooks:
            full_path = ROOT / hook_path
            assert full_path.exists(), f"Hook file not found: {hook_path}"

    def test_macros_module_exists(self):
        """Req 3.10: The macros module referenced in config must exist."""
        config = load_mkdocs_config()
        for p in config.get("plugins", []):
            if isinstance(p, dict) and "macros" in p:
                module_name = p["macros"].get("module_name")
                if module_name:
                    module_path = ROOT / (module_name + ".py")
                    assert module_path.exists(), f"Macros module not found: {module_name}.py"


# ---------------------------------------------------------------------------
# Requirement 3.8: Navigation structure functions properly
# ---------------------------------------------------------------------------

class TestNavigationStructure:
    """Preservation: Navigation structure must remain functional."""

    def test_nav_section_exists(self):
        """Req 3.8: nav section must exist in mkdocs.yml."""
        config = load_mkdocs_config()
        assert "nav" in config, "nav section missing from mkdocs.yml"
        assert isinstance(config["nav"], list), "nav must be a list"
        assert len(config["nav"]) > 0, "nav must not be empty"

    def test_top_level_sections_present(self):
        """Req 3.8: Expected top-level navigation sections must be present."""
        config = load_mkdocs_config()
        nav = config["nav"]
        section_names = []
        for item in nav:
            if isinstance(item, dict):
                section_names.extend(item.keys())
            elif isinstance(item, str):
                section_names.append(item)
        # The three main documentation sections
        expected = ["User Manual", "Developer Guide", "Documentation Guide"]
        for section in expected:
            assert section in section_names, f"Missing top-level section: {section}"

    def test_nav_files_exist(self):
        """Req 3.8: All files referenced in nav must exist on disk."""
        config = load_mkdocs_config()
        nav_paths = collect_nav_paths(config["nav"])
        missing = []
        for p in nav_paths:
            # Skip external URLs and HTML files (API reference)
            if p.startswith("http") or p.endswith(".html"):
                continue
            full = ROOT / config["docs_dir"] / p
            if not full.exists():
                missing.append(p)
        assert len(missing) == 0, (
            f"{len(missing)} nav entries point to missing files. "
            f"First 5: {missing[:5]}"
        )

    def test_nav_has_index_pages(self):
        """Req 3.8: Major sections should have index pages."""
        config = load_mkdocs_config()
        nav_paths = collect_nav_paths(config["nav"])
        index_pages = [p for p in nav_paths if p.endswith("index.md")]
        # There should be many index pages for section landing pages
        assert len(index_pages) >= 10, (
            f"Expected at least 10 index pages in nav, found {len(index_pages)}"
        )

    def test_nav_no_duplicate_entries(self):
        """Req 3.8: Nav should not have duplicate file entries."""
        config = load_mkdocs_config()
        nav_paths = collect_nav_paths(config["nav"])
        # Filter out HTML/external
        md_paths = [p for p in nav_paths if not p.startswith("http") and p.endswith(".md")]
        seen = set()
        duplicates = []
        for p in md_paths:
            if p in seen:
                duplicates.append(p)
            seen.add(p)
        assert len(duplicates) == 0, (
            f"Duplicate nav entries found: {duplicates[:5]}"
        )

    def test_user_manual_has_expected_subsections(self):
        """Req 3.8: User Manual must have key subsections."""
        config = load_mkdocs_config()
        nav = config["nav"]
        user_manual = None
        for item in nav:
            if isinstance(item, dict) and "User Manual" in item:
                user_manual = item["User Manual"]
                break
        assert user_manual is not None, "User Manual section not found"

        # Collect subsection names
        subsection_names = []
        for entry in user_manual:
            if isinstance(entry, dict):
                subsection_names.extend(entry.keys())

        expected_subsections = [
            "Introduction", "Installation", "Data", "Styling",
            "Services", "Security", "Extensions",
        ]
        for sub in expected_subsections:
            assert sub in subsection_names, (
                f"Missing User Manual subsection: {sub}"
            )

    def test_navigation_indexes_feature_enabled(self):
        """Req 3.8: navigation.indexes feature must be enabled for section index pages."""
        config = load_mkdocs_config()
        features = config.get("theme", {}).get("features", [])
        assert "navigation.indexes" in features, (
            "navigation.indexes feature must be enabled"
        )


# ---------------------------------------------------------------------------
# Requirement 3.9: Page metadata is preserved
# ---------------------------------------------------------------------------

# Pages known to have frontmatter with render_macros
PAGES_WITH_FRONTMATTER = [
    "doc/en/user/index.md",
    "doc/en/developer/index.md",
    "doc/en/docguide/index.md",
]

# Sample pages that should NOT have frontmatter (plain content pages)
PAGES_WITHOUT_FRONTMATTER = [
    "doc/en/user/introduction/overview.md",
    "doc/en/user/introduction/history.md",
    "doc/en/user/introduction/license.md",
    "doc/en/user/production/java.md",
]


class TestPageMetadata:
    """Preservation: Page metadata (frontmatter) must be preserved."""

    @pytest.mark.parametrize("page_path", PAGES_WITH_FRONTMATTER)
    def test_frontmatter_preserved(self, page_path):
        """Req 3.9: Pages with frontmatter must retain their YAML frontmatter."""
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"File not found: {page_path}")
        assert content.startswith("---"), (
            f"{page_path} should start with YAML frontmatter (---)"
        )
        fm = extract_frontmatter(content)
        assert len(fm) > 0, f"{page_path} frontmatter is empty"

    @pytest.mark.parametrize("page_path", PAGES_WITH_FRONTMATTER)
    def test_render_macros_metadata(self, page_path):
        """Req 3.9: Index pages with macros must have render_macros: true."""
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"File not found: {page_path}")
        fm = extract_frontmatter(content)
        assert fm.get("render_macros") is True, (
            f"{page_path} must have render_macros: true in frontmatter"
        )

    @pytest.mark.parametrize("page_path", PAGES_WITHOUT_FRONTMATTER)
    def test_plain_pages_have_h1_title(self, page_path):
        """Req 3.9: Pages without frontmatter must still have an H1 title."""
        content = read_md_file(page_path)
        if content is None:
            pytest.skip(f"File not found: {page_path}")
        # Strip any leading whitespace/blank lines
        stripped = content.lstrip()
        # Should start with # (H1) or have frontmatter then #
        has_h1 = bool(re.search(r'^# .+', stripped, re.MULTILINE))
        assert has_h1, f"{page_path} must have an H1 title"

    def test_version_macros_module_defines_variables(self):
        """Req 3.9: The version macros module must define expected variables."""
        version_py = ROOT / "doc" / "version.py"
        assert version_py.exists(), "doc/version.py not found"
        content = version_py.read_text(encoding="utf-8")
        # Check that key variables are defined
        assert "env.variables['version']" in content, "version variable not defined"
        assert "env.variables['release']" in content, "release variable not defined"

    def test_exclude_docs_configured(self):
        """Req 3.9: exclude_docs must be configured to skip include-only files."""
        config = load_mkdocs_config()
        assert "exclude_docs" in config, "exclude_docs section missing"
        exclude = config["exclude_docs"]
        assert isinstance(exclude, str), "exclude_docs must be a string"
        assert len(exclude.strip()) > 0, "exclude_docs must not be empty"


# ---------------------------------------------------------------------------
# Requirement 3.7: Theme and styling work correctly
# ---------------------------------------------------------------------------

class TestThemeAndStyling:
    """Preservation: Theme configuration and custom styling must remain functional."""

    def test_theme_is_material(self):
        """Req 3.7: Theme must be 'material'."""
        config = load_mkdocs_config()
        theme = config.get("theme", {})
        assert theme.get("name") == "material", "Theme must be 'material'"

    def test_custom_dir_exists(self):
        """Req 3.7: Custom theme directory must exist."""
        config = load_mkdocs_config()
        custom_dir = config.get("theme", {}).get("custom_dir")
        assert custom_dir is not None, "custom_dir not set in theme"
        full_path = ROOT / custom_dir
        assert full_path.is_dir(), f"Custom theme dir not found: {custom_dir}"

    def test_logo_and_favicon_exist(self):
        """Req 3.7: Logo and favicon files must exist."""
        config = load_mkdocs_config()
        theme = config.get("theme", {})
        custom_dir = theme.get("custom_dir", "")
        logo = theme.get("logo")
        favicon = theme.get("favicon")
        if logo:
            # Logo/favicon paths resolve via custom_dir (theme override directory)
            logo_path = ROOT / custom_dir / logo
            assert logo_path.exists(), f"Logo not found: {logo} (checked {logo_path})"
        if favicon:
            favicon_path = ROOT / custom_dir / favicon
            assert favicon_path.exists(), f"Favicon not found: {favicon} (checked {favicon_path})"

    def test_extra_css_files_exist(self):
        """Req 3.7: Extra CSS files referenced in config must exist."""
        config = load_mkdocs_config()
        custom_dir = config.get("theme", {}).get("custom_dir", config["docs_dir"])
        extra_css = config.get("extra_css", [])
        for css_path in extra_css:
            # extra_css/js are served from custom_dir in Material theme
            full_path = ROOT / custom_dir / css_path
            assert full_path.exists(), f"Extra CSS not found: {css_path} (checked {full_path})"

    def test_extra_javascript_files_exist(self):
        """Req 3.7: Extra JavaScript files referenced in config must exist."""
        config = load_mkdocs_config()
        custom_dir = config.get("theme", {}).get("custom_dir", config["docs_dir"])
        extra_js = config.get("extra_javascript", [])
        for js_path in extra_js:
            full_path = ROOT / custom_dir / js_path
            assert full_path.exists(), f"Extra JS not found: {js_path} (checked {full_path})"

    def test_palette_has_light_and_dark_modes(self):
        """Req 3.7: Theme palette must support light and dark modes."""
        config = load_mkdocs_config()
        palette = config.get("theme", {}).get("palette", [])
        assert isinstance(palette, list), "palette must be a list"
        assert len(palette) >= 2, "palette must have at least light and dark modes"
        schemes = [p.get("scheme") for p in palette]
        assert "default" in schemes, "Light mode (default scheme) missing"
        assert "slate" in schemes, "Dark mode (slate scheme) missing"

    def test_theme_features_configured(self):
        """Req 3.7: Key theme features must be enabled."""
        config = load_mkdocs_config()
        features = config.get("theme", {}).get("features", [])
        required_features = [
            "search.suggest",
            "search.highlight",
            "content.code.copy",
            "navigation.tabs",
            "navigation.top",
            "navigation.indexes",
        ]
        for feat in required_features:
            assert feat in features, f"Missing theme feature: {feat}"

    def test_extra_css_has_page_contents_label(self):
        """Req 3.7: Custom CSS must include 'Page Contents' label override."""
        css_path = ROOT / "doc" / "themes" / "geoserver" / "stylesheets" / "extra.css"
        assert css_path.exists(), "extra.css not found"
        content = css_path.read_text(encoding="utf-8")
        assert "Page Contents" in content, (
            "extra.css must contain 'Page Contents' label customization"
        )

    def test_hide_empty_toc_js_exists(self):
        """Req 3.7: JavaScript to hide empty TOC must exist."""
        js_path = ROOT / "doc" / "themes" / "geoserver" / "javascripts" / "hide-empty-toc.js"
        assert js_path.exists(), "hide-empty-toc.js not found"
        content = js_path.read_text(encoding="utf-8")
        assert "md-nav--secondary" in content, (
            "hide-empty-toc.js must target secondary nav elements"
        )

    def test_admonition_extension_enabled(self):
        """Req 3.7: Admonition extension must be enabled for styled note/warning boxes."""
        config = load_mkdocs_config()
        extensions = []
        for ext in config.get("markdown_extensions", []):
            if isinstance(ext, str):
                extensions.append(ext)
            elif isinstance(ext, dict):
                extensions.extend(ext.keys())
        assert "admonition" in extensions, "admonition extension must be enabled"
        assert "pymdownx.details" in extensions, "pymdownx.details extension must be enabled"
        assert "pymdownx.superfences" in extensions, "pymdownx.superfences must be enabled"

    def test_code_highlighting_extensions_enabled(self):
        """Req 3.7: Code highlighting extensions must be enabled."""
        config = load_mkdocs_config()
        extensions = []
        for ext in config.get("markdown_extensions", []):
            if isinstance(ext, str):
                extensions.append(ext)
            elif isinstance(ext, dict):
                extensions.extend(ext.keys())
        assert "pymdownx.highlight" in extensions, "pymdownx.highlight must be enabled"
        assert "pymdownx.inlinehilite" in extensions, "pymdownx.inlinehilite must be enabled"
