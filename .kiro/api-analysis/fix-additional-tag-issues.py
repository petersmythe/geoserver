#!/usr/bin/env python3
"""
Fix additional tag and path issues identified in task 15.5.

Subtasks:
- 15.5.8: Fix malformed path `/.{ext:xml|json}` in REST Security
- 15.5.9: Fix DELETE / endpoint path to /rest/metadata
- 15.5.10: Sort REST Extensions endpoints alphabetically
"""

import json
import yaml
from pathlib import Path
from collections import OrderedDict

def fix_malformed_authproviders_path(spec_data):
    """Fix the malformed /.{ext:xml|json} path to proper /security/authproviders path."""
    if 'paths' not in spec_data:
        return 0
    
    fixed_count = 0
    paths_to_remove = []
    paths_to_add = {}
    
    for path, path_item in spec_data['paths'].items():
        # Find the malformed path
        if path == '/.{ext:xml|json}':
            print(f"  Found malformed path: {path}")
            # This should be /security/authproviders with optional extension
            new_path = '/security/authproviders'
            paths_to_add[new_path] = path_item
            paths_to_remove.append(path)
            fixed_count += 1
    
    # Apply changes
    for path in paths_to_remove:
        del spec_data['paths'][path]
    for path, item in paths_to_add.items():
        spec_data['paths'][path] = item
    
    return fixed_count

def fix_delete_root_path(spec_data):
    """Fix DELETE / to DELETE /rest/metadata."""
    if 'paths' not in spec_data:
        return 0
    
    fixed_count = 0
    
    # Check if / exists and has DELETE method
    if '/' in spec_data['paths']:
        path_item = spec_data['paths']['/']
        if 'delete' in path_item:
            delete_op = path_item['delete']
            # Verify this is the metadata clearAll operation
            if 'operationId' in delete_op and 'MetaDataRestService' in delete_op['operationId']:
                print(f"  Found DELETE / (metadata clearAll)")
                # Move to /rest/metadata
                if '/rest/metadata' not in spec_data['paths']:
                    spec_data['paths']['/rest/metadata'] = {}
                spec_data['paths']['/rest/metadata']['delete'] = delete_op
                
                # Remove from /
                del path_item['delete']
                # If / has no other methods, remove it entirely
                if not path_item or all(k in ['description', 'summary', 'parameters'] for k in path_item.keys()):
                    del spec_data['paths']['/']
                
                fixed_count += 1
    
    return fixed_count

def sort_paths_alphabetically(spec_data):
    """Sort all paths alphabetically."""
    if 'paths' not in spec_data:
        return 0
    
    # Sort paths - use regular dict, not OrderedDict to avoid Python-specific YAML tags
    sorted_paths = dict(sorted(spec_data['paths'].items()))
    spec_data['paths'] = sorted_paths
    
    return len(sorted_paths)

def fix_yaml_spec(input_path, output_path):
    """Fix issues in YAML spec."""
    print(f"Processing YAML: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        spec_data = yaml.safe_load(f)
    
    # Fix malformed authproviders path
    count1 = fix_malformed_authproviders_path(spec_data)
    print(f"  Fixed {count1} malformed authproviders paths")
    
    # Fix DELETE / path
    count2 = fix_delete_root_path(spec_data)
    print(f"  Fixed {count2} DELETE / paths")
    
    # Sort paths alphabetically
    count3 = sort_paths_alphabetically(spec_data)
    print(f"  Sorted {count3} paths alphabetically")
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(spec_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"  Written to: {output_path}")

def fix_json_spec(input_path, output_path):
    """Fix issues in JSON spec."""
    print(f"Processing JSON: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        spec_data = json.load(f)
    
    # Fix malformed authproviders path
    count1 = fix_malformed_authproviders_path(spec_data)
    print(f"  Fixed {count1} malformed authproviders paths")
    
    # Fix DELETE / path
    count2 = fix_delete_root_path(spec_data)
    print(f"  Fixed {count2} DELETE / paths")
    
    # Sort paths alphabetically
    count3 = sort_paths_alphabetically(spec_data)
    print(f"  Sorted {count3} paths alphabetically")
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spec_data, f, indent=2)
    
    print(f"  Written to: {output_path}")

def main():
    """Main execution."""
    base_dir = Path(__file__).parent
    
    # Fix bundled specs (modular specs don't have these paths since they're placeholders)
    print("\n=== Fixing Bundled Specifications ===")
    bundled_yaml = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.yaml'
    bundled_json = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.json'
    
    if bundled_yaml.exists():
        fix_yaml_spec(bundled_yaml, bundled_yaml)
    else:
        print(f"Warning: {bundled_yaml} not found")
    
    if bundled_json.exists():
        fix_json_spec(bundled_json, bundled_json)
    else:
        print(f"Warning: {bundled_json} not found")
    
    print("\n=== Additional Tag Issues Fix Complete ===")

if __name__ == '__main__':
    main()
