#!/usr/bin/env python3
"""
YAML Configuration Validation Script

Validates the unified mkdocs.yml configuration:
- Parses YAML structure
- Validates all nav paths exist in filesystem
- Checks theme configuration is valid
"""

import sys
import yaml
from pathlib import Path


def parse_mkdocs_config(config_path):
    """Parse mkdocs.yml and return configuration."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"✓ Successfully parsed {config_path}")
        return config
    except yaml.YAMLError as e:
        print(f"✗ YAML parsing error: {e}")
        return None
    except FileNotFoundError:
        print(f"✗ Configuration file not found: {config_path}")
        return None


def extract_nav_paths(nav_structure, paths=None):
    """Recursively extract all file paths from nav structure."""
    if paths is None:
        paths = []
    
    if isinstance(nav_structure, list):
        for item in nav_structure:
            extract_nav_paths(item, paths)
    elif isinstance(nav_structure, dict):
        for key, value in nav_structure.items():
            if isinstance(value, str):
                # This is a file path
                paths.append(value)
            else:
                # Recurse into nested structure
                extract_nav_paths(value, paths)
    elif isinstance(nav_structure, str):
        paths.append(nav_structure)
    
    return paths


def validate_nav_paths(config, workspace_root):
    """Validate that all nav paths exist in filesystem."""
    nav = config.get('nav', [])
    docs_dir = config.get('docs_dir', 'docs')
    
    nav_paths = extract_nav_paths(nav)
    print(f"\n📋 Found {len(nav_paths)} paths in navigation")
    
    missing_paths = []
    valid_paths = []
    
    for nav_path in nav_paths:
        # Skip external URLs and HTML files (like API reference)
        if nav_path.startswith('http') or nav_path.endswith('.html'):
            print(f"  ⊙ Skipping external/HTML: {nav_path}")
            continue
        
        # Construct full path: workspace_root / docs_dir / nav_path
        full_path = workspace_root / docs_dir / nav_path
        
        if full_path.exists():
            valid_paths.append(nav_path)
            print(f"  ✓ {nav_path}")
        else:
            missing_paths.append(nav_path)
            print(f"  ✗ Missing: {nav_path} (expected at {full_path})")
    
    print(f"\n📊 Validation Results:")
    print(f"  Valid paths: {len(valid_paths)}")
    print(f"  Missing paths: {len(missing_paths)}")
    
    return len(missing_paths) == 0


def validate_theme_config(config):
    """Validate theme configuration."""
    theme = config.get('theme', {})
    
    if not theme:
        print("\n✗ No theme configuration found")
        return False
    
    print("\n🎨 Theme Configuration:")
    
    # Check theme name
    theme_name = theme.get('name')
    if theme_name:
        print(f"  ✓ Theme name: {theme_name}")
    else:
        print("  ✗ Missing theme name")
        return False
    
    # Check custom_dir
    custom_dir = theme.get('custom_dir')
    if custom_dir:
        print(f"  ✓ Custom directory: {custom_dir}")
    else:
        print("  ⊙ No custom directory specified")
    
    # Check features
    features = theme.get('features', [])
    print(f"  ✓ Features: {len(features)} configured")
    
    # Check for navigation tabs
    if 'navigation.tabs' in features:
        print("    ✓ navigation.tabs enabled")
    else:
        print("    ✗ navigation.tabs NOT enabled")
        return False
    
    if 'navigation.tabs.sticky' in features:
        print("    ✓ navigation.tabs.sticky enabled")
    else:
        print("    ⊙ navigation.tabs.sticky not enabled (optional)")
    
    return True


def validate_required_fields(config):
    """Validate required configuration fields."""
    print("\n📝 Required Fields:")
    
    required_fields = ['site_name', 'site_url', 'docs_dir', 'site_dir', 'theme', 'nav']
    all_present = True
    
    for field in required_fields:
        if field in config:
            value = config[field]
            if isinstance(value, (dict, list)):
                print(f"  ✓ {field}: <{type(value).__name__}>")
            else:
                print(f"  ✓ {field}: {value}")
        else:
            print(f"  ✗ Missing required field: {field}")
            all_present = False
    
    return all_present


def main():
    """Main validation function."""
    workspace_root = Path.cwd()
    config_path = workspace_root / 'mkdocs.yml'
    
    print("=" * 60)
    print("MkDocs Configuration Validation")
    print("=" * 60)
    print(f"Workspace: {workspace_root}")
    print(f"Config: {config_path}")
    print()
    
    # Parse configuration
    config = parse_mkdocs_config(config_path)
    if not config:
        sys.exit(1)
    
    # Validate required fields
    if not validate_required_fields(config):
        print("\n❌ Required fields validation FAILED")
        sys.exit(1)
    
    # Validate theme configuration
    if not validate_theme_config(config):
        print("\n❌ Theme configuration validation FAILED")
        sys.exit(1)
    
    # Validate nav paths
    if not validate_nav_paths(config, workspace_root):
        print("\n❌ Navigation paths validation FAILED")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All validations PASSED")
    print("=" * 60)
    sys.exit(0)


if __name__ == '__main__':
    main()
