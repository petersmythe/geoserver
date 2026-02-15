#!/usr/bin/env python3
"""
Bundle GeoWebCache REST API into the unified GeoServer OpenAPI specification.
This script reads the modular rest-gwc.yaml and merges it into the bundled specs.
"""

import json
import yaml
import sys
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

def merge_gwc_into_bundled(bundled_spec, gwc_spec):
    """Merge GWC REST API paths into bundled specification"""
    
    # Ensure paths dict exists
    if 'paths' not in bundled_spec:
        bundled_spec['paths'] = {}
    
    # Add GWC paths
    if 'paths' in gwc_spec:
        for path, path_item in gwc_spec['paths'].items():
            bundled_spec['paths'][path] = path_item
            print(f"  Added path: {path}")
    
    # Ensure tags list exists
    if 'tags' not in bundled_spec:
        bundled_spec['tags'] = []
    
    # Check if REST GWC tag already exists
    has_gwc_tag = any(tag.get('name') == 'REST GWC' for tag in bundled_spec['tags'])
    if not has_gwc_tag:
        # Add REST GWC tag if not present
        bundled_spec['tags'].append({
            'name': 'REST GWC',
            'description': 'REST API endpoints for GeoWebCache tile caching'
        })
        print("  Added REST GWC tag")
    
    # Merge security schemes if present
    if 'components' in gwc_spec and 'securitySchemes' in gwc_spec['components']:
        if 'components' not in bundled_spec:
            bundled_spec['components'] = {}
        if 'securitySchemes' not in bundled_spec['components']:
            bundled_spec['components']['securitySchemes'] = {}
        
        for scheme_name, scheme_def in gwc_spec['components']['securitySchemes'].items():
            if scheme_name not in bundled_spec['components']['securitySchemes']:
                bundled_spec['components']['securitySchemes'][scheme_name] = scheme_def
                print(f"  Added security scheme: {scheme_name}")
    
    return bundled_spec

def main():
    """Main function"""
    base_dir = Path(__file__).parent
    
    # Load GWC REST API spec
    gwc_spec_path = base_dir / 'specs' / 'rest' / 'rest-gwc.yaml'
    print(f"Loading GWC REST API spec from: {gwc_spec_path}")
    gwc_spec = load_yaml(gwc_spec_path)
    print(f"  Found {len(gwc_spec.get('paths', {}))} GWC paths")
    
    # Load bundled YAML spec
    bundled_yaml_path = Path('doc/en/api/geoserver-bundled.yaml')
    print(f"\nLoading bundled YAML spec from: {bundled_yaml_path}")
    bundled_yaml = load_yaml(bundled_yaml_path)
    
    # Load bundled JSON spec
    bundled_json_path = Path('doc/en/api/geoserver-bundled.json')
    print(f"Loading bundled JSON spec from: {bundled_json_path}")
    bundled_json = load_json(bundled_json_path)
    
    # Merge GWC into both formats
    print("\nMerging GWC REST API into bundled YAML...")
    bundled_yaml = merge_gwc_into_bundled(bundled_yaml, gwc_spec)
    
    print("\nMerging GWC REST API into bundled JSON...")
    bundled_json = merge_gwc_into_bundled(bundled_json, gwc_spec)
    
    # Sort paths alphabetically
    print("\nSorting paths alphabetically...")
    bundled_yaml['paths'] = dict(sorted(bundled_yaml['paths'].items()))
    bundled_json['paths'] = dict(sorted(bundled_json['paths'].items()))
    
    # Save updated bundled specs
    print(f"\nSaving updated bundled YAML to: {bundled_yaml_path}")
    save_yaml(bundled_yaml, bundled_yaml_path)
    
    print(f"Saving updated bundled JSON to: {bundled_json_path}")
    save_json(bundled_json, bundled_json_path)
    
    print("\n✓ Successfully merged GeoWebCache REST API into bundled specifications")
    print(f"  Total paths in bundled spec: {len(bundled_yaml['paths'])}")
    
    # Count GWC paths
    gwc_paths = [p for p in bundled_yaml['paths'].keys() if p.startswith('/gwc/rest')]
    print(f"  GeoWebCache REST paths: {len(gwc_paths)}")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
