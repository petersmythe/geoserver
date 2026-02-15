#!/usr/bin/env python3
"""
Fix missing path parameters in GeoWebCache REST API endpoints.
Path-level parameters need to be copied to each operation.
"""

import json
import yaml
from pathlib import Path

def load_yaml(file_path):
    """Load YAML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_yaml(data, file_path):
    """Save data as YAML"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)

def save_json(data, file_path):
    """Save data as JSON with pretty printing"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fix_gwc_parameters(spec):
    """Fix missing path parameters in GWC endpoints"""
    fixed_count = 0
    
    for path, path_item in spec.get('paths', {}).items():
        if not path.startswith('/gwc/rest'):
            continue
        
        # Get path-level parameters
        path_level_params = path_item.get('parameters', [])
        if not path_level_params:
            continue
        
        # For each operation, ensure path parameters are present
        for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
            if method not in path_item:
                continue
            
            operation = path_item[method]
            if not isinstance(operation, dict):
                continue
            
            # Get existing operation parameters
            if 'parameters' not in operation:
                operation['parameters'] = []
            
            # Get names of existing parameters
            existing_param_names = {p.get('name') for p in operation['parameters'] if isinstance(p, dict)}
            
            # Add missing path-level parameters to operation
            for param in path_level_params:
                if isinstance(param, dict) and param.get('name') not in existing_param_names:
                    operation['parameters'].append(param)
                    fixed_count += 1
                    print(f"  Added parameter '{param.get('name')}' to {method.upper()} {path}")
    
    return spec, fixed_count

def main():
    """Main function"""
    # Load bundled YAML spec
    bundled_yaml_path = Path('../../doc/en/api/geoserver-bundled.yaml')
    print(f"Loading bundled YAML spec from: {bundled_yaml_path}")
    bundled_yaml = load_yaml(bundled_yaml_path)
    
    # Load bundled JSON spec
    bundled_json_path = Path('../../doc/en/api/geoserver-bundled.json')
    print(f"Loading bundled JSON spec from: {bundled_json_path}")
    bundled_json = load_json(bundled_json_path)
    
    # Fix GWC parameters in both formats
    print("\nFixing GWC parameters in bundled YAML...")
    bundled_yaml, yaml_fixed = fix_gwc_parameters(bundled_yaml)
    
    print("\nFixing GWC parameters in bundled JSON...")
    bundled_json, json_fixed = fix_gwc_parameters(bundled_json)
    
    # Save updated bundled specs
    print(f"\nSaving updated bundled YAML to: {bundled_yaml_path}")
    save_yaml(bundled_yaml, bundled_yaml_path)
    
    print(f"Saving updated bundled JSON to: {bundled_json_path}")
    save_json(bundled_json, bundled_json_path)
    
    print(f"\n✓ Successfully fixed GWC parameters")
    print(f"  YAML: {yaml_fixed} parameters added")
    print(f"  JSON: {json_fixed} parameters added")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
