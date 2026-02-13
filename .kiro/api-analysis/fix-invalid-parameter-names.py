#!/usr/bin/env python3
"""
Fix invalid parameter names in the OpenAPI spec.

Issue: Parameter named "ext:xml|json" which is invalid.
This should be removed since the path /security/authproviders doesn't have path variables.
"""

import json
from pathlib import Path

def fix_json_spec(json_path):
    """Fix invalid parameter names in JSON spec."""
    print(f"Loading: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    fixed_count = 0
    
    # Check all paths
    for path, path_item in spec.get('paths', {}).items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                if 'parameters' in operation:
                    # Filter out invalid parameters
                    original_params = operation['parameters']
                    valid_params = []
                    
                    for param in original_params:
                        param_name = param.get('name', '')
                        # Check if parameter name contains invalid characters
                        if ':' in param_name or '|' in param_name:
                            print(f"  Removing invalid parameter '{param_name}' from {method.upper()} {path}")
                            fixed_count += 1
                        else:
                            valid_params.append(param)
                    
                    operation['parameters'] = valid_params
                
                # Also fix summary if it contains the old path
                if 'summary' in operation:
                    old_summary = operation['summary']
                    # Fix summary that still references old path
                    if '.{ext:xml|json' in old_summary:
                        operation['summary'] = old_summary.replace('/.{ext:xml|json', '/security/authproviders')
                        print(f"  Fixed summary for {method.upper()} {path}")
                        fixed_count += 1
    
    print(f"Fixed {fixed_count} issues")
    
    # Write back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    print(f"Written to: {json_path}")

def main():
    """Main execution."""
    base_dir = Path(__file__).parent
    
    print("\n=== Fixing Invalid Parameter Names ===")
    
    # Fix bundled JSON
    bundled_json = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.json'
    
    if bundled_json.exists():
        fix_json_spec(bundled_json)
    else:
        print(f"Error: {bundled_json} not found")
    
    print("\n=== Fix Complete ===")
    print("\nNow regenerate YAML from JSON using: python regenerate-yaml-from-json.py")

if __name__ == '__main__':
    main()
