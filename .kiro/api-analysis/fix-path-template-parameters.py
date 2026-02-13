#!/usr/bin/env python3
"""
Fix path template parameter mismatches in the bundled OpenAPI spec.

Issue: Paths contain regex patterns like {folder:.*} but parameters don't match.
Solution: Remove regex from path template and add proper parameter definitions.
"""

import json
import yaml

def fix_path_parameters(spec):
    """Fix path template parameters that contain regex patterns."""
    
    paths_to_fix = {
        "/gsr/services/{folder:.*}": {
            "new_path": "/gsr/services/{folder}",
            "parameter": {
                "name": "folder",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string",
                    "pattern": ".*"
                },
                "description": "The folder path parameter"
            }
        },
        "/rest/imports/{importId}/data/files/{fileName:.+}": {
            "new_path": "/rest/imports/{importId}/data/files/{fileName}",
            "parameter": {
                "name": "fileName",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string",
                    "pattern": ".+"
                },
                "description": "The fileName parameter"
            }
        },
        "/rest/workspaces/{workspaceName}/coveragestores/{storeName}/coverages/{coverageName}/index/granules/{granuleId:.+}": {
            "new_path": "/rest/workspaces/{workspaceName}/coveragestores/{storeName}/coverages/{coverageName}/index/granules/{granuleId}",
            "parameter": {
                "name": "granuleId",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string",
                    "pattern": ".+"
                },
                "description": "The granuleId parameter"
            }
        }
    }
    
    # Fix paths
    if 'paths' in spec:
        new_paths = {}
        for path, path_item in spec['paths'].items():
            if path in paths_to_fix:
                fix_info = paths_to_fix[path]
                new_path = fix_info['new_path']
                
                print(f"Fixing path: {path}")
                print(f"  -> New path: {new_path}")
                
                # Add parameter to all operations in this path
                for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    if method in path_item:
                        operation = path_item[method]
                        
                        # Ensure parameters array exists
                        if 'parameters' not in operation:
                            operation['parameters'] = []
                        
                        # Check if parameter already exists
                        param_name = fix_info['parameter']['name']
                        param_exists = any(p.get('name') == param_name for p in operation['parameters'])
                        
                        if not param_exists:
                            operation['parameters'].append(fix_info['parameter'])
                            print(f"    Added parameter '{param_name}' to {method.upper()} operation")
                
                new_paths[new_path] = path_item
            else:
                new_paths[path] = path_item
        
        spec['paths'] = new_paths
    
    return spec

def main():
    """Main function."""
    bundled_json = 'doc/en/api/geoserver-bundled.json'
    bundled_yaml = 'doc/en/api/geoserver-bundled.yaml'
    
    print("Loading bundled JSON spec...")
    with open(bundled_json, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    print("\nFixing path template parameters...")
    spec = fix_path_parameters(spec)
    
    print("\nWriting fixed JSON spec...")
    with open(bundled_json, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    
    print("Regenerating YAML from JSON...")
    with open(bundled_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("\n✓ Path template parameters fixed successfully!")
    print("\nFixed paths:")
    print("  1. /gsr/services/{folder:.*} -> /gsr/services/{folder}")
    print("  2. /rest/imports/{importId}/data/files/{fileName:.+} -> /rest/imports/{importId}/data/files/{fileName}")
    print("  3. /rest/workspaces/.../granules/{granuleId:.+} -> /rest/workspaces/.../granules/{granuleId}")

if __name__ == '__main__':
    main()
