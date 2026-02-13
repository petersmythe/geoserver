#!/usr/bin/env python3
"""
Fix Python-specific YAML tags that break Swagger UI.

The issue: PyYAML's dump() with OrderedDict creates !!python/object/apply:collections.OrderedDict
tags which are not standard YAML and break Swagger UI.

Solution: Remove the Python-specific tag from the file.
"""

import re
from pathlib import Path

def fix_yaml_file(input_path, output_path):
    """Fix YAML file by removing Python-specific tags."""
    print(f"Processing: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the Python-specific OrderedDict tag
    # Pattern: paths: !!python/object/apply:collections.OrderedDict
    # Replace with just: paths:
    original_content = content
    content = re.sub(
        r'^(paths:)\s*!!python/object/apply:collections\.OrderedDict\s*$',
        r'\1',
        content,
        flags=re.MULTILINE
    )
    
    if content != original_content:
        print("  Removed Python-specific OrderedDict tag")
    else:
        print("  No Python-specific tags found")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Written to: {output_path}")

def main():
    """Main execution."""
    base_dir = Path(__file__).parent
    
    print("\n=== Fixing Python-Specific YAML Tags ===")
    
    # Fix bundled YAML
    bundled_yaml = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.yaml'
    
    if bundled_yaml.exists():
        fix_yaml_file(bundled_yaml, bundled_yaml)
    else:
        print(f"Warning: {bundled_yaml} not found")
    
    print("\n=== YAML Fix Complete ===")

if __name__ == '__main__':
    main()
