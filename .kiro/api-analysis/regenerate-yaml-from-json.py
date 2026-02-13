#!/usr/bin/env python3
"""
Regenerate YAML from JSON to fix broken YAML structure.

The JSON file is correct, so we'll use it as the source of truth
and regenerate the YAML file properly.
"""

import json
import yaml
from pathlib import Path

def regenerate_yaml_from_json(json_path, yaml_path):
    """Load JSON and save as proper YAML."""
    print(f"Loading JSON: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"  Loaded {len(data.get('paths', {}))} paths")
    
    print(f"Writing YAML: {yaml_path}")
    
    # Use yaml.dump with sort_keys=False to maintain order
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
    
    print(f"  Written successfully")

def main():
    """Main execution."""
    base_dir = Path(__file__).parent
    
    print("\n=== Regenerating YAML from JSON ===")
    
    # Regenerate bundled YAML from JSON
    bundled_json = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.json'
    bundled_yaml = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.yaml'
    
    if bundled_json.exists() and bundled_yaml.exists():
        regenerate_yaml_from_json(bundled_json, bundled_yaml)
    else:
        if not bundled_json.exists():
            print(f"Error: {bundled_json} not found")
        if not bundled_yaml.exists():
            print(f"Error: {bundled_yaml} not found")
    
    print("\n=== YAML Regeneration Complete ===")

if __name__ == '__main__':
    main()
