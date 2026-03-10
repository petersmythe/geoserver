#!/usr/bin/env python3
"""
Path Resolution Test Script

Validates source-to-output path mapping:
- Verifies doc/en/user/index.md maps to mkdocs_output/en/user/index.html
- Validates /en/ appears in all output paths
- Tests path resolution logic
"""

import sys
import yaml
from pathlib import Path


def load_mkdocs_config(config_path):
    """Load mkdocs.yml configuration."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return None


def resolve_output_path(source_path, docs_dir, site_dir):
    """
    Resolve source path to expected output path.
    
    MkDocs strips docs_dir from output but preserves structure within it.
    Example: docs_dir='doc', source='doc/en/user/index.md' -> 'mkdocs_output/en/user/index.html'
    """
    # Remove docs_dir prefix
    if source_path.startswith(docs_dir + '/'):
        relative_path = source_path[len(docs_dir) + 1:]
    else:
        relative_path = source_path
    
    # Convert .md to .html
    if relative_path.endswith('.md'):
        relative_path = relative_path[:-3] + '.html'
    
    # Construct output path
    output_path = f"{site_dir}/{relative_path}"
    
    return output_path


def test_path_resolution(config, workspace_root):
    """Test path resolution for key documentation files."""
    docs_dir = config.get('docs_dir', 'docs')
    site_dir = config.get('site_dir', 'site')
    
    print("\n🔍 Testing Path Resolution")
    print(f"  docs_dir: {docs_dir}")
    print(f"  site_dir: {site_dir}")
    print()
    
    # Test cases: (source_path, expected_output_path)
    test_cases = [
        ('en/user/index.md', f'{site_dir}/en/user/index.html'),
        ('en/developer/index.md', f'{site_dir}/en/developer/index.html'),
        ('en/docguide/index.md', f'{site_dir}/en/docguide/index.html'),
        ('en/user/introduction/index.md', f'{site_dir}/en/user/introduction/index.html'),
        ('en/developer/introduction.md', f'{site_dir}/en/developer/introduction.html'),
    ]
    
    all_passed = True
    
    for source_path, expected_output in test_cases:
        # Resolve output path
        actual_output = resolve_output_path(source_path, docs_dir, site_dir)
        
        # Check if it matches expected
        if actual_output == expected_output:
            print(f"  ✓ {source_path}")
            print(f"    → {actual_output}")
        else:
            print(f"  ✗ {source_path}")
            print(f"    Expected: {expected_output}")
            print(f"    Got:      {actual_output}")
            all_passed = False
    
    return all_passed


def validate_en_in_paths(config):
    """Validate that /en/ appears in output paths."""
    docs_dir = config.get('docs_dir', 'docs')
    site_dir = config.get('site_dir', 'site')
    
    print("\n📍 Validating /en/ in Output Paths")
    
    # Sample paths from each manual
    sample_paths = [
        'en/user/index.md',
        'en/developer/index.md',
        'en/docguide/index.md',
    ]
    
    all_have_en = True
    
    for source_path in sample_paths:
        output_path = resolve_output_path(source_path, docs_dir, site_dir)
        
        if '/en/' in output_path:
            print(f"  ✓ {output_path} contains /en/")
        else:
            print(f"  ✗ {output_path} missing /en/")
            all_have_en = False
    
    return all_have_en


def test_actual_build_output(workspace_root, config):
    """Test actual build output if it exists."""
    site_dir = config.get('site_dir', 'site')
    output_dir = workspace_root / site_dir
    
    print(f"\n🏗️  Checking Build Output: {output_dir}")
    
    if not output_dir.exists():
        print("  ⊙ Build output directory does not exist (run 'mkdocs build' first)")
        return True  # Not a failure, just not built yet
    
    # Check for expected directory structure
    expected_dirs = [
        output_dir / 'en' / 'user',
        output_dir / 'en' / 'developer',
        output_dir / 'en' / 'docguide',
        output_dir / 'en' / 'api',
    ]
    
    all_exist = True
    
    for expected_dir in expected_dirs:
        if expected_dir.exists():
            # Count HTML files
            html_files = list(expected_dir.rglob('*.html'))
            print(f"  ✓ {expected_dir.relative_to(workspace_root)} ({len(html_files)} HTML files)")
        else:
            print(f"  ✗ Missing: {expected_dir.relative_to(workspace_root)}")
            all_exist = False
    
    # Check for index.html files
    print("\n  Checking index files:")
    index_files = [
        output_dir / 'en' / 'user' / 'index.html',
        output_dir / 'en' / 'developer' / 'index.html',
        output_dir / 'en' / 'docguide' / 'index.html',
    ]
    
    for index_file in index_files:
        if index_file.exists():
            print(f"    ✓ {index_file.relative_to(workspace_root)}")
        else:
            print(f"    ✗ Missing: {index_file.relative_to(workspace_root)}")
            all_exist = False
    
    return all_exist


def main():
    """Main validation function."""
    workspace_root = Path.cwd()
    config_path = workspace_root / 'mkdocs.yml'
    
    print("=" * 60)
    print("Path Resolution Validation")
    print("=" * 60)
    print(f"Workspace: {workspace_root}")
    print(f"Config: {config_path}")
    
    # Load configuration
    config = load_mkdocs_config(config_path)
    if not config:
        sys.exit(1)
    
    # Test path resolution logic
    if not test_path_resolution(config, workspace_root):
        print("\n❌ Path resolution tests FAILED")
        sys.exit(1)
    
    # Validate /en/ in paths
    if not validate_en_in_paths(config):
        print("\n❌ /en/ validation FAILED")
        sys.exit(1)
    
    # Test actual build output (if exists)
    if not test_actual_build_output(workspace_root, config):
        print("\n❌ Build output validation FAILED")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All path resolution tests PASSED")
    print("=" * 60)
    sys.exit(0)


if __name__ == '__main__':
    main()
