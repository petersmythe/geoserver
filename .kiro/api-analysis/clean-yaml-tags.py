#!/usr/bin/env python3
"""
Fix YAML structure after OrderedDict sorting.
Re-write the YAML file with proper structure.
"""

import json
from pathlib import Path
import yaml

def fix_yaml_structure(yaml_path, json_path):
    """Fix YAML by loading from JSON and re-writing."""
    print(f"Fixing YAML structure: {yaml_path}")
    
    # Load from JSON (which doesn't have the OrderedDict issue)
    with open(json_path, 'r', encoding='utf-8') as f:
        spec_data = json.load(f)
    
    # Write as proper YAML
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(spec_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    
    print(f"  Fixed: {yaml_path}")

def main():
    """Main execution."""
    base_dir = Path(__file__).parent
    
    print("=== Fixing YAML Structure ===\n")
    
    bundled_yaml = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.yaml'
    bundled_json = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.json'
    
    if bundled_yaml.exists() and bundled_json.exists():
        fix_yaml_structure(bundled_yaml, bundled_json)
    else:
        print(f"Warning: Files not found")
    
    print("\n=== YAML Structure Fix Complete ===")

if __name__ == '__main__':
    main()
